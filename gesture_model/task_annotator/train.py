import time
import pandas as pd
import torch
import os
import csv
from datapath import ANNOTATOR_BASE_FOLDER, DC_P0_LABEL_CSV
from data_collection_study.src.task import TrueTaskType
from share.utils import extend_landmark_columns
from gesture_model.model_trainer import (
    TensorDataset,
    TrainingConfig,
    GestureModelTrainer,
    setup_logging,
)
from gesture_model.task_annotator.model import TaskAnnotator


ANNOTATOR_MAPPING_CSV = ANNOTATOR_BASE_FOLDER + "task_label_mappings.csv"


def save_y_mapping(y_mapping):
    with open(ANNOTATOR_MAPPING_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["task", "original", "mapped"])
        for task, labels in y_mapping.items():
            original = list(labels.keys())
            mapped = [labels[ol] for ol in original]
            writer.writerow([task, original, mapped])


def read_y_mapping():
    y_mapping = {}
    with open(ANNOTATOR_MAPPING_CSV, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            task = row["task"]
            original = eval(row["original"])
            mapped = eval(row["mapped"])
            y_mapping[task] = {o: m for o, m in zip(original, mapped)}
    return y_mapping


if __name__ == "__main__":
    logger = setup_logging(ANNOTATOR_BASE_FOLDER + "train.log")
    logger.info(f"Start training script: {time.asctime()}")

    df = pd.read_csv(DC_P0_LABEL_CSV)
    df = df[df["label"] != "-1"]  # keep only labeled frames

    avaliable_tasks = list(df["task"].unique())
    y_mappings = {}

    for t in TrueTaskType:
        if t.name not in avaliable_tasks:
            logger.warning(f"\n- Skipping task: {t.name} (no data found)")
            continue
        logger.info(f"\n+ Training model for task: {t.name}")

        output_dir = ANNOTATOR_BASE_FOLDER + "models/" + t.name + "/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        task_group = df[df["task"] == t.name]

        # create y mapping
        original_labels = sorted(task_group["label"].unique())
        mapped_labels = list(range(len(original_labels)))
        y_mapping = {ol: ml for ol, ml in zip(original_labels, mapped_labels)}
        y_mappings[t.name] = y_mapping
        logger.info(f"label mapping: {y_mapping}")

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

                X.append(TaskAnnotator.landmarks_window_to_X(landmark_window))
                y.append(y_mapping[label])

        X_tensor = torch.stack(X)  # (N, window_length, feature_dim)
        y_tensor = torch.tensor(y, dtype=torch.long)  # (N,)
        logger.info(f"dataset shape: {X_tensor.shape}, {y_tensor.shape}")
        dataset = TensorDataset(X_tensor, y_tensor)

        model = TaskAnnotator(y_mapping)

        config = TrainingConfig(
            name="default",
            weight=None,
            learning_rate=1e-3,
            max_epochs=200,
        )

        trainer = GestureModelTrainer(
            output_dir=output_dir,
            model=model,
            dataset=dataset,
            test_size=0.0,
            configs=[config],
        )

        trainer.run_all()

    # save y mappings
    save_y_mapping(y_mappings)
