import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from share import DATASET_FOLDER, NASA_TLX_SUBSCALES
from share import print_divider

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 8)


def calculate_sus_score(df):
    """
    Calculate System Usability Scale (SUS) score
    SUS scoring:
    - For odd items (1,3,5,7,9): subtract 1 from the user response
    - For even items (2,4,6,8,10): subtract the user responses from 5
    - Sum the converted responses and multiply by 2.5
    """
    sus_scores = []

    for idx, row in df.iterrows():
        score = 0
        # Odd questions (1,3,5,7,9) - subtract 1
        score += row["sus-q1"] - 1
        score += row["sus-q3"] - 1
        score += row["sus-q5"] - 1
        score += row["sus-q7"] - 1
        score += row["sus-q9"] - 1

        # Even questions (2,4,6,8,10) - subtract from 5
        score += 5 - row["sus-q2"]
        score += 5 - row["sus-q4"]
        score += 5 - row["sus-q6"]
        score += 5 - row["sus-q8"]
        score += 5 - row["sus-q10"]

        # Multiply by 2.5 to get final score (0-100)
        sus_scores.append(score * 2.5)

    return sus_scores


def analyze_sus(df):
    """Analyze SUS scores"""
    print("\n" + "=" * 60)
    print("SYSTEM USABILITY SCALE (SUS) ANALYSIS")
    print("=" * 60)

    sus_scores = calculate_sus_score(df)
    df["sus_score"] = sus_scores

    print(f"\nSUS Score Statistics:")
    print(f"  Mean: {np.mean(sus_scores):.2f}")
    print(f"  Median: {np.median(sus_scores):.2f}")
    print(f"  Std Dev: {np.std(sus_scores):.2f}")
    print(f"  Min: {np.min(sus_scores):.2f}")
    print(f"  Max: {np.max(sus_scores):.2f}")

    # SUS Interpretation
    mean_sus = np.mean(sus_scores)
    if mean_sus >= 80:
        interpretation = "Excellent"
    elif mean_sus >= 68:
        interpretation = "Good (Above Average)"
    elif mean_sus >= 50:
        interpretation = "OK (Below Average)"
    else:
        interpretation = "Poor"

    print(f"\nSUS Interpretation: {interpretation}")
    print(f"  (Industry average is ~68)")

    # Individual scores
    print(f"\nIndividual SUS Scores:")
    for idx, score in enumerate(sus_scores):
        print(f"  Participant {df.iloc[idx]['pid']}: {score:.2f}")

    return df


def calculate_nasa_tlx(df, system):
    """
    Calculate NASA-TLX workload score for a given system
    NASA-TLX has 6 dimensions, each rated 0-20
    Overall score is the average of all dimensions
    """
    dimensions = [f"{system}-{subscale}" for subscale in NASA_TLX_SUBSCALES]

    scores = []
    for idx, row in df.iterrows():
        dimension_scores = [row[dim] for dim in dimensions]
        avg_score = np.mean(dimension_scores)
        scores.append(avg_score)

    return scores, dimensions


