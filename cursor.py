import pyautogui
from typing import Tuple

try:
    from .cursor_motion import CursorSmoother, normalized_to_screen
except ImportError:  # Supports direct loading used by lightweight test tooling.
    from cursor_motion import CursorSmoother, normalized_to_screen

pyautogui.FAILSAFE = False


class CursorController:
    """Wrapper around pyautogui for normalized cursor control.

    Smoothing is opt-in so existing callers keep the original direct-motion
    behavior when ``smoothing_alpha=1.0``.
    """

    def __init__(
        self,
        screen_size: Tuple[int, int] = None,
        smoothing_alpha: float = 1.0,
    ):
        if screen_size is None:
            self.screen_width, self.screen_height = pyautogui.size()
        else:
            self.screen_width, self.screen_height = screen_size
        self._smoother = CursorSmoother(smoothing_alpha)
        self._previous_position = None

    def move_to_norm(self, x_norm: float, y_norm: float) -> None:
        """Move cursor to normalized coordinates (0..1).

        With ``smoothing_alpha=1.0`` the target is used directly. Lower values
        move part of the distance toward each new target to reduce jitter.
        """
        target = (
            max(0.0, min(1.0, float(x_norm))),
            max(0.0, min(1.0, float(y_norm))),
        )
        if self._previous_position is None:
            position = target
        else:
            position = self._smoother.update(self._previous_position, target)
        self._previous_position = position
        x, y = normalized_to_screen(
            position[0], position[1], (self.screen_width, self.screen_height)
        )
        pyautogui.moveTo(x, y)

    def reset_motion(self) -> None:
        """Forget the previous position before starting a new tracking session."""
        self._previous_position = None

    def left_click(self) -> None:
        pyautogui.click()

    def right_click(self) -> None:
        pyautogui.click(button="right")

    def scroll(self, clicks: int) -> None:
        pyautogui.scroll(clicks)


_global = None


def get_controller() -> "CursorController":
    global _global
    if _global is None:
        _global = CursorController()
    return _global


def move_cursor(x_norm: float, y_norm: float):
    get_controller().move_to_norm(x_norm, y_norm)


def click():
    get_controller().left_click()
