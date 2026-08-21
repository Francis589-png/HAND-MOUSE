import asyncio
import os
import subprocess
import sys
import time
import unittest
import uuid

import pyautogui
from websockets.asyncio.client import connect


class TestCompanionIntegration(unittest.TestCase):
    def test_authenticated_move_reaches_real_virtual_display(self):
        token = uuid.uuid4().hex + uuid.uuid4().hex
        port = 18765
        env = os.environ.copy()
        env.setdefault("DISPLAY", ":99")

        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "companion",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--token",
                token,
            ],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        try:
            asyncio.run(self._exercise(process, token, port))
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)

    async def _exercise(self, process: subprocess.Popen[str], token: str, port: int) -> None:
        deadline = time.monotonic() + 10
        last_error: Exception | None = None
        uri = f"ws://127.0.0.1:{port}"
        websocket = None

        while time.monotonic() < deadline:
            try:
                websocket = await connect(uri, open_timeout=0.5)
                break
            except Exception as exc:
                last_error = exc
                await asyncio.sleep(0.1)

        if websocket is None:
            output = process.stdout.read() if process.stdout else ""
            raise AssertionError(f"Companion did not start: {last_error}\n{output}")

        async with websocket:
            await websocket.send('{"type":"auth","token":"' + token + '"}')
            auth = await asyncio.wait_for(websocket.recv(), timeout=3)
            self.assertIn('"type":"authenticated"', str(auth))

            await websocket.send('{"command":"move","x":0.25,"y":0.75}')
            executed = await asyncio.wait_for(websocket.recv(), timeout=3)
            self.assertIn('"type":"executed"', str(executed))

        width, height = pyautogui.size()
        expected = (round(0.25 * (width - 1)), round(0.75 * (height - 1)))
        actual = pyautogui.position()
        self.assertEqual((actual.x, actual.y), expected)


if __name__ == "__main__":
    unittest.main()
