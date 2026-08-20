"""Pure cursor-motion helpers for HAND-MOUSE.

This module deliberately has no operating-system or GUI dependencies. It
provides deterministic smoothing and coordinate mapping that can be tested
without a physical mouse or display.
"""

from dataclasses import dataclass
from math import isfinite
from typing import Tuple


def _finite_unit(value: float, name: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError(f"{name} must be a number")
    value = float(value)
    if not isfinite(value):
        raise ValueError(f"{name} must be finite")
    return max(0.0, min(1.0, value))


@dataclass(frozen=True)
class CursorSmoother:
    """Exponential cursor smoothing.

    ``alpha=1`` follows the newest point exactly. Smaller values retain more
    of the previous position and therefore reduce camera-induced jitter.
    """

    alpha: float = 0.35

    def __post_init__(self) -> None:
        if not isinstance(self.alpha, (int, float)) or isinstance(self.alpha, bool):
            raise TypeError("alpha must be a number")
        if not isfinite(float(self.alpha)):
            raise ValueError("alpha must be finite")
        if not 0.0 < float(self.alpha) <= 1.0:
            raise ValueError("alpha must be > 0 and <= 1")

    def update(
        self,
        previous: Tuple[float, float],
        target: Tuple[float, float],
    ) -> Tuple[float, float]:
        if len(previous) != 2 or len(target) != 2:
            raise ValueError("previous and target must contain exactly two coordinates")
        px = _finite_unit(previous[0], "previous.x")
        py = _finite_unit(previous[1], "previous.y")
        tx = _finite_unit(target[0], "target.x")
        ty = _finite_unit(target[1], "target.y")
        alpha = float(self.alpha)
        return (
            px + alpha * (tx - px),
            py + alpha * (ty - py),
        )


def normalized_to_screen(
    x_norm: float,
    y_norm: float,
    screen_size: Tuple[int, int],
) -> Tuple[int, int]:
    """Map normalized coordinates to valid zero-based screen pixels."""
    if len(screen_size) != 2:
        raise ValueError("screen_size must contain width and height")
    width, height = screen_size
    if not isinstance(width, int) or isinstance(width, bool) or width < 1:
        raise ValueError("screen width must be a positive integer")
    if not isinstance(height, int) or isinstance(height, bool) or height < 1:
        raise ValueError("screen height must be a positive integer")

    x = _finite_unit(x_norm, "x_norm")
    y = _finite_unit(y_norm, "y_norm")
    return (
        min(width - 1, int(x * width)),
        min(height - 1, int(y * height)),
    )
