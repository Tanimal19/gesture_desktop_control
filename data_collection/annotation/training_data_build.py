import pandas as pd
import numpy as np
from data_collection.annotation.utils import (
    split_landmarks,
    offset_landmarks,
    generate_frame_windows,
)
from gesture_model.model import WINDOW_LENGTH

df_label = pd.read_csv("./data_collection/datasets/p0/labels.csv")
df_lm = pd.read_csv("./data_collection/datasets/p0/task_result.csv")
df = df_lm.merge(df_label, on=["timestamp"], how="left")
df = df.dropna(subset=["label"]).reset_index(drop=True)

df = split_landmarks(df)
df = offset_landmarks(df)

# build training samples
samples = []
df_groups = df.groupby(["task", "trail"])
for (task, trail), group in df_groups:
    print(f"Processing: task={task}, trail={trail}, total frames={len(group)}")
    samples.extend(generate_frame_windows(group, WINDOW_LENGTH, has_label=True))


# convert samples to NPY arrays and save
landmark_data = np.array([sample["landmarks"] for sample in samples])
print("X shape:", landmark_data.shape)  # (num_samples, frame_window, num_landmarks, 3)

labels = np.array([sample["label"] for sample in samples])
print("y shape:", labels.shape)  # (num_samples,)
print("Unique labels:", np.unique(labels))

np.save("./gesture_model/datasets/X.npy", landmark_data)
np.save("./gesture_model/datasets/y.npy", labels)
