import unittest
import os
import importlib.util
# load keyboard module directly
keyboard_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'keyboard.py'))
spec = importlib.util.spec_from_file_location("keyboard", keyboard_path)
keyboard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(keyboard)
OnScreenKeyboard = keyboard.OnScreenKeyboard


class TestKeyboard(unittest.TestCase):
    def test_key_at_letters_page(self):
        k = OnScreenKeyboard()
        k.current = 0
        w, h = 300, 300
        # top-left should be 'Q'
        key = k.key_at(0.05, 0.05, w, h)[0]
        self.assertEqual(key, 'Q')
        # bottom control row leftmost should be 'SPACE'
        key = k.key_at(0.05, 0.95, w, h)[0]
        self.assertEqual(key, 'SPACE')

    def test_page_switch(self):
        k = OnScreenKeyboard()
        self.assertEqual(len(k.pages), 2)
        cur = k.current
        k.next_page()
        self.assertNotEqual(cur, k.current)
        k.prev_page()
        self.assertEqual(cur, k.current)

    def test_shift_and_caps(self):
        k = OnScreenKeyboard()
        # start with no shift/caps -> display should be lowercase
        self.assertEqual(k.get_display_label('Q'), 'q')
        k.toggle_shift()
        self.assertEqual(k.get_display_label('Q'), 'Q')
        # shift resets only when applied; caps is persistent
        k.toggle_shift()  # turn off
        k.toggle_caps()
        self.assertEqual(k.get_display_label('Q'), 'Q')
        # applied char respects caps
        typ, val = k.get_applied_char('Q')
        self.assertEqual(typ, 'char')
        self.assertEqual(val, 'Q')

    def test_shift_lock(self):
        k = OnScreenKeyboard()
        k.set_shift_locked(True)
        self.assertTrue(k.shift)
        self.assertTrue(k.shift_locked)
        # toggling shift should unlock when locked
        k.toggle_shift()
        self.assertFalse(k.shift)
        self.assertFalse(getattr(k, 'shift_locked', False))


if __name__ == '__main__':
    unittest.main()
