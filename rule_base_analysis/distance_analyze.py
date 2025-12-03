import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


def process_log_file(log_file_path):
    # Regular expression to match the log format
    index_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \[DEBUG\] mouse_event_mapper\.detect\(\): thumb-index distances: current=([0-9.]+), past=([0-9.]+)"
    middle_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \[DEBUG\] mouse_event_mapper\.detect\(\): thumb-middle distances: current=([0-9.]+), past=([0-9.]+)"

    index_data = []
    middle_data = []

    with open(log_file_path, "r") as file:
        for line in file:
            match = re.search(index_pattern, line.strip())
            if match:
                timestamp_str, current_distance, past_distance = match.groups()
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")
                index_data.append(
                    {
                        "timestamp": timestamp,
                        "current_index_distance": float(current_distance),
                        "past_index_distance": float(past_distance),
                    }
                )

            match = re.search(middle_pattern, line.strip())
            if match:
                timestamp_str, current_distance, past_distance = match.groups()
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")
                middle_data.append(
                    {
                        "timestamp": timestamp,
                        "current_middle_distance": float(current_distance),
                        "past_middle_distance": float(past_distance),
                    }
                )

    # Merge index and middle data on timestamp
    df_index = pd.DataFrame(index_data).set_index("timestamp")
    df_middle = pd.DataFrame(middle_data).set_index("timestamp")
    df = pd.merge_asof(
        df_index.sort_index(),
        df_middle.sort_index(),
        left_index=True,
        right_index=True,
        direction="nearest",
    ).dropna()

    print(df)

    return df


def visualize_data(df, output_image_path=None):
    # Time series of current and past distances
    plt.figure(figsize=(12, 6))
    plt.plot(
        df.index, df["current_index_distance"], label="Current Thumb-Index Distance"
    )
    plt.plot(df.index, df["past_index_distance"], label="Past Thumb-Index Distance")
    plt.plot(
        df.index,
        df["current_middle_distance"],
        label="Current Thumb-Middle Distance",
    )
    plt.plot(df.index, df["past_middle_distance"], label="Past Thumb-Middle Distance")
    plt.xlabel("Time")
    plt.ylabel("Distance")
    plt.title("Thumb-Index and Thumb-Middle Distances Over Time")
    plt.legend()
    plt.grid()

    if output_image_path:
        plt.savefig(output_image_path)
    plt.show()


if __name__ == "__main__":
    base_folder = "rule_base_analysis/"
    log_file_path = base_folder + "mainapp.log"
    df = process_log_file(log_file_path)
    visualize_data(df, base_folder + "distance_analysis.png")
