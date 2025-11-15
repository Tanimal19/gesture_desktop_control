import numpy as np
from gesture_model.model import LABELS
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmark


def label_to_index(label):
    return LABELS.index(label)


def index_to_label(index):
    return LABELS[index]


def generate_adjacent_matrix(landmarks: list[HandLandmark], connections):

    N = len(landmarks)
    adj = np.zeros((N, N), dtype=int)

    node2idx = {lm.name: idx for idx, lm in enumerate(landmarks)}
    print(node2idx)

    for a, b in connections:
        i, j = node2idx[a], node2idx[b]
        adj[i, j] = 1
        adj[j, i] = 1

    return adj
