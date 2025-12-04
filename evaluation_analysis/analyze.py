import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import seaborn as sns


def load_data(csv_file):
    """Load the questionnaire data from CSV file"""
    return pd.read_csv(csv_file)


def calculate_nasa_tlx_scores(df):
    """Calculate NASA TLX scores for S1 and S2"""
    # NASA TLX subscales
    tlx_subscales = [
        "mental-demand",
        "physical-demand",
        "temporal-demand",
        "performance",
        "effort",
        "frustration",
    ]

    # Calculate S1 and S2 TLX scores
    s1_scores = []
    s2_scores = []

    for subscale in tlx_subscales:
        s1_col = f"s1-{subscale}"
        s2_col = f"s2-{subscale}"

        if s1_col in df.columns and s2_col in df.columns:
            s1_scores.append(df[s1_col].values)
            s2_scores.append(df[s2_col].values)

    # Calculate overall TLX scores (average across subscales)
    s1_overall = np.mean(s1_scores, axis=0)
    s2_overall = np.mean(s2_scores, axis=0)

    return {
        "subscales": tlx_subscales,
        "s1_subscales": np.array(s1_scores),
        "s2_subscales": np.array(s2_scores),
        "s1_overall": s1_overall,
        "s2_overall": s2_overall,
    }


def analyze_nasa_tlx(df):
    """Analyze and compare NASA TLX scores between S1 and S2"""
    print("=" * 60)
    print("NASA TLX ANALYSIS")
    print("=" * 60)

    tlx_data = calculate_nasa_tlx_scores(df)

    # Statistical comparison
    print("\n1. Overall NASA TLX Comparison:")
    print(
        f"S1 Mean: {np.mean(tlx_data['s1_overall']):.2f} (±{np.std(tlx_data['s1_overall']):.2f})"
    )
    print(
        f"S2 Mean: {np.mean(tlx_data['s2_overall']):.2f} (±{np.std(tlx_data['s2_overall']):.2f})"
    )

    # Paired t-test
    t_stat, p_value = stats.ttest_rel(tlx_data["s1_overall"], tlx_data["s2_overall"])
    print(f"Paired t-test: t={t_stat:.3f}, p={p_value:.3f}")

    # Subscale analysis
    print("\n2. Subscale Comparison:")
    for i, subscale in enumerate(tlx_data["subscales"]):
        s1_mean = np.mean(tlx_data["s1_subscales"][i])
        s1_std = np.std(tlx_data["s1_subscales"][i])
        s2_mean = np.mean(tlx_data["s2_subscales"][i])
        s2_std = np.std(tlx_data["s2_subscales"][i])

        # Paired t-test for subscale
        t_stat_sub, p_value_sub = stats.ttest_rel(
            tlx_data["s1_subscales"][i], tlx_data["s2_subscales"][i]
        )

        print(
            f"{subscale.title():>18}: S1={s1_mean:5.1f}(±{s1_std:.1f}) vs S2={s2_mean:5.1f}(±{s2_std:.1f}) "
            f"| t={t_stat_sub:6.3f}, p={p_value_sub:.3f}"
        )

    return tlx_data


def analyze_preferences(df):
    """Analyze task preferences"""
    print("\n" + "=" * 60)
    print("TASK PREFERENCE ANALYSIS")
    print("=" * 60)

    preference_tasks = [
        "menu-selection-preference",
        "dragdrop-preference",
        "keyboard-input-preference",
    ]

    for task in preference_tasks:
        if task in df.columns:
            print(f"\n{task.replace('-', ' ').title()}:")
            preference_counts = df[task].value_counts()
            total_responses = len(df)

            for preference, count in preference_counts.items():
                percentage = (count / total_responses) * 100
                print(f"  {preference}: {count} participants ({percentage:.1f}%)")

    return {
        task: df[task].value_counts() for task in preference_tasks if task in df.columns
    }


def calculate_sus_score(df):
    """Calculate System Usability Scale (SUS) score"""
    print("\n" + "=" * 60)
    print("SYSTEM USABILITY SCALE (SUS) ANALYSIS")
    print("=" * 60)

    sus_columns = [f"sus-q{i}" for i in range(1, 11)]

    # Check if all SUS columns exist
    missing_cols = [col for col in sus_columns if col not in df.columns]
    if missing_cols:
        print(f"Warning: Missing SUS columns: {missing_cols}")
        return None

    sus_scores = []

    for index, row in df.iterrows():
        score = 0
        for i, col in enumerate(sus_columns):
            question_num = i + 1
            response = row[col]

            # SUS scoring: odd questions (1,3,5,7,9): subtract 1 from response
            # even questions (2,4,6,8,10): subtract response from 5
            if question_num % 2 == 1:  # Odd questions
                score += response - 1
            else:  # Even questions
                score += 5 - response

        # Multiply by 2.5 to get final SUS score (0-100 scale)
        sus_scores.append(score * 2.5)

    # Analysis
    mean_sus = np.mean(sus_scores)
    std_sus = np.std(sus_scores)
    median_sus = np.median(sus_scores)

    print(f"SUS Score Statistics:")
    print(f"  Mean: {mean_sus:.1f}")
    print(f"  Std Dev: {std_sus:.1f}")
    print(f"  Median: {median_sus:.1f}")
    print(f"  Range: {min(sus_scores):.1f} - {max(sus_scores):.1f}")

    # SUS interpretation
    if mean_sus >= 80:
        interpretation = "Excellent"
    elif mean_sus >= 70:
        interpretation = "Good"
    elif mean_sus >= 50:
        interpretation = "OK"
    else:
        interpretation = "Poor"

    print(f"  Interpretation: {interpretation}")

    # Individual SUS question analysis
    print(f"\nIndividual SUS Question Analysis:")
    for i, col in enumerate(sus_columns):
        question_num = i + 1
        mean_response = df[col].mean()
        std_response = df[col].std()
        print(f"  Q{question_num}: {mean_response:.2f} (±{std_response:.2f})")

    return {
        "scores": sus_scores,
        "mean": mean_sus,
        "std": std_sus,
        "median": median_sus,
        "interpretation": interpretation,
    }


