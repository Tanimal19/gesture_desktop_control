import time
import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import csv
from config import ANNOTATOR_BASE_FOLDER
from data_collection.src.task import TrueTaskType
from gesture_model.utils import extend_landmark_columns
from gesture_model.model import GestureDataset
from gesture_model.model_runner import GestureModelTrainer
from gesture_model.task_annotator.model import TaskAnnotator


y_mapping_csv = ANNOTATOR_BASE_FOLDER + "task_label_mappings.csv"


def save_y_mapping(y_mapping):
    with open(y_mapping_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["task", "original", "mapped"])
        for task, labels in y_mapping.items():
            original = list(labels.keys())
            mapped = [labels[ol] for ol in original]
            writer.writerow([task, original, mapped])


def read_y_mapping():
    y_mapping = {}
    with open(y_mapping_csv, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            task = row["task"]
            original = eval(row["original"])
            mapped = eval(row["mapped"])
            y_mapping[task] = {o: m for o, m in zip(original, mapped)}
    return y_mapping


if __name__ == "__main__":
    print(f"Start training script: {time.asctime()}")

    df = pd.read_csv(ANNOTATOR_BASE_FOLDER + "training_data.csv")

    avaliable_tasks = list(df["task"].unique())
    y_mappings = {}

    for t in TrueTaskType:
        if t.name not in avaliable_tasks:
            print(f"- Skipping task: {t.name} (no data found)")
            continue
        print(f"+ Generate datasets for task: {t.name}")

        task_group = df[df["task"] == t.name]

        # create y mapping
        original_labels = sorted(task_group["label"].unique())
        mapped_labels = list(range(len(original_labels)))
        y_mapping = {ol: ml for ol, ml in zip(original_labels, mapped_labels)}
        print(f"> y_mapping: {y_mapping}")
        y_mappings[t.name] = y_mapping

        model = TaskAnnotator(y_mapping)

        # generate dataset
        X: list[torch.Tensor] = []
        y: list[int] = []
        for _, trail in task_group.groupby("trail"):
            for start_idx in range(0, len(trail) - TaskAnnotator.WINDOW_LENGTH + 1):
                # each window
                end_idx = start_idx + TaskAnnotator.WINDOW_LENGTH
                window = trail.iloc[start_idx:end_idx]

                landmark_window = extend_landmark_columns(
                    window, TaskAnnotator.WINDOW_LENGTH
                )
                label = window.iloc[-1]["label"]

                X.append(model.landmarks_window_to_X(landmark_window))
                y.append(y_mapping[label])

        X_tensor = torch.stack(X)  # (N, window_length, feature_dim)
        y_tensor = torch.tensor(y, dtype=torch.long)  # (N,)
        print(f"> Dataset shpae: {X_tensor.shape}, {y_tensor.shape}")

        dataset = GestureDataset(X_tensor, y_tensor)

        trainer = GestureModelTrainer(
            output_path=ANNOTATOR_BASE_FOLDER
            + "models/"
            + f"{t.name}_wieghted_annotator.pth",
            model=model,
            dataset=dataset,
        )

        weights = [0.1 if label == "NONE" else 1.0 for label in y_mapping.keys()]
        print(f"> Using weights: {weights}")

        criterion = nn.CrossEntropyLoss(weight=torch.tensor(weights))
        optimizer = optim.Adam(model.parameters(), lr=1e-3)

        # start training
        start_time = time.time()
        print(f"+ Start training for task {t.name}.")
        trainer.train(criterion, optimizer, epochs=200)
        print(f"Completed in {time.time() - start_time:.2f} seconds.")

    # save y mappings
    save_y_mapping(y_mappings)
