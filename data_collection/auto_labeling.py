import pandas as pd
import numpy as np
from config import ANNOTATOR_BASE_FOLDER, DC_DATASET_FOLDER
from data_collection.src.task import TrueTaskType
from data_collection.postprocess import RESULT_CSV, update_label_csv
from gesture_model.utils import extend_landmark_columns
from gesture_model.task_annotator.model import TaskAnnotator
from gesture_model.task_annotator.train import read_y_mapping
from gesture_model.model_runner import GestureModelRunner


df = pd.read_csv(RESULT_CSV)
df["label"] = ""
df["row_id"] = range(len(df))
print(df)

y_mapping = read_y_mapping()

for t in TrueTaskType:
    if t.name not in y_mapping.keys():
        print(f"- Skipping task: {t.name} (no trained model found)")
        continue
    print(f"+ Processing task: {t.name}")

    task_group = df[df["task"] == t.name]

    model = TaskAnnotator(y_mapping[t.name])
    model_path = ANNOTATOR_BASE_FOLDER + "models/" + f"{t.name}_wieghted_annotator.pth"
    runner = GestureModelRunner(model, model_path, device="cpu")

    for _, trail in task_group.groupby("trail"):
        for start_idx in range(0, len(trail) - TaskAnnotator.WINDOW_LENGTH + 1):
            # for each window, predict label
            end_idx = start_idx + TaskAnnotator.WINDOW_LENGTH
            window = trail.iloc[start_idx:end_idx]

            landmark_window = extend_landmark_columns(
                window, TaskAnnotator.WINDOW_LENGTH
            )

            predict_label = runner.inference(landmark_window)

            row_id = window.iloc[-1]["row_id"]
            df.at[row_id, "label"] = predict_label.name
            print("> Predicted label:", row_id, predict_label.name)

label_df = df[["participant_id", "timestamp", "task", "trail", "label"]]
update_label_csv(label_df, DC_DATASET_FOLDER + "auto_labels.csv")
