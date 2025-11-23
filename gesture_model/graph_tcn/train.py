import time
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from config import GTCN_BASE_FOLDER, DC_DATASET_FOLDER
from gesture_model.utils import extend_landmark_columns
from gesture_model.model import GestureDataset, GestureLabel
from gesture_model.model_runner import GestureModelTrainer
from gesture_model.graph_tcn.model import GTCNModel


def create_dataset(filename):
    df = pd.read_csv(filename)
    df = df[df["label"] != "-1"]  # keep only labeled frames

    model = GTCNModel()

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

            landmark_window = extend_landmark_columns(window, GTCNModel.WINDOW_LENGTH)
            label = window.iloc[-1]["label"]

            X.append(model.landmarks_window_to_X(landmark_window))
            y.append(GestureLabel[label].value)

    X_tensor = torch.stack(X)  # (N, window_length, feature_dim)
    y_tensor = torch.tensor(y, dtype=torch.long)  # (N,)
    print(f"> Dataset shape: {X_tensor.shape}, {y_tensor.shape}")

    # save the dataset to .pkl file
    X_tensor.numpy().dump(GTCN_BASE_FOLDER + "X.pkl")
    y_tensor.numpy().dump(GTCN_BASE_FOLDER + "y.pkl")


def training():
    print(f"Start training script: {time.asctime()}")

    # load the dataset from .pkl file
    X_array = np.load(GTCN_BASE_FOLDER + "X.pkl", allow_pickle=True)
    y_array = np.load(GTCN_BASE_FOLDER + "y.pkl", allow_pickle=True)
    X_tensor = torch.tensor(X_array, dtype=torch.float32)
    y_tensor = torch.tensor(y_array, dtype=torch.long)
    print(f"> Loaded dataset shape: {X_tensor.shape}, {y_tensor.shape}")

    model = GTCNModel()
    dataset = GestureDataset(X_tensor, y_tensor)

    trainer = GestureModelTrainer(
        output_path=GTCN_BASE_FOLDER + "model.pth",
        model=model,
        dataset=dataset,
    )

    # weights = [0.1 if label == GestureLabel.NONE else 1.0 for label in GestureLabel]
    # print(f"> Using weights: {weights}")
    # criterion = nn.CrossEntropyLoss(weight=torch.tensor(weights))

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)

    # start training
    start_time = time.time()
    print(f"+ Start training GTCN.")
    trainer.train(criterion, optimizer, epochs=200)
    print(f"Completed in {time.time() - start_time:.2f} seconds.")


if __name__ == "__main__":
    # create_dataset(DC_DATASET_FOLDER + "task_result_labeled_auto.csv")
    training()


# python -u -m gesture_model.graph_tcn.train 2>&1 | tee -a ./gesture_model/graph_tcn/train.log
