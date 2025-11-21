import torch
import torch.nn as nn
import numpy as np
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmark
from gesture_model.model import GestureLabel, AbstractGestureModel


class TaskAnnotator(AbstractGestureModel):
    WINDOW_LENGTH = 5
    LANDMARKS = [
        HandLandmark.THUMB_TIP,
        HandLandmark.INDEX_FINGER_TIP,
        HandLandmark.MIDDLE_FINGER_TIP,
    ]
    DIST_FEATURES = [
        (HandLandmark.THUMB_TIP, HandLandmark.INDEX_FINGER_TIP),
        (HandLandmark.THUMB_TIP, HandLandmark.MIDDLE_FINGER_TIP),
        (HandLandmark.INDEX_FINGER_TIP, HandLandmark.MIDDLE_FINGER_TIP),
    ]
    feature_dim = len(LANDMARKS) * 3 + len(DIST_FEATURES)

    def __init__(self, y_mapping):
        super().__init__()
        self.y_mapping = y_mapping

        self.net = nn.Sequential(
            nn.Conv1d(self.feature_dim, 32, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.Conv1d(32, 64, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
        )
        self.fc = nn.Linear(64, len(y_mapping))

    def forward(self, x):
        # x: (B, window_length, feature_dim)
        x = x.permute(0, 2, 1)  # (B, feature_dim, window_length)
        x = self.net(x)
        x = x.squeeze(-1)
        x = self.fc(x)
        return x

    def landmarks_window_to_X(self, landmarks_window: np.ndarray) -> torch.Tensor:

        # compute distance features
        dist_features = []
        for lm1, lm2 in self.DIST_FEATURES:
            vec = landmarks_window[:, lm1.value, :] - landmarks_window[:, lm2.value, :]
            dist = np.linalg.norm(vec, axis=1)  # (window_length,)
            dist_features.append(dist)
        dist_features = np.stack(
            dist_features, axis=1
        )  # (window_length, num_dist_features)

        # convert landmarks position to offset position w.r.t. wrist
        wrist_landmark = landmarks_window[:, HandLandmark.WRIST.value, :]
        filtered_window = np.zeros((self.WINDOW_LENGTH, len(self.LANDMARKS), 3))
        for i, lm in enumerate(self.LANDMARKS):
            lm_pos = landmarks_window[:, lm.value, :]
            offset_lm_pos = lm_pos - wrist_landmark
            filtered_window[:, i, :] = offset_lm_pos
        filtered_window = filtered_window.reshape(
            self.WINDOW_LENGTH, -1
        )  # (window_length, num_landmarks * 3)

        features = np.concatenate(
            [filtered_window, dist_features], axis=1
        )  # (window_length, feature_dim)
        x_tensor = torch.tensor(features, dtype=torch.float32)
        return x_tensor

    def y_to_label(self, y: int) -> GestureLabel:
        mapped_label = "NONE"
        for o, m in self.y_mapping.items():
            if m == y:
                mapped_label = o
                break
        return GestureLabel[mapped_label]
