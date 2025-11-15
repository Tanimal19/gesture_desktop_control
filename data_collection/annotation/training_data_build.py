import pandas as pd
from gesture_model.utils import label_to_index

frame_window = 30  # number of frames in each training sample


df_label = pd.read_csv("./data_collection/datasets/p0/labels.csv")
df_lm = pd.read_csv("./data_collection/datasets/p0/task_result.csv")
df = df_lm.merge(df_label, on=["timestamp", "task", "trail"], how="left")

# split landmark columns into x, y, z
meta_cols = ["timestamp", "task", "trail", "label"]
LANDMARKS = [c for c in df.columns if c not in meta_cols]
for lm in LANDMARKS:
    df[[f"{lm}_x", f"{lm}_y", f"{lm}_z"]] = (
        df[lm].str.split("_", expand=True).astype(float)
    )
df = df.drop(columns=LANDMARKS)

# drop rows with missing labels
df = df.dropna(subset=["label"]).reset_index(drop=True)

# offset landmarks by WRIST position
for lm in LANDMARKS:
    if lm != "WRIST":
        for dim in ["x", "y", "z"]:
            df[f"{lm}_{dim}"] = df[f"{lm}_{dim}"] - df[f"WRIST_{dim}"]

wrist_cols = [f"WRIST_{dim}" for dim in ["x", "y", "z"]]
df = df.drop(columns=wrist_cols)
LANDMARKS = [c for c in df.columns if c not in meta_cols]  # update


# build training samples
samples = []
df_groups = df.groupby(["task", "trail"])
for (task, trail), group in df_groups:
    print(f"Processing: task={task}, trail={trail}, total frames={len(group)}")

    num_frames = len(group)
    for start_idx in range(0, num_frames - frame_window + 1):
        end_idx = start_idx + frame_window
        window = group.iloc[start_idx:end_idx]

        # extract landmark data
        lm_array = window[LANDMARKS].copy()
        lm_array = lm_array.values.reshape(
            (frame_window, len(LANDMARKS) // 3, 3)
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
import numpy as np

landmark_data = np.array([sample["landmarks"] for sample in samples])
print("X shape:", landmark_data.shape)  # (num_samples, frame_window, num_landmarks, 3)

labels = np.array([sample["label"] for sample in samples])
print("y shape:", labels.shape)  # (num_samples,)
print("Unique labels:", np.unique(labels))

np.save("./gesture_model/datasets/X.npy", landmark_data)
np.save("./gesture_model/datasets/y.npy", labels)
