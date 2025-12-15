import os
import sys
import unittest
import importlib.util
# load HandTracker directly to avoid importing heavy package-level deps
tracker_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tracker.py'))
spec = importlib.util.spec_from_file_location("tracker", tracker_path)
tracker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tracker)
HandTracker = tracker.HandTracker


class FakeLandmark:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class FakeHand:
    def __init__(self, coords):
        self.landmark = [FakeLandmark(x, y) for (x, y) in coords]


class FakeResults:
    def __init__(self, hands):
        self.multi_hand_landmarks = hands


class TestHandClap(unittest.TestCase):
    def test_is_clap_true(self):
        ht = HandTracker()
        # two wrists close together
        a = FakeHand([(0.5, 0.5)])
        b = FakeHand([(0.52, 0.51)])
        res = FakeResults([a, b])
        self.assertTrue(ht.is_clap(res, threshold=0.05) or ht.is_clap(res, threshold=0.06))

    def test_is_clap_false(self):
        ht = HandTracker()
        a = FakeHand([(0.1, 0.1)])
        b = FakeHand([(0.9, 0.9)])
        res = FakeResults([a, b])
        self.assertFalse(ht.is_clap(res, threshold=0.05))


if __name__ == '__main__':
    unittest.main()
