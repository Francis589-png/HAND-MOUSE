"""Deterministic gesture state management for HAND-MOUSE."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Gesture(str, Enum):
    """Gestures understood by the state engine."""

    NONE = "none"
    PINCH = "pinch"
    TWO_FINGER_PINCH = "two_finger_pinch"
    SWIPE_UP = "swipe_up"
    SWIPE_DOWN = "swipe_down"
    CLAP = "clap"


@dataclass(frozen=True)
class GestureConfig:
    """Confirmation settings for the gesture state machine."""

    confirmation_frames: int = 3
    cooldown_seconds: float = 0.5

    def __post_init__(self) -> None:
        if not isinstance(self.confirmation_frames, int) or isinstance(
            self.confirmation_frames, bool
        ):
            raise TypeError("confirmation_frames must be an integer")
        if self.confirmation_frames < 1:
            raise ValueError("confirmation_frames must be >= 1")
        if not isinstance(self.cooldown_seconds, (int, float)) or isinstance(
            self.cooldown_seconds, bool
        ):
            raise TypeError("cooldown_seconds must be a number")
        if self.cooldown_seconds < 0:
            raise ValueError("cooldown_seconds must be >= 0")


class GestureEngine:
    """Turn noisy per-frame candidates into one-shot gesture events.

    A gesture must remain present for ``confirmation_frames`` consecutive
    frames before it is emitted. Once emitted, it cannot fire again until the
    detector observes ``Gesture.NONE``. This edge-triggered behavior prevents
    one held pinch from generating a stream of clicks.

    The engine contains no camera, MediaPipe, OpenCV, or OS input code, so it
    can be tested independently of hardware.
    """

    def __init__(self, config: Optional[GestureConfig] = None) -> None:
        self.config = config or GestureConfig()
        self.current = Gesture.NONE
        self._candidate = Gesture.NONE
        self._candidate_frames = 0
        self._armed = True
        self._last_event_time: Optional[float] = None

    @property
    def candidate_frames(self) -> int:
        """Number of consecutive frames matching the current candidate."""
        return self._candidate_frames

    @property
    def armed(self) -> bool:
        """Whether a confirmed gesture is currently allowed to fire."""
        return self._armed

    def reset(self) -> None:
        """Return the engine to its initial state."""
        self.current = Gesture.NONE
        self._candidate = Gesture.NONE
        self._candidate_frames = 0
        self._armed = True
        self._last_event_time = None

    def update(self, gesture: Gesture, timestamp: float) -> Optional[Gesture]:
        """Process one frame and return a newly confirmed gesture event."""
        if not isinstance(gesture, Gesture):
            try:
                gesture = Gesture(gesture)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"unknown gesture: {gesture!r}") from exc

        if not isinstance(timestamp, (int, float)) or isinstance(timestamp, bool):
            raise TypeError("timestamp must be a number")
        if self._last_event_time is not None and timestamp < self._last_event_time:
            raise ValueError("timestamp must not move backwards")

        if gesture is Gesture.NONE:
            self.current = Gesture.NONE
            self._candidate = Gesture.NONE
            self._candidate_frames = 0
            self._armed = True
            return None

        if gesture is self._candidate:
            self._candidate_frames += 1
        else:
            self._candidate = gesture
            self._candidate_frames = 1

        self.current = gesture

        if not self._armed or self._candidate_frames < self.config.confirmation_frames:
            return None

        self._armed = False
        self._last_event_time = float(timestamp)
        return gesture
