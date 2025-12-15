import os
import sys
import unittest
import time
import importlib.util
# load utils module directly to avoid importing package-level heavy deps
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils.py'))
spec = importlib.util.spec_from_file_location("utils", utils_path)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)


class TestSmoothFilter(unittest.TestCase):
    def test_smoothing(self):
        f = utils.SmoothFilter(alpha=0.5)
        x, y = f.update(1.0, 0.0)
        self.assertAlmostEqual(x, 1.0)
        self.assertAlmostEqual(y, 0.0)
        x, y = f.update(0.0, 1.0)
        # smoothed values should be halfway
        self.assertAlmostEqual(x, 0.5)
        self.assertAlmostEqual(y, 0.5)


class TestDwellSelector(unittest.TestCase):
    def test_dwell_selects_after_threshold(self):
        d = utils.DwellSelector(threshold=0.5)
        t0 = 100.0
        self.assertFalse(d.update('A', t0))
        # halfway
        self.assertFalse(d.update('A', t0 + 0.25))
        # complete
        self.assertTrue(d.update('A', t0 + 0.6))
        # after selection resets, progress should be zero and require dwell again
        self.assertFalse(d.update('A', t0 + 0.61))

    def test_dwell_resets_on_key_change(self):
        d = utils.DwellSelector(threshold=0.5)
        t0 = 200.0
        self.assertFalse(d.update('A', t0))
        self.assertFalse(d.update('A', t0 + 0.3))
        self.assertFalse(d.update('B', t0 + 0.35))
        self.assertFalse(d.update('B', t0 + 0.6))


if __name__ == '__main__':
    unittest.main()
