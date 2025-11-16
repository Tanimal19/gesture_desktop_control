import torch.nn as nn
from gesture_model.share import GestureLabel

WINDOW_LENGTH = 10


class DistNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(3, 32, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.Conv1d(32, 64, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
        )
        self.fc = nn.Linear(64, len(GestureLabel))

    def forward(self, x):
        # x: (B, 10, 3)
        x = x.permute(0, 2, 1)  # (B, 3, 10)
        x = self.net(x)
        x = x.squeeze(-1)
        x = self.fc(x)
        return x
