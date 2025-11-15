from gesture_model.utils import LANDMARKS as GM_LANDMARKS, label_to_index
import pandas as pd


def split_landmarks(df):
    meta_cols = ["timestamp", "task", "trail", "label"]
    landmarks = [c for c in df.columns if c not in meta_cols]
    for lm in landmarks:
        df[[f"{lm}_x", f"{lm}_y", f"{lm}_z"]] = (
            df[lm].str.split("_", expand=True).astype(float)
        )
    df = df.drop(columns=landmarks)  # drop original columns
    return df


def offset_landmarks(df):
    for lm in GM_LANDMARKS:
        for dim in ["x", "y", "z"]:
            df[f"{lm}_{dim}"] = df[f"{lm}_{dim}"] - df[f"WRIST_{dim}"]
    return df


def generate_frame_windows(df, window_length, has_label=False):
    EXTEND_LANDMARKS = [f"{lm}_{dim}" for lm in GM_LANDMARKS for dim in ["x", "y", "z"]]

    # pad the beginning with the first row to ensure enough frames
    pad = window_length - 1
    first_row = df.iloc[[0]].copy()
    padding = pd.concat([first_row] * pad, ignore_index=True)
    df = pd.concat([padding, df.reset_index(drop=True)], ignore_index=True)

    samples = []
    num_frames = len(df)
    for start_idx in range(0, num_frames - window_length + 1):
        end_idx = start_idx + window_length
        window = df.iloc[start_idx:end_idx]

        # extract landmark data
        lm_array = window[EXTEND_LANDMARKS].copy()
        lm_array = lm_array.values.reshape(
            (window_length, len(EXTEND_LANDMARKS) // 3, 3)
        )  # shape: (frame_window, num_landmarks, 3)
        lm_array = lm_array.astype("float32")

        # get label (label of the last frame in the window)
        label = label_to_index(window["label"].values[-1]) if has_label else None

        samples.append(
            {
                "timestamp": window["timestamp"].values[-1],
                "landmarks": lm_array,
                "label": label,
            }
        )
    return samples
