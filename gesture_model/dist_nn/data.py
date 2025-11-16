import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmark
from gesture_model.share import GestureLabel
from gesture_model.dist_nn.model import WINDOW_LENGTH


DIST_COLUMNS = ["thumb_index_dist", "thumb_middle_dist", "index_middle_dist"]


def compute_distance_features(df, landmark1, landmark2, name):
    df[name] = 0.0
    for dim in ["x", "y", "z"]:
        df[name] += (df[f"{landmark1}_{dim}"] - df[f"{landmark2}_{dim}"]) ** 2
    df[name] = np.sqrt(df[name])
    return df


def extract_samples(df, window_length):
    # pad the beginning with the first row to ensure enough frames
    pad = window_length - 1
    first_row = df.iloc[[0]].copy()
    padding = pd.concat([first_row] * pad, ignore_index=True)
    df = pd.concat([padding, df.reset_index(drop=True)], ignore_index=True)

    samples = []
    num_frames = len(df)
    for start_idx in range(0, num_frames - window_length + 1):
        end_idx = start_idx + window_length
        window = df.iloc[start_idx:end_idx]

        # extract landmark data
        lm_array = window[DIST_COLUMNS].copy()
        lm_array = lm_array.values.reshape(
            (window_length, len(DIST_COLUMNS))
        )  # shape: (frame_window, 3)
        lm_array = lm_array.astype("float32")

        samples.append(
            {
                "timestamp": window["timestamp"].values[-1],
                "landmarks": lm_array,
                "label": GestureLabel[window["label"].values[-1].upper()].value,
            }
        )
    return samples


class DistDataset(Dataset):
    def __init__(self, X_path, y_path):
        self.X = np.load(X_path)  # (N, T, 3)
        self.y = np.load(y_path)  # (N,)
        self.X = torch.tensor(self.X, dtype=torch.float32)
        self.y = torch.tensor(self.y, dtype=torch.long)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


if __name__ == "__main__":
    label_df = pd.read_csv("./data_collection/datasets/p0/labels.csv")
    landmark_df = pd.read_csv("./data_collection/datasets/p0/task_result_processed.csv")

    df = pd.merge(landmark_df, label_df, on=["timestamp", "task", "trail"], how="left")
    df = df[df["label"].notnull()]  # keep only labeled frames

    df = compute_distance_features(
        df,
        HandLandmark.THUMB_TIP.name,
        HandLandmark.INDEX_FINGER_TIP.name,
        "thumb_index_dist",
    )
    df = compute_distance_features(
        df,
        HandLandmark.THUMB_TIP.name,
        HandLandmark.MIDDLE_FINGER_TIP.name,
        "thumb_middle_dist",
    )
    df = compute_distance_features(
        df,
        HandLandmark.INDEX_FINGER_TIP.name,
        HandLandmark.MIDDLE_FINGER_TIP.name,
        "index_middle_dist",
    )

    groups = df.groupby(["task", "trail"])
    samples = []
    for (task, trail), group in groups:
        print(f"Processing: task={task}, trail={trail}, total frames={len(group)}")
        samples.extend(extract_samples(group, WINDOW_LENGTH))
    print(f"Total samples extracted: {len(samples)}")

    # save samples as .npy
    X = np.array([sample["landmarks"] for sample in samples])  # (N, T, 3)
    y = np.array([sample["label"] for sample in samples])  # (N
    print(f"X shape: {X.shape}, y shape: {y.shape}")
    np.save("./gesture_model/dist_nn/X.npy", X)
    np.save("./gesture_model/dist_nn/y.npy", y)
