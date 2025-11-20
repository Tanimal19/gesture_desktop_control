import pandas as pd
import os
from data_collection.src.recorder import DataCollectionRecorder

DATASET_FOLDER = "./data_collection/datasets/"


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


if __name__ == "__main__":

    df = pd.DataFrame()

    for participant in range(12):
        p_folder = os.path.join(DATASET_FOLDER, f"p{participant}")
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

    output_path = os.path.join(DATASET_FOLDER, "task_result_merged.csv")
    df.to_csv(output_path, index=False)
