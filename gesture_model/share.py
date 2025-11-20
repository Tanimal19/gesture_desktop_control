from enum import Enum
from abc import ABC, abstractmethod
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset


class GestureLabel(Enum):
    NONE = 0
    LEFT_PRESS = 1
    LEFT_RELEASE = 2
    RIGHT_PRESS = 3
    RIGHT_RELEASE = 4
    SCROLL_UP = 5
    SCROLL_DOWN = 6


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
