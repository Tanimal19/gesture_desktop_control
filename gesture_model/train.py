import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torch.utils.data import random_split
import torch.nn as nn
import torch.optim as optim
from model import GestureNet
import time


class GestureDataset(Dataset):
    def __init__(self, X_path, y_path):
        self.X = np.load(X_path)  # (N, 30, 12, 3)
        self.y = np.load(y_path)  # (N,)
        self.X = torch.tensor(self.X, dtype=torch.float32)
        self.y = torch.tensor(self.y, dtype=torch.long)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


def train_one_epoch(model, loader, optimizer, criterion, device):
    model.train()
    total_loss = 0
    total_correct = 0
    total = 0

    for X, y in loader:
        X, y = X.to(device), y.to(device)

        optimizer.zero_grad()
        out = model(X)  # (B, 8)
        loss = criterion(out, y)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * X.size(0)
        pred = out.argmax(dim=1)
        total_correct += (pred == y).sum().item()
        total += X.size(0)

    return total_loss / total, total_correct / total


def validate(model, loader, criterion, device):
    model.eval()
    total_loss = 0
    total_correct = 0
    total = 0

    with torch.no_grad():
        for X, y in loader:
            X, y = X.to(device), y.to(device)

            out = model(X)
            loss = criterion(out, y)

            total_loss += loss.item() * X.size(0)
            pred = out.argmax(dim=1)
            total_correct += (pred == y).sum().item()
            total += X.size(0)

    return total_loss / total, total_correct / total


if __name__ == "__main__":
    start_time = time.time()
    print(f"start train: {time.asctime()}")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    data_folder = "./gesture_model/datasets/"
    dataset = GestureDataset(data_folder + "X.npy", data_folder + "y.npy")

    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_ds, val_ds = random_split(dataset, [train_size, val_size])
    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=32, shuffle=False)
    print(f"Train size: {train_size}, Val size: {val_size}")

    model = GestureNet()
    model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)


    EPOCHS = 100
    best_val_loss = float("inf")
    patience = 10
    count = 0

    for epoch in range(EPOCHS):
        train_loss, train_acc = train_one_epoch(
            model, train_loader, optimizer, criterion, device
        )
        val_loss, val_acc = validate(model, val_loader, criterion, device)

        print(
            f"[Epoch {epoch+1}/{EPOCHS}] "
            f"Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f}"
        )

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            count = 0
        else:
            count += 1
            if count >= patience:
                print("Early stopping triggered.")
                break

    torch.save(model.state_dict(), "gesture_model.pth")


    print(f"Completed in {time.time() - start_time:.2f} seconds.")

# nohup python train.py &