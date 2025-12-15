import cv2
import mediapipe as mp
import math
import time

class HandTracker:
    def __init__(self, cam_index=0):
        self.cap = cv2.VideoCapture(cam_index)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

        self.last_typed_time = 0
        self.debounce_delay = 0.5

    def get_frame(self):
        success, frame = self.cap.read()
        if not success:
            return None, None
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        if results.multi_hand_landmarks:
            for lm in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, lm, self.mp_hands.HAND_CONNECTIONS)
        return frame, results

    def get_index_finger_position(self, landmarks, img_shape=(480, 640)):
        h, w = img_shape
        index_tip = landmarks.landmark[8]
        return int(index_tip.x * w), int(index_tip.y * h)

    def is_pinch(self, landmarks, threshold=0.05):
        thumb = landmarks.landmark[4]
        index = landmarks.landmark[8]
        distance = math.sqrt((thumb.x - index.x) ** 2 + (thumb.y - index.y) ** 2)
        return distance < threshold

    def is_swipe_up(self, landmarks, threshold=0.1):
        tip_y = landmarks.landmark[8].y
        base_y = landmarks.landmark[0].y
        return (base_y - tip_y) > threshold

    def is_swipe_down(self, landmarks, threshold=0.1):
        tip_y = landmarks.landmark[8].y
        base_y = landmarks.landmark[0].y
        return (tip_y - base_y) > threshold

    def two_finger_pinch_distance(self, landmarks):
        index_tip = landmarks.landmark[8]
        middle_tip = landmarks.landmark[12]
        return ((index_tip.x - middle_tip.x) ** 2 + (index_tip.y - middle_tip.y) ** 2) ** 0.5

    def is_two_fingers_apart(self, landmarks, threshold: float = 0.08) -> bool:
        """Return True when index and middle fingers are sufficiently apart (used for scroll mode)."""
        return self.two_finger_pinch_distance(landmarks) > threshold

    def get_index_y(self, landmarks) -> float:
        """Return normalized y of index tip (0..1)."""
        return landmarks.landmark[8].y

    def is_air_typing(self, landmarks):
        distance = self.two_finger_pinch_distance(landmarks)
        now = time.time()
        if distance < 0.05 and (now - self.last_typed_time) > self.debounce_delay:
            self.last_typed_time = now
            return True
        return False

    def get_air_typing_key(self, landmarks):
        index_tip = landmarks.landmark[8]
        col = 0
        row = 0
        if index_tip.x < 0.33:
            col = 0
        elif index_tip.x < 0.66:
            col = 1
        else:
            col = 2
        if index_tip.y < 0.33:
            row = 0
        elif index_tip.y < 0.66:
            row = 1
        else:
            row = 2
        keys = [['Q','W','E'], ['A','S','D'], ['Z','X','C']]
        return keys[row][col]

    def is_clap(self, results, threshold: float = 0.06):
        """Detect a clap gesture when two hands' wrist/base points come close."""
        if not results or not results.multi_hand_landmarks or len(results.multi_hand_landmarks) < 2:
            return False
        a = results.multi_hand_landmarks[0].landmark[0]
        b = results.multi_hand_landmarks[1].landmark[0]
        distance = ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5
        return distance < threshold

    def toggle_typing_mode_on_clap(self, results):
        now = time.time()
        if self.is_clap(results) and (now - getattr(self, 'last_clap_time', 0)) > 0.6:
            self.last_clap_time = now
            self.typing_mode = not getattr(self, 'typing_mode', False)
            return True
        return False

    def show(self, frame):
        cv2.imshow("Hand Mouse", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            self.cap.release()
            cv2.destroyAllWindows()
            exit()
