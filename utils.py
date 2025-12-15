"""Utility helpers for coordinate conversions and small helpers."""

from typing import Tuple


def clamp01(v: float) -> float:
	return max(0.0, min(1.0, v))


def to_normalized(x: int, y: int, width: int, height: int) -> Tuple[float, float]:
	"""Convert pixel coordinates to normalized coordinates in [0,1]."""
	if width == 0 or height == 0:
		return 0.0, 0.0
	return clamp01(x / width), clamp01(y / height)


def normalized_to_screen(x_norm: float, y_norm: float, screen_size: Tuple[int, int]) -> Tuple[int, int]:
	w, h = screen_size
	return int(clamp01(x_norm) * w), int(clamp01(y_norm) * h)


def delta_to_scroll(delta_norm: float, scale: int = 800) -> int:
	"""Convert normalized vertical delta to scroll click amount.

	Positive delta_norm means pointer moved down; map to negative/positive scroll
	in a way that small deltas produce small scrolls.
	"""
	return int(delta_norm * scale)


class SmoothFilter:
	"""Simple exponential smoothing for 2D points.

	Usage:
		f = SmoothFilter(alpha=0.5)
		x_s, y_s = f.update(x, y)
	"""
	def __init__(self, alpha: float = 0.5):
		if not 0.0 < alpha <= 1.0:
			raise ValueError("alpha must be in (0,1]")
		self.alpha = alpha
		self._state = None

	def update(self, x: float, y: float) -> Tuple[float, float]:
		if self._state is None:
			self._state = (x, y)
			return x, y
		sx, sy = self._state
		nx = self.alpha * x + (1 - self.alpha) * sx
		ny = self.alpha * y + (1 - self.alpha) * sy
		self._state = (nx, ny)
		return nx, ny


class DwellSelector:
	"""Tracks a focused key and confirms selection after dwell time.

	- Call `update(key, now)` every frame with the currently focused `key` and
	  a monotonically increasing `now` (seconds). Returns True when the key
	  has been selected (dwell completed).
	- Use `progress` attribute to read dwell progress in [0,1].
	"""
	def __init__(self, threshold: float = 0.6):
		self.threshold = threshold
		self.current = None
		self.start = None
		self.progress = 0.0

	def update(self, key, now: float) -> bool:
		if key is None:
			self.current = None
			self.start = None
			self.progress = 0.0
			return False
		if key != self.current:
			self.current = key
			self.start = now
			self.progress = 0.0
			return False
		# same key
		elapsed = now - (self.start or now)
		self.progress = min(1.0, elapsed / self.threshold)
		if self.progress >= 1.0:
			# confirm and reset so next frame starts fresh
			self.last_elapsed = elapsed
			self.start = now
			self.progress = 0.0
			return True
		return False