def create_visualizations(df, tlx_data, preference_data, sus_data):
    """Create visualizations for the analysis"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    # 1. NASA TLX comparison
    ax1 = axes[0, 0]
    subscales = tlx_data["subscales"]
    x_pos = np.arange(len(subscales))

    s1_means = [np.mean(tlx_data["s1_subscales"][i]) for i in range(len(subscales))]
    s2_means = [np.mean(tlx_data["s2_subscales"][i]) for i in range(len(subscales))]
    s1_stds = [np.std(tlx_data["s1_subscales"][i]) for i in range(len(subscales))]
    s2_stds = [np.std(tlx_data["s2_subscales"][i]) for i in range(len(subscales))]

    width = 0.35
    ax1.bar(
        x_pos - width / 2,
        s1_means,
        width,
        label="S1",
        alpha=0.8,
        yerr=s1_stds,
        capsize=5,
    )
    ax1.bar(
        x_pos + width / 2,
        s2_means,
        width,
        label="S2",
        alpha=0.8,
        yerr=s2_stds,
        capsize=5,
    )

    ax1.set_xlabel("NASA TLX Subscales")
    ax1.set_ylabel("Score")
    ax1.set_title("NASA TLX Subscale Comparison")
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(
        [s.replace("-", "\n") for s in subscales], rotation=45, ha="right"
    )
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 2. Overall TLX comparison
    ax2 = axes[0, 1]
    ax2.boxplot([tlx_data["s1_overall"], tlx_data["s2_overall"]], labels=["S1", "S2"])
    ax2.set_ylabel("Overall NASA TLX Score")
    ax2.set_title("Overall NASA TLX Comparison")
    ax2.grid(True, alpha=0.3)

    # 3. Task preferences
    ax3 = axes[1, 0]
    preference_tasks = list(preference_data.keys())
    if preference_tasks:
        # Create stacked bar chart for preferences
        task_labels = [
            task.replace("-preference", "").replace("-", " ").title()
            for task in preference_tasks
        ]

        # Get unique preferences across all tasks
        all_preferences = set()
        for task_prefs in preference_data.values():
            all_preferences.update(task_prefs.index)
        all_preferences = list(all_preferences)

        # Create data matrix
        data_matrix = np.zeros((len(all_preferences), len(preference_tasks)))
        for j, task in enumerate(preference_tasks):
            for i, pref in enumerate(all_preferences):
                data_matrix[i, j] = preference_data[task].get(pref, 0)

        # Create stacked bar chart
        bottom = np.zeros(len(preference_tasks))
        # Use basic matplotlib colors
        base_colors = [
            "blue",
            "orange",
            "green",
            "red",
            "purple",
            "brown",
            "pink",
            "gray",
            "olive",
            "cyan",
        ]
        colors = [
            base_colors[i % len(base_colors)] for i in range(len(all_preferences))
        ]

        for i, pref in enumerate(all_preferences):
            ax3.bar(
                task_labels, data_matrix[i], bottom=bottom, label=pref, color=colors[i]
            )
            bottom += data_matrix[i]

        ax3.set_ylabel("Number of Participants")
        ax3.set_title("Task Preferences")
        ax3.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        ax3.set_xticklabels(task_labels, rotation=45, ha="right")

    # 4. SUS scores
    ax4 = axes[1, 1]
    if sus_data:
        ax4.hist(sus_data["scores"], bins=10, alpha=0.7, edgecolor="black")
        ax4.axvline(
            sus_data["mean"],
            color="red",
            linestyle="--",
            label=f"Mean: {sus_data['mean']:.1f}",
        )
        ax4.axvline(
            sus_data["median"],
            color="green",
            linestyle="--",
            label=f"Median: {sus_data['median']:.1f}",
        )
        ax4.set_xlabel("SUS Score")
        ax4.set_ylabel("Frequency")
        ax4.set_title("SUS Score Distribution")
        ax4.legend()
        ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        "/Users/bobch/Desktop/projects/aircursor/evaluation_analysis/analysis_results.png",
        dpi=300,
        bbox_inches="tight",
    )
    print(f"\nVisualization saved as 'analysis_results.png'")
    plt.show()


def main():
    """Main analysis function"""
    csv_file = "/Users/bobch/Desktop/projects/aircursor/evaluation_analysis/questionnaire_filtered.csv"

    # Load data
    print("Loading questionnaire data...")
    df = load_data(csv_file)
    print(f"Loaded data for {len(df)} participants")

    # Analyze NASA TLX scores
    tlx_data = analyze_nasa_tlx(df)

    # Analyze preferences
    preference_data = analyze_preferences(df)

    # Calculate SUS scores
    sus_data = calculate_sus_score(df)

    # Create visualizations
    create_visualizations(df, tlx_data, preference_data, sus_data)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total participants: {len(df)}")
    print(
        f"S1 vs S2 NASA TLX difference: {np.mean(tlx_data['s1_overall']) - np.mean(tlx_data['s2_overall']):.2f}"
    )
    if sus_data:
        print(
            f"Overall SUS score: {sus_data['mean']:.1f} ({sus_data['interpretation']})"
        )


if __name__ == "__main__":
    main()
