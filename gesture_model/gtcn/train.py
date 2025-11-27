import time
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from datapath import GTCN_BASE_FOLDER, DC_FULL_LABEL_CSV
from share.utils import extend_landmark_columns
from gesture_model.model_trainer import (
    TensorDataset,
    TrainingConfig,
    GestureModelTrainer,
    setup_logging,
)
from gesture_model.model import GestureLabel
from gesture_model.gtcn.model import GTCNModel


if __name__ == "__main__":
    logger = setup_logging(GTCN_BASE_FOLDER + "train.log")
    logger.info(f"Start training script: {time.asctime()}")

    # TODO: set to False to skip dataset regeneration
    regenerate_dataset = True

    if regenerate_dataset:
        logger.info(f"Generating dataset from labeled CSV.")
        df = pd.read_csv(DC_FULL_LABEL_CSV)
        df = df[df["label"] != "-1"]  # keep only labeled frames

        # generate dataset
        X: list[torch.Tensor] = []
        y: list[int] = []

        groups = df.groupby(["participant_id", "task", "trail"])

        for (pid, taskid, trailid), trail in groups:
            print(f"+ Processing participant {pid}, task {taskid}, trail {trailid}")

            for start_idx in range(0, len(trail) - GTCNModel.WINDOW_LENGTH + 1):
                # each window
                end_idx = start_idx + GTCNModel.WINDOW_LENGTH
                window = trail.iloc[start_idx:end_idx]

                landmark_window = extend_landmark_columns(
                    window, GTCNModel.WINDOW_LENGTH
                )
                label = window.iloc[-1]["label"]

                X.append(GTCNModel.landmarks_window_to_X(landmark_window))
                y.append(GestureLabel[label].value)

        X_tensor = torch.stack(X)  # (N, window_length, feature_dim)
        y_tensor = torch.tensor(y, dtype=torch.long)  # (N,)

        # save the dataset to .pkl file
        X_tensor.numpy().dump(GTCN_BASE_FOLDER + "X.pkl")
        y_tensor.numpy().dump(GTCN_BASE_FOLDER + "y.pkl")

    # start training
    X_array = np.load(GTCN_BASE_FOLDER + "X.pkl", allow_pickle=True)
    y_array = np.load(GTCN_BASE_FOLDER + "y.pkl", allow_pickle=True)
    X_tensor = torch.tensor(X_array, dtype=torch.float32)
    y_tensor = torch.tensor(y_array, dtype=torch.long)
    logger.info(f"dataset shape: {X_tensor.shape}, {y_tensor.shape}")

    dataset = TensorDataset(X_tensor, y_tensor)

    # TODO: try different training configs
    configs = [
        TrainingConfig(
            name="default-1e3",
            weight=None,
            learning_rate=1e-3,
            max_epochs=100,
        ),
        TrainingConfig(
            name="default-5e3",
            weight=None,
            learning_rate=5e-3,
            max_epochs=100,
        ),
        TrainingConfig(
            name="weight-5e3",
            weight=[
                0.2 if label == GestureLabel.NONE.value else 1.0
                for label in GestureLabel
            ],
            learning_rate=5e-3,
            max_epochs=100,
        ),
    ]

    trainer = GestureModelTrainer(
        output_dir=GTCN_BASE_FOLDER + "models/",
        model=GTCNModel,
        dataset=dataset,
        test_size=0.2,
        configs=configs,
    )

    trainer.run_all()
