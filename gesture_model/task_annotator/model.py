import torch
import torch.nn as nn
import numpy as np
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmark
from gesture_model.share import GestureLabel, GestureModel

BASE_FOLDER = "./gesture_model/task_annotator/"


class TaskAnnotator(GestureModel):
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

    def __init__(self, num_classes):
        super().__init__()
        self.num_classes = num_classes
        self.feature_dim = len(self.LANDMARKS) * 3 + len(self.DIST_FEATURES)

        self.net = nn.Sequential(
            nn.Conv1d(self.feature_dim, 32, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.Conv1d(32, 64, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
        )
        self.fc = nn.Linear(64, num_classes)

    def forward(self, x):
        # x: (B, window_length, feature_dim)
        x = x.permute(0, 2, 1)  # (B, feature_dim, window_length)
        x = self.net(x)
        x = x.squeeze(-1)
        x = self.fc(x)
        return x

    def inference(self, landmarks_window: np.ndarray) -> GestureLabel:

        # filter to required landmarks
        idxs = [lm.value for lm in self.LANDMARKS]
        landmarks_window = landmarks_window[:, idxs, :]  # (window_length, 9, 3)

        for lm1, lm2 in self.DIST_FEATURES:
            landmarks_window = self._compute_distance_features(
                landmarks_window,
                lm1,
                lm2,
            )

        with torch.no_grad():
            x_tensor = torch.tensor(landmarks_window, dtype=torch.float32).unsqueeze(0)
            x_tensor = x_tensor.to(next(self.parameters()).device)

            out = self.forward(x_tensor)  # (1, num_classes)
            pred_idx = out.argmax(dim=1).item()
            pred_label = GestureLabel(pred_idx)

        return pred_label

    @staticmethod
    def _compute_distance_features(landmarks_window, lm1, lm2):
        vec = landmarks_window[:, lm1.value, :] - landmarks_window[:, lm2.value, :]
        dist = np.linalg.norm(vec, axis=1)  # (window_length,)

        dist = dist.reshape((-1, 1))  # (window_length, 1)
        landmarks_window = np.concatenate((landmarks_window, dist), axis=1)

        return landmarks_window
