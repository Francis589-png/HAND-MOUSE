"""WebSocket desktop companion for HAND-MOUSE.

The browser owns camera/vision work. This process is responsible only for
authenticated OS input on the host. Non-loopback connections require TLS.
"""

from __future__ import annotations

import asyncio
import hmac
import json
import logging
import ssl
from dataclasses import dataclass
from typing import Any

try:
    import pyautogui
except ImportError as exc:  # pragma: no cover - exercised during installation
    raise RuntimeError("pyautogui is required to run the HAND-MOUSE companion") from exc

try:
    from websockets.asyncio.server import serve
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("websockets>=17 is required to run the HAND-MOUSE companion") from exc

from .protocol import validate_command

LOGGER = logging.getLogger("hand_mouse.companion")
MAX_MESSAGE_SIZE = 4096
MAX_AUTH_FAILURES = 5


@dataclass(frozen=True)
class CompanionConfig:
    host: str = "127.0.0.1"
    port: int = 8765
    token: str = ""
    origin: str | None = None
    certfile: str | None = None
    keyfile: str | None = None

    def __post_init__(self) -> None:
        if not self.token or len(self.token) < 16:
            raise ValueError("token must contain at least 16 characters")
        if not 1 <= self.port <= 65535:
            raise ValueError("port must be between 1 and 65535")
        if (self.certfile is None) != (self.keyfile is None):
            raise ValueError("certfile and keyfile must be provided together")
        if self.is_non_loopback and self.certfile is None:
            raise ValueError("TLS certificate and key are required for non-loopback hosts")

    @property
    def is_non_loopback(self) -> bool:
        return self.host not in {"127.0.0.1", "localhost", "::1"}

    @property
    def tls_enabled(self) -> bool:
        return self.certfile is not None


class CompanionServer:
    """Authenticated WebSocket server that executes validated OS commands."""

    def __init__(self, config: CompanionConfig) -> None:
        self.config = config

    def _ssl_context(self) -> ssl.SSLContext | None:
        if not self.config.tls_enabled:
            return None
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.load_cert_chain(self.config.certfile, self.config.keyfile)
        return context

    async def _send(self, websocket: Any, payload: dict[str, Any]) -> None:
        await websocket.send(json.dumps(payload, separators=(",", ":")))

    def _execute(self, command: dict[str, Any]) -> None:
        name = command["command"]
        if name == "move":
            width, height = pyautogui.size()
            x = min(width - 1, max(0, round(command["x"] * (width - 1))))
            y = min(height - 1, max(0, round(command["y"] * (height - 1))))
            pyautogui.moveTo(x, y)
        elif name == "left_click":
            pyautogui.click()
        elif name == "right_click":
            pyautogui.click(button="right")
        elif name == "scroll":
            pyautogui.scroll(command["amount"])
        elif name == "key":
            action = command["action"]
            key = command["key"]
            if action == "press":
                pyautogui.press(key)
            elif action == "down":
                pyautogui.keyDown(key)
            else:
                pyautogui.keyUp(key)

    async def handler(self, websocket: Any) -> None:
        authenticated = False
        auth_failures = 0
        try:
            async for raw in websocket:
                if not isinstance(raw, str) or len(raw.encode("utf-8")) > MAX_MESSAGE_SIZE:
                    await self._send(websocket, {"ok": False, "error": "message too large"})
                    await websocket.close(code=1009, reason="message too large")
                    return

                try:
                    message = json.loads(raw)
                    if not authenticated:
                        expected = self.config.token
                        supplied = message.get("token") if isinstance(message, dict) else None
                        if (
                            message.get("type") != "auth"
                            or not isinstance(supplied, str)
                            or not hmac.compare_digest(supplied, expected)
                        ):
                            auth_failures += 1
                            await self._send(websocket, {"ok": False, "error": "authentication failed"})
                            if auth_failures >= MAX_AUTH_FAILURES:
                                await websocket.close(code=1008, reason="too many authentication failures")
                                return
                            continue
                        authenticated = True
                        await self._send(websocket, {"ok": True, "type": "authenticated"})
                        continue

                    command = validate_command(message)
                    await asyncio.to_thread(self._execute, command)
                    await self._send(websocket, {"ok": True, "type": "executed", "command": command["command"]})
                except (ValueError, json.JSONDecodeError, TypeError) as exc:
                    await self._send(websocket, {"ok": False, "error": str(exc)})
                except Exception:
                    LOGGER.exception("OS input command failed")
                    await self._send(websocket, {"ok": False, "error": "OS input action failed"})
        except Exception:
            LOGGER.exception("WebSocket connection failed")

    async def run(self) -> None:
        origins = [self.config.origin] if self.config.origin else None
        ssl_context = self._ssl_context()
        LOGGER.info(
            "HAND-MOUSE companion listening on %s:%s (%s)",
            self.config.host,
            self.config.port,
            "TLS" if ssl_context else "local-only",
        )
        async with serve(
            self.handler,
            self.config.host,
            self.config.port,
            origins=origins,
            max_size=MAX_MESSAGE_SIZE,
            ssl=ssl_context,
        ):
            await asyncio.Future()
