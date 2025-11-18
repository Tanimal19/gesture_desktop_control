import pandas as pd
import numpy as np
from gesture_model.utils import generate_samples, GestureLabel
from gesture_model.task_annotator.model import TaskAnnotator, BASE_FOLDER
from collections import Counter


if __name__ == "__main__":
    label_df = pd.read_csv("./data_collection/datasets/processed/labels.csv")
    landmark_df = pd.read_csv(
        "./data_collection/datasets/processed/task_result_processed.csv"
    )

    df = pd.merge(landmark_df, label_df, on=["timestamp", "task", "trail"], how="left")
    df = df[df["label"].notnull()]  # keep only labeled frames

    feature_columns = [
        f"{lm.name}_{dim}" for dim in ["x", "y", "z"] for lm in NNAnnotator.LANDMARKS
    ]

    # compute distance features
    # for lm1, lm2 in NNAnnotator.DIST_FEATURES:
    #     dist_name = f"{lm1.name}_{lm2.name}_dist"
    #     df = compute_distance_features(df, f"{lm1.name}", f"{lm2.name}", dist_name)
    #     feature_columns.append(dist_name)

    groups = df.groupby("task")
    for task, group in groups:
        print(f"Processing task: {task}")
        task_samples = []

        trail_groups = group.groupby("trail")
        for trail, tgroup in trail_groups:
            samples = generate_samples(
                tgroup, NNAnnotator.WINDOW_LENGTH, feature_columns, padding=False
            )

            for sample in samples:
                sample["features"] = sample["features"].values.reshape(
                    (NNAnnotator.WINDOW_LENGTH, len(feature_columns))
                )  # shape: (frame_window, num_features)
                sample["features"] = sample["features"].astype("float32")

            task_samples.extend(samples)

        # save samples for this task
        X = np.array([sample["features"] for sample in task_samples])  # (N, T, F)
        y = np.array([sample["label"] for sample in task_samples])  # (N,)
        print(f"X shape: {X.shape}, y shape: {y.shape}")
        np.save(BASE_FOLDER + "datasets/" + str(task) + "_X.npy", X)
        np.save(BASE_FOLDER + "datasets/" + str(task) + "_y.npy", y)
