import unittest
import os
import importlib.util
# load tracker and utils without importing package-level heavy deps
tracker_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tracker.py'))
spec = importlib.util.spec_from_file_location("tracker", tracker_path)
tracker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tracker)
HandTracker = tracker.HandTracker

utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils.py'))
spec2 = importlib.util.spec_from_file_location("utils", utils_path)
utils = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(utils)


class FakeLandmark:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class FakeHand:
    def __init__(self, coords):
        self.landmark = [FakeLandmark(x, y) for (x, y) in coords]


class TestScroll(unittest.TestCase):
    def test_two_fingers_apart(self):
        ht = HandTracker()
        # index and middle far apart
        coords = [(0,0)] * 21
        coords[8] = (0.5, 0.5)
        coords[12] = (0.7, 0.5)
        h = FakeHand(coords)
        self.assertTrue(ht.is_two_fingers_apart(h, threshold=0.1))

    def test_delta_to_scroll(self):
        self.assertEqual(utils.delta_to_scroll(0.1, scale=1000), 100)
        self.assertEqual(utils.delta_to_scroll(-0.2, scale=500), -100)


if __name__ == '__main__':
    unittest.main()
