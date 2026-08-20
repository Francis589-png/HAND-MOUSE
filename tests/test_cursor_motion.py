import unittest

from cursor_motion import CursorSmoother, normalized_to_screen


class TestCursorMotion(unittest.TestCase):
    def test_smoother_moves_toward_target(self):
        smoother = CursorSmoother(alpha=0.5)
        self.assertEqual(smoother.update((0.0, 0.0), (1.0, 1.0)), (0.5, 0.5))

    def test_alpha_one_follows_target_exactly(self):
        smoother = CursorSmoother(alpha=1.0)
        self.assertEqual(smoother.update((0.2, 0.8), (0.9, 0.1)), (0.9, 0.1))

    def test_smoothing_is_bounded(self):
        smoother = CursorSmoother(alpha=0.2)
        result = smoother.update((0.4, 0.6), (1.0, 0.0))
        self.assertGreaterEqual(result[0], 0.0)
        self.assertLessEqual(result[0], 1.0)
        self.assertGreaterEqual(result[1], 0.0)
        self.assertLessEqual(result[1], 1.0)

    def test_normalized_coordinates_map_to_valid_pixels(self):
        self.assertEqual(normalized_to_screen(0.0, 0.0, (1920, 1080)), (0, 0))
        self.assertEqual(normalized_to_screen(0.5, 0.5, (1920, 1080)), (960, 540))
        self.assertEqual(normalized_to_screen(1.0, 1.0, (1920, 1080)), (1919, 1079))

    def test_out_of_range_coordinates_are_clamped(self):
        self.assertEqual(normalized_to_screen(-1.0, 2.0, (100, 80)), (0, 79))

    def test_invalid_alpha_is_rejected(self):
        with self.assertRaises(ValueError):
            CursorSmoother(alpha=0)
        with self.assertRaises(ValueError):
            CursorSmoother(alpha=1.1)
        with self.assertRaises(TypeError):
            CursorSmoother(alpha="0.5")

    def test_invalid_screen_size_is_rejected(self):
        with self.assertRaises(ValueError):
            normalized_to_screen(0.5, 0.5, (0, 1080))
        with self.assertRaises(ValueError):
            normalized_to_screen(0.5, 0.5, (1920, 0))


if __name__ == "__main__":
    unittest.main()
