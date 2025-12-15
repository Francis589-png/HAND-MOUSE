import cv2
import mediapipe as mp
import time
import math
from typing import Optional, Tuple, List


class EyeTracker:
    """Detects iris centers and blinks using MediaPipe Face Mesh.

    Notes:
        - Provides `get_frame()` returning (frame, landmarks)
        - `get_iris_position()` returns normalized iris position (x,y) in [0,1]
        - `is_blink()` detects blinks using EAR threshold with debounce
    """

    # Common MediaPipe indices used for EAR/blink detection and iris
    LEFT_EYE = [33, 160, 158, 133, 153, 144]
    RIGHT_EYE = [362, 385, 387, 263, 373, 380]
    LEFT_IRIS = [468, 469, 470, 471]
    RIGHT_IRIS = [473, 474, 475, 476]

    def __init__(self, cam_index: int = 0, ear_threshold: float = 0.23, blink_debounce: float = 0.5):
        self.cap = cv2.VideoCapture(cam_index)
        self.mp_face = mp.solutions.face_mesh
        self.face_mesh = self.mp_face.FaceMesh(refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.ear_threshold = ear_threshold
        self.last_blink_time = 0
        self.blink_debounce = blink_debounce
        # Per-eye tracking for wink/double-wink
        self._last_blink_time = {'left': 0.0, 'right': 0.0}
        self._blink_history = {'left': [], 'right': []}
        self._double_wink_interval = 0.6

    def get_frame(self) -> Tuple[Optional[any], Optional[object]]:
        success, frame = self.cap.read()
        if not success:
            return None, None
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)
        return frame, results

    def _landmarks_to_points(self, results, h: int, w: int) -> Optional[List[Tuple[int, int]]]:
        if not results or not results.multi_face_landmarks:
            return None
        lm = results.multi_face_landmarks[0]
        pts = [(int(p.x * w), int(p.y * h)) for p in lm.landmark]
        return pts

    def get_iris_position(self, results) -> Optional[Tuple[float, float]]:
        """Return normalized average iris position (x,y) based on left iris if available."""
        if not results or not results.multi_face_landmarks:
            return None
        h, w = results._image_shape[:2] if hasattr(results, '_image_shape') else (480, 640)
        pts = self._landmarks_to_points(results, h, w)
        if not pts:
            return None
        # Prefer left iris, fall back to right
        for iris_indices in (self.LEFT_IRIS, self.RIGHT_IRIS):
            try:
                iris_pts = [pts[i] for i in iris_indices]
            except Exception:
                continue
            cx = sum(p[0] for p in iris_pts) / len(iris_pts)
            cy = sum(p[1] for p in iris_pts) / len(iris_pts)
            return cx / w, cy / h
        return None

    def _eye_aspect_ratio(self, eye_pts: List[Tuple[int, int]]) -> float:
        # eye_pts expected as [p1,p2,p3,p4,p5,p6]
        def dist(a, b):
            return math.hypot(a[0] - b[0], a[1] - b[1])
        A = dist(eye_pts[1], eye_pts[5])
        B = dist(eye_pts[2], eye_pts[4])
        C = dist(eye_pts[0], eye_pts[3])
        if C == 0:
            return 0.0
        return (A + B) / (2.0 * C)

    def process_blink_event(self, eye: str, now: float = None) -> bool:
        """Record a blink for `eye` ('left'|'right'), return True if it's a double-wink."""
        if now is None:
            now = time.time()
        hist = self._blink_history.get(eye, [])
        hist.append(now)
        # keep only last 3
        hist = hist[-3:]
        self._blink_history[eye] = hist
        if len(hist) >= 2 and (hist[-1] - hist[-2]) <= self._double_wink_interval:
            # consume those two blinks
            self._blink_history[eye] = []
            return True
        return False

    def detect_eye_blinks(self, results) -> dict:
        """Detect blinks per eye, with debounce, and return dict {'left':bool,'right':bool} when blink started."""
        out = {'left': False, 'right': False}
        if not results or not results.multi_face_landmarks:
            return out
        h, w = results._image_shape[:2] if hasattr(results, '_image_shape') else (480, 640)
        pts = self._landmarks_to_points(results, h, w)
        if not pts:
            return out
        try:
            left_eye = [pts[i] for i in self.LEFT_EYE]
            right_eye = [pts[i] for i in self.RIGHT_EYE]
        except Exception:
            return out
        left_ear = self._eye_aspect_ratio(left_eye)
        right_ear = self._eye_aspect_ratio(right_eye)
        now = time.time()
        if left_ear < self.ear_threshold and (now - self._last_blink_time['left']) > self.blink_debounce:
            self._last_blink_time['left'] = now
            out['left'] = True
        if right_ear < self.ear_threshold and (now - self._last_blink_time['right']) > self.blink_debounce:
            self._last_blink_time['right'] = now
            out['right'] = True
        return out

    def is_blink(self, results) -> bool:
        pts = None
        if not results or not results.multi_face_landmarks:
            return False
        h, w = results._image_shape[:2] if hasattr(results, '_image_shape') else (480, 640)
        pts = self._landmarks_to_points(results, h, w)
        if not pts:
            return False
        try:
            left_eye = [pts[i] for i in self.LEFT_EYE]
            right_eye = [pts[i] for i in self.RIGHT_EYE]
        except Exception:
            return False
        left_ear = self._eye_aspect_ratio(left_eye)
        right_ear = self._eye_aspect_ratio(right_eye)
        ear = (left_ear + right_ear) / 2.0
        now = time.time()
        if ear < self.ear_threshold and (now - self.last_blink_time) > self.blink_debounce:
            self.last_blink_time = now
            return True
        return False

    def release(self) -> None:
        try:
            self.cap.release()
        except Exception:
            pass

