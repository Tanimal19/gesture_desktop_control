import pandas as pd
import numpy as np
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmark


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
