import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import seaborn as sns
from share import (
    QUALITATIVE_RESULT_FOLDER,
    TASK,
    NASA_TLX_SUBSCALES,
    COLOR,
)


def plot_task_preference(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 3))
    fig.suptitle("Task Preference by System", fontsize=16, fontweight="bold")

    task_labels = [task.replace("-", " ").title() for task in TASK]
    gesture_counts = []
    touchpad_counts = []

    for task in TASK:
        col_name = f"{task}-preference"
        gesture_count = (df[col_name] == "Gesture control").sum()
        touchpad_count = (df[col_name] == "Touchpad").sum()
        gesture_counts.append(gesture_count)
        touchpad_counts.append(touchpad_count)

    y_pos = np.arange(len(TASK))
    bars1 = ax.barh(
        y_pos, gesture_counts, color=COLOR[0], label="Gesture Control", height=0.5
    )
    bars2 = ax.barh(
        y_pos,
        touchpad_counts,
        left=gesture_counts,
        color=COLOR[1],
        label="Touchpad",
        height=0.5,
    )
    ax.set_yticks(y_pos)
    ax.set_yticklabels(task_labels)
    ax.set_xlabel("Number of Participants")
    ax.set_xticks(np.arange(0, len(df) + 1, 1))
    ax.legend(loc="upper right")
    ax.invert_yaxis()
    ax.margins(y=0.15)  # 15% padding on top and bottom

    for i, (g_count, t_count) in enumerate(zip(gesture_counts, touchpad_counts)):
        # Label for gesture control (left section)
        if g_count > 0:
            ax.text(
                g_count / 2,
                i,
                str(g_count),
                ha="center",
                va="center",
                fontweight="bold",
                color="black",
            )
        # Label for touchpad (right section)
        if t_count > 0:
            ax.text(
                g_count + t_count / 2,
                i,
                str(t_count),
                ha="center",
                va="center",
                fontweight="bold",
                color="black",
            )

    plt.tight_layout()
    plt.savefig(
        QUALITATIVE_RESULT_FOLDER + "preference_analysis.png",
        dpi=300,
        bbox_inches="tight",
    )


def calculate_sus_score(row):
    # Calculate SUS score for each participant
    # SUS scoring: Odd questions (1,3,5,7,9): score - 1
    #              Even questions (2,4,6,8,10): 5 - score
    #              Total: Sum all * 2.5

    score = 0
    # Odd questions (1, 3, 5, 7, 9)
    for q in [1, 3, 5, 7, 9]:
        score += row[f"sus-q{q}"] - 1
    # Even questions (2, 4, 6, 8, 10)
    for q in [2, 4, 6, 8, 10]:
        score += 5 - row[f"sus-q{q}"]
    return score * 2.5


def plot_sus_scores(df: pd.DataFrame):
    df["sus_score"] = df.apply(calculate_sus_score, axis=1)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    fig.suptitle(
        "System Usability Scale (SUS) Analysis", fontsize=16, fontweight="bold"
    )

    mean_sus = np.mean(df["sus_score"])

    # Individual participant scores
    sns.barplot(
        data=df,
        y="pid",
        x="sus_score",
        ax=ax1,
        color=COLOR[1],
        orient="h",
        order=df["pid"].astype(str).sort_values(),
    )
    ax1.axvline(
        x=68, color="red", linestyle="--", label="Average SUS (68)", linewidth=2
    )
    ax1.axvline(
        x=mean_sus,
        color="green",
        linestyle="--",
        label=f"Mean ({mean_sus:.1f})",
        linewidth=2,
    )
    ax1.set_xlabel("SUS Score")
    ax1.set_ylabel("Participant ID")
    ax1.set_title("SUS Score by Participant")
    ax1.legend()
    ax1.set_xlim(0, 100)
    sns.despine(ax=ax1, left=True)

    # Add value labels
    for i, v in enumerate(df["sus_score"]):
        ax1.text(v + 1, i, f"{v:.1f}", va="center")

    # Individual question responses - prepare data for seaborn
    sus_questions = [f"sus-q{i}" for i in range(1, 11)]

    # Reshape data for seaborn
    sus_df = pd.DataFrame()
    for i, q in enumerate(sus_questions, 1):
        q_data = df[q].copy()
        q_data = pd.DataFrame(
            {
                "Question": f"Q{i}",
                "Score": q_data,
                "Type": "Odd" if i % 2 == 1 else "Even",
            }
        )
        sus_df = pd.concat([sus_df, q_data], ignore_index=True)

    # Create boxplot with seaborn
    sns.boxplot(
        data=sus_df,
        x="Question",
        y="Score",
        hue="Type",
        palette={"Odd": COLOR[1], "Even": COLOR[0]},
        ax=ax2,
        width=0.6,
        linewidth=1.5,
        fliersize=5,
        legend=False,
    )

    ax2.set_ylabel("Score (1-5)")
    ax2.set_xlabel("SUS Question")
    ax2.set_title("SUS Question Responses Distribution")
    ax2.set_ylim(0.5, 5.5)
    ax2.set_yticks(np.arange(1, 6, 1))
    ax2.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        QUALITATIVE_RESULT_FOLDER + "sus_analysis.png", dpi=300, bbox_inches="tight"
    )


