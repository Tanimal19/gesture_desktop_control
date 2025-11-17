from enum import Enum
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split
from sklearn.metrics import confusion_matrix, classification_report


class GestureLabel(Enum):
    NONE = 0
    LEFT_PRESS = 1
    LEFT_RELEASE = 2
    RIGHT_PRESS = 3
    RIGHT_RELEASE = 4
    SCROLL_UP = 5
    SCROLL_DOWN = 6


def generate_samples(df, window_length, feature_columns, padding=True) -> list[dict]:
    # pad the beginning with the first row to ensure enough frames
    if padding:
        pad = window_length - 1
        first_row = df.iloc[[0]].copy()
        padding = pd.concat([first_row] * pad, ignore_index=True)
        df = pd.concat([padding, df.reset_index(drop=True)], ignore_index=True)

    samples = []
    num_frames = len(df)
    for start_idx in range(0, num_frames - window_length + 1):
        end_idx = start_idx + window_length
        window = df.iloc[start_idx:end_idx]
        feature_array = window[feature_columns].copy()

        samples.append(
            {
                "features": feature_array,
                "label": GestureLabel[window["label"].values[-1].upper()].value,
            }
        )
    return samples


class GestureModel(ABC, nn.Module):
    WINDOW_LENGTH: int

    @abstractmethod
    def inference(self, landmarks_window: np.ndarray) -> GestureLabel:
        """
        landmarks_window: np.array of shape (WINDOW_LENGTH, len(HandLandmark), 3)\n
        subclass should transform input data to their required feature and return predicted GestureLabel
        """
        pass


class GestureDataset(Dataset):
    def __init__(self, X_path, y_path):
        X = np.load(X_path)
        y = np.load(y_path)
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class ModelTrainer:
    def __init__(
        self, output_folder: str, model: GestureModel, dataset: GestureDataset
    ):
        self.output_folder = output_folder
        self.model = model
        self.dataset = dataset
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        self.model.to(self.device)

    def split_data(self, train_ratio: float = 0.8):
        train_size = int(train_ratio * len(self.dataset))
        val_size = len(self.dataset) - train_size
        train_ds, val_ds = random_split(self.dataset, [train_size, val_size])
        self.train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
        self.val_loader = DataLoader(val_ds, batch_size=32, shuffle=False)
        print(f"Train size: {train_size}, Val size: {val_size}")

    def training_epochs(self, criterion, optimizer, epochs: int = 100):
        best_val_loss = float("inf")
        patience = 10
        count = 0

        for epoch in range(epochs):
            train_loss, train_acc = self.train_one_epoch(
                self.model, self.train_loader, optimizer, criterion, self.device
            )
            val_loss, val_acc = self.validate(
                self.model, self.val_loader, criterion, self.device
            )

            print(
                f"[Epoch {epoch+1}/{epochs}] "
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

        torch.save(self.model.state_dict(), self.output_folder + "model.pth")

    @staticmethod
    def train_one_epoch(model, loader, optimizer, criterion, device):
        model.train()
        total_loss = 0
        total_correct = 0
        total = 0

        for X, y in loader:
            X, y = X.to(device), y.to(device)

            optimizer.zero_grad()
            out = model(X)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * X.size(0)
            pred = out.argmax(dim=1)
            total_correct += (pred == y).sum().item()
            total += X.size(0)

        return total_loss / total, total_correct / total

    @staticmethod
    def validate(model, loader, criterion, device):
        model.eval()
        total_loss = 0
        total_correct = 0
        total = 0

        with torch.no_grad():
            true_y = []
            pred_y = []
            for X, y in loader:
                X, y = X.to(device), y.to(device)

                out = model(X)
                loss = criterion(out, y)

                total_loss += loss.item() * X.size(0)
                pred = out.argmax(dim=1)
                total_correct += (pred == y).sum().item()
                total += X.size(0)

                true_y.extend(y.cpu().numpy())
                pred_y.extend(pred.cpu().numpy())

            print("Confusion Matrix:")
            print(confusion_matrix(true_y, pred_y))
            print("Classification Report:")
            print(classification_report(true_y, pred_y))

        return total_loss / total, total_correct / total
