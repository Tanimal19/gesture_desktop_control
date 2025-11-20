import pandas as pd
import numpy as np
import csv
from gesture_model.utils import generate_samples, split_landmark_columns
from gesture_model.task_annotator.model import TaskAnnotator, BASE_FOLDER
from collections import Counter


def compute_distance_features(df: pd.DataFrame, lm1: str, lm2: str, dist_name: str):
    vec = (
        df[[f"{lm1}_x", f"{lm1}_y", f"{lm1}_z"]].values
        - df[[f"{lm2}_x", f"{lm2}_y", f"{lm2}_z"]].values
    )
    dist = np.linalg.norm(vec, axis=1)
    df[dist_name] = dist
    return df


if __name__ == "__main__":
    df = pd.read_csv("./data_collection/datasets/task_result_labeled.csv")

    df = split_landmark_columns(df, TaskAnnotator.LANDMARKS)
    feature_columns = [
        f"{lm.name}_{dim}" for dim in ["x", "y", "z"] for lm in TaskAnnotator.LANDMARKS
    ]

    for lm1, lm2 in TaskAnnotator.DIST_FEATURES:
        dist_name = f"{lm1.name}_{lm2.name}_dist"
        df = compute_distance_features(df, lm1.name, lm2.name, dist_name)
        feature_columns.append(dist_name)

    task_y_mapping = {}
    task_groups = df.groupby("task")
    for task, group in task_groups:
        print(f"Processing task: {task}")

        # remapping labels to start from 0
        unique_labels = group["label"].unique()
        label_mapping = {old: i for i, old in enumerate(sorted(unique_labels))}
        task_y_mapping[task] = label_mapping
        print(f"Label mapping: {label_mapping}")

        # generate samples (sliding window) for each trail
        task_samples = []
        trail_groups = group.groupby("trail")
        for trail, tgroup in trail_groups:
            samples = generate_samples(
                tgroup,
                TaskAnnotator.WINDOW_LENGTH,
                feature_columns,
                label_mapping,
                padding=False,
            )

            for sample in samples:
                sample["features"] = sample["features"].values.reshape(
                    (TaskAnnotator.WINDOW_LENGTH, len(feature_columns))
                )  # shape: (frame_window, num_features)
                sample["features"] = sample["features"].astype("float32")

            task_samples.extend(samples)

        # save samples for this task
        X = np.array([sample["features"] for sample in task_samples])  # (N, T, F)
        y = np.array([sample["label"] for sample in task_samples])  # (N,)
        print(f"X shape: {X.shape}, y shape: {y.shape}")
        print(f"Label distribution: {Counter(y)}")
        np.save(BASE_FOLDER + "datasets/" + str(task) + "_X.npy", X)
        np.save(BASE_FOLDER + "datasets/" + str(task) + "_y.npy", y)

    # save task label mappings
    with open(
        BASE_FOLDER + "datasets/task_label_mappings.csv", "w", newline=""
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["task", "original_label", "mapped_label"])
        for task, mapping in task_y_mapping.items():
            for original_label, mapped_label in mapping.items():
                writer.writerow([task, original_label, mapped_label])
