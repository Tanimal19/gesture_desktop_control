import pandas as pd
from datapath import ANNOTATOR_BASE_FOLDER, DC_FULL_LABEL_CSV
from data_collection_study.src.task import TrueTaskType
from data_collection_study.post_process import update_labeled_csv
from share.utils import extend_landmark_columns
from gesture_model.task_annotator import TaskAnnotator
from gesture_model.task_annotator.train import read_y_mapping
from gesture_model.model_runner import GestureModelRunner


df = pd.read_csv(DC_FULL_LABEL_CSV)
df["label"] = "NONE"
df["row_id"] = range(len(df))

y_mapping = read_y_mapping()

for t in TrueTaskType:
    if t.name not in y_mapping.keys():
        print(f"- Skipping task: {t.name} (no trained model found)")
        continue
    print(f"+ Processing task: {t.name}")

    task_group = df[df["task"] == t.name]

    model = TaskAnnotator(y_mapping[t.name])
    model_path = ANNOTATOR_BASE_FOLDER + "models/" + t.name + "/best_model_default.pth"
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


update_labeled_csv(DC_FULL_LABEL_CSV, df)
