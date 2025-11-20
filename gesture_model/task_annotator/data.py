import pandas as pd
import numpy as np
import csv
from gesture_model.utils import generate_samples, split_landmark_columns
from gesture_model.task_annotator.model import TaskAnnotator, BASE_FOLDER
from data_collection.src.task import TrueTaskType


Y_MAPPING_CSV = BASE_FOLDER + "task_label_mappings.csv"


def compute_distance_features(df: pd.DataFrame, lm1: str, lm2: str, dist_name: str):
    vec = (
        df[[f"{lm1}_x", f"{lm1}_y", f"{lm1}_z"]].values
        - df[[f"{lm2}_x", f"{lm2}_y", f"{lm2}_z"]].values
    )
    dist = np.linalg.norm(vec, axis=1)
    df[dist_name] = dist
    return df


def save_y_mapping(y_mapping):
    with open(Y_MAPPING_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["task", "original", "mapped"])
        for task, labels in y_mapping.items():
            original = list(labels.keys())
            mapped = [labels[ol] for ol in original]
            writer.writerow([task, original, mapped])


def read_y_mapping():
    y_mapping = {}
    with open(Y_MAPPING_CSV, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            task = row["task"]
            original = eval(row["original"])
            mapped = eval(row["mapped"])
            y_mapping[task] = {o: m for o, m in zip(original, mapped)}
    return y_mapping


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

    y_mapping = {}

    for t in TrueTaskType:
        if t.name not in list(df["task"].unique()):
            print(f"- Skipping task: {t.name} (no data found)")
            continue
        print(f"+ Processing task: {t.name}")

        task_group = df[df["task"] == t.name]

        # remapping labels to start from 0
        unique_labels = task_group["label"].unique()
        y_mapping[t.name] = {old: i for i, old in enumerate(sorted(unique_labels))}
        print(f"Label mapping: {y_mapping[t.name]}")

        # generate samples for each trail
        task_samples = []
        trail_groups = task_group.groupby("trail")
        for trail, trail_group in trail_groups:
            samples = generate_samples(
                trail_group,
                TaskAnnotator.WINDOW_LENGTH,
                feature_columns,
                y_mapping[t.name],
                padding=False,
            )
            task_samples.extend(samples)

        # preprocess samples
        for sample in task_samples:
            sample["features"] = sample["features"].values.reshape(
                (TaskAnnotator.WINDOW_LENGTH, len(feature_columns))
            )  # shape: (frame_window, num_features)
            sample["features"] = sample["features"].astype("float32")

        # save samples as numpy arrays
        X = np.array([sample["features"] for sample in task_samples])  # (N, T, F)
        y = np.array([sample["label"] for sample in task_samples])  # (N,)
        print(f"X shape: {X.shape}, y shape: {y.shape}")
        np.save(BASE_FOLDER + "datasets/" + t.name + "_X.npy", X)
        np.save(BASE_FOLDER + "datasets/" + t.name + "_y.npy", y)

    save_y_mapping(y_mapping)
