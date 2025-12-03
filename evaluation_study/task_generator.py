# generating and reading task configuration file

import csv
import os

from evaluation_study.src.task import TrueTaskType, TASK_WIDGET_MAP
from evaluation_study.src.recorder import EVA_DATASET_FOLDER

NUM_PARTICIPANT = 5
config_path = EVA_DATASET_FOLDER + "/task_configs.csv"


def generate_configs():
    tasks = [
        (TrueTaskType.MenuSelect, 10),
        (TrueTaskType.DragDrop, 10),
        (TrueTaskType.KeyboardInput, 10),
    ]

    with open(config_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["pid", "task_type", "trial_num", "configs"])

        for p in range(NUM_PARTICIPANT):
            # latin square counterbalance for the order of other tasks
            i = p % len(tasks)
            latin_tasks = tasks[i:] + tasks[:i]

            for t in latin_tasks:
                tclass = TASK_WIDGET_MAP[t[0]]
                configs_str = tclass.generate_configs_str(t[1])
                writer.writerow([p, t[0].name, t[1], configs_str])


def read_configs(pid=0) -> list[tuple[TrueTaskType, int, list[dict]]]:
    """
    output: (TrueTaskType, trial_num, [list of config dict])
    """

    task_configs = []

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, mode="r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if int(row["pid"]) == pid:
                task_type = TrueTaskType[row["task_type"]]
                tclass = TASK_WIDGET_MAP[task_type]
                configs = tclass.parse_configs(row["configs"])
                task_configs.append(
                    (
                        task_type,
                        int(row["trial_num"]),
                        configs,
                    )
                )

    return task_configs


if __name__ == "__main__":
    generate_configs()
    # print(read_configs(0))
