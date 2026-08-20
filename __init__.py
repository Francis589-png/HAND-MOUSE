from .tracker import HandTracker
from .cursor import CursorController
from .eye_tracker import EyeTracker
from .gesture_engine import Gesture, GestureConfig, GestureEngine
from .utils import *

__all__ = [
    "HandTracker",
    "EyeTracker",
    "CursorController",
    "Gesture",
    "GestureConfig",
    "GestureEngine",
]

# Package metadata
__author__ = "FRANCIS JUSU"
__email__ = "jusufrancis08@gmail.com"
__bio__ = "Developer focused on human-computer interaction, accessibility, and lightweight computer-vision tools for assistive input."
__version__ = "0.1.0"
