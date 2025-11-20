import pandas as pd
import numpy as np
from gesture_model.task_annotator.model import TaskAnnotator
from gesture_model.task_annotator.data import read_y_mapping
from data_collection.data_process.utils import RESULT_CSV, update_label_csv
from data_collection.src.task import TrueTaskType
from share.worker.gesture import GestureModelRunner
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmark


df = pd.read_csv(RESULT_CSV)
df["label"] = ""

y_mapping = read_y_mapping()

for t in TrueTaskType:
    if t.name not in y_mapping.keys():
        print(f"- Skipping task: {t.name} (no trained model found)")
        continue
    print(f"+ Processing task: {t.name}")

    task_group = df[df["task"] == t.name]

    model = TaskAnnotator(y_mapping[t.name])
    model_path = f"./gesture_model/task_annotator/models/{t.name}.pth"
    runner = GestureModelRunner(model, model_path, device="cpu")

    trail_groups = task_group.groupby("trail")
    for trail, trail_group in trail_groups:
        # for each window, predict label
        for start_idx in range(0, len(trail_group) - TaskAnnotator.WINDOW_LENGTH + 1):
            end_idx = start_idx + TaskAnnotator.WINDOW_LENGTH
            window = df.iloc[start_idx:end_idx]

            input = []
            for lm in HandLandmark:
                if lm.name in window.columns:
                    x, y, z = (
                        window[lm.name]
                        .str.split("_", expand=True)
                        .astype(float)
                        .values.T
                    )
                else:
                    x = y = z = np.zeros((TaskAnnotator.WINDOW_LENGTH,))

                landmark_feautures = np.stack(
                    [x, y, z], axis=1
                )  # shape: (frame_window, 3)
                input.append(landmark_feautures)

            input = np.stack(input, axis=1).astype(
                "float32"
            )  # shape: (frame_window, landmarks, 3)

            predict_label = runner.run_inference(input)
            print(
                f"Trail {trail}, Timestamp {window['timestamp'].values[-1]}: Predicted label: {predict_label.name}"
            )
            df.loc[
                (df["task"] == t.name)
                & (df["trail"] == trail)
                & (df["timestamp"] == window["timestamp"].values[-1]),
                "label",
            ] = predict_label.name

    label_df = df[df["task"] == t.name][
        ["participant_id", "timestamp", "task", "trail", "label"]
    ]
    update_label_csv(label_df)
