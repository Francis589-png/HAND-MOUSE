# hand_mouse: Hands & Eyes — A Practical Course

This course teaches you how to use and extend `hand_mouse` to control your computer with hand gestures and eye gaze. It is structured as short lessons with exercises and practical tips.

**Estimated time:** 60–120 minutes to complete core lessons; 2–4 hours for advanced exercises.

---

## Prerequisites

- A laptop or desktop with a webcam.
- Python 3.8+ and dependencies installed (see `requirements.txt`).
- Optional: quiet, well-lit environment for better tracking.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run unit tests to ensure the environment is healthy:

```bash
python -m unittest discover -s hand_mouse/tests -v
```

---

## Course Outline

1. Lesson 1 — Quick Start & Demos
2. Lesson 2 — Hand Mode: Cursor, Pinch, Scroll
3. Lesson 3 — Typing Mode & On-Screen Keyboard
4. Lesson 4 — Eye Mode: Gaze, Wink, Edge Scrolling
5. Lesson 5 — Tuning & Troubleshooting
6. Exercises & Assessment

---

## Lesson 1 — Quick Start & Demos

Run the eye and hand demos:

```bash
python demo.py --mode eye
python demo.py --mode hand
```

Controls:
- Press ESC to exit the demo window.
- The demos will move your system cursor (be careful while testing).

Try both modes briefly to get familiar with the overlays and behavior.

---

## Lesson 2 — Hand Mode (cursor, pinch, scroll)

Core gestures:
- Move cursor: index finger controls pointer.
- Left click: pinch (thumb + index).
- Scroll mode: spread index + middle fingers, then move vertically to scroll.
- Toggle Typing Mode: clap once (two hands close to each other).

Useful command-line options (dwell & smoothing):

```bash
python demo.py --mode hand --dwell 0.6 --alpha 0.6 --verbose
```

- `--dwell`: how long to dwell for typing selections (seconds).
- `--alpha`: smoothing alpha (higher = more reactive, lower = smoother slow tracking).
- `--verbose`: prints debug logs during typing mode.

Tips:
- Use a steady hand when practicing; increase `--dwell` if selections happen accidentally.
- If clap detection misses, move both palms together with wrists approximately aligned.

---

## Lesson 3 — Typing Mode & On-Screen Keyboard

Typing Mode flow:
1. Clap once to enter Typing Mode (clap again to exit).
2. Move your index finger over the on-screen keyboard; dwell selects keys.
3. Special keys: `SHIFT`, `CAPS`, `SPACE`, `BACK`, `ENTER`, `NEXT`/`PREV` to switch pages.

Key behavior:
- Short press `SHIFT` enables a transient capital on next letter; long-press `SHIFT` (dwell longer) locks it.
- `CAPS` toggles caps lock for letters.

Troubleshooting typing:
- Enable `--verbose` to see live logs and HUD (index pixel, smoothed coordinates, selected `key`, dwell `progress`).
- If keys never reach 100% progress, raise `--dwell` (try 1.0–1.5s) and reduce camera jitter or smoothing (`--alpha`).

---

## Lesson 4 — Eye Mode (gaze, wink, edge scrolling)

Core features:
- Move pointer by gaze center (iris detection).
- Blink/wink: single blink = click; quick double-wink = double-click (can be disabled with `--no-wink`).
- Edge scroll: linger at top/bottom edges to scroll; long gaze confirms action.

Start with defaults, then tune:

```bash
python demo.py --mode eye --dwell 0.6 --alpha 0.6 --scroll-scale 800
python demo.py --mode eye --no-wink --no-edge-scroll
```

Tips:
- Use a stable head pose; leverage smoothing (`--alpha`) to reduce jitter.
- If edge scroll feels too sensitive, reduce `--scroll-scale`.

---

## Lesson 5 — Tuning & Troubleshooting

- Lighting and camera angle are important — face/hand detectors perform best with even lighting.
- If the cursor jumps, decrease `--alpha` (more smoothing).
- If dwell selections are too slow, reduce `--dwell` (but avoid accidental activations).
- For typing reliability, use `--verbose` and watch the HUD text that shows key/progress; adjust `--dwell` accordingly.

Common fixes:
- No hands detected: ensure permissions for camera and proper device index (default `0`).
- Clap not recognized: clap with both palms close to wrists, try a larger motion or smaller clap threshold (code-level tweak).

---

## Exercises & Assessment

1. Basic exploration (5–10 min): run both demos, practice pinch click and edge scroll.
2. Typing practice (15–20 min): enter typing mode and type "hello" using dwell; adjust `--dwell` to reach 80–100% success.
3. Extend: change `DwellSelector.threshold` in `demo.py` locally and observe behavior.

Optional assignment: Add a new keyboard page for punctuation or international characters and validate its layout.

---

## Extending & Developing

- The project is designed to be modular; add gestures in `hand_mouse/tracker.py` or improve eye detection in `hand_mouse/eye_tracker.py`.
- Add unit tests under `hand_mouse/tests/` for new gesture logic and helpers.

---

**Author:** FRANCIS JUSU — jusufrancis08@gmail.com

**Bio:** FRANCIS JUSU is a developer and researcher working at the intersection of computer vision and accessibility. He builds lightweight tools and demos to make hands-free interaction more reliable and approachable.

---

## Troubleshooting Checklist

- Camera feed blank: check permissions and try `python -m pip install opencv-python`.
- Incorrect key hit detection: confirm `keyboard.key_at` logic and the on-screen overlay placement (width/height calculations).
- Unintended clicks: increase `--dwell` or add additional gesture debouncing.

---

If you'd like, I can convert this course into separate lesson files, add images/screencasts, or create a short troubleshooting FAQ — tell me which next step you want.
