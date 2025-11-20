import pandas as pd
import numpy as np
from gesture_model.task_annotator.model import TaskAnnotator
from gesture_model.utils import split_landmark_columns
from share.worker.gesture import GestureModelRunner

from data_collection.src.task import TrueTaskType


df = pd.read_csv("./data_collection/datasets/task_result_merged.csv")

df = split_landmark_columns(df, TaskAnnotator.LANDMARKS)
feature_columns = [
    f"{lm.name}_{dim}" for dim in ["x", "y", "z"] for lm in TaskAnnotator.LANDMARKS
]


def compute_distance_features(df, lm1_name, lm2_name, dist_name):
    vec = (
        df[[f"{lm1_name}_x", f"{lm1_name}_y", f"{lm1_name}_z"]].values
        - df[[f"{lm2_name}_x", f"{lm2_name}_y", f"{lm2_name}_z"]].values
    )
    dist = np.linalg.norm(vec, axis=1)
    df[dist_name] = dist
    return df


for lm1, lm2 in TaskAnnotator.DIST_FEATURES:
    dist_name = f"{lm1.name}_{lm2.name}_dist"
    df = compute_distance_features(df, f"{lm1.name}", f"{lm2.name}", dist_name)
    feature_columns.append(dist_name)


def generate_samples(df, window_length, feature_columns, padding=True) -> list[dict]:
    # pad the beginning with the first row to ensure enough frames
    if padding:
        pad = window_length - 1
        first_row = df.iloc[[0]].copy()
        padding = pd.concat([first_row] * pad, ignore_index=True)
        df = pd.concat([padding, df.reset_index(drop=True)], ignore_index=True)

    samples = []
    num_frames = len(df)
    for start_idx in range(0, num_frames - window_length + 1):
        end_idx = start_idx + window_length
        window = df.iloc[start_idx:end_idx]
        feature_array = window[feature_columns].copy()

        samples.append(feature_array)
    return samples


groups = df.groupby("task")
for task, group in groups:
    
    
    model = TaskAnnotator(num_classes= len(TrueTaskType))
    runner = GestureModelRunner()
    print(f"Processing task: {task}")
    task_samples = []

    trail_groups = group.groupby("trail")
    for trail, tgroup in trail_groups:
        samples = generate_samples(
            tgroup, TaskAnnotator.WINDOW_LENGTH, feature_columns, padding=False
        )

        for sample in samples:
            GestureModelRunner.
        # save samples for this task
        X = np.array([sample["features"] for sample in task_samples])  # (N, T, F)
        y = np.array([sample["label"] for sample in task_samples])  # (N,)
        print(f"X shape: {X.shape}, y shape: {y.shape}")
        print(f"Label distribution: {Counter(y)}")
        np.save(BASE_FOLDER + "datasets/" + str(task) + "_X.npy", X)
        np.save(BASE_FOLDER + "datasets/" + str(task) + "_y.npy", y)

for t in TrueTaskType:

    df = pd.read_csv(f"./data_collection/datasets/merged.csv")

    num_classes = len(torch.unique(dataset.y))
    model = TaskAnnotator(num_classes=num_classes)

    trainer = ModelTrainer(
        output_path=f"{BASE_FOLDER}models/{t.name}.pth",
        model=model,
        dataset=dataset,
    )

    trainer.split_data(train_ratio=0.8)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)

    trainer.training_epochs(criterion, optimizer, epochs=100)

    print(f"Completed in {time.time() - start_time:.2f} seconds.")
