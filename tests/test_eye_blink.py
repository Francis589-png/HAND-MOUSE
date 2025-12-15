import unittest
import time
import os
import types
import importlib.util
# load EyeTracker directly
eye_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'eye_tracker.py'))
spec = importlib.util.spec_from_file_location("eye_tracker", eye_path)
eyemod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eyemod)
EyeTracker = eyemod.EyeTracker


class TestEyeBlink(unittest.TestCase):
    def test_double_wink_detection(self):
        et = EyeTracker()
        now = time.time()
        # simulate two quick blinks on left eye
        res = types.SimpleNamespace()
        # instead of building heavy landmarks, call process_blink_event directly
        res = None
        self.assertFalse(et.process_blink_event('left', now=now))
        self.assertTrue(et.process_blink_event('left', now=now + 0.3))

    def test_no_double_wink_if_slow(self):
        et = EyeTracker()
        now = time.time()
        self.assertFalse(et.process_blink_event('right', now=now))
        self.assertFalse(et.process_blink_event('right', now=now + 1.0))


if __name__ == '__main__':
    unittest.main()
