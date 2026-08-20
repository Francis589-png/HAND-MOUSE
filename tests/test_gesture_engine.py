import unittest

from gesture_engine import Gesture, GestureConfig, GestureEngine


class TestGestureEngine(unittest.TestCase):
    def test_requires_consecutive_confirmation_frames(self):
        engine = GestureEngine(GestureConfig(confirmation_frames=3, cooldown_seconds=0))

        self.assertIsNone(engine.update(Gesture.PINCH, 0.0))
        self.assertIsNone(engine.update(Gesture.PINCH, 0.1))
        self.assertEqual(engine.update(Gesture.PINCH, 0.2), Gesture.PINCH)

    def test_noise_resets_confirmation(self):
        engine = GestureEngine(GestureConfig(confirmation_frames=3, cooldown_seconds=0))

        self.assertIsNone(engine.update(Gesture.PINCH, 0.0))
        self.assertIsNone(engine.update(Gesture.NONE, 0.1))
        self.assertIsNone(engine.update(Gesture.PINCH, 0.2))
        self.assertIsNone(engine.update(Gesture.PINCH, 0.3))
        self.assertEqual(engine.update(Gesture.PINCH, 0.4), Gesture.PINCH)

    def test_held_gesture_fires_only_once(self):
        engine = GestureEngine(GestureConfig(confirmation_frames=2, cooldown_seconds=0))

        self.assertIsNone(engine.update(Gesture.PINCH, 0.0))
        self.assertEqual(engine.update(Gesture.PINCH, 0.1), Gesture.PINCH)
        for timestamp in (0.2, 0.3, 1.0):
            self.assertIsNone(engine.update(Gesture.PINCH, timestamp))

    def test_none_rearms_engine(self):
        engine = GestureEngine(GestureConfig(confirmation_frames=2, cooldown_seconds=0))

        self.assertIsNone(engine.update(Gesture.PINCH, 0.0))
        self.assertEqual(engine.update(Gesture.PINCH, 0.1), Gesture.PINCH)
        self.assertIsNone(engine.update(Gesture.NONE, 0.2))
        self.assertIsNone(engine.update(Gesture.PINCH, 0.3))
        self.assertEqual(engine.update(Gesture.PINCH, 0.4), Gesture.PINCH)

    def test_cooldown_applies_after_rearm(self):
        engine = GestureEngine(GestureConfig(confirmation_frames=2, cooldown_seconds=1.0))

        self.assertIsNone(engine.update(Gesture.PINCH, 0.0))
        self.assertEqual(engine.update(Gesture.PINCH, 1.0), Gesture.PINCH)
        self.assertIsNone(engine.update(Gesture.NONE, 1.1))
        self.assertIsNone(engine.update(Gesture.PINCH, 1.2))
        self.assertIsNone(engine.update(Gesture.PINCH, 1.3))
        self.assertIsNone(engine.update(Gesture.PINCH, 1.9))
        self.assertEqual(engine.update(Gesture.PINCH, 2.0), Gesture.PINCH)

    def test_rejects_backwards_time(self):
        engine = GestureEngine()
        engine.update(Gesture.PINCH, 1.0)
        with self.assertRaises(ValueError):
            engine.update(Gesture.NONE, 0.9)

    def test_configuration_validation(self):
        with self.assertRaises(ValueError):
            GestureConfig(confirmation_frames=0)
        with self.assertRaises(ValueError):
            GestureConfig(cooldown_seconds=-1)
        with self.assertRaises(TypeError):
            GestureConfig(confirmation_frames=1.5)
        with self.assertRaises(TypeError):
            GestureConfig(cooldown_seconds="0.5")

    def test_string_gesture_values_are_supported(self):
        engine = GestureEngine(GestureConfig(confirmation_frames=1, cooldown_seconds=0))
        self.assertEqual(engine.update("pinch", 0.0), Gesture.PINCH)

    def test_invalid_gesture_is_rejected(self):
        engine = GestureEngine()
        with self.assertRaises(ValueError):
            engine.update("not-a-gesture", 0.0)

    def test_invalid_timestamp_is_rejected(self):
        engine = GestureEngine()
        with self.assertRaises(TypeError):
            engine.update(Gesture.PINCH, "0.0")
        with self.assertRaises(TypeError):
            engine.update(Gesture.PINCH, True)


if __name__ == "__main__":
    unittest.main()
