"""Deterministic gesture state management for HAND-MOUSE.

This module intentionally contains no camera, MediaPipe, OpenCV, or OS input
code. Vision code can report a gesture candidate here, while this module is
responsible for confirmation, cooldowns, and safe state transitions.
"""

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
    """Timing and confirmation settings for :class:`GestureEngine`.

    ``confirmation_frames`` prevents a single noisy frame from triggering an
    action. ``cooldown_seconds`` prevents the same gesture from firing again
    immediately after it has been accepted.
    """

    confirmation_frames: int = 3
    cooldown_seconds: float = 0.5

    def __post_init__(self) -> None:
        if not isinstance(self.confirmation_frames, int) or isinstance(
            self.confirmation_frames, bool
        ):
            raise TypeError("confirmation_frames must be an integer")
        if self.confirmation_frames < 1:
            raise ValueError("confirmation_frames must be >= 1")
        if self.cooldown_seconds < 0:
            raise ValueError("cooldown_seconds must be >= 0")


class GestureEngine:
    """Convert noisy per-frame gesture candidates into discrete events.

    The engine is deterministic when a timestamp is supplied to ``update``.
    It does not perform any system input itself, making it safe to unit test.
    """

    def __init__(self, config: Optional[GestureConfig] = None) -> None:
        self.config = config or GestureConfig()
        self.current = Gesture.NONE
        self._candidate = Gesture.NONE
        self._candidate_frames = 0
        self._last_event_gesture = Gesture.NONE
        self._last_event_time: Optional[float] = None

    @property
    def candidate_frames(self) -> int:
        """Number of consecutive frames matching the current candidate."""
        return self._candidate_frames

    def reset(self) -> None:
        """Return the engine to its initial state."""
        self.current = Gesture.NONE
        self._candidate = Gesture.NONE
        self._candidate_frames = 0
        self._last_event_gesture = Gesture.NONE
        self._last_event_time = None

    def update(self, gesture: Gesture, timestamp: float) -> Optional[Gesture]:
        """Process one frame and return a newly confirmed gesture event.

        ``None`` means no new action should be triggered for this frame.
        ``Gesture.NONE`` is treated as the absence of a gesture and clears the
        confirmation counter.
        """
        if not isinstance(gesture, Gesture):
            try:
                gesture = Gesture(gesture)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"unknown gesture: {gesture!r}") from exc

        if not isinstance(timestamp, (int, float)) or isinstance(timestamp, bool):
            raise TypeError("timestamp must be a number")

        if gesture is Gesture.NONE:
            self.current = Gesture.NONE
            self._candidate = Gesture.NONE
            self._candidate_frames = 0
            return None

        if gesture is self._candidate:
            self._candidate_frames += 1
        else:
            self._candidate = gesture
            self._candidate_frames = 1

        self.current = gesture

        if self._candidate_frames < self.config.confirmation_frames:
            return None

        if self._last_event_gesture is gesture and self._last_event_time is not None:
            elapsed = timestamp - self._last_event_time
            if elapsed < 0:
                raise ValueError("timestamp must not move backwards")
            if elapsed < self.config.cooldown_seconds:
                return None

        self._last_event_gesture = gesture
        self._last_event_time = float(timestamp)
        return gesture
