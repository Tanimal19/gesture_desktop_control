import numpy as np
import logging
from main.utils import HandLandmark

logger = logging.getLogger(__name__)


class PointerLandmarkMapper:
    """
    Map hand landmarks to screen coordinates.\n

    `mapping_use_palm()`: use palm plane intersection for mapping.\n
    `mapping_use_index()`: use index finger direction for mapping.\n
    """

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.margin = (0.2, 0.4, 0.4, 0.1)  # right, left, top, bottom
        self.screenz = -0.2
        self.sensitivity = (1.0, 3.0)  # x, y

        self.stationary_detector = StationaryDetector()
        self.scaler = SigmoidScaler()
        self.smoother = EMASmoother()

        self.last_pos = (0, 0)

    def mapping_use_palm(self, landmarks: np.ndarray) -> tuple[int, int]:
        assert landmarks.shape == (len(HandLandmark), 3)

        palm_landmarks = np.array(
            [
                landmarks[HandLandmark.WRIST.value],
                landmarks[HandLandmark.INDEX_FINGER_MCP.value],
                landmarks[HandLandmark.PINKY_MCP.value],
            ]
        )

        if self.stationary_detector.update(palm_landmarks):
            return self.last_pos

        # palm_landmarks = self.scaler.update(palm_landmarks)

        WRIST = palm_landmarks[0]
        INDEX_MCP = palm_landmarks[1]
        PINKY_MCP = palm_landmarks[2]

        # find center of palm (center of mass)
        M = (WRIST + INDEX_MCP + PINKY_MCP) / 3.0

        # calculate normal vector of palm plane
        u = INDEX_MCP - WRIST
        v = PINKY_MCP - WRIST
        normal = np.cross(u, v)

        # compute intersection with screenz plane
        t = (self.screenz - M[2]) / normal[2]
        x = M[0] + normal[0] * t * self.sensitivity[0]
        y = M[1] + normal[1] * t * self.sensitivity[1]

        x, y = self.corp_and_rescale(x, y)
        px = int((1 - x) * self.screen_width)
        py = int(y * self.screen_height)

        smoothed_pos = self.smoother.update((px, py))

        self.last_pos = smoothed_pos
        return smoothed_pos

    def mapping_use_index(self, landmarks: np.ndarray) -> tuple[int, int]:
        assert landmarks.shape == (len(HandLandmark), 3)

        index_landmarks = np.array(
            [
                landmarks[HandLandmark.INDEX_FINGER_TIP.value],
                landmarks[HandLandmark.INDEX_FINGER_DIP.value],
            ]
        )

        if self.stationary_detector.update(index_landmarks):
            return self.last_pos

        index_landmarks = self.scaler.update(index_landmarks)

        tipx = index_landmarks[0][0]
        tipy = index_landmarks[0][1]
        tipz = index_landmarks[0][2]
        dipx = index_landmarks[1][0]
        dipy = index_landmarks[1][1]
        dipz = index_landmarks[1][2]

        if tipz >= dipz:
            return self.last_pos

        # compute intersection with screenz plane
        vx = tipx - dipx
        vy = tipy - dipy
        t = (tipz - self.screenz) / (dipz - tipz)

        x = tipx + vx * t
        y = tipy + vy * t

        x, y = self.corp_and_rescale(x, y)

        px = int((1 - x) * self.screen_width)
        py = int(y * self.screen_height)

        self.last_pos = (px, py)
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
        self.smoother.reset()


class StationaryDetector:
    """
    Detect if the landmarks are stationary based on standard deviation and velocity.
    """

    def __init__(self, window_size=5, std_thresh=1e-3, vel_thresh=1e-3):
        self.window_size = window_size
        self.window = []
        self.std_thresh = std_thresh
        self.vel_thresh = vel_thresh

    def update(self, landmarks: np.ndarray) -> bool:
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
    """
    Scale slow movements using a sigmoid function to reduce jitter.
    """

    def __init__(self, vel_thresh=5e-3, k=100, gain_min=0):
        self.prev = None
        self.vel_thresh = vel_thresh
        self.k = k
        self.gain_min = gain_min

    def update(self, landmarks: np.ndarray) -> np.ndarray:
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


class EMASmoother:
    """
    Exponential Moving Average (EMA) smoother for pointer position.
    """

    def __init__(self, alpha=0.2):
        self.alpha = alpha
        self.smoothed = None

    def update(self, pos: tuple[int, int]) -> tuple[int, int]:
        if self.smoothed is None:
            self.smoothed = pos
        else:
            x = self.alpha * pos[0] + (1 - self.alpha) * self.smoothed[0]
            y = self.alpha * pos[1] + (1 - self.alpha) * self.smoothed[1]
            self.smoothed = (x, y)

        return (int(self.smoothed[0]), int(self.smoothed[1]))

    def reset(self):
        self.smoothed = None
