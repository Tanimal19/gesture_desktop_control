import os
import csv
from datapath import EVA_PARTICIPANT_FOLDER_TEMPLATE
from evaluation_study.src.task_widget import TrueTaskType, TASK_WIDGET_MAP
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


class EvaluationRecorder:
    def __init__(self, pid):
        self.pid = pid
        output_dir = EVA_PARTICIPANT_FOLDER_TEMPLATE.format(pid=pid)
        os.makedirs(output_dir, exist_ok=True)

        setup_logging(output_dir + "run.log")

        self.task_result_csv = os.path.join(output_dir, "task_result.csv")
        with open(self.task_result_csv, "w") as f:
            writer = csv.writer(f)
            global_header = [
                "pid",
                "task_type",
                "trial_index",
                "complete_time",
                "correctness",
            ]
            task_headers = [
                ttype.name + "-" + item
                for ttype in TrueTaskType
                for item in TASK_WIDGET_MAP[ttype].payload_header
            ]
            header = global_header + task_headers
            writer.writerow(header)
            self.header_index = {name: i for i, name in enumerate(header)}

    def write_trial_result(
        self,
        task_type: TrueTaskType,
        trail_index: int,
        complete_time: float,
        correctness: bool,
        payload: dict,
    ):
        with open(self.task_result_csv, "a", newline="") as f:
            writer = csv.writer(f)
            row = [
                self.pid,
                task_type.name,
                trail_index,
                complete_time,
                correctness,
            ]
            row += [""] * (len(self.header_index) - len(row))

            for key, value in payload.items():
                col_index = self.header_index.get(f"{task_type.name}-{key}")
                if col_index is not None:
                    row[col_index] = value

            writer.writerow(row)
