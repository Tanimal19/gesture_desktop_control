from gesture_model.utils import LANDMARKS as GM_LANDMARKS


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
