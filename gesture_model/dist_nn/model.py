import torch
import torch.nn as nn
import numpy as np
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmark
from gesture_model.share import GestureLabel, GestureModel


class DistNN(GestureModel):
    WINDOW_LENGTH = 6

    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(3, 32, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.Conv1d(32, 64, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
        )
        self.fc = nn.Linear(64, len(GestureLabel))

    def forward(self, x):
        # x: (B, 10, 3)
        x = x.permute(0, 2, 1)  # (B, 3, 10)
        x = self.net(x)
        x = x.squeeze(-1)
        x = self.fc(x)
        return x

    def inference(self, landmarks_window: np.ndarray) -> GestureLabel:

        thumb_index_dist = np.linalg.norm(
            landmarks_window[:, HandLandmark.THUMB_TIP.value, :]
            - landmarks_window[:, HandLandmark.INDEX_FINGER_TIP.value, :],
            axis=-1,
        )
        thumb_middle_dist = np.linalg.norm(
            landmarks_window[:, HandLandmark.THUMB_TIP.value, :]
            - landmarks_window[:, HandLandmark.MIDDLE_FINGER_TIP.value, :],
            axis=-1,
        )
        index_middle_dist = np.linalg.norm(
            landmarks_window[:, HandLandmark.INDEX_FINGER_TIP.value, :]
            - landmarks_window[:, HandLandmark.MIDDLE_FINGER_TIP.value, :],
            axis=-1,
        )

        with torch.no_grad():
            x = np.stack(
                [thumb_index_dist, thumb_middle_dist, index_middle_dist], axis=-1
            )  # (WINDOW_LENGTH, 3)
            x_tensor = torch.tensor(x, dtype=torch.float32).unsqueeze(0)
            x_tensor = x_tensor.to(next(self.parameters()).device)

            out = self.forward(x_tensor)  # (1, num_classes)
            pred_idx = out.argmax(dim=1).item()
            pred_label = GestureLabel(pred_idx)

        return pred_label
