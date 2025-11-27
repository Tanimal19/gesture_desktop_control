import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from share.utils import HandLandmark
from gesture_model.model import GestureLabel, AbstractGestureModel

BASE_FOLDER = "./gesture_model/graph_tcn/"


class GCNLayer(nn.Module):
    """
    Graph Convolution Layer
    Input: (12, 3)
    A: (12, 12)
    Output: (12, gcn_hidden_dim)
    """

    def __init__(self, hidden_dim):
        super().__init__()
        in_dim = 3
        out_dim = hidden_dim

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

    def __init__(self, in_ch, out_ch):
        super().__init__()
        layers = []

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


class GTCNModel(AbstractGestureModel):
    """
    Gesture Recognition Network
    Input: (B, window_length, 12, 3)
    Output: (B, 7)
    """

    WINDOW_LENGTH = 6
    GCN_HIDDEN_DIM = 16  # GCN hidden dimension
    TCN_HIDDEN_DIM = 64  # TCN hidden dimension
    LANDMARKS = [
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
        (HandLandmark.THUMB_CMC, HandLandmark.THUMB_MCP),
        (HandLandmark.THUMB_MCP, HandLandmark.THUMB_IP),
        (HandLandmark.THUMB_IP, HandLandmark.THUMB_TIP),
        (HandLandmark.INDEX_FINGER_MCP, HandLandmark.INDEX_FINGER_PIP),
        (HandLandmark.INDEX_FINGER_PIP, HandLandmark.INDEX_FINGER_DIP),
        (HandLandmark.INDEX_FINGER_DIP, HandLandmark.INDEX_FINGER_TIP),
        (HandLandmark.MIDDLE_FINGER_MCP, HandLandmark.MIDDLE_FINGER_PIP),
        (HandLandmark.MIDDLE_FINGER_PIP, HandLandmark.MIDDLE_FINGER_DIP),
        (HandLandmark.MIDDLE_FINGER_DIP, HandLandmark.MIDDLE_FINGER_TIP),
    ]

    BETWEEN_FINGER_CONNECTIONS = [
        (HandLandmark.THUMB_CMC, HandLandmark.INDEX_FINGER_MCP),
        (HandLandmark.THUMB_MCP, HandLandmark.INDEX_FINGER_PIP),
        (HandLandmark.THUMB_IP, HandLandmark.INDEX_FINGER_DIP),
        (HandLandmark.THUMB_TIP, HandLandmark.INDEX_FINGER_TIP),
        (HandLandmark.THUMB_CMC, HandLandmark.MIDDLE_FINGER_MCP),
        (HandLandmark.THUMB_MCP, HandLandmark.MIDDLE_FINGER_PIP),
        (HandLandmark.THUMB_IP, HandLandmark.MIDDLE_FINGER_DIP),
        (HandLandmark.THUMB_TIP, HandLandmark.MIDDLE_FINGER_TIP),
        (HandLandmark.INDEX_FINGER_MCP, HandLandmark.MIDDLE_FINGER_MCP),
        (HandLandmark.INDEX_FINGER_PIP, HandLandmark.MIDDLE_FINGER_PIP),
        (HandLandmark.INDEX_FINGER_DIP, HandLandmark.MIDDLE_FINGER_DIP),
        (HandLandmark.INDEX_FINGER_TIP, HandLandmark.MIDDLE_FINGER_TIP),
    ]

    def __init__(self):
        super().__init__()

        # GCN
        self.gcn = GCNLayer(self.GCN_HIDDEN_DIM)
        self.pool = FingerPooling()

        # TCN
        self.tcn = TemporalConvNet(self.GCN_HIDDEN_DIM * 3, self.TCN_HIDDEN_DIM)

        # Classifier
        self.fc = nn.Linear(self.TCN_HIDDEN_DIM, len(GestureLabel))

        # Adjacency matrices (fixed)
        self.register_buffer(
            "A1",
            self.generate_adjacent_matrix(
                self.LANDMARKS, self.INSIDE_FINGER_CONNECTIONS
            )
        )
        self.register_buffer(
            "A2",
            self.generate_adjacent_matrix(
                self.LANDMARKS, self.BETWEEN_FINGER_CONNECTIONS
            )
        )

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

    @staticmethod
    def landmarks_window_to_X(landmarks_window: np.ndarray) -> torch.Tensor:
        # convert landmarks position to offset position w.r.t. wrist
        wrist_landmark = landmarks_window[:, HandLandmark.WRIST.value, :]
        features = np.zeros((GTCNModel.WINDOW_LENGTH, len(GTCNModel.LANDMARKS), 3))
        for i, lm in enumerate(GTCNModel.LANDMARKS):
            lm_pos = landmarks_window[:, lm.value, :]
            offset_lm_pos = lm_pos - wrist_landmark
            features[:, i, :] = offset_lm_pos
        # (window_length, 12, 3)

        x_tensor = torch.tensor(features, dtype=torch.float32)
        return x_tensor

    def y_to_label(self, y: int) -> GestureLabel:
        return GestureLabel(y)

    @staticmethod
    def generate_adjacent_matrix(
        landmarks: list[HandLandmark],
        connections: list[tuple[HandLandmark, HandLandmark]],
    ):
        N = len(landmarks)
        adj = np.zeros((N, N), dtype=int)

        node2idx = {lm.name: idx for idx, lm in enumerate(landmarks)}
        for a, b in connections:
            i, j = node2idx[a.name], node2idx[b.name]
            adj[i, j] = 1
            adj[j, i] = 1

        adj = torch.tensor(adj, dtype=torch.float32)
        return adj
