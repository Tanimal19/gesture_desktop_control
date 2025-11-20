import time
import os
import torch
import torch.nn as nn
import torch.optim as optim
from gesture_model.share import GestureDataset
from gesture_model.trainer import ModelTrainer
from gesture_model.task_annotator.model import TaskAnnotator, BASE_FOLDER
from data_collection.src.task import TrueTaskType
from gesture_model.task_annotator.data import read_y_mapping


if __name__ == "__main__":

    y_mapping = read_y_mapping()

    for t in TrueTaskType:
        X_path = BASE_FOLDER + "datasets/" + t.name + "_X.npy"
        y_path = BASE_FOLDER + "datasets/" + t.name + "_y.npy"

        if not os.path.exists(X_path) or not os.path.exists(y_path):
            print(f"- Skipping task {t.name} (no dataset found)")
            continue
        start_time = time.time()
        print(f"+ Start training for task {t.name}: {time.asctime()}")

        dataset = GestureDataset(X_path, y_path)
        num_classes = len(torch.unique(dataset.y))
        model = TaskAnnotator(y_mapping[t.name])

        trainer = ModelTrainer(
            output_path=f"{BASE_FOLDER}models/{t.name}.pth",
            model=model,
            dataset=dataset,
        )

        trainer.split_data(train_ratio=0.8)

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=5e-4)

        trainer.training_epochs(criterion, optimizer, epochs=200)

        print(f"Completed in {time.time() - start_time:.2f} seconds.")
