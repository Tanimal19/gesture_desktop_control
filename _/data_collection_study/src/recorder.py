import os
import csv
from share.utils import HandLandmark
from share.datapath import DC_PARTICIPANT_FOLDER_TEMPLATE
import logging


def setup_logging(filepath):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(filepath, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(module)s.%(funcName)s(): %(message)s"
    )
    file_handler.setFormatter(file_fmt)
    logger.addHandler(file_handler)


class DataCollectionRecorder:
    RECORDED_LANDMARKS = [
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

    def __init__(self, pid):
        output_dir = DC_PARTICIPANT_FOLDER_TEMPLATE.format(pid=pid)
        os.makedirs(output_dir, exist_ok=True)

        setup_logging(os.path.join(output_dir, "run.log"))

        self.raw_landmarks_csv = os.path.join(output_dir, "raw_landmarks.csv")
        self.camera_video_path = os.path.join(output_dir, "camera.mp4")
        self.task_result_csv = os.path.join(output_dir, "task_result.csv")

        with open(self.task_result_csv, "w") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["timestamp", "task", "trail"]
                + [lt.name for lt in self.RECORDED_LANDMARKS]
            )

    def write_task_result(self, timestamp, task_type, trail_n, landmarks):
        with open(self.task_result_csv, "a", newline="") as f:
            writer = csv.writer(f)
            row = [timestamp, task_type.name, trail_n]
            for lt in self.RECORDED_LANDMARKS:
                lm = landmarks[lt.value]
                row.append(f"{lm[0]}_{lm[1]}_{lm[2]}")
            writer.writerow(row)

    def mark_task_start(self, task_type, trail_n):
        with open(self.task_result_csv, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [-1, task_type.name, trail_n] + ["" for _ in self.RECORDED_LANDMARKS]
            )
