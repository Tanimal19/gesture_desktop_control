import os
import csv
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmark
from share.logger import setup_logging


class DataCollectionRecorder:
    def __init__(self, output_dir, pid):
        output_dir = os.path.join(output_dir, "p" + str(pid))
        os.makedirs(output_dir, exist_ok=True)

        setup_logging(os.path.join(output_dir, "run.log"))

        self.raw_landmarks_csv = os.path.join(output_dir, "raw_landmarks.csv")
        self.record_video_path = os.path.join(output_dir, "record.mp4")
        self.task_result_csv = os.path.join(output_dir, "task_result.csv")

        self.recorded_landmarks = [
            HandLandmark.WRIST,
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

        with open(self.task_result_csv, "w") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["timestamp", "task", "trail"]
                + [lt.name for lt in self.recorded_landmarks]
            )

    def write_task_result(self, timestamp, task_type, trail_n, landmarks):
        with open(self.task_result_csv, "a", newline="") as f:
            writer = csv.writer(f)
            row = [timestamp, task_type.name, trail_n]
            for lt in self.recorded_landmarks:
                lm = landmarks[lt.value]
                row.append(f"{lm[0]}_{lm[1]}_{lm[2]}")
            writer.writerow(row)

    def mark_task_start(self, task_type, trail_n):
        with open(self.task_result_csv, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [-1, task_type.name, trail_n] + ["" for _ in self.recorded_landmarks]
            )
