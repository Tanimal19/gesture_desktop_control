import pandas as pd
import os


DATASET_DIR = "./data_collection/datasets/"
RESULT_CSV = DATASET_DIR + "task_result_merged.csv"
LABEL_CSV = DATASET_DIR + "labels.csv"
LABELED_RESULT_CSV = DATASET_DIR + "task_result_labeled.csv"


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
        p_folder = os.path.join(DATASET_DIR, f"p{participant}")
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


def create_label_csv():
    df = pd.read_csv(RESULT_CSV)
    df["label"] = -1  # initialize all labels to -1 (unlabeled)
    label_df = df[["participant_id", "timestamp", "task", "trail", "label"]]
    label_df.to_csv(LABEL_CSV, index=False)


def update_label_csv(new_labels_df):
    label_df = pd.read_csv(LABEL_CSV)
    updated_label_df = pd.merge(
        label_df,
        new_labels_df,
        on=["participant_id", "timestamp", "task", "trail"],
        how="left",
        suffixes=("", "_new"),
    )

    # Update labels where new labels are provided
    updated_label_df["label"] = updated_label_df["label_new"].combine_first(
        updated_label_df["label"]
    )
    updated_label_df = updated_label_df.drop(columns=["label_new"])
    updated_label_df.to_csv(LABEL_CSV, index=False)


def create_labeled_result_csv():
    result_df = pd.read_csv(RESULT_CSV)
    label_df = pd.read_csv(LABEL_CSV)

    merged_df = pd.merge(
        result_df,
        label_df,
        on=["participant_id", "timestamp", "task", "trail"],
        how="left",
    )
    merged_df = merged_df[merged_df["label"] != "-1"]  # keep only labeled frames
    merged_df.to_csv(LABELED_RESULT_CSV, index=False)


if __name__ == "__main__":
    id = input(
        "[1] Merge task result CSV\n[2] Create empty label CSV\n[3] Merge result and label\nSelect a function: "
    )

    if id == "1":
        create_task_result_csv()
    elif id == "2":
        create_label_csv()
    elif id == "3":
        create_labeled_result_csv()
    else:
        print("Invalid selection.")
