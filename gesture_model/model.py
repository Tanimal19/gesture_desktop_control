import torch
import torch.nn as nn
import torch.nn.functional as F
from gesture_model.utils import generate_adjacent_matrix
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmark


# landmark_num = 12, dimension = 3, gesture_num = 7
WINDOW_LENGTH = 20  # number of frames in input sequence
GCN_HIDDEN_DIM = 16  # GCN hidden dimension
TCN_HIDDEN_DIM = 64  # TCN hidden dimension

LABELS = [
    "none",
    "left_press",
    "left_release",
    "right_press",
    "right_release",
    "scroll_up",
    "scroll_down",
]

INPUT_LANDMARKS = [
    HandLandmark.THUMB_CMC,
    HandLandmark.THUMB_MCP,
    HandLandmark.THUMB_IP,
    HandLandmark.THUMB_TIP,
    HandLandmark.INDEX_FINGER_MCP,
    HandLandmark.INDEX_FINGER_PIP,
    HandLandmark.INDEX_FINGER_DIP,
    HandLandmark.INDEX_FINGER_TIP,
    HandLandmark.MIDDLE_FINGER_MCP,
    HandLandmark.MIDDLE_FINGER_PIP,
    HandLandmark.MIDDLE_FINGER_DIP,
    HandLandmark.MIDDLE_FINGER_TIP,
]


INSIDE_FINGER_CONNECTIONS = [
    ("THUMB_CMC", "THUMB_MCP"),
    ("THUMB_MCP", "THUMB_IP"),
    ("THUMB_IP", "THUMB_TIP"),
    ("INDEX_FINGER_MCP", "INDEX_FINGER_PIP"),
    ("INDEX_FINGER_PIP", "INDEX_FINGER_DIP"),
    ("INDEX_FINGER_DIP", "INDEX_FINGER_TIP"),
    ("MIDDLE_FINGER_MCP", "MIDDLE_FINGER_PIP"),
    ("MIDDLE_FINGER_PIP", "MIDDLE_FINGER_DIP"),
    ("MIDDLE_FINGER_DIP", "MIDDLE_FINGER_TIP"),
]

BETWEEN_FINGER_CONNECTIONS = [
    ("THUMB_CMC", "INDEX_FINGER_MCP"),
    ("THUMB_MCP", "INDEX_FINGER_PIP"),
    ("THUMB_IP", "INDEX_FINGER_DIP"),
    ("THUMB_TIP", "INDEX_FINGER_TIP"),
    ("INDEX_FINGER_MCP", "MIDDLE_FINGER_MCP"),
    ("INDEX_FINGER_PIP", "MIDDLE_FINGER_PIP"),
    ("INDEX_FINGER_DIP", "MIDDLE_FINGER_DIP"),
    ("INDEX_FINGER_TIP", "MIDDLE_FINGER_TIP"),
    ("THUMB_CMC", "MIDDLE_FINGER_MCP"),
    ("THUMB_MCP", "MIDDLE_FINGER_PIP"),
    ("THUMB_IP", "MIDDLE_FINGER_DIP"),
    ("THUMB_TIP", "MIDDLE_FINGER_TIP"),
]


class GCNLayer(nn.Module):
    """
    Graph Convolution Layer
    Input: (12, 3)
    A: (12, 12)
    Output: (12, gcn_hidden_dim)
    """

    def __init__(self):
        super().__init__()
        in_dim = 3
        out_dim = GCN_HIDDEN_DIM

        self.W1 = nn.Linear(in_dim, out_dim, bias=False)
        self.W2 = nn.Linear(in_dim, out_dim, bias=False)

    def forward(self, X, A1, A2):
        AX1 = torch.matmul(A1, X)
        AX2 = torch.matmul(A2, X)

        out = self.W1(AX1) + self.W2(AX2)
        return F.relu(out)


class FingerPooling(nn.Module):
    """
    Finger-group Average Pooling.
    Input: (12, gcn_hidden_dim)
    Output: (3, gcn_hidden_dim)
    """

    def __init__(self):
        super().__init__()
        self.groups = [
            [0, 1, 2, 3],  # thumb
            [4, 5, 6, 7],  # index finger
            [8, 9, 10, 11],  # middle finger
        ]

    def forward(self, X):
        pooled = []
        for idxs in self.groups:
            pooled.append(X[:, idxs].mean(dim=1))
        return torch.stack(pooled, dim=1)


class TemporalConvNet(nn.Module):
    """
    Temporal Convolution Network
    Input: (B, gcn_hidden_dim*3, window_length)
    Output: (B, tcn_hidden_dim) after GAP
    """

    def __init__(self):
        super().__init__()
        layers = []
        in_ch = 3 * GCN_HIDDEN_DIM
        out_ch = TCN_HIDDEN_DIM

        kernel_size = 3
        dilations = [1, 3, 9]
        self.padding = [d * (kernel_size - 1) for d in dilations]

        for d in dilations:
            layers.append(
                nn.Sequential(
                    nn.Conv1d(
                        in_ch, out_ch, kernel_size=kernel_size, padding=0, dilation=d
                    ),
                    nn.ReLU(),
                )
            )
            in_ch = out_ch

        self.layers = nn.ModuleList(layers)

    def forward(self, x):
        for conv, p in zip(self.layers, self.padding):
            x = F.pad(x, (0, p))  # pad at the end
            x = conv(x)

        # Global Average Pooling (over window_length)
        x = x.mean(dim=2)
        return x


class GestureModel(nn.Module):
    """
    Gesture Recognition Network
    Input: (B, window_length, 12, 3)
    Output: (B, 7)
    """

    def __init__(self):
        super().__init__()

        # GCN
        self.gcn = GCNLayer()
        self.pool = FingerPooling()

        # TCN
        self.tcn = TemporalConvNet()

        # Classifier
        self.fc = nn.Linear(TCN_HIDDEN_DIM, len(LABELS))

        # Adjacency matrices (fixed)
        self.A1 = generate_adjacent_matrix(INPUT_LANDMARKS, INSIDE_FINGER_CONNECTIONS)
        self.A2 = generate_adjacent_matrix(INPUT_LANDMARKS, BETWEEN_FINGER_CONNECTIONS)

    def forward(self, x):
        B, T, N, C = x.shape

        x_seq = x.reshape(B * T, N, C)  # vectorize over time
        g = self.gcn(x_seq, self.A1, self.A2)  # (B*T, 12, gcn_hidden_dim)
        g = self.pool(g)  # (B*T, 3, gcn_hidden_dim)
        g = g.reshape(B, T, -1)  # (B, T, gcn_hidden_dim*3)
        g = g.transpose(1, 2)  # (B, gcn_hidden_dim*3, T)
        feat = self.tcn(g)  # (B, tcn_hidden_dim)
        out = self.fc(feat)  # classify

        return out
