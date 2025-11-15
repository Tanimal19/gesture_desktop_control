import torch
import torch.nn as nn
import torch.nn.functional as F


# landmark_num = 12, dimension = 3, gesture_num = 8
window_length = 30  # number of frames in input sequence
gcn_hidden_dim = 16  # GCN hidden dimension
tcn_hidden_dim = 64  # TCN hidden dimension


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
        out_dim = gcn_hidden_dim

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
        in_ch = 3 * gcn_hidden_dim
        out_ch = tcn_hidden_dim

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
        # x: (B, window_length, gcn_hidden_dim*3)
        x = x.transpose(1, 2)

        for conv, pad in zip(self.layers, self.padding):
            x = F.pad(x, (0, pad))  # pad at the end
            x = conv(x)

        # Global Average Pooling (over window_length)
        x = x.mean(dim=2)
        return x


class GestureNet(nn.Module):
    """
    Gesture Recognition Network
    Input: (B, window_length, 12, 3)
    Output: (B, 8)
    """

    def __init__(self):
        super().__init__()

        # GCN
        self.gcn = GCNLayer()
        self.pool = FingerPooling()

        # TCN
        self.tcn = TemporalConvNet()

        # Classifier
        self.fc = nn.Linear(tcn_hidden_dim, 8)

        # Predefine adjacency matrices
        self.A1 = nn.Parameter(torch.eye(12), requires_grad=False)
        self.A2 = nn.Parameter(torch.eye(12), requires_grad=False)

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
