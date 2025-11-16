import pandas as pd
import numpy as np
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmark
from gesture_model.share import generate_samples
from gesture_model.dist_nn.model import DistNN


DIST_COLUMNS = ["thumb_index_dist", "thumb_middle_dist", "index_middle_dist"]


def compute_distance_features(df, landmark1, landmark2, name):
    df[name] = 0.0
    for dim in ["x", "y", "z"]:
        df[name] += (df[f"{landmark1}_{dim}"] - df[f"{landmark2}_{dim}"]) ** 2
    df[name] = np.sqrt(df[name])
    return df


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
    all_samples = []
    for (task, trail), group in groups:
        samples = generate_samples(
            group, DistNN.WINDOW_LENGTH, DIST_COLUMNS, padding=False
        )

        for sample in samples:
            sample["features"] = sample["features"].values.reshape(
                (DistNN.WINDOW_LENGTH, len(DIST_COLUMNS))
            )  # shape: (frame_window, 3)
            sample["features"] = sample["features"].astype("float32")

        all_samples.extend(samples)

    # save samples as .npy
    X = np.array([sample["features"] for sample in all_samples])  # (N, T, 3)
    y = np.array([sample["label"] for sample in all_samples])  # (N
    print(f"X shape: {X.shape}, y shape: {y.shape}")
    np.save("./gesture_model/dist_nn/X.npy", X)
    np.save("./gesture_model/dist_nn/y.npy", y)
