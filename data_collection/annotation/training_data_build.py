import pandas as pd
import numpy as np
from data_collection.annotation.utils import split_landmarks, offset_landmarks
from gesture_model.utils import label_to_index, LANDMARKS as GM_LANDMARKS
from gesture_model.model import WINDOW_LENGTH

df_label = pd.read_csv("./data_collection/datasets/p0/labels.csv")
df_lm = pd.read_csv("./data_collection/datasets/p0/task_result.csv")
df = df_lm.merge(df_label, on=["timestamp", "task", "trail"], how="left")
df = df.dropna(subset=["label"]).reset_index(drop=True)

df = split_landmarks(df)
df = offset_landmarks(df)


# build training samples
samples = []
df_groups = df.groupby(["task", "trail"])
for (task, trail), group in df_groups:
    print(f"Processing: task={task}, trail={trail}, total frames={len(group)}")

    num_frames = len(group)
    for start_idx in range(0, num_frames - WINDOW_LENGTH + 1):
        end_idx = start_idx + WINDOW_LENGTH
        window = group.iloc[start_idx:end_idx]

        # extract landmark data
        lm_array = window[GM_LANDMARKS].copy()
        lm_array = lm_array.values.reshape(
            (WINDOW_LENGTH, len(GM_LANDMARKS) // 3, 3)
        )  # shape: (frame_window, num_landmarks, 3)
        lm_array = lm_array.astype("float32")

        # get label (label of the last frame in the window)
        label = window["label"].values[-1]

        samples.append(
            {
                "landmarks": lm_array,
                "label": label_to_index(label),
            }
        )


# convert samples to NPY arrays and save
landmark_data = np.array([sample["landmarks"] for sample in samples])
print("X shape:", landmark_data.shape)  # (num_samples, frame_window, num_landmarks, 3)

labels = np.array([sample["label"] for sample in samples])
print("y shape:", labels.shape)  # (num_samples,)
print("Unique labels:", np.unique(labels))

np.save("./gesture_model/datasets/X.npy", landmark_data)
np.save("./gesture_model/datasets/y.npy", labels)
