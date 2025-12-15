import os
import sys
import unittest
import importlib.util
# Load module directly to avoid importing heavy package-level deps
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils.py'))
spec = importlib.util.spec_from_file_location("utils", utils_path)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)


class TestUtils(unittest.TestCase):
    def test_clamp01(self):
        self.assertEqual(utils.clamp01(-1), 0.0)
        self.assertEqual(utils.clamp01(0.5), 0.5)
        self.assertEqual(utils.clamp01(2), 1.0)
    def test_to_normalized(self):
        x, y = utils.to_normalized(320, 240, 640, 480)
        self.assertAlmostEqual(x, 0.5)
        self.assertAlmostEqual(y, 0.5)

    def test_normalized_to_screen(self):
        x, y = utils.normalized_to_screen(0.5, 0.5, (1920, 1080))
        self.assertEqual((x, y), (960, 540))


if __name__ == "__main__":
    unittest.main()
