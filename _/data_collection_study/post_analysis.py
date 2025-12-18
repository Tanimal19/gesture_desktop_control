from share.datapath import DC_FINAL_LABEL_CSV, DC_MANUAL_LABEL_CSV, DC_DATASET_FOLDER
import pandas as pd


def analyze_consecutive_frames(filepath):
    """
    Analyze the average consecutive frames of each gesture label.
    """
    # Load the data
    df = pd.read_csv(filepath)

    # Sort by participant, task, trail, and timestamp to ensure proper ordering
    df = df.sort_values(["participant_id", "task", "trail", "timestamp"])

    consecutive_sequences = []

    # Group by participant, task, and trail to analyze each sequence separately
    for (participant_id, task, trail), group in df.groupby(
        ["participant_id", "task", "trail"]
    ):
        # Reset index for this group
        group = group.reset_index(drop=True)

        # Track consecutive frames for each label
        current_label = None
        current_count = 0

        for idx, row in group.iterrows():
            label = row["label"]

            if label == current_label:
                # Continue counting consecutive frames
                current_count += 1
            else:
                # Label changed, record the previous sequence if it exists
                if current_label is not None:
                    consecutive_sequences.append(
                        {
                            "participant_id": participant_id,
                            "task": task,
                            "trail": trail,
                            "label": current_label,
                            "consecutive_frames": current_count,
                        }
                    )

                # Start new sequence
                current_label = label
                current_count = 1

        # Don't forget the last sequence
        if current_label is not None:
            consecutive_sequences.append(
                {
                    "participant_id": participant_id,
                    "task": task,
                    "trail": trail,
                    "label": current_label,
                    "consecutive_frames": current_count,
                }
            )

    # Convert to DataFrame for analysis
    sequences_df = pd.DataFrame(consecutive_sequences)

    # Calculate statistics for each gesture label
    stats = (
        sequences_df.groupby("label")["consecutive_frames"]
        .agg(
            [
                "count",  # number of sequences
                "mean",  # average consecutive frames
                "std",  # standard deviation
                "min",  # minimum consecutive frames
                "max",  # maximum consecutive frames
                "median",  # median consecutive frames
            ]
        )
        .round(2)
    )

    stats.columns = [
        "total_sequences",
        "avg_consecutive_frames",
        "std_dev",
        "min_frames",
        "max_frames",
        "median_frames",
    ]

    return stats, sequences_df


def print_detailed_analysis(stats, sequences_df, summary_file):
    from contextlib import redirect_stdout

    with open(summary_file, "w") as f:
        with redirect_stdout(f):

            print("=" * 60)
            print("CONSECUTIVE FRAMES ANALYSIS BY GESTURE")
            print("=" * 60)

            print("\nSUMMARY STATISTICS:")
            print(stats.to_string())

            print("\n" + "=" * 60)
            print("DETAILED BREAKDOWN BY GESTURE:")
            print("=" * 60)

            for label in sorted(sequences_df["label"].unique()):
                label_data = sequences_df[sequences_df["label"] == label][
                    "consecutive_frames"
                ]

                print(f"\n{label}:")
                print(f"  Total sequences: {len(label_data)}")
                print(f"  Average consecutive frames: {label_data.mean():.2f}")
                print(f"  Standard deviation: {label_data.std():.2f}")
                print(f"  Min: {label_data.min()} frames")
                print(f"  Max: {label_data.max()} frames")
                print(f"  Median: {label_data.median():.2f} frames")

                # Show distribution
                percentiles = [25, 50, 75, 90, 95]
                percentile_values = [label_data.quantile(p / 100) for p in percentiles]
                print(f"  Percentiles: {dict(zip(percentiles, percentile_values))}")


if __name__ == "__main__":
    # Run the analysis
    stats, sequences_df = analyze_consecutive_frames(DC_MANUAL_LABEL_CSV)

    # Print detailed results
    summary_file = DC_DATASET_FOLDER + "gesture_statistics_summary.txt"
    print_detailed_analysis(stats, sequences_df, summary_file)

    # Save detailed sequences to CSV for further analysis
    output_file = DC_DATASET_FOLDER + "consecutive_frames_analysis.csv"
    sequences_df.to_csv(output_file, index=False)
    print(f"Detailed sequences saved to: {output_file}")
