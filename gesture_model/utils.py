from enum import Enum
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
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
