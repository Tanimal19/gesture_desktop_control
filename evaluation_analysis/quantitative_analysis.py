import pandas as pd
import numpy as np
import pprint
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
from share import QUANTITATIVE_RESULT_FOLDER, print_divider


pp = pprint.PrettyPrinter(compact=True, width=120)


# ==== Metric Calculation (each task) ====
def _calculate_accuracy_rates(group_df, target_column, input_column):
    total_counts = len(group_df)
    correct_counts = 0
    wrong_counts = 0
    fail_counts = 0

    for _, row in group_df.iterrows():
        if pd.isna(row[input_column]):
            fail_counts += 1
        else:
            if row[input_column] == row[target_column]:
                correct_counts += 1
            else:
                wrong_counts += 1

    correct_rate = correct_counts / total_counts
    wrong_rate = wrong_counts / total_counts
    failed_rate = fail_counts / total_counts
    return total_counts, correct_rate, wrong_rate, failed_rate


def _calculate_efficiency(group_df, numerator_column, denominator_column):
    l = []
    for _, row in group_df.iterrows():
        l.append(row[numerator_column] / row[denominator_column])
    return l


def _remove_failed_trials(df, input_column):
    failed_trails = []
    for _, row in df.iterrows():
        if pd.isna(row[input_column]):
            failed_trails.append((row["pid"], row["trial_index"]))

    for pid, trial_index in failed_trails:
        print(f"Removing failed trial: pid={pid}, trial={trial_index} in both systems")
        df = df[~((df["pid"] == pid) & (df["trial_index"] == trial_index))]

    return df


def calculate_menu_select_metrics(df):
    print("calculate_menu_select_metrics()")

    df = df[df["task_type"] == "MenuSelect"].copy()
    # Cap moving_distance to target_distance if moving_distance < target_distance
    df["MenuSelect-moving_distance"] = np.where(
        df["MenuSelect-moving_distance"] < df["MenuSelect-target_distance"],
        df["MenuSelect-target_distance"],
        df["MenuSelect-moving_distance"],
    )

    data = {}
    for system, group in df.groupby("system"):
        data[system] = {}
        (
            data[system]["total_trail_num"],
            data[system]["correct_rate"],
            data[system]["wrong_rate"],
            data[system]["failed_rate"],
        ) = _calculate_accuracy_rates(
            group, "MenuSelect-target_index", "MenuSelect-selected_index"
        )

    clean_df = _remove_failed_trials(df, "MenuSelect-selected_index")
    for system, group in clean_df.groupby("system"):
        data[system]["efficiency"] = _calculate_efficiency(
            group, "MenuSelect-moving_distance", "MenuSelect-target_distance"
        )
        data[system]["complete_time"] = group["complete_time"].tolist()
        data[system]["moving_distance"] = group["MenuSelect-moving_distance"].tolist()

    pp.pprint(data)
    print()
    return data


def calculate_drag_drop_metrics(df):
    print("calculate_drag_drop_metrics()")

    df = df[df["task_type"] == "DragDrop"].copy()
    df["DragDrop-moving_distance"] = np.where(
        df["DragDrop-moving_distance"] < df["DragDrop-target_distance"],
        df["DragDrop-target_distance"],
        df["DragDrop-moving_distance"],
    )

    data = {}
    for system, group in df.groupby("system"):
        data[system] = {}
        (
            data[system]["total_trail_num"],
            data[system]["correct_rate"],
            data[system]["wrong_rate"],
            data[system]["failed_rate"],
        ) = _calculate_accuracy_rates(
            group, "DragDrop-target_area", "DragDrop-dropped_area"
        )

    clean_df = _remove_failed_trials(df, "DragDrop-dropped_area")
    for system, group in clean_df.groupby("system"):
        data[system]["efficiency"] = _calculate_efficiency(
            group, "DragDrop-moving_distance", "DragDrop-target_distance"
        )
        data[system]["complete_time"] = group["complete_time"].tolist()
        data[system]["moving_distance"] = group["DragDrop-moving_distance"].tolist()

    pp.pprint(data)
    print()
    return data


