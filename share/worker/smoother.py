import numpy as np
import logging
from share.utils import HandLandmark

logger = logging.getLogger(__name__)


class EMASmoother:
    def __init__(self, alpha=0.2, jump_thresh=1.5):
        self.alpha = alpha
        self.jump_thresh = jump_thresh
        self.prev = None

    def update(self, landmarks: np.ndarray) -> np.ndarray:
        assert landmarks.shape == (len(HandLandmark), 3)

        if self.prev is None:
            self.prev = landmarks
            return landmarks

        vel = np.linalg.norm(landmarks - self.prev)
        logger.debug(f"velocity={vel}")
        if vel > self.jump_thresh:
            logger.debug("jump detected")
            return self.prev

        smoothed = self.alpha * landmarks + (1 - self.alpha) * self.prev
        self.prev = smoothed.copy()

        return smoothed

    def reset(self):
        self.prev = None
