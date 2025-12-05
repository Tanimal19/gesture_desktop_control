import pandas as pd
import os
from pathlib import Path


def combine_task_results():
    """
    Combine all task result CSV files from evaluation study datasets.
    Reads all task_result_gesture.csv and task_result_touchpad.csv files
    from participant folders (p0, p1, p2, ...) and combines them into a single dataframe.
    """
    # Define the base directory for datasets
    base_dir = Path(__file__).parent.parent / "evaluation_study" / "datasets"

    # List to store all dataframes
    all_dataframes = []

    # Get all participant folders (p0, p1, p2, ...)
    participant_folders = sorted(
        [d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith("p")]
    )

    print(f"Found {len(participant_folders)} participant folders")

    # Iterate through each participant folder
    for participant_folder in participant_folders:
        participant_id = participant_folder.name

        # Look for both gesture and touchpad result files
        for input_method in ["gesture", "touchpad"]:
            result_file = participant_folder / f"task_result_{input_method}.csv"

            if result_file.exists():
                print(f"Reading: {result_file}")
                df = pd.read_csv(result_file)

                # Add input method column to distinguish between gesture and touchpad
                df["input_method"] = input_method

                all_dataframes.append(df)
            else:
                print(f"Warning: File not found - {result_file}")

    # Combine all dataframes
    if all_dataframes:
        combined_df = pd.concat(all_dataframes, ignore_index=True)

        # Sort by pid, input_method, task_type, and trial_index for better organization
        combined_df = combined_df.sort_values(
            ["pid", "input_method", "task_type", "trial_index"]
        )
        combined_df = combined_df.reset_index(drop=True)

        print(f"\nCombined dataframe shape: {combined_df.shape}")
        print(f"Total records: {len(combined_df)}")
        print(f"\nUnique participants: {sorted(combined_df['pid'].unique())}")
        print(f"Input methods: {sorted(combined_df['input_method'].unique())}")
        print(f"Task types: {sorted(combined_df['task_type'].unique())}")

        # Save to CSV
        output_file = Path(__file__).parent / "combined_task_results.csv"
        combined_df.to_csv(output_file, index=False)
        print(f"\nCombined data saved to: {output_file}")

        return combined_df
    else:
        print("No data files found!")
        return None


if __name__ == "__main__":
    combined_df = combine_task_results()