def calculate_keyboard_input_metrics(df):
    print("calculate_keyboard_input_metrics()")

    df = df[df["task_type"] == "KeyboardInput"].copy()

    data = {}
    for system, group in df.groupby("system"):
        data[system] = {}
        (
            data[system]["total_trail_num"],
            data[system]["correct_rate"],
            data[system]["wrong_rate"],
            data[system]["failed_rate"],
        ) = _calculate_accuracy_rates(
            group, "KeyboardInput-target_word", "KeyboardInput-entered_word"
        )

        data[system]["wpm"] = []
        data[system]["backspace_rate"] = []
        data[system]["efficiency"] = []

    clean_df = _remove_failed_trials(df, "KeyboardInput-entered_word")
    for system, group in clean_df.groupby("system"):
        for _, row in group.iterrows():
            data[system]["wpm"].append(
                (len(row["KeyboardInput-entered_word"]) / 5)
                / (row["complete_time"] / 60)
            )
            data[system]["backspace_rate"].append(
                row["KeyboardInput-num_backspaces"]
                / len(row["KeyboardInput-entered_word"])
            )
            data[system]["efficiency"].append(
                row["KeyboardInput-num_key_clicks"]
                / len(row["KeyboardInput-target_word"])
            )

        data[system]["complete_time"] = group["complete_time"].tolist()
        data[system]["moving_distance"] = group[
            "KeyboardInput-moving_distance"
        ].tolist()

    pp.pprint(data)
    print()
    return data


# ==== Statistical Analysis ====
def test_normality_shapiro(data, alpha=0.05):
    stat, p_value = stats.shapiro(data)
    is_normal = p_value > alpha
    return is_normal, stat, p_value


def compare_metric(metric_name, data):
    gesture_data = data["gesture"][metric_name]
    touchpad_data = data["touchpad"][metric_name]
    print(f"[{metric_name}]")
    print(
        f"gesture: n={len(gesture_data)}, mean={np.mean(gesture_data):.4f}, std={np.std(gesture_data):.4f}"
    )
    print(
        f"touchpad: n={len(touchpad_data)}, mean={np.mean(touchpad_data):.4f}, std={np.std(touchpad_data):.4f}"
    )

    # Test normality for both systems
    gesture_is_normal, gesture_stat, gesture_p = test_normality_shapiro(gesture_data)
    touchpad_is_normal, touchpad_stat, touchpad_p = test_normality_shapiro(
        touchpad_data
    )
    print("> Normality test results:")
    print(
        f"  gesture - W={gesture_stat:.4f}, p={gesture_p:.4f}, {'Normal' if gesture_is_normal else 'Not Normal'}"
    )
    print(
        f"  touchpad - W={touchpad_stat:.4f}, p={touchpad_p:.4f}, {'Normal' if touchpad_is_normal else 'Not Normal'}"
    )

    if gesture_is_normal and touchpad_is_normal:
        # Paired samples t-test
        test_stat, p_value = stats.ttest_rel(gesture_data, touchpad_data)
        print("> Paired Samples t-test results:")
    else:
        # Wilcoxon signed-rank test
        test_stat, p_value = stats.wilcoxon(gesture_data, touchpad_data)
        print("> Wilcoxon Signed-Rank Test results:")

    is_significant = p_value < 0.05
    print(
        f"  stat={test_stat:.4f}, p={p_value:.4f}, {'SIGNIFICANT' if is_significant else 'NOT SIGNIFICANT'} difference\n"
    )


