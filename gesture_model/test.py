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

device = "cpu"

model = GestureNet()
model.to(device)
model.load_state_dict(torch.load("./gesture_model.pth", map_location=device))
model.eval()


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