def analysis_nasa_tlx(df: pd.DataFrame):
    # statistical comparison for each dimension
    print(f"Statistical Comparison (Wilcoxon Signed-Rank Test):")
    print(f"{'Dimension':<20} {'stat':<12} {'p-value':<12} {'Significant'}")
    print("-" * 60)

    for dim in NASA_TLX_SUBSCALES:
        gesture_col = f"gesture-{dim}"
        touchpad_col = f"touchpad-{dim}"

        # Wilcoxon signed-rank test
        stat, p_value = stats.wilcoxon(df[gesture_col], df[touchpad_col])
        significant = "Yes (p<0.05)" if p_value < 0.05 else "No"

        print(f"{dim.title():<20} {stat:<12.4f} {p_value:<12.4f} {significant}")


def plot_nasa_tlx(df: pd.DataFrame):
    # Prepare data for seaborn
    tlx_data = []
    for subscale in NASA_TLX_SUBSCALES:
        for system in ["Gesture", "Touchpad"]:
            col_name = f"{system.lower()}-{subscale}"
            mean_score = df[col_name].mean()
            tlx_data.append(
                {
                    "Dimension": subscale.replace("-", " ").title(),
                    "System": system,
                    "Score": mean_score,
                }
            )

    # Calculate overall scores
    gesture_overall = df[[f"gesture-{s}" for s in NASA_TLX_SUBSCALES]].mean().mean()
    touchpad_overall = df[[f"touchpad-{s}" for s in NASA_TLX_SUBSCALES]].mean().mean()
    tlx_data.append(
        {"Dimension": "Overall", "System": "Gesture", "Score": gesture_overall}
    )
    tlx_data.append(
        {"Dimension": "Overall", "System": "Touchpad", "Score": touchpad_overall}
    )

    tlx_df = pd.DataFrame(tlx_data)

    # Visualize NASA-TLX comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.suptitle("NASA-TLX Workload Comparison", fontsize=16, fontweight="bold")

    # Create grouped barplot with seaborn
    dim_order = [dim.replace("-", " ").title() for dim in NASA_TLX_SUBSCALES] + [
        "Overall"
    ]
    sns.barplot(
        data=tlx_df,
        y="Dimension",
        x="Score",
        hue="System",
        palette={"Gesture": COLOR[0], "Touchpad": COLOR[1]},
        ax=ax,
        orient="h",
        order=dim_order[::-1],
    )

    # Bold the "Overall" label on y-axis
    yticklabels = ax.get_yticklabels()
    for label in yticklabels:
        if "Overall" in label.get_text():
            label.set_fontweight("bold")

    ax.set_ylabel("NASA-TLX Dimension")
    ax.set_xlabel("Mean Score (0-20, lower is better)")
    ax.set_title("NASA-TLX Scores by Dimension")
    ax.set_xticks(np.arange(0, 101, 5))
    ax.legend(title="System")
    sns.despine(ax=ax, left=True)

    # Add value labels
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f", padding=3)

    plt.tight_layout()
    plt.savefig(
        QUALITATIVE_RESULT_FOLDER + "nasa_tlx_analysis.png",
        dpi=300,
        bbox_inches="tight",
    )


if __name__ == "__main__":
    df = pd.read_csv(QUALITATIVE_RESULT_FOLDER + "raw.csv")
    plot_task_preference(df)
    plot_sus_scores(df)
    analysis_nasa_tlx(df)
    plot_nasa_tlx(df)
