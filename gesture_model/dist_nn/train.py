import time
import torch.nn as nn
import torch.optim as optim
from gesture_model.share import GestureDataset, ModelTrainer
from gesture_model.dist_nn.model import DistNN


if __name__ == "__main__":
    start_time = time.time()
    print(f"start train: {time.asctime()}")

    model = DistNN()
    dataset = GestureDataset(
        X_path="./gesture_model/dist_nn/X.npy",
        y_path="./gesture_model/dist_nn/y.npy",
    )

    trainer = ModelTrainer(
        output_folder="./gesture_model/dist_nn/",
        model=model,
        dataset=dataset,
    )

    trainer.split_data(train_ratio=0.8)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)

    trainer.training_epochs(criterion, optimizer, epochs=100)

    print(f"Completed in {time.time() - start_time:.2f} seconds.")
