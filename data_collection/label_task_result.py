import pandas as pd
import os

DATASET_FOLDER = "./data_collection/datasets/"


if __name__ == "__main__":

    landmarks_df = pd.read_csv(os.path.join(DATASET_FOLDER, "task_result_merged.csv"))
    labels_df = pd.read_csv(os.path.join(DATASET_FOLDER, "labels.csv"))
    labeled_df = pd.merge(
        landmarks_df,
        labels_df,
        on=["participant_id", "timestamp", "task", "trail"],
        how="left",
    )
    labeled_df = labeled_df[labeled_df["label"].notnull()]  # keep only labeled frames
    labeled_df.to_csv(
        os.path.join(DATASET_FOLDER, "task_result_labeled.csv"), index=False
    )
