import time
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import csv
import numpy as np
from config import GTCN_BASE_FOLDER
from gesture_model.utils import extend_landmark_columns
from gesture_model.model import GestureDataset, GestureLabel
from gesture_model.model_runner import GestureModelTrainer
from gesture_model.graph_tcn.model import GTCNModel

if __name__ == "__main__":
    print(f"Start training script: {time.asctime()}")

    # df = pd.read_csv(GTCN_BASE_FOLDER + "task_result_labeled_auto.csv")
    # df = df[df["label"] != "-1"]  # keep only labeled frames

    # model = GTCNModel()

    # # generate dataset
    # X: list[torch.Tensor] = []
    # y: list[int] = []

    # groups = df.groupby(["participant_id", "task", "trail"])

    # for (pid, taskid, trailid), trail in groups:
    #     print(f"+ Processing participant {pid}, task {taskid}, trail {trailid}")

    #     for start_idx in range(0, len(trail) - GTCNModel.WINDOW_LENGTH + 1):
    #         # each window
    #         end_idx = start_idx + GTCNModel.WINDOW_LENGTH
    #         window = trail.iloc[start_idx:end_idx]

    #         landmark_window = extend_landmark_columns(window, GTCNModel.WINDOW_LENGTH)
    #         label = window.iloc[-1]["label"]

    #         X.append(model.landmarks_window_to_X(landmark_window))
    #         y.append(GestureLabel[label].value)

    # X_tensor = torch.stack(X)  # (N, window_length, feature_dim)
    # y_tensor = torch.tensor(y, dtype=torch.long)  # (N,)
    # print(f"> Dataset shape: {X_tensor.shape}, {y_tensor.shape}")

    # # save the dataset to .npy file
    # X_tensor.numpy().dump(GTCN_BASE_FOLDER + "X.npy")
    # y_tensor.numpy().dump(GTCN_BASE_FOLDER + "y.npy")

    # load the dataset from .npy file
    X_tensor = torch.from_numpy(np.load(GTCN_BASE_FOLDER + "X.npy"))
    y_tensor = torch.from_numpy(np.load(GTCN_BASE_FOLDER + "y.npy"))

    model = GTCNModel()
    dataset = GestureDataset(X_tensor, y_tensor)

    trainer = GestureModelTrainer(
        output_path=GTCN_BASE_FOLDER + "model.pth",
        model=model,
        dataset=dataset,
    )

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)

    # start training
    start_time = time.time()
    print(f"+ Start training GTCN.")
    trainer.train(criterion, optimizer, epochs=200)
    print(f"Completed in {time.time() - start_time:.2f} seconds.")

# python -u -m gesture_model.graph_tcn.train 2>&1 | tee -a ./gesture_model/graph_tcn/train.log
