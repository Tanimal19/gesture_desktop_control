import time
import pandas as pd
import torch
import numpy as np
from datapath import GTCN_BASE_FOLDER, DC_FINAL_LABEL_CSV, DC_MANUAL_LABEL_CSV
from share.utils import extend_landmark_columns
from gesture_model.model_trainer import (
    TensorDataset,
    TrainingConfig,
    GestureModelTrainer,
    setup_logging,
)
from gesture_model import GestureLabel
from gesture_model.gtcn import GTCNModel


if __name__ == "__main__":
    logger = setup_logging(GTCN_BASE_FOLDER + "train.log")
    logger.info(f"Start training script: {time.asctime()}")

    regenerate_dataset = True

    if regenerate_dataset:
        logger.info(f"Generating dataset from labeled CSV.")
        df = pd.read_csv(DC_MANUAL_LABEL_CSV)
        df = df[df["label"] != "-1"]  # keep only labeled frames

        # generate dataset
        X: list[torch.Tensor] = []
        y: list[int] = []

        groups = df.groupby(["participant_id", "task", "trail"])

        for (pid, taskid, trailid), trail in groups:
            logger.info(
                f"+ Processing participant {pid}, task {taskid}, trail {trailid}"
            )

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
        X_tensor.numpy().dump(
            GTCN_BASE_FOLDER + "datasets/" + f"X{GTCNModel.WINDOW_LENGTH}_manual.pkl"
        )
        y_tensor.numpy().dump(
            GTCN_BASE_FOLDER + "datasets/" + f"y{GTCNModel.WINDOW_LENGTH}_manual.pkl"
        )

    # start training
    X_array = np.load(
        GTCN_BASE_FOLDER + "datasets/" + f"X{GTCNModel.WINDOW_LENGTH}_manual.pkl",
        allow_pickle=True,
    )
    y_array = np.load(
        GTCN_BASE_FOLDER + "datasets/" + f"y{GTCNModel.WINDOW_LENGTH}_manual.pkl",
        allow_pickle=True,
    )
    X_tensor = torch.tensor(X_array, dtype=torch.float32)
    y_tensor = torch.tensor(y_array, dtype=torch.long)
    logger.info(f"dataset shape: {X_tensor.shape}, {y_tensor.shape}")

    dataset = TensorDataset(X_tensor, y_tensor)

    configs = [
        TrainingConfig(
            name=f"win{GTCNModel.WINDOW_LENGTH}-noweight-manual",
            learning_rate=5e-3,
        ),
        TrainingConfig(
            name=f"win{GTCNModel.WINDOW_LENGTH}-weight01-manual",
            weight=[
                0.1 if label == GestureLabel.NONE.value else 1.0
                for label in GestureLabel
            ],
            learning_rate=5e-3,
        ),
        TrainingConfig(
            name=f"win{GTCNModel.WINDOW_LENGTH}-weight05-manual",
            weight=[
                0.5 if label == GestureLabel.NONE.value else 1.0
                for label in GestureLabel
            ],
            learning_rate=5e-3,
        ),
    ]

    trainer = GestureModelTrainer(
        output_dir=GTCN_BASE_FOLDER + "models/",
        model=GTCNModel(),
        dataset=dataset,
        test_size=0.2,
        configs=configs,
    )

    trainer.run_all()
