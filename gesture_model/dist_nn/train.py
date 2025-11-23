import time
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from config import DISTNN_BASE_FOLDER, DC_DATASET_FOLDER
from gesture_model.utils import extend_landmark_columns
from gesture_model.model import GestureDataset, GestureLabel
from gesture_model.model_runner import GestureModelTrainer
from gesture_model.dist_nn.model import DistNN


if __name__ == "__main__":
    print(f"Start training script: {time.asctime()}")

    df = pd.read_csv(DC_DATASET_FOLDER + "task_result_labeled_auto.csv")
    df = df[df["label"] != "-1"]  # keep only labeled frames

    model = DistNN()

    # generate dataset
    X: list[torch.Tensor] = []
    y: list[int] = []

    groups = df.groupby(["participant_id", "task", "trail"])

    for (pid, taskid, trailid), trail in groups:
        print(f"+ Processing participant {pid}, task {taskid}, trail {trailid}")

        for start_idx in range(0, len(trail) - DistNN.WINDOW_LENGTH + 1):
            # each window
            end_idx = start_idx + DistNN.WINDOW_LENGTH
            window = trail.iloc[start_idx:end_idx]

            landmark_window = extend_landmark_columns(window, DistNN.WINDOW_LENGTH)
            label = window.iloc[-1]["label"]

            X.append(model.landmarks_window_to_X(landmark_window))
            y.append(GestureLabel[label].value)

    X_tensor = torch.stack(X)  # (N, window_length, feature_dim)
    y_tensor = torch.tensor(y, dtype=torch.long)  # (N,)
    print(f"> Dataset shape: {X_tensor.shape}, {y_tensor.shape}")

    dataset = GestureDataset(X_tensor, y_tensor)

    trainer = GestureModelTrainer(
        output_path=DISTNN_BASE_FOLDER + "model_weighted.pth",
        model=model,
        dataset=dataset,
    )

    weights = [0.5 if label == GestureLabel.NONE else 1.0 for label in GestureLabel]
    print(f"> Using weights: {weights}")
    criterion = nn.CrossEntropyLoss(weight=torch.tensor(weights))

    # criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=5e-3)

    # start training
    start_time = time.time()
    print(f"+ Start training task annotator")
    trainer.train(criterion, optimizer, epochs=200)
    print(f"Completed in {time.time() - start_time:.2f} seconds.")

# python -u -m gesture_model.dist_nn.train 2>&1 | tee -a gesture_model/dist_nn/train.log
