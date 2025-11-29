import os
import csv
from datapath import EVA_PARTICIPANT_FOLDER_TEMPLATE


class EvaluationRecorder:
    def __init__(self, pid):
        output_dir = EVA_PARTICIPANT_FOLDER_TEMPLATE.format(pid=pid)
        os.makedirs(output_dir, exist_ok=True)

        self.task_result_csv = os.path.join(output_dir, "task_result.csv")
        with open(self.task_result_csv, "w") as f:
            writer = csv.writer(f)
            global_header = [
                "pid",
                "task_type",
                "trial_index",
                "complete_time",
                "correct",
                "precision",
            ]

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
