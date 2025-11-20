import pandas as pd
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmark


def generate_samples(
    df, window_length, feature_columns, label_mapping, padding=True
) -> list[dict]:
    """
    Generate sliding window samples from the dataframe.
    """

    # pad the beginning with the first row to ensure enough frames
    if padding:
        pad = window_length - 1
        first_row = df.iloc[[0]].copy()
        padding = pd.concat([first_row] * pad, ignore_index=True)
        df = pd.concat([padding, df.reset_index(drop=True)], ignore_index=True)

    samples = []
    num_frames = len(df)
    for start_idx in range(0, num_frames - window_length + 1):
        end_idx = start_idx + window_length
        window = df.iloc[start_idx:end_idx]
        feature_array = window[feature_columns].copy()

        samples.append(
            {
                "timestamp": window["timestamp"].values[-1],
                "features": feature_array,
                "label": (label_mapping[window["label"].values[-1]]),
            }
        )
    return samples


def split_landmark_columns(df, landmarks: list[HandLandmark]):
    """
    Split specified landmark columns into x, y, z columns, and drop the original columns.
    """

    landmarks_name = [lm.name for lm in landmarks]
    for lm in landmarks_name:
        df[[f"{lm}_x", f"{lm}_y", f"{lm}_z"]] = (
            df[lm].str.split("_", expand=True).astype(float)
        )
    df = df.drop(columns=landmarks_name)  # drop original columns
    return df
