import math
import unittest

from companion.protocol import validate_command


class TestProtocol(unittest.TestCase):
    def test_move_is_normalized(self):
        self.assertEqual(
            validate_command({"command": "move", "x": 0.25, "y": 0.75}),
            {"command": "move", "x": 0.25, "y": 0.75},
        )

    def test_move_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            validate_command({"command": "move", "x": -0.1, "y": 0.5})
        with self.assertRaises(ValueError):
            validate_command({"command": "move", "x": 0.5, "y": 1.1})

    def test_move_rejects_non_finite(self):
        with self.assertRaises(ValueError):
            validate_command({"command": "move", "x": math.nan, "y": 0.5})
        with self.assertRaises(ValueError):
            validate_command({"command": "move", "x": 0.5, "y": math.inf})

    def test_clicks(self):
        self.assertEqual(validate_command({"command": "left_click"}), {"command": "left_click"})
        self.assertEqual(validate_command({"command": "right_click"}), {"command": "right_click"})

    def test_scroll_is_bounded_integer(self):
        self.assertEqual(validate_command({"command": "scroll", "amount": -20}), {"command": "scroll", "amount": -20})
        with self.assertRaises(ValueError):
            validate_command({"command": "scroll", "amount": 20.5})
        with self.assertRaises(ValueError):
            validate_command({"command": "scroll", "amount": 21})

    def test_key_commands(self):
        self.assertEqual(
            validate_command({"command": "key", "action": "press", "key": "enter"}),
            {"command": "key", "action": "press", "key": "enter"},
        )

    def test_rejects_unknown_command(self):
        with self.assertRaises(ValueError):
            validate_command({"command": "shell", "value": "rm -rf /"})

    def test_rejects_malformed_input(self):
        with self.assertRaises(ValueError):
            validate_command([])
        with self.assertRaises(ValueError):
            validate_command({"command": "key", "action": "press", "key": ""})


if __name__ == "__main__":
    unittest.main()
