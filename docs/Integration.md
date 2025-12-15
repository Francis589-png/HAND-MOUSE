# Integrating `hand_mouse` into Your Project

This guide shows practical ways to embed `hand_mouse` into your application or workflow — from quick imports to building a small gesture-driven controller.

Audience: developers who want to use the library as a module (not run the demos).

## 1. Install and import

Install dev requirements:

```bash
python -m pip install -r requirements.txt
```

Import core classes in your script:

```python
from hand_mouse import HandTracker, EyeTracker, CursorController
```

Both trackers provide a `get_frame()` method returning `(frame, results)` and helper methods for gesture detection.

## 2. Simple programmatic usage examples

Example A — Move the cursor programmatically using eye gaze (polling loop):

```python
from hand_mouse import EyeTracker, CursorController, utils
import time

eye = EyeTracker()
cursor = CursorController()
filter = utils.SmoothFilter(alpha=0.6)
try:
    while True:
        frame, res = eye.get_frame()
        if frame is None:
            break
        gaze = eye.get_iris_position(res)
        if gaze:
            sx, sy = filter.update(*gaze)
            cursor.move_to_norm(sx, sy)
        time.sleep(0.01)
finally:
    eye.release()
```

Example B — Map hand gestures to actions (non-blocking main loop):

```python
from hand_mouse import HandTracker
import pyautogui

hand = HandTracker()
try:
    while True:
        frame, results = hand.get_frame()
        if results and getattr(results, 'multi_hand_landmarks', None):
            # use first hand
            primary = results.multi_hand_landmarks[0]
            if hand.is_pinch(primary):
                pyautogui.click()
            if hand.is_two_fingers_apart(primary):
                # e.g. interpret as scroll mode — application specific
                print('scroll-mode')
finally:
    hand.cap.release()
```

## 3. Embed in a GUI (PyQt/Tkinter)

- Run `get_frame()` in a background thread (do not call blocking GUI operations from camera thread).
- Avoid calling GUI updates from the tracker thread directly; use thread-safe queues or signals.
- Keep the tracking loop lightweight; use `utils.SmoothFilter` to reduce per-frame jitter.

## 4. Example project ideas

- Gesture media controller: pinch = play/pause, swipe up/down = volume.
- Assistive typing overlay: integrate `OnScreenKeyboard` and add persistent typed buffer.
- Game input adapter: map pinches/winks to keyboard presses for simple games.

## 5. Tips for production use

- Add configuration for camera index and thresholds (dwell, alpha) and provide a simple settings UI.
- For stability, add a small debounce time for sensitive gestures and prefer dwell for reliable selections.
- Add unit tests for all gesture mapping logic (the detectors in `hand_mouse/tracker.py` are deterministic and easy to test).

## 6. Packaging and distributing

- Keep only necessary runtime deps: `mediapipe`, `opencv-python`, `pyautogui`.
- Include usage examples under `examples/` and document them in your README.

## 7. Further reading & references

- See the main [Course](Course.md) for tutorials and troubleshooting.
- Check `hand_mouse/tests/` for example unit tests and how to validate logic without a camera.

---

If you'd like, I can: add a step-by-step example app in `examples/` wired to a small GUI, or produce a short screencast script.