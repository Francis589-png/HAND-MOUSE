import pyautogui
from typing import Tuple

pyautogui.FAILSAFE = False


class CursorController:
    """Simple wrapper around pyautogui for normalized cursor control."""
    def __init__(self, screen_size: Tuple[int, int] = None):
        if screen_size is None:
            self.screen_width, self.screen_height = pyautogui.size()
        else:
            self.screen_width, self.screen_height = screen_size

    def move_to_norm(self, x_norm: float, y_norm: float) -> None:
        """Move cursor to normalized coordinates (0..1).

        Args:
            x_norm: horizontal position normalized [0,1]
            y_norm: vertical position normalized [0,1]
        """
        x = int(max(0, min(1, x_norm)) * self.screen_width)
        y = int(max(0, min(1, y_norm)) * self.screen_height)
        pyautogui.moveTo(x, y)

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