def analyze_nasa_tlx(df):
    print_divider("NASA-TLX WORKLOAD ANALYSIS")

    gesture_scores, gesture_dims = calculate_nasa_tlx(df, "gesture")
    touchpad_scores, touchpad_dims = calculate_nasa_tlx(df, "touchpad")

    df["gesture_tlx_score"] = gesture_scores
    df["touchpad_tlx_score"] = touchpad_scores

    print("\n--- Gesture Control System ---")
    print(
        f"Overall TLX Score: {np.mean(gesture_scores):.2f} ± {np.std(gesture_scores):.2f}"
    )
    print("\nDimension Scores (Mean):")
    for dim in gesture_dims:
        print(
            f"  {dim.replace('gesture-', '').replace('-', ' ').title()}: {df[dim].mean():.2f}"
        )

    print("\n--- Touchpad System ---")
    print(
        f"Overall TLX Score: {np.mean(touchpad_scores):.2f} ± {np.std(touchpad_scores):.2f}"
    )
    print("\nDimension Scores (Mean):")
    for dim in touchpad_dims:
        print(
            f"  {dim.replace('touchpad-', '').replace('-', ' ').title()}: {df[dim].mean():.2f}"
        )

    # Statistical comparison
    print("\n--- Statistical Comparison ---")
    t_stat, p_value = stats.ttest_rel(gesture_scores, touchpad_scores)
    print(f"Paired t-test:")
    print(f"  t-statistic: {t_stat:.4f}")
    print(f"  p-value: {p_value:.4f}")

    if p_value < 0.05:
        winner = (
            "Touchpad"
            if np.mean(touchpad_scores) < np.mean(gesture_scores)
            else "Gesture Control"
        )
        print(f"  Result: {winner} has significantly lower workload (p < 0.05)")
    else:
        print(f"  Result: No significant difference (p >= 0.05)")

    # Effect size (Cohen's d)
    mean_diff = np.mean(gesture_scores) - np.mean(touchpad_scores)
    pooled_std = np.sqrt(
        (np.std(gesture_scores) ** 2 + np.std(touchpad_scores) ** 2) / 2
    )
    cohens_d = mean_diff / pooled_std if pooled_std != 0 else 0
    print(f"  Cohen's d: {cohens_d:.4f}")

    # Dimension-by-dimension comparison
    print("\n--- Dimension-by-Dimension Comparison ---")
    dimension_names = [
        "mental-demand",
        "physical-demand",
        "temporal-demand",
        "performance",
        "effort",
        "frustration",
    ]

    for dim_name in dimension_names:
        gesture_col = f"gesture-{dim_name}"
        touchpad_col = f"touchpad-{dim_name}"

        gesture_mean = df[gesture_col].mean()
        touchpad_mean = df[touchpad_col].mean()

        t_stat, p_value = stats.ttest_rel(df[gesture_col], df[touchpad_col])

        print(f"\n{dim_name.replace('-', ' ').title()}:")
        print(f"  Gesture: {gesture_mean:.2f}, Touchpad: {touchpad_mean:.2f}")
        print(f"  Difference: {gesture_mean - touchpad_mean:+.2f}")
        print(f"  p-value: {p_value:.4f} {'*' if p_value < 0.05 else ''}")

    return df


def analyze_preferences(df):
    """Analyze user preferences for different tasks"""
    print("\n" + "=" * 60)
    print("USER PREFERENCE ANALYSIS")
    print("=" * 60)

    tasks = [
        "menu-selection-preference",
        "dragdrop-preference",
        "keyboard-input-preference",
    ]

    for task in tasks:
        print(f"\n--- {task.replace('-preference', '').replace('-', ' ').title()} ---")

        # Count preferences
        preference_counts = df[task].value_counts()
        total = len(df)

        for pref, count in preference_counts.items():
            percentage = (count / total) * 100
            print(f"  {pref}: {count}/{total} ({percentage:.1f}%)")

        # Chi-square test (if we expect 50-50 split)
        if len(preference_counts) == 2:
            gesture_count = preference_counts.get("Gesture control", 0)
            touchpad_count = preference_counts.get("Touchpad", 0)

            chi2, p_value = stats.chisquare([gesture_count, touchpad_count])
            print(f"  Chi-square test p-value: {p_value:.4f}")

            if p_value < 0.05:
                winner = (
                    "Gesture control" if gesture_count > touchpad_count else "Touchpad"
                )
                print(f"  Result: {winner} is significantly preferred (p < 0.05)")
            else:
                print(f"  Result: No significant preference (p >= 0.05)")

    # Overall preference summary
    print("\n--- Overall Preference Summary ---")
    gesture_total = sum(
        [
            (df["menu-selection-preference"] == "Gesture control").sum(),
            (df["dragdrop-preference"] == "Gesture control").sum(),
            (df["keyboard-input-preference"] == "Gesture control").sum(),
        ]
    )
    touchpad_total = sum(
        [
            (df["menu-selection-preference"] == "Touchpad").sum(),
            (df["dragdrop-preference"] == "Touchpad").sum(),
            (df["keyboard-input-preference"] == "Touchpad").sum(),
        ]
    )
    total_preferences = gesture_total + touchpad_total

    print(
        f"  Gesture control: {gesture_total}/{total_preferences} ({gesture_total/total_preferences*100:.1f}%)"
    )
    print(
        f"  Touchpad: {touchpad_total}/{total_preferences} ({touchpad_total/total_preferences*100:.1f}%)"
    )

    return df


