import os
import csv
from share.datapath import EVA_PARTICIPANT_FOLDER_TEMPLATE
from evaluation_study.src.task import TrueTaskType, TASK_WIDGET_MAP


class EvaluationResultRecorder:
    def __init__(self, pid, condition):
        self.pid = pid
        self.condition = condition

        output_dir = EVA_PARTICIPANT_FOLDER_TEMPLATE.format(pid=pid)
        os.makedirs(output_dir, exist_ok=True)

        self.task_result_csv = os.path.join(
            output_dir, f"task_result_{self.condition}.csv"
        )
        with open(self.task_result_csv, "w") as f:
            writer = csv.writer(f)
            global_header = [
                "pid",
                "task_type",
                "trial_index",
                "complete_time",
                "is_correct",
            ]
            task_headers = []
            for ttype in TrueTaskType:
                for item in TASK_WIDGET_MAP[ttype].payload_header:
                    if item not in global_header:
                        task_headers.append(f"{ttype.name}-{item}")

            header = global_header + task_headers
            writer.writerow(header)
            self.header_index = {name: i for i, name in enumerate(header)}

    def write_trial_result(
        self,
        task_type: TrueTaskType,
        trail_index: int,
        complete_time: float,
        is_correct: bool,
        payload: dict,
    ):
        with open(self.task_result_csv, "a", newline="") as f:
            writer = csv.writer(f)
            row = [
                self.pid,
                task_type.name,
                trail_index + 1,
                complete_time,
                is_correct,
            ]
            row += [""] * (len(self.header_index) - len(row))

            for key, value in payload.items():
                col_index = self.header_index.get(f"{task_type.name}-{key}")
                if col_index is not None:
                    row[col_index] = value

            writer.writerow(row)
