import pandas as pd
import gspread
import re
from pathlib import Path
from share import (
    SHEET_HEADER,
    NASA_TLX_SUBSCALES,
    SYSTEM,
    DATASET_FOLDER,
    QUALITATIVE_RESULT_FOLDER,
    QUANTITATIVE_RESULT_FOLDER,
)


# ==== Questionnaire Sheet Parsing ====
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


def parse_questionnaire_sheet(sheet_url: str) -> pd.DataFrame:
    gc = gspread.service_account(filename=DATASET_FOLDER + "credentials.json")

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
    merged_df = merged_df[merged_df["pid"] != 0]  # Exclude pilot participant

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
            merged_df[f"{sys}-{metric}"] = (
                pd.to_numeric(merged_df[f"{sys}-{metric}"]) * 5
            )

    # Drop the original s1/s2 columns and system1/system2 columns
    columns_to_drop = (
        [f"s1-{metric}" for metric in NASA_TLX_SUBSCALES]
        + [f"s2-{metric}" for metric in NASA_TLX_SUBSCALES]
        + ["system1", "system2"]
    )

    final_df = merged_df.drop(columns=columns_to_drop)
    return final_df


# ==== Combine Task Results ====
def combine_task_results() -> pd.DataFrame:
    base_dir = Path(__file__).parent.parent / "evaluation_study" / "datasets"

    # Get all participant folders (p0, p1, p2, ...)
    participant_folders = sorted(
        [d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith("p")]
    )
    print(f"Found {len(participant_folders)} participant folders")

    # Iterate through each participant folder
    all_dataframes = []
    for participant_folder in participant_folders:
        pid = participant_folder.name
        if pid == "p0":
            continue  # Skip pilot participant

        for system in SYSTEM:
            result_file = participant_folder / f"task_result_{system}.csv"

            if result_file.exists():
                df = pd.read_csv(result_file)
                df["system"] = system
                all_dataframes.append(df)
            else:
                print(f"Warning: File not found - {result_file}")

    # Combine all dataframes
    combined_df = pd.concat(all_dataframes, ignore_index=True)

    combined_df = combined_df.sort_values(["pid", "system", "task_type", "trial_index"])
    combined_df = combined_df.reset_index(drop=True)

    return combined_df


# ==== Main ====
if __name__ == "__main__":
    questionnire_df = parse_questionnaire_sheet(
        "https://docs.google.com/spreadsheets/d/17x2tE15Vy4zHrtOQnIAZm3iR1hqoU4mafqt8BvrHGQQ/edit?usp=sharing"
    )

    result_df = combine_task_results()

    print("Questionnaire DataFrame:")
    print(questionnire_df)

    print("\nCombined Task Results DataFrame:")
    print(result_df)

    questionnire_df.to_csv(QUALITATIVE_RESULT_FOLDER + "raw.csv", index=False)
    result_df.to_csv(QUANTITATIVE_RESULT_FOLDER + "raw.csv", index=False)
