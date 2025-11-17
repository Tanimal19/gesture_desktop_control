import pandas as pd
import numpy as np
from gesture_model.share import generate_samples
from gesture_model.graph_tcn.model import GTCNModel


if __name__ == "__main__":
    label_df = pd.read_csv("./data_collection/datasets/p0/labels.csv")
    landmark_df = pd.read_csv("./data_collection/datasets/p0/task_result_processed.csv")

    df = pd.merge(landmark_df, label_df, on=["timestamp", "task", "trail"], how="left")
    df = df[df["label"].notnull()]  # keep only labeled frames

    feature_columns = [
        f"{lm.name}_{dim}" for dim in ["x", "y", "z"] for lm in GTCNModel.LANDMARKS
    ]

    groups = df.groupby(["task", "trail"])
    all_samples = []
    for (task, trail), group in groups:
        samples = generate_samples(
            group, GTCNModel.WINDOW_LENGTH, feature_columns, padding=False
        )

        for sample in samples:
            sample["features"] = sample["features"].values.reshape(
                (GTCNModel.WINDOW_LENGTH, len(GTCNModel.LANDMARKS), 3)
            )  # shape: (frame_window, num_landmarks, 3)
            sample["features"] = sample["features"].astype("float32")

        all_samples.extend(samples)

    # save samples as .npy
    X = np.array([sample["features"] for sample in all_samples])  # (N, T, 3)
    y = np.array([sample["label"] for sample in all_samples])  # (N
    print(f"X shape: {X.shape}, y shape: {y.shape}")
    np.save("./gesture_model/graph_tcn/X.npy", X)
    np.save("./gesture_model/graph_tcn/y.npy", y)
