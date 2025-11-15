# generating and reading task configuration file

from src.task import *
from src.config import BASE_DIR
import pandas as pd
import csv
import ast

num_participant = 12 + 1
config_path = BASE_DIR + "/task_configs.csv"

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
        (TrueTaskType.BA_POINT, 5),  # number of trials
        (TrueTaskType.BA_LEFT_CLICK, 5),
        (TrueTaskType.BA_RIGHT_CLICK, 5),
        (TrueTaskType.BA_SCROLL_UP, 5),
        (TrueTaskType.BA_SCROLL_DOWN, 5),
    ]
    other_tasks = [
        (TrueTaskType.MENU_NAVIGATION, 5),
        (TrueTaskType.DRAGGING, 5),
        (TrueTaskType.POINT_N_CLICK, 5),
    ]

    with open(config_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["pid", "task", "count", "configs"])

        for p in range(num_participant):
            # latin square counterbalance for the order of other tasks
            i = p % len(other_tasks)
            latin_tasks = other_tasks[i:] + other_tasks[:i]

            for t in basic_tasks + latin_tasks:
                tclass = return_tclass(t[0].value)
                configs = tclass.generate_configs(t[1], canva_bound)
                writer.writerow([p, t[0].value, t[1], configs])


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
        {"task": row["task"], "configs": row["configs"]} for _, row in pdf.iterrows()
    ]

    return tasks


if __name__ == "__main__":
    generate_configs()