def statistical_analysis(
    menu_select_metrics, drag_drop_metrics, keyboard_input_metrics
):
    print_divider("Menu Selection Task")
    compare_metric("efficiency", menu_select_metrics)
    compare_metric("complete_time", menu_select_metrics)
    compare_metric("moving_distance", menu_select_metrics)

    print_divider("Drag Drop Task")
    compare_metric("efficiency", drag_drop_metrics)
    compare_metric("complete_time", drag_drop_metrics)
    compare_metric("moving_distance", drag_drop_metrics)

    print_divider("Keyboard Input Task")
    compare_metric("wpm", keyboard_input_metrics)
    compare_metric("backspace_rate", keyboard_input_metrics)
    compare_metric("efficiency", keyboard_input_metrics)
    compare_metric("complete_time", keyboard_input_metrics)
    compare_metric("moving_distance", keyboard_input_metrics)


# ==== Visualization ====
def plot_task_correct_rate(data):
    """
    Plot correct rate for both systems using grouped bar plots.

    Args:
        data: Dictionary with task names as keys, each containing 'gesture' and 'touchpad'
              subdictionaries with 'correct_rate' values
    """
    # Prepare data for seaborn
    plot_data = []
    for task_name, task_data in data.items():
        for system in ["gesture", "touchpad"]:
            plot_data.append(
                {
                    "Task": task_name,
                    "System": system.capitalize(),
                    "Correct Rate": task_data[system]["correct_rate"]
                    * 100,  # Convert to percentage
                }
            )

    plot_df = pd.DataFrame(plot_data)

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Create grouped bar plot
    sns.barplot(
        data=plot_df,
        x="Task",
        y="Correct Rate",
        hue="System",
        width=0.6,
        ax=ax,
        palette=["#FF6B6B", "#4ECDC4"],
        alpha=0.8,
    )

    ax.set_title("Task Correct Rate by System", fontsize=14, fontweight="bold", pad=20)
    ax.set_xlabel("Task Type", fontsize=12)
    ax.set_ylabel("Correct Rate (%)", fontsize=12)
    ax.set_ylim(0, 110)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.legend(title="System", fontsize=10)

    # Add value labels on bars
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f%%", padding=3)

    plt.tight_layout()
    return fig


