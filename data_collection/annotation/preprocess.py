import pandas as pd
import numpy as np

# preprocess the raw csv
# 1. split each landmark column into x, y, z columns
# 2. drop failed trails


def split_landmarks(df):
    meta_cols = ["timestamp", "task", "trail", "label"]
    landmarks = [c for c in df.columns if c not in meta_cols]
    for lm in landmarks:
        df[[f"{lm}_x", f"{lm}_y", f"{lm}_z"]] = (
            df[lm].str.split("_", expand=True).astype(float)
        )
    df = df.drop(columns=landmarks)  # drop original columns
    return df


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
    return df


def remove_trail_indicators(df):
    df = df[df["timestamp"] != -1].reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = pd.read_csv("./data_collection/datasets/p0/task_result.csv")
    df = split_landmarks(df)
    df = remove_failed_trails(df)
    df = remove_trail_indicators(df)
    df.to_csv("./data_collection/datasets/p0/task_result_processed.csv", index=False)
