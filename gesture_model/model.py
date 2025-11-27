from enum import Enum
from abc import ABC, abstractmethod
import numpy as np
import torch
import torch.nn as nn


class GestureLabel(Enum):
    NONE = 0
    LEFT_PRESS = 1
    LEFT_RELEASE = 2
    RIGHT_PRESS = 3
    RIGHT_RELEASE = 4
    SCROLL_UP = 5
    SCROLL_DOWN = 6


class AbstractGestureModel(ABC, nn.Module):
    WINDOW_LENGTH: int

    @staticmethod
    @abstractmethod
    def landmarks_window_to_X(landmarks_window: np.ndarray) -> torch.Tensor:
        """
        landmarks_window: np.array of shape (WINDOW_LENGTH, len(HandLandmark), 3)\n
        transform raw landmarks window to model required feature representation.
        """
        pass

    @abstractmethod
    def y_to_label(self, y: int) -> GestureLabel:
        """
        map model output y to GestureLabel
        """
        pass