def create_visualizations(df):
    """Create visualizations for the analysis"""
    print("\n" + "=" * 60)
    print("GENERATING VISUALIZATIONS")
    print("=" * 60)

    # 1. NASA-TLX Comparison
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle(
        "NASA-TLX Comparison: Gesture Control vs Touchpad",
        fontsize=16,
        fontweight="bold",
    )

    dimension_names = [
        "Mental Demand",
        "Physical Demand",
        "Temporal Demand",
        "Performance",
        "Effort",
        "Frustration",
    ]
    dimension_cols = [
        "mental-demand",
        "physical-demand",
        "temporal-demand",
        "performance",
        "effort",
        "frustration",
    ]

    for idx, (dim_name, dim_col) in enumerate(zip(dimension_names, dimension_cols)):
        ax = axes[idx // 3, idx % 3]

        gesture_data = df[f"gesture-{dim_col}"]
        touchpad_data = df[f"touchpad-{dim_col}"]

        x = np.arange(len(df))
        width = 0.35

        ax.bar(
            x - width / 2,
            gesture_data,
            width,
            label="Gesture",
            alpha=0.8,
            color="#3498db",
        )
        ax.bar(
            x + width / 2,
            touchpad_data,
            width,
            label="Touchpad",
            alpha=0.8,
            color="#e74c3c",
        )

        ax.set_ylabel("Score (0-20)")
        ax.set_xlabel("Participant")
        ax.set_title(dim_name)
        ax.set_xticks(x)
        ax.set_xticklabels([f"P{pid}" for pid in df["pid"]])
        ax.legend()
        ax.set_ylim(0, 20)

    plt.tight_layout()
    plt.savefig("nasa_tlx_comparison.png", dpi=300, bbox_inches="tight")
    print("  ✓ Saved: nasa_tlx_comparison.png")

    # 2. Overall NASA-TLX Scores
    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(df))
    width = 0.35

    ax.bar(
        x - width / 2,
        df["gesture_tlx_score"],
        width,
        label="Gesture Control",
        alpha=0.8,
        color="#3498db",
    )
    ax.bar(
        x + width / 2,
        df["touchpad_tlx_score"],
        width,
        label="Touchpad",
        alpha=0.8,
        color="#e74c3c",
    )

    ax.set_ylabel("Overall NASA-TLX Score (0-20)", fontsize=12)
    ax.set_xlabel("Participant", fontsize=12)
    ax.set_title("Overall NASA-TLX Workload Comparison", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([f"P{pid}" for pid in df["pid"]])
    ax.legend(fontsize=11)
    ax.set_ylim(0, 20)

    # Add mean lines
    ax.axhline(
        y=df["gesture_tlx_score"].mean(),
        color="#3498db",
        linestyle="--",
        alpha=0.5,
        label=f'Gesture Mean: {df["gesture_tlx_score"].mean():.2f}',
    )
    ax.axhline(
        y=df["touchpad_tlx_score"].mean(),
        color="#e74c3c",
        linestyle="--",
        alpha=0.5,
        label=f'Touchpad Mean: {df["touchpad_tlx_score"].mean():.2f}',
    )

    plt.tight_layout()
    plt.savefig("nasa_tlx_overall.png", dpi=300, bbox_inches="tight")
    print("  ✓ Saved: nasa_tlx_overall.png")

    # 3. SUS Scores
    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(df))
    bars = ax.bar(x, df["sus_score"], alpha=0.8, color="#2ecc71")

    # Color code based on quality
    for i, bar in enumerate(bars):
        score = df["sus_score"].iloc[i]
        if score >= 80:
            bar.set_color("#27ae60")  # Excellent - dark green
        elif score >= 68:
            bar.set_color("#2ecc71")  # Good - green
        elif score >= 50:
            bar.set_color("#f39c12")  # OK - orange
        else:
            bar.set_color("#e74c3c")  # Poor - red

    ax.set_ylabel("SUS Score (0-100)", fontsize=12)
    ax.set_xlabel("Participant", fontsize=12)
    ax.set_title("System Usability Scale (SUS) Scores", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([f"P{pid}" for pid in df["pid"]])
    ax.set_ylim(0, 100)

    # Add mean line and benchmark
    mean_sus = df["sus_score"].mean()
    ax.axhline(
        y=mean_sus,
        color="blue",
        linestyle="--",
        alpha=0.7,
        label=f"Mean: {mean_sus:.2f}",
    )
    ax.axhline(
        y=68, color="gray", linestyle=":", alpha=0.5, label="Industry Average: 68"
    )

    ax.legend(fontsize=11)

    plt.tight_layout()
    plt.savefig("sus_scores.png", dpi=300, bbox_inches="tight")
    print("  ✓ Saved: sus_scores.png")

    # 4. Preference Summary
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("User Preferences by Task Type", fontsize=16, fontweight="bold")

    tasks = [
        ("menu-selection-preference", "Menu Selection"),
        ("dragdrop-preference", "Drag & Drop"),
        ("keyboard-input-preference", "Keyboard Input"),
    ]

    colors = ["#3498db", "#e74c3c"]

    for idx, (task_col, task_name) in enumerate(tasks):
        ax = axes[idx]

        preference_counts = df[task_col].value_counts()
        labels = preference_counts.index.tolist()
        sizes = preference_counts.values.tolist()

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors[: len(labels)],
            autopct="%1.1f%%",
            startangle=90,
        )

        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")

        ax.set_title(task_name, fontsize=12, fontweight="bold")

    plt.tight_layout()
    plt.savefig("preferences_summary.png", dpi=300, bbox_inches="tight")
    print("  ✓ Saved: preferences_summary.png")

    # 5. NASA-TLX Radar Chart
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(14, 6), subplot_kw=dict(projection="polar")
    )
    fig.suptitle("NASA-TLX Radar Chart Comparison", fontsize=16, fontweight="bold")

    categories = [
        "Mental\nDemand",
        "Physical\nDemand",
        "Temporal\nDemand",
        "Performance",
        "Effort",
        "Frustration",
    ]

    dimension_cols = [
        "mental-demand",
        "physical-demand",
        "temporal-demand",
        "performance",
        "effort",
        "frustration",
    ]

    gesture_means = [df[f"gesture-{col}"].mean() for col in dimension_cols]
    touchpad_means = [df[f"touchpad-{col}"].mean() for col in dimension_cols]

    # Number of variables
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    gesture_means += gesture_means[:1]
    touchpad_means += touchpad_means[:1]
    angles += angles[:1]

    # Plot Gesture
    ax1.plot(
        angles,
        gesture_means,
        "o-",
        linewidth=2,
        color="#3498db",
        label="Gesture Control",
    )
    ax1.fill(angles, gesture_means, alpha=0.25, color="#3498db")
    ax1.set_xticks(angles[:-1])
    ax1.set_xticklabels(categories)
    ax1.set_ylim(0, 20)
    ax1.set_title("Gesture Control", fontsize=14, fontweight="bold", pad=20)
    ax1.grid(True)

    # Plot Touchpad
    ax2.plot(
        angles, touchpad_means, "o-", linewidth=2, color="#e74c3c", label="Touchpad"
    )
    ax2.fill(angles, touchpad_means, alpha=0.25, color="#e74c3c")
    ax2.set_xticks(angles[:-1])
    ax2.set_xticklabels(categories)
    ax2.set_ylim(0, 20)
    ax2.set_title("Touchpad", fontsize=14, fontweight="bold", pad=20)
    ax2.grid(True)

    plt.tight_layout()
    plt.savefig("nasa_tlx_radar.png", dpi=300, bbox_inches="tight")
    print("  ✓ Saved: nasa_tlx_radar.png")

    print("\nAll visualizations saved successfully!")


def main():
    print("=" * 60)
    print("QUALITATIVE ANALYSIS: NASA-TLX, SUS, AND PREFERENCES")
    print("=" * 60)

    df = pd.read_csv(DATASET_FOLDER + "questionnaire_filtered.csv")
    df = df[df["pid"] != 0]  # exclude pilot data
    print(f"\nLoaded data for {len(df)} participants")

    df = analyze_nasa_tlx(df)
    df = analyze_sus(df)
    df = analyze_preferences(df)

    create_visualizations(df)

    # Save processed data
    df.to_csv(DATASET_FOLDER + "qualitative_result/" + "result.csv", index=False)


if __name__ == "__main__":
    main()
