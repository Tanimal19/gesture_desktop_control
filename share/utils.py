# utils that do not depend on mediapipe

import numpy as np
import pandas as pd
from enum import Enum
import logging


def setup_logging(filepath=None):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    if filepath:
        file_handler = logging.FileHandler(filepath, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(module)s.%(funcName)s(): %(message)s"
        )
        file_handler.setFormatter(file_fmt)
        logger.addHandler(file_handler)


# simulate mediapipe.tasks.python.vision.hand_landmarker.HandLandmark
# becuase it can't be imported in some environments
class HandLandmark(Enum):
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_FINGER_MCP = 5
    INDEX_FINGER_PIP = 6
    INDEX_FINGER_DIP = 7
    INDEX_FINGER_TIP = 8
    MIDDLE_FINGER_MCP = 9
    MIDDLE_FINGER_PIP = 10
    MIDDLE_FINGER_DIP = 11
    MIDDLE_FINGER_TIP = 12
    RING_FINGER_MCP = 13
    RING_FINGER_PIP = 14
    RING_FINGER_DIP = 15
    RING_FINGER_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20


def merge_landmarks(hand_landmarks, world_landmarks):
    return np.array(
        [
            [norm.x, norm.y, world.z]
            for norm, world in zip(
                hand_landmarks,
                world_landmarks,
            )
        ]
    )


def extend_landmark_columns(window: pd.DataFrame, window_length: int) -> np.ndarray:
    """
    Extend the landmark columns in the given window to a 3D numpy array of shape.\n
    Pad with zeros for missing landmarks.
    """

    landmark_window = []
    for lm in HandLandmark:
        if lm.name in window.columns:
            x, y, z = window[lm.name].str.split("_", expand=True).astype(float).values.T
        else:
            x = y = z = np.zeros((window_length,))

        landmark_feautures = np.stack([x, y, z], axis=1)  # shape: (frame_window, 3)
        landmark_window.append(landmark_feautures)
    landmark_window = np.stack(landmark_window, axis=1).astype(
        "float32"
    )  # shape: (frame_window, landmarks, 3)
    return landmark_window
