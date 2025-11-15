import torch
from model import GestureNet
import pandas as pd
from gesture_model.utils import index_to_label, LANDMARKS as GM_LANDMARKS
from data_collection.annotation.utils import split_landmarks, offset_landmarks

csv_file = "./data_collection/datasets/p0/task_result.csv"
df = pd.read_csv(csv_file)

df = split_landmarks(df)
df = offset_landmarks(df)


device = "cpu"

model = GestureNet()
model.to(device)

model.load_state_dict(torch.load("./gesture_model.pth", map_location=device))

# 切換成 eval 模式
model.eval()
