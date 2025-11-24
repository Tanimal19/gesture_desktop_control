import numpy as np
import logging
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmark

logger = logging.getLogger(__name__)


class LandmarkMapper:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.margin = (0.2, 0.4, 0.3, 0.1)  # right, left, top, bottom
        self.screenz = -0.1

        self.stationary_detector = StationaryDetector()
        self.scaler = SigmoidScaler()

    def map_to_screen_pos(self, landmarks: np.ndarray) -> tuple[int, int] | None:
        assert landmarks.shape == (len(HandLandmark), 3)

        index_landmarks = np.array(
            [
                landmarks[HandLandmark.INDEX_FINGER_TIP.value],
                landmarks[HandLandmark.INDEX_FINGER_DIP.value],
            ]
        )
        logger.debug(f"Index finger landmarks: {index_landmarks}")

        if self.stationary_detector.update_and_detect(index_landmarks):
            return None

        index_landmarks = self.scaler.update_and_compute(index_landmarks)

        tipx = index_landmarks[0][0]
        tipy = index_landmarks[0][1]
        tipz = index_landmarks[0][2]
        dipx = index_landmarks[1][0]
        dipy = index_landmarks[1][1]
        dipz = index_landmarks[1][2]

        if tipz >= dipz:
            return None

        # compute intersection with screenz plane
        vx = tipx - dipx
        vy = tipy - dipy
        t = (tipz - self.screenz) / (dipz - tipz)

        x = tipx + vx * t
        y = tipy + vy * t

        x, y = self.corp_and_rescale(x, y)

        px = int((1 - x) * self.screen_width)
        py = int(y * self.screen_height)

        logger.debug(f"mapping pos: ({px}, {py})")

        return (px, py)

    def corp_and_rescale(self, x, y):
        if x < self.margin[0]:
            x = self.margin[0]
        elif x > 1 - self.margin[1]:
            x = 1 - self.margin[1]
        if y < self.margin[2]:
            y = self.margin[2]
        elif y > 1 - self.margin[3]:
            y = 1 - self.margin[3]

        x_scale = 1 - (self.margin[0] + self.margin[1])
        y_scale = 1 - (self.margin[2] + self.margin[3])
        x = (x - self.margin[0]) / x_scale
        y = (y - self.margin[2]) / y_scale

        return x, y

    def reset(self):
        self.stationary_detector.reset()
        self.scaler.reset()


class StationaryDetector:
    def __init__(self, window_size=5, std_thresh=1e-3, vel_thresh=1e-3):
        self.window_size = window_size
        self.window = []
        self.std_thresh = std_thresh
        self.vel_thresh = vel_thresh

    def update_and_detect(self, landmarks: np.ndarray) -> bool:
        self.window.append(landmarks)
        if len(self.window) >= self.window_size:
            self.window.pop(0)

        std = np.max(np.std(self.window, axis=0))
        vel = np.linalg.norm(self.window[-1] - np.mean(self.window, axis=0))
        logger.debug(f"std={std}, velocity={vel}")

        if std < self.std_thresh and vel < self.vel_thresh:
            logger.debug("stationary detected")
            return True

        return False

    def reset(self):
        self.window = []


class SigmoidScaler:
    def __init__(self, vel_thresh=5e-3, k=100, gain_min=0):
        self.prev = None
        self.vel_thresh = vel_thresh
        self.k = k
        self.gain_min = gain_min

    def update_and_compute(self, landmarks: np.ndarray) -> np.ndarray:
        if self.prev is None:
            self.prev = landmarks
            return landmarks

        delta = landmarks - self.prev
        vel = np.linalg.norm(delta)
        logger.debug(f"velocity={vel}")

        scaled = landmarks
        if vel < self.vel_thresh:
            s = vel / self.vel_thresh
            factor = self.gain_min + (1 - self.gain_min) / (
                1 + np.exp(-self.k * (s - 0.5))
            )
            scaled = self.prev + delta * factor
            logger.debug(f"slow movement detected, applying scaling factor: {factor}")

        self.prev = scaled
        return scaled

    def reset(self):
        self.prev = None
