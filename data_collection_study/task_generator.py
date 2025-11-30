# generating and reading task configuration file

from datapath import DC_DATASET_FOLDER
from data_collection_study.src.task import TrueTaskType, TASK_BUILDER_MAP
import pandas as pd
import csv
import ast

NUM_PARTICIPANT = 6 + 1
config_path = DC_DATASET_FOLDER + "/task_configs.csv"

display_width = 1512
display_height = 982

margin = 100
canva_bound = (
    margin + 300,  # to avoid sidebar
    display_width - margin,  # to avoid sidebar
    margin + 50,  # to avoid taskbar
    display_height - margin,
)


def generate_configs():
    basic_tasks = [
        (TrueTaskType.LEFT_CLICK, 10),
        (TrueTaskType.RIGHT_CLICK, 10),
    ]
    other_tasks = [
        (TrueTaskType.MENU_NAVIGATION, 5),
        (TrueTaskType.DRAGGING, 5),
        (TrueTaskType.POINT_N_CLICK, 5),
    ]

    with open(config_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["pid", "task", "count", "configs"])

        for p in range(NUM_PARTICIPANT):
            # latin square counterbalance for the order of other tasks
            i = p % len(other_tasks)
            latin_tasks = other_tasks[i:] + other_tasks[:i]

            for t in basic_tasks + latin_tasks:
                tclass = TASK_BUILDER_MAP[t[0]]
                configs = tclass.generate_configs(t[1], canva_bound)
                writer.writerow([p, t[0].name, t[1], configs])


def read_configs(pid=0):
    """
    [{
        "task": task type,
        "configs": [t1, t2, ...], where the length is the number of trials
    }, ...]
    """

    df = pd.read_csv(config_path)
    df["configs"] = df["configs"].apply(ast.literal_eval)

    # filter by participant id
    pdf = df[df["pid"] == pid]
    pdf.drop(columns=["pid"], inplace=True)

    # convert to dict
    tasks = [
        {"task": TrueTaskType[row["task"]], "configs": row["configs"]}
        for _, row in pdf.iterrows()
    ]

    return tasks


if __name__ == "__main__":
    generate_configs()
