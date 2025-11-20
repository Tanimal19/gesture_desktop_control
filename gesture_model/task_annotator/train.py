import time
import torch
import torch.nn as nn
import torch.optim as optim
from gesture_model.share import GestureDataset
from gesture_model.trainer import ModelTrainer
from gesture_model.task_annotator.model import TaskAnnotator, BASE_FOLDER


if __name__ == "__main__":

    from data_collection.src.task import TrueTaskType

    for t in TrueTaskType:
        start_time = time.time()
        print(f"Start training model for task {t.name}: {time.asctime()}")

        dataset = GestureDataset(
            X_path=f"{BASE_FOLDER}datasets/{t.name}_X.npy",
            y_path=f"{BASE_FOLDER}datasets/{t.name}_y.npy",
        )

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
