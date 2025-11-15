import numpy as np

LABELS = [
    "none",
    "point",
    "left_press",
    "left_release",
    "right_press",
    "right_release",
    "scroll_up",
    "scroll_down",
]

LANDMARKS = [
    "THUMB_CMC",
    "THUMB_MCP",
    "THUMB_IP",
    "THUMB_TIP",
    "INDEX_FINGER_MCP",
    "INDEX_FINGER_PIP",
    "INDEX_FINGER_DIP",
    "INDEX_FINGER_TIP",
    "MIDDLE_FINGER_MCP",
    "MIDDLE_FINGER_PIP",
    "MIDDLE_FINGER_DIP",
    "MIDDLE_FINGER_TIP",
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


def label_to_index(label):
    return LABELS.index(label)


def index_to_label(index):
    return LABELS[index]


def generate_adjacent_matrix(landmarks, connections):

    N = len(landmarks)
    adj = np.zeros((N, N), dtype=int)

    node2idx = {lm: idx for idx, lm in enumerate(landmarks)}
    print(node2idx)

    for a, b in connections:
        i, j = node2idx[a], node2idx[b]
        adj[i, j] = 1
        adj[j, i] = 1

    return adj
