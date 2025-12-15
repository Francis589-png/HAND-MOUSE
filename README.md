# hand_mouse

Control your computer using hand gestures or eye gaze (experimental).

- `HandTracker`: simple finger/pinch detection using MediaPipe Hands.
- `EyeTracker`: iris center and blink detection using MediaPipe Face Mesh.
- `CursorController`: moves the system cursor via `pyautogui`.

Quick demo:

```bash
python demo.py --mode eye
python demo.py --mode hand
```

Requirements:

```text
mediapipe
opencv-python
pyautogui
numpy
```

Notes:
- This project is experimental — tune thresholds and camera settings for your setup.
- Running demos will move your system cursor; be careful when testing.

## Tutorial / Course

A step-by-step course and troubleshooting guide is available at [docs/Course.md](docs/Course.md).

**Author:** FRANCIS JUSU — jusufrancis08@gmail.com

**Bio:** FRANCIS JUSU is a developer focused on human-computer interaction, accessibility, and lightweight computer-vision tools for assistive input. This project was created to explore hands- and eyes-driven interaction techniques and to provide a foundation for further research and prototyping.

## Development

Run tests:

```bash
python -m unittest discover -s hand_mouse/tests -v
```

Integration guide and programmatic examples: [docs/Integration.md](docs/Integration.md)

Example integration script: [examples/integrate_app.py](../examples/integrate_app.py)
# HAND-MOUSE
