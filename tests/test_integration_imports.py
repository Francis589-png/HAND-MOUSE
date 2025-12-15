import unittest

class TestIntegrationImports(unittest.TestCase):
    def test_core_imports(self):
        # Importing modules should succeed without opening camera
        from hand_mouse import HandTracker, EyeTracker, CursorController
        self.assertTrue(hasattr(HandTracker, '__init__'))
        self.assertTrue(hasattr(EyeTracker, '__init__'))
        self.assertTrue(hasattr(CursorController, '__init__'))

if __name__ == '__main__':
    unittest.main()