def plot_task_metrics_in_single_figure(task_name, metrics_dict, metric_configs):
    """
    Plot all metrics for a single task in one figure with subplots.

    Args:
        task_name: Name of the task (e.g., "Menu Selection")
        metrics_dict: Dictionary containing metric data for both systems
        metric_configs: List of tuples (metric_name, ylabel) for metrics to plot
    """
    n_metrics = len(metric_configs)
    fig, axes = plt.subplots(1, n_metrics, figsize=(4 * n_metrics, 5))

    # Handle single metric case
    if n_metrics == 1:
        axes = [axes]

    fig.suptitle(
        f"{task_name} - Metric Distributions", fontsize=16, fontweight="bold", y=1.02
    )

    for idx, (metric_name, ylabel) in enumerate(metric_configs):
        ax = axes[idx]

        # Prepare data for seaborn
        plot_data = []
        for system in ["gesture", "touchpad"]:
            for value in metrics_dict[system][metric_name]:
                plot_data.append({"System": system.capitalize(), ylabel: value})

        plot_df = pd.DataFrame(plot_data)

        # Create strip plot
        sns.stripplot(
            data=plot_df,
            x="System",
            y=ylabel,
            hue="System",
            ax=ax,
            palette=["#FF6B6B", "#4ECDC4"],
            size=8,
            alpha=0.6,
            jitter=0.2,
            legend=False,
            zorder=1,
        )

        # Add mean lines and labels
        for i, system in enumerate(["Gesture", "Touchpad"]):
            system_data = plot_df[plot_df["System"] == system][ylabel]
            mean_val = system_data.mean()
            ax.hlines(
                mean_val,
                i - 0.3,
                i + 0.3,
                colors="black",
                linestyles="solid",
                linewidth=2,
                zorder=3,
            )
            # Add mean value label
            ax.text(
                i,
                mean_val + (0.03 * (ax.get_ylim()[1] - ax.get_ylim()[0])),
                f"  {mean_val:.2f}",
                ha="left",
                fontsize=9,
                fontweight="bold",
                color="black",
                zorder=4,
            )

        ax.set_title(ylabel, fontsize=12, fontweight="bold")
        ax.set_xlabel("System", fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.grid(axis="y", alpha=0.3, linestyle="--")

    plt.tight_layout()
    return fig


def visualization(menu_select_metrics, drag_drop_metrics, keyboard_input_metrics):
    """
    Generate all visualization plots for the quantitative analysis.
    """
    print_divider("Generating Visualizations")

    # Plot correct rate comparison across all tasks
    print("Plotting correct rate comparison...")
    task_correct_rate_data = {
        "Menu Selection": menu_select_metrics,
        "Drag & Drop": drag_drop_metrics,
        "Keyboard Input": keyboard_input_metrics,
    }
    fig_correct_rate = plot_task_correct_rate(task_correct_rate_data)
    fig_correct_rate.savefig(
        QUANTITATIVE_RESULT_FOLDER + "correct_rate_comparison.png",
        dpi=300,
        bbox_inches="tight",
    )
    print(f"Saved: {QUANTITATIVE_RESULT_FOLDER}correct_rate_comparison.png")
    plt.close(fig_correct_rate)

    # Plot Menu Selection metrics
    print("Plotting Menu Selection metrics...")
    menu_configs = [
        ("efficiency", "Efficiency"),
        ("complete_time", "Complete Time (s)"),
        ("moving_distance", "Moving Distance (pixels)"),
    ]
    fig_menu = plot_task_metrics_in_single_figure(
        "Menu Selection", menu_select_metrics, menu_configs
    )
    fig_menu.savefig(
        QUANTITATIVE_RESULT_FOLDER + "menu_select_metrics.png",
        dpi=300,
        bbox_inches="tight",
    )
    print(f"Saved: {QUANTITATIVE_RESULT_FOLDER}menu_select_metrics.png")
    plt.close(fig_menu)

    # Plot Drag & Drop metrics
    print("Plotting Drag & Drop metrics...")
    dragdrop_configs = [
        ("efficiency", "Efficiency"),
        ("complete_time", "Complete Time (s)"),
        ("moving_distance", "Moving Distance (pixels)"),
    ]
    fig_dragdrop = plot_task_metrics_in_single_figure(
        "Drag & Drop", drag_drop_metrics, dragdrop_configs
    )
    fig_dragdrop.savefig(
        QUANTITATIVE_RESULT_FOLDER + "drag_drop_metrics.png",
        dpi=300,
        bbox_inches="tight",
    )
    print(f"Saved: {QUANTITATIVE_RESULT_FOLDER}drag_drop_metrics.png")
    plt.close(fig_dragdrop)

    # Plot Keyboard Input metrics
    print("Plotting Keyboard Input metrics...")
    keyboard_configs = [
        ("wpm", "WPM"),
        ("backspace_rate", "Backspace Rate"),
        ("efficiency", "Efficiency"),
        ("complete_time", "Complete Time (s)"),
        ("moving_distance", "Moving Distance (pixels)"),
    ]
    fig_keyboard = plot_task_metrics_in_single_figure(
        "Keyboard Input", keyboard_input_metrics, keyboard_configs
    )
    fig_keyboard.savefig(
        QUANTITATIVE_RESULT_FOLDER + "keyboard_input_metrics.png",
        dpi=300,
        bbox_inches="tight",
    )
    print(f"Saved: {QUANTITATIVE_RESULT_FOLDER}keyboard_input_metrics.png")
    plt.close(fig_keyboard)

    print("\nAll visualizations completed!")


if __name__ == "__main__":
    df = pd.read_csv(QUANTITATIVE_RESULT_FOLDER + "raw.csv")

    menu_select_metrics = calculate_menu_select_metrics(df)
    drag_drop_metrics = calculate_drag_drop_metrics(df)
    keyboard_input_metrics = calculate_keyboard_input_metrics(df)

    statistical_analysis(menu_select_metrics, drag_drop_metrics, keyboard_input_metrics)
    visualization(menu_select_metrics, drag_drop_metrics, keyboard_input_metrics)
