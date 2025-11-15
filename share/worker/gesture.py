import torch
from gesture_model.model import GestureNet, WINDOW_LENGTH
import pandas as pd
import numpy as np
from gesture_model.utils import index_to_label, LANDMARKS
from data_collection.annotation.utils import (
    split_landmarks,
    offset_landmarks,
    generate_frame_windows,
)
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmark


csv_file = "./data_collection/datasets/p0/task_result.csv"
df = pd.read_csv(csv_file)

df = split_landmarks(df)
df = offset_landmarks(df)
df_groups = df.groupby(["task", "trail"])

results = []

with torch.no_grad():
    for (task, trail), group in df_groups:
        samples = generate_frame_windows(group, WINDOW_LENGTH)
        print(f"Processing: task={task}, trail={trail}, total frames={len(group)}")

        for sample in samples:
            assert sample["landmarks"].shape == (WINDOW_LENGTH, len(LANDMARKS), 3)
            lm_tensor = torch.tensor(
                sample["landmarks"], dtype=torch.float32
            ).unsqueeze(0)
            lm_tensor = lm_tensor.to(device)

            out = model(lm_tensor)  # (1, 8)
            pred_idx = out.argmax(dim=1).item()
            pred_label = index_to_label(pred_idx)

            results.append(
                {
                    "timestamp": sample["timestamp"],
                    "label": pred_label,
                }
            )

df_results = pd.DataFrame(results)
df_results.to_csv("./gesture_model/datasets/test_results.csv", index=False)


class GestureModel:
    def __init__(self, model_path="./gesture_model.pth", device="cpu"):

        self.support_landmarks = [
            HandLandmark.THUMB_CMC,
            HandLandmark.THUMB_MCP,
            HandLandmark.THUMB_IP,
            HandLandmark.THUMB_TIP,
            HandLandmark.INDEX_FINGER_MCP,
            HandLandmark.INDEX_FINGER_PIP,
            HandLandmark.INDEX_FINGER_DIP,
            HandLandmark.INDEX_FINGER_TIP,
            HandLandmark.MIDDLE_FINGER_MCP,
            HandLandmark.MIDDLE_FINGER_PIP,
            HandLandmark.MIDDLE_FINGER_DIP,
            HandLandmark.MIDDLE_FINGER_TIP,
        ]

        self.device = device
        self.model = GestureNet()
        self.model.to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()

    def predict(self, landmarks_window):
        """
        landmarks_window: np.array of shape (WINDOW_LENGTH, len(LANDMARKS), 3)
        """
        assert landmarks_window.shape == (WINDOW_LENGTH, len(LANDMARKS), 3)

        with torch.no_grad():
            lm_tensor = torch.tensor(landmarks_window, dtype=torch.float32).unsqueeze(0)
            lm_tensor = lm_tensor.to(self.device)

            out = self.model(lm_tensor)  # (1, num_classes)
            pred_idx = out.argmax(dim=1).item()
            pred_label = index_to_label(pred_idx)

        return pred_label
