import pandas as pd
import os
from config import DC_DATASET_FOLDER, DC_PARTICIPANT_FOLDER_TEMPLATE


RESULT_CSV = DC_DATASET_FOLDER + "task_result_merged.csv"
MANUAL_LABEL_CSV = DC_DATASET_FOLDER + "task_result_labeled_manual.csv"
AUTO_LABEL_CSV = DC_DATASET_FOLDER + "task_result_labeled_auto.csv"


def remove_failed_trails(df):
    split_indices = df.index[df["timestamp"] == -1].tolist()

    dropped_indices = []
    for i in range(len(split_indices) - 2):
        current_trail = df.iloc[split_indices[i]]["trail"]
        next_trail = df.iloc[split_indices[i + 1]]["trail"]

        if current_trail == next_trail:
            print(
                f"Detect failed trail: {df.iloc[split_indices[i]]["task"]}-{current_trail}"
            )
            dropped_indices.append((split_indices[i], split_indices[i + 1]))

    # drop failed trails
    for a, b in dropped_indices:
        df = df.drop(index=range(a, b)).reset_index(drop=True)

    # remove all -1 timestamp rows
    df = df[df["timestamp"] != -1].reset_index(drop=True)

    return df


def create_task_result_csv():
    df = pd.DataFrame()
    for participant in range(12):
        p_folder = DC_PARTICIPANT_FOLDER_TEMPLATE.format(pid=participant)
        if not os.path.exists(p_folder):
            print(f"- Skipping participant {participant} (data not found)")
            continue
        print(f"+ Processing participant {participant}")

        p_df = pd.read_csv(os.path.join(p_folder, "task_result.csv"))
        p_df = remove_failed_trails(p_df)

        p_df["participant_id"] = participant  # add participant ID column

        df = pd.concat([df, p_df], ignore_index=True)

    # rearragne participant ID column to the front
    cols = df.columns.tolist()
    cols.insert(0, cols.pop(cols.index("participant_id")))
    df = df[cols]

    df.to_csv(RESULT_CSV, index=False)


def init_labeled_csv():
    df = pd.read_csv(RESULT_CSV)
    df["label"] = -1  # initialize all labels to -1 (unlabeled)
    df.to_csv(DC_DATASET_FOLDER + "task_result_labeled_init.csv", index=False)


def update_labeled_result_csv(csv_path, new_df):
    new_df = new_df[["participant_id", "timestamp", "task", "trail", "label"]]

    old_df = pd.read_csv(csv_path)
    df = pd.merge(
        old_df,
        new_df,
        on=["participant_id", "timestamp", "task", "trail"],
        how="left",
        suffixes=("", "_new"),
    )

    # Update labels where new labels are provided
    df["label"] = df["label_new"].combine_first(df["label"])
    df = df.drop(columns=["label_new"])

    old_df.to_csv(csv_path + " backup", index=False)
    df.to_csv(csv_path, index=False)


if __name__ == "__main__":
    create_task_result_csv()
    init_labeled_csv()
