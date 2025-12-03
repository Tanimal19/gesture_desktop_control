import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


def process_log_file(log_file_path):
    # Regular expression to match the log format
    patterns = {
        "ti": r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \[DEBUG\] mouse_event_mapper\.detect\(\): thumb-index distances: ([0-9.]+)",
        "tm": r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \[DEBUG\] mouse_event_mapper\.detect\(\): thumb-middle distances: ([0-9.]+)",
    }

    datas = {
        "ti": [],
        "tm": [],
    }

    with open(log_file_path, "r") as file:
        for line in file:
            for id, pattern in patterns.items():
                match = re.search(pattern, line.strip())
                if match:
                    timestamp_str, distance = match.groups()
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")
                    datas[id].append(
                        {
                            "timestamp": timestamp,
                            f"{id}_distance": float(distance),
                        }
                    )

    # Merge dataframes on timestamp
    df_ti = pd.DataFrame(datas["ti"]).set_index("timestamp")
    df_tm = pd.DataFrame(datas["tm"]).set_index("timestamp")

    df = pd.merge_asof(
        df_ti.sort_index(),
        df_tm.sort_index(),
        left_index=True,
        right_index=True,
        direction="nearest",
    ).dropna()
    print(df)

    return df


def visualize_data(df, output_image_path=None):
    # Time series of current and past distances
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df["ti_distance"], label="Thumb-Index")
    plt.plot(df.index, df["tm_distance"], label="Thumb-Middle")
    plt.xlabel("Time")
    plt.ylabel("Distance")
    plt.title("Finger Distances Over Time")
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
