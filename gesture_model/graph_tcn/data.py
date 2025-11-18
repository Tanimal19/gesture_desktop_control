import pandas as pd
import numpy as np
from collections import Counter
from gesture_model.utils import generate_samples, GestureLabel
from gesture_model.graph_tcn.model import GTCNModel, BASE_FOLDER


if __name__ == "__main__":
    df = pd.read_csv("./data_collection/datasets/processed/task_result_labeled.csv")
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
    X = np.array([sample["features"] for sample in all_samples])
    y = np.array([sample["label"] for sample in all_samples])
    print(f"X={X.shape}, y={y.shape}")

    counts = Counter(y)
    print("label distribution:")
    for label_id, count in counts.items():
        print(f"{GestureLabel(label_id).name}: {count}")

    np.save(f"{BASE_FOLDER}X.npy", X)
    np.save(f"{BASE_FOLDER}y.npy", y)
