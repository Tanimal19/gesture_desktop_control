import torch
import numpy as np
from torch.utils.data import DataLoader, random_split
from sklearn.metrics import confusion_matrix, classification_report
from gesture_model.model import AbstractGestureModel, GestureDataset, GestureLabel
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmark


class GestureModelTrainer:
    def __init__(
        self, output_path: str, model: AbstractGestureModel, dataset: GestureDataset
    ):
        self.output_path = output_path
        self.model = model
        self.dataset = dataset
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        self.model.to(self.device)

    def train(self, criterion, optimizer, epochs=100):
        # split dataset
        train_size = int(0.8 * len(self.dataset))
        val_size = len(self.dataset) - train_size
        print(f"Train size: {train_size}, Val size: {val_size}")

        train_ds, val_ds = random_split(self.dataset, [train_size, val_size])
        train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
        val_loader = DataLoader(val_ds, batch_size=32, shuffle=False)

        best_val_loss = float("inf")
        patience = 15
        count = 0

        for epoch in range(epochs):
            train_loss, train_acc = self.train_one_epoch(
                self.model, train_loader, optimizer, criterion, self.device
            )
            val_loss, val_acc = self.validate(
                self.model, val_loader, criterion, self.device
            )
            print(
                f"[Epoch {epoch+1}/{epochs}]"
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

        torch.save(self.model.state_dict(), self.output_path)

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


class GestureModelRunner:
    def __init__(self, model: AbstractGestureModel, model_path: str, device: str):
        self.device = device
        self.model = model
        self.model.to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()

    def inference(self, landmark_window: np.ndarray) -> GestureLabel:
        """
        landmarks_window: np.array of shape (WINDOW_LENGTH, len(HandLandmark), 3)\n
        """
        assert (
            landmark_window.shape[1] == len(HandLandmark)
            and landmark_window.shape[2] == 3
        )

        with torch.no_grad():
            x_tensor = self.model.landmarks_window_to_X(landmark_window)
            x_tensor = x_tensor.unsqueeze(0)  # add batch dimension
            x_tensor = x_tensor.to(next(self.model.parameters()).device)
            out = self.model.forward(x_tensor)
            pred_idx = out.argmax(dim=1).item()
            mappped_label = self.model.y_to_label(pred_idx)

        return mappped_label
