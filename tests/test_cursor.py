import os
import sys
import unittest
import importlib.util
from unittest.mock import patch
# Load cursor module directly to avoid importing package-level heavy deps
cursor_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cursor.py'))
spec = importlib.util.spec_from_file_location("cursor", cursor_path)
cursor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cursor)
CursorController = cursor.CursorController


class TestCursor(unittest.TestCase):
    @patch.object(cursor, 'pyautogui')
    def test_move_to_norm(self, mock_pyautogui):
        mock_pyautogui.size.return_value = (1000, 800)
        c = CursorController()
        c.move_to_norm(0.5, 0.25)
        mock_pyautogui.moveTo.assert_called_once()
        args, _ = mock_pyautogui.moveTo.call_args
        # expect roughly (500, 200)
        self.assertAlmostEqual(args[0], 500)
        self.assertAlmostEqual(args[1], 200)

    @patch.object(cursor, 'pyautogui')
    def test_clicks(self, mock_pyautogui):
        c = CursorController(screen_size=(800, 600))
        c.left_click()
        mock_pyautogui.click.assert_called()
        c.right_click()
        mock_pyautogui.click.assert_called_with(button='right')


if __name__ == "__main__":
    unittest.main()
