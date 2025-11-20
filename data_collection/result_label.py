import pandas as pd
import os

DATASET_FOLDER = "./data_collection/datasets/"


if __name__ == "__main__":

    landmarks_df = pd.read_csv(os.path.join(DATASET_FOLDER, "task_result_merged.csv"))

    labels_df = pd.DataFrame()
    for participant in range(12):
        p_file = os.path.join(DATASET_FOLDER, f"p{participant}", "labels.csv")
        if not os.path.exists(p_file):
            print(f"- Skipping participant {participant} (data not found)")
            continue
        print(f"+ Processing participant {participant}")

        p_df = pd.read_csv(p_file)

        p_df["participant_id"] = participant  # add participant ID column

        labels_df = pd.concat([labels_df, p_df], ignore_index=True)

    df = pd.merge(
        landmarks_df,
        labels_df,
        on=["participant_id", "timestamp", "task", "trail"],
        how="left",
    )
    df = df[df["label"].notnull()]  # keep only labeled frames
    df.to_csv(os.path.join(DATASET_FOLDER, "task_result_labeled.csv"), index=False)
