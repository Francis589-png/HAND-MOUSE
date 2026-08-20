"""Validation and normalization for HAND-MOUSE companion commands."""

from __future__ import annotations

import math
from typing import Any

ALLOWED_COMMANDS = frozenset({"move", "left_click", "right_click", "scroll", "key"})
MAX_SCROLL = 20
MAX_KEY_LENGTH = 64


def _finite_number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def validate_command(message: Any) -> dict[str, Any]:
    """Validate a JSON-decoded command and return a normalized copy.

    The validator deliberately accepts only a small command vocabulary. It
    never executes an OS action and therefore remains safe to test directly.
    """
    if not isinstance(message, dict):
        raise ValueError("command must be a JSON object")

    command = message.get("command")
    if command not in ALLOWED_COMMANDS:
        raise ValueError("unsupported command")

    if command == "move":
        x = _finite_number(message.get("x"), "x")
        y = _finite_number(message.get("y"), "y")
        if not 0.0 <= x <= 1.0 or not 0.0 <= y <= 1.0:
            raise ValueError("move coordinates must be between 0 and 1")
        return {"command": "move", "x": x, "y": y}

    if command in {"left_click", "right_click"}:
        return {"command": command}

    if command == "scroll":
        amount = _finite_number(message.get("amount"), "amount")
        if not amount.is_integer() or abs(amount) > MAX_SCROLL:
            raise ValueError(f"scroll amount must be an integer between {-MAX_SCROLL} and {MAX_SCROLL}")
        return {"command": "scroll", "amount": int(amount)}

    action = message.get("action")
    key = message.get("key")
    if action not in {"down", "up", "press"}:
        raise ValueError("key action must be down, up, or press")
    if not isinstance(key, str) or not key or len(key) > MAX_KEY_LENGTH:
        raise ValueError("key must be a non-empty string of at most 64 characters")
    return {"command": "key", "action": action, "key": key}
