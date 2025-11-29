# generating and reading task configuration file

import csv
import os

from datapath import EVA_DATASET_FOLDER
from evaluation_study.src.config import TrueTaskType
from evaluation_study.src.task_widget.menu_select import MenuSelectTaskWidget
from evaluation_study.src.task_widget.dragdrop import DragDropTaskWidget

NUM_PARTICIPANT = 8
config_path = EVA_DATASET_FOLDER + "/task_configs.csv"

TASK_TYPE_TO_CLASS = {
    TrueTaskType.MenuSelect: MenuSelectTaskWidget,
    TrueTaskType.DragDrop: DragDropTaskWidget,
}


def generate_configs():
    tasks = [
        (TrueTaskType.MenuSelect, 5),
        (TrueTaskType.DragDrop, 5),
    ]

    with open(config_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["pid", "task_type", "trial_index", "configs"])

        for p in range(NUM_PARTICIPANT):
            # latin square counterbalance for the order of other tasks
            i = p % len(tasks)
            latin_tasks = tasks[i:] + tasks[:i]

            for t in latin_tasks:
                tclass = TASK_TYPE_TO_CLASS[t[0]]
                configs_str = tclass.generate_configs(t[1])
                writer.writerow([p, t[0].name, t[1], configs_str])


def read_configs(pid=0):
    task_configs = []

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, mode="r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if int(row["pid"]) == pid:
                task_type = TrueTaskType[row["task_type"]]
                tclass = TASK_TYPE_TO_CLASS[task_type]
                configs = tclass.parse_configs(row["configs"])
                task_configs.append(
                    (
                        task_type,
                        int(row["trial_index"]),
                        configs,
                    )
                )

    return task_configs


if __name__ == "__main__":
    generate_configs()
