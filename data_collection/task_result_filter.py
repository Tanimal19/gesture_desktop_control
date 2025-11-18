import pandas as pd
import os
from data_collection.src.recorder import DataCollectionRecorder

DATASET_FOLDER = "./data_collection/datasets/"


def remove_failed_trails(df):
    split_indices = df.index[df["timestamp"] == -1].tolist()
    split_indices.append(len(df))

    for i in range(len(split_indices) - 2):
        current_trail = df.iloc[split_indices[i]]["trail"]
        next_trail = df.iloc[split_indices[i + 1]]["trail"]

        if current_trail == next_trail:  # drop current trail
            print(
                f"Removing failed trail: {df.iloc[split_indices[i]]["task"]}-{current_trail}"
            )
            df = df.drop(
                index=range(split_indices[i], split_indices[i + 1])
            ).reset_index(drop=True)

    # remove all -1 timestamp rows
    df = df[df["timestamp"] != -1].reset_index(drop=True)

    return df


def split_landmarks(df):
    landmarks = [lm.name for lm in DataCollectionRecorder.RECORDED_LANDMARKS]
    for lm in landmarks:
        df[[f"{lm}_x", f"{lm}_y", f"{lm}_z"]] = (
            df[lm].str.split("_", expand=True).astype(float)
        )
    df = df.drop(columns=landmarks)  # drop original columns
    return df


if __name__ == "__main__":

    df = pd.DataFrame()

    for participant in range(12):
        print(f"Processing participant {participant}")
        p_folder = os.path.join(DATASET_FOLDER, f"p{participant}")
        if not os.path.exists(p_folder):
            print("skip.")
            continue

        p_df = pd.read_csv(os.path.join(p_folder, "task_result.csv"))
        p_df = remove_failed_trails(p_df)
        p_df = split_landmarks(p_df)

        df = pd.concat([df, p_df], ignore_index=True)

    output_path = os.path.join(DATASET_FOLDER, "processed", "task_result_processed.csv")
    df.to_csv(output_path, index=False)
