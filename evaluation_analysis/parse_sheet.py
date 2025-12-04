import pandas as pd
import gspread
import re
from share import SHEET_HEADER, NASA_TLX_SUBSCALES, SYSTEM


def _extract_sheet_id(sheet_url: str) -> str:
    pattern = r"/spreadsheets/d/([a-zA-Z0-9-_]+)"
    match = re.search(pattern, sheet_url)

    if not match:
        raise ValueError(f"Could not extract sheet ID from URL: {sheet_url}")

    return match.group(1)


def _letter_to_col_index(s: str) -> int:
    if not s or not any(ch.isalpha() for ch in s):
        raise ValueError("Invalid column letter")
    s = s.upper()
    col = 0
    for ch in s:
        if ch.isalpha():
            col = col * 26 + (ord(ch) - ord("A") + 1)
    return col - 1


if __name__ == "__main__":
    data_folder = "./evaluation_analysis/"

    gc = gspread.service_account(filename=data_folder + "credentials.json")
    sheet_url = "https://docs.google.com/spreadsheets/d/17x2tE15Vy4zHrtOQnIAZm3iR1hqoU4mafqt8BvrHGQQ/edit?usp=sharing"

    sheet_id = _extract_sheet_id(sheet_url)
    sh = gc.open_by_key(sheet_id)
    questionnaire_ws = sh.worksheet("questionnaire")
    order_ws = sh.worksheet("order")

    data = []
    v = questionnaire_ws.get_all_values()
    for row in v[1:]:
        record = {}
        for key, letter in SHEET_HEADER.items():
            col_idx = _letter_to_col_index(letter)
            record[key] = row[col_idx]
        data.append(record)
    df = pd.DataFrame(data)

    # Get the order data and merge with main dataframe
    order_df = pd.DataFrame(order_ws.get_all_records())

    # Align pid types and merge
    df["pid"] = df["pid"].astype(int)
    order_df["pid"] = order_df["pid"].astype(int)
    merged_df = df.merge(order_df, on="pid", how="left")

    # Create new columns based on system order
    for metric in NASA_TLX_SUBSCALES:
        for sys in SYSTEM:
            merged_df[f"{sys}-{metric}"] = merged_df.apply(
                lambda row: (
                    row[f"s1-{metric}"]
                    if row["system1"] == sys
                    else row[f"s2-{metric}"]
                ),
                axis=1,
            )

    # Drop the original s1/s2 columns and system1/system2 columns
    columns_to_drop = (
        [f"s1-{metric}" for metric in NASA_TLX_SUBSCALES]
        + [f"s2-{metric}" for metric in NASA_TLX_SUBSCALES]
        + ["system1", "system2"]
    )

    final_df = merged_df.drop(columns=columns_to_drop)

    # Save the processed dataframe
    final_df.to_csv(data_folder + "questionnaire_filtered.csv", index=False)
