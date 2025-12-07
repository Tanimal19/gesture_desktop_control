import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
from share import DATASET_FOLDER, QUANTITATIVE_RESULT_FOLDER, print_divider
import Levenshtein


class MenuSelect:
    @staticmethod
    def calculate_accuracy(group_df):
        total_counts = len(group_df)
        correct_counts = 0
        wrong_counts = 0
        fail_counts = 0

        for _, row in group_df.iterrows():
            if pd.isna(row["MenuSelect-selected_index"]):
                fail_counts += 1
            else:
                if row["MenuSelect-selected_index"] == row["MenuSelect-target_index"]:
                    correct_counts += 1
                else:
                    wrong_counts += 1

        correct_rate = correct_counts / total_counts
        wrong_rate = wrong_counts / total_counts
        failed_rate = fail_counts / total_counts
        return total_counts, correct_rate, wrong_rate, failed_rate

    @staticmethod
    def calculate_efficiency(group_df):
        group_df = group_df.dropna(subset=["MenuSelect-selected_index"])

        efficiency_list = []
        for _, row in group_df.iterrows():
            efficiency_list.append(
                row["MenuSelect-moving_distance"] / row["MenuSelect-target_distance"]
            )

        return efficiency_list

    @staticmethod
    def calculate_metrics(df):
        df = df[df["task_type"] == "MenuSelect"].copy()

        result = {}
        system_group = df.groupby("system")
        for system, group in system_group:
            accuracy_n, correct_rate, wrong_rate, failed_rate = (
                MenuSelect.calculate_accuracy(group)
            )
            efficiency_list = MenuSelect.calculate_efficiency(group)
            result[system] = {
                "accuracy_n": accuracy_n,
                "correct_rate": correct_rate,
                "wrong_rate": wrong_rate,
                "failed_rate": failed_rate,
                "efficiency_list": efficiency_list,
                "complete_time_list": group.dropna(
                    subset=["MenuSelect-selected_index"]
                )["complete_time"].tolist(),
                "moving_distance_list": group.dropna(
                    subset=["MenuSelect-selected_index"]
                )["MenuSelect-moving_distance"].tolist(),
            }

        return result


class DragDrop:
    @staticmethod
    def calculate_accuracy(group_df):
        total_counts = len(group_df)
        correct_counts = 0
        wrong_counts = 0
        fail_counts = 0

        for _, row in group_df.iterrows():
            if pd.isna(row["DragDrop-dropped_area"]):
                fail_counts += 1
            else:
                if row["DragDrop-dropped_area"] == row["DragDrop-target_area"]:
                    correct_counts += 1
                else:
                    wrong_counts += 1

        correct_rate = correct_counts / total_counts
        wrong_rate = wrong_counts / total_counts
        failed_rate = fail_counts / total_counts
        return total_counts, correct_rate, wrong_rate, failed_rate

    @staticmethod
    def calculate_efficiency(group_df):
        group_df = group_df.dropna(subset=["DragDrop-dropped_area"])

        efficiency_list = []
        for _, row in group_df.iterrows():
            efficiency_list.append(
                row["DragDrop-moving_distance"] / row["DragDrop-target_distance"]
            )

        return efficiency_list

    @staticmethod
    def calculate_metrics(df):
        df = df[df["task_type"] == "DragDrop"].copy()

        result = {}
        system_group = df.groupby("system")
        for system, group in system_group:
            accuracy_n, correct_rate, wrong_rate, failed_rate = (
                DragDrop.calculate_accuracy(group)
            )
            efficiency_list = DragDrop.calculate_efficiency(group)
            result[system] = {
                "accuracy_n": accuracy_n,
                "correct_rate": correct_rate,
                "wrong_rate": wrong_rate,
                "failed_rate": failed_rate,
                "efficiency_list": efficiency_list,
                "complete_time_list": group.dropna(subset=["DragDrop-dropped_area"])[
                    "complete_time"
                ].tolist(),
                "moving_distance_list": group.dropna(subset=["DragDrop-dropped_area"])[
                    "DragDrop-moving_distance"
                ].tolist(),
            }

        return result


class KeyboardInput:
    @staticmethod
    def calculate_accuracy(group_df):
        accuracy_list = []
        for _, row in group_df.iterrows():
            target_word = row["KeyboardInput-target_word"]
            entered_word = row["KeyboardInput-entered_word"]

            if pd.isna(entered_word):
                accuracy_list.append(np.nan)
                continue

            lev_distance = Levenshtein.distance(target_word, entered_word)
            accuracy_list.append(1 - (lev_distance / len(target_word)))

        return accuracy_list

    @staticmethod
    def calculate_efficiency(group_df):
        efficiency_list = []
        for _, row in group_df.iterrows():
            efficiency_list.append(
                row["KeyboardInput-num_key_clicks"]
                / len(row["KeyboardInput-target_word"])
            )

        return efficiency_list

    @staticmethod
    @staticmethod
    def calculate_metrics(df):
        df = df[df["task_type"] == "KeyboardInput"].copy()

        result = {}
        system_group = df.groupby("system")
        for system, group in system_group:
            accuracy_list = KeyboardInput.calculate_accuracy(group)
            efficiency_list = KeyboardInput.calculate_efficiency(group)
            result[system] = {
                "accuracy_list": accuracy_list,
                "efficiency_list": efficiency_list,
                "complete_time_list": group["complete_time"].tolist(),
                "moving_distance_list": group["KeyboardInput-moving_distance"].tolist(),
            }

        return result


def load_and_compute_metrics():
    df = pd.read_csv(QUANTITATIVE_RESULT_FOLDER + "raw.csv")

    menu_select_metrics = MenuSelect.calculate_metrics(df)
    drag_drop_metrics = DragDrop.calculate_metrics(df)
    keyboard_input_metrics = KeyboardInput.calculate_metrics(df)

    return menu_select_metrics, drag_drop_metrics, keyboard_input_metrics


def test_normality(data, system_name, metric_name, alpha=0.05):
    """
    Test normality using Shapiro-Wilk test.
    Returns: (is_normal, statistic, p_value)
    """
    if len(data) < 3:
        return None, None, None

    stat, p_value = stats.shapiro(data)
    is_normal = p_value > alpha
    return is_normal, stat, p_value


def compare_two_systems(system1_data, system2_data, metric_name, alpha=0.05):
    """
    Compare two systems using appropriate statistical test.
    First tests normality, then applies either:
    - Independent t-test (if both normal)
    - Mann-Whitney U test (if either non-normal)

    Returns a dictionary with test results.
    """
    result = {
        "metric": metric_name,
        "system1_n": len(system1_data),
        "system2_n": len(system2_data),
        "system1_mean": np.mean(system1_data),
        "system2_mean": np.mean(system2_data),
        "system1_std": np.std(system1_data, ddof=1),
        "system2_std": np.std(system2_data, ddof=1),
        "system1_median": np.median(system1_data),
        "system2_median": np.median(system2_data),
    }

    # Test normality for both systems
    is_normal1, stat1, p1 = test_normality(system1_data, "system1", metric_name, alpha)
    is_normal2, stat2, p2 = test_normality(system2_data, "system2", metric_name, alpha)

    result["system1_normality"] = {
        "is_normal": is_normal1,
        "statistic": stat1,
        "p_value": p1,
    }
    result["system2_normality"] = {
        "is_normal": is_normal2,
        "statistic": stat2,
        "p_value": p2,
    }

    # Choose appropriate test
    if is_normal1 and is_normal2:
        # Both normal: use independent t-test
        test_stat, p_value = stats.ttest_ind(system1_data, system2_data)

        # Calculate Cohen's d effect size
        pooled_std = np.sqrt(
            (
                (len(system1_data) - 1) * result["system1_std"] ** 2
                + (len(system2_data) - 1) * result["system2_std"] ** 2
            )
            / (len(system1_data) + len(system2_data) - 2)
        )
        cohens_d = (result["system1_mean"] - result["system2_mean"]) / pooled_std

        result["test_used"] = "Independent t-test"
        result["test_statistic"] = test_stat
        result["p_value"] = p_value
        result["effect_size"] = cohens_d
        result["effect_size_type"] = "Cohen's d"
    else:
        # At least one non-normal: use Mann-Whitney U test
        test_stat, p_value = stats.mannwhitneyu(
            system1_data, system2_data, alternative="two-sided"
        )

        # Calculate rank-biserial correlation as effect size
        n1, n2 = len(system1_data), len(system2_data)
        rank_biserial = 1 - (2 * test_stat) / (n1 * n2)

        result["test_used"] = "Mann-Whitney U test"
        result["test_statistic"] = test_stat
        result["p_value"] = p_value
        result["effect_size"] = rank_biserial
        result["effect_size_type"] = "Rank-biserial correlation"

    result["is_significant"] = p_value < alpha

    return result


def interpret_effect_size(effect_size, effect_type):
    """Interpret effect size magnitude."""
    abs_effect = abs(effect_size)

    if effect_type == "Cohen's d":
        if abs_effect < 0.2:
            return "negligible"
        elif abs_effect < 0.5:
            return "small"
        elif abs_effect < 0.8:
            return "medium"
        else:
            return "large"
    elif effect_type == "Rank-biserial correlation":
        if abs_effect < 0.1:
            return "negligible"
        elif abs_effect < 0.3:
            return "small"
        elif abs_effect < 0.5:
            return "medium"
        else:
            return "large"
    else:
        return "unknown"


def analyze_metrics_statistically(
    menu_select_metrics, drag_drop_metrics, keyboard_input_metrics
):
    """
    Perform comprehensive statistical analysis on all metrics.
    """
    print_divider("STATISTICAL ANALYSIS RESULTS")

    results = {}

    # Assume two systems: gesture and touchpad
    systems = list(menu_select_metrics.keys())
    if len(systems) != 2:
        print(f"Warning: Expected 2 systems, found {len(systems)}: {systems}")
        return results

    system1, system2 = systems[0], systems[1]
    print(f"\nComparing System 1: {system1} vs System 2: {system2}\n")

    # ===== MENU SELECT =====
    print_divider("MENU SELECT TASK")
    results["menu_select"] = {}

    # Accuracy rates (using Chi-square test for proportions)
    print("\n--- Accuracy (Categorical) ---")
    gesture_correct = int(
        menu_select_metrics[system1]["correct_rate"]
        * menu_select_metrics[system1]["accuracy_n"]
    )
    touchpad_correct = int(
        menu_select_metrics[system2]["correct_rate"]
        * menu_select_metrics[system2]["accuracy_n"]
    )
    gesture_total = menu_select_metrics[system1]["accuracy_n"]
    touchpad_total = menu_select_metrics[system2]["accuracy_n"]

    contingency_table = np.array(
        [
            [gesture_correct, gesture_total - gesture_correct],
            [touchpad_correct, touchpad_total - touchpad_correct],
        ]
    )
    chi2, p_chi, dof, expected = stats.chi2_contingency(contingency_table)

    print(
        f"Correct Rate - {system1}: {menu_select_metrics[system1]['correct_rate']:.2%}, {system2}: {menu_select_metrics[system2]['correct_rate']:.2%}"
    )
    print(
        f"Chi-square test: χ²={chi2:.4f}, p={p_chi:.4f}, {'significant' if p_chi < 0.05 else 'not significant'}"
    )

    results["menu_select"]["accuracy"] = {
        "test": "Chi-square test",
        "chi2": chi2,
        "p_value": p_chi,
        "is_significant": p_chi < 0.05,
    }

    # Efficiency
    print("\n--- Efficiency ---")
    eff_result = compare_two_systems(
        menu_select_metrics[system1]["efficiency_list"],
        menu_select_metrics[system2]["efficiency_list"],
        "Menu Select Efficiency",
    )
    print_comparison_result(eff_result, system1, system2)
    results["menu_select"]["efficiency"] = eff_result

    # Complete time
    print("\n--- Complete Time ---")
    time_result = compare_two_systems(
        menu_select_metrics[system1]["complete_time_list"],
        menu_select_metrics[system2]["complete_time_list"],
        "Menu Select Complete Time",
    )
    print_comparison_result(time_result, system1, system2)
    results["menu_select"]["complete_time"] = time_result

    # Moving distance
    print("\n--- Moving Distance ---")
    dist_result = compare_two_systems(
        menu_select_metrics[system1]["moving_distance_list"],
        menu_select_metrics[system2]["moving_distance_list"],
        "Menu Select Moving Distance",
    )
    print_comparison_result(dist_result, system1, system2)
    results["menu_select"]["moving_distance"] = dist_result

    # ===== DRAG DROP =====
    print_divider("DRAG DROP TASK")
    results["drag_drop"] = {}

    # Accuracy rates
    print("\n--- Accuracy (Categorical) ---")
    gesture_correct = int(
        drag_drop_metrics[system1]["correct_rate"]
        * drag_drop_metrics[system1]["accuracy_n"]
    )
    touchpad_correct = int(
        drag_drop_metrics[system2]["correct_rate"]
        * drag_drop_metrics[system2]["accuracy_n"]
    )
    gesture_total = drag_drop_metrics[system1]["accuracy_n"]
    touchpad_total = drag_drop_metrics[system2]["accuracy_n"]

    contingency_table = np.array(
        [
            [gesture_correct, gesture_total - gesture_correct],
            [touchpad_correct, touchpad_total - touchpad_correct],
        ]
    )
    chi2, p_chi, dof, expected = stats.chi2_contingency(contingency_table)

    print(
        f"Correct Rate - {system1}: {drag_drop_metrics[system1]['correct_rate']:.2%}, {system2}: {drag_drop_metrics[system2]['correct_rate']:.2%}"
    )
    print(
        f"Chi-square test: χ²={chi2:.4f}, p={p_chi:.4f}, {'significant' if p_chi < 0.05 else 'not significant'}"
    )

    results["drag_drop"]["accuracy"] = {
        "test": "Chi-square test",
        "chi2": chi2,
        "p_value": p_chi,
        "is_significant": p_chi < 0.05,
    }

    # Efficiency
    print("\n--- Efficiency ---")
    eff_result = compare_two_systems(
        drag_drop_metrics[system1]["efficiency_list"],
        drag_drop_metrics[system2]["efficiency_list"],
        "Drag Drop Efficiency",
    )
    print_comparison_result(eff_result, system1, system2)
    results["drag_drop"]["efficiency"] = eff_result

    # Complete time
    print("\n--- Complete Time ---")
    time_result = compare_two_systems(
        drag_drop_metrics[system1]["complete_time_list"],
        drag_drop_metrics[system2]["complete_time_list"],
        "Drag Drop Complete Time",
    )
    print_comparison_result(time_result, system1, system2)
    results["drag_drop"]["complete_time"] = time_result

    # Moving distance
    print("\n--- Moving Distance ---")
    dist_result = compare_two_systems(
        drag_drop_metrics[system1]["moving_distance_list"],
        drag_drop_metrics[system2]["moving_distance_list"],
        "Drag Drop Moving Distance",
    )
    print_comparison_result(dist_result, system1, system2)
    results["drag_drop"]["moving_distance"] = dist_result

    # ===== KEYBOARD INPUT =====
    print_divider("KEYBOARD INPUT TASK")
    results["keyboard_input"] = {}

    # Accuracy
    print("\n--- Accuracy ---")
    acc_result = compare_two_systems(
        [
            x
            for x in keyboard_input_metrics[system1]["accuracy_list"]
            if not np.isnan(x)
        ],
        [
            x
            for x in keyboard_input_metrics[system2]["accuracy_list"]
            if not np.isnan(x)
        ],
        "Keyboard Input Accuracy",
    )
    print_comparison_result(acc_result, system1, system2)
    results["keyboard_input"]["accuracy"] = acc_result

    # Efficiency
    print("\n--- Efficiency ---")
    eff_result = compare_two_systems(
        keyboard_input_metrics[system1]["efficiency_list"],
        keyboard_input_metrics[system2]["efficiency_list"],
        "Keyboard Input Efficiency",
    )
    print_comparison_result(eff_result, system1, system2)
    results["keyboard_input"]["efficiency"] = eff_result

    # Complete time
    print("\n--- Complete Time ---")
    time_result = compare_two_systems(
        keyboard_input_metrics[system1]["complete_time_list"],
        keyboard_input_metrics[system2]["complete_time_list"],
        "Keyboard Input Complete Time",
    )
    print_comparison_result(time_result, system1, system2)
    results["keyboard_input"]["complete_time"] = time_result

    # Moving distance
    print("\n--- Moving Distance ---")
    dist_result = compare_two_systems(
        keyboard_input_metrics[system1]["moving_distance_list"],
        keyboard_input_metrics[system2]["moving_distance_list"],
        "Keyboard Input Moving Distance",
    )
    print_comparison_result(dist_result, system1, system2)
    results["keyboard_input"]["moving_distance"] = dist_result

    return results


def print_comparison_result(result, system1_name, system2_name):
    """Pretty print comparison result."""
    print(f"Normality Test:")
    print(
        f"  {system1_name}: {'Normal' if result['system1_normality']['is_normal'] else 'Not Normal'} "
        f"(W={result['system1_normality']['statistic']:.4f}, p={result['system1_normality']['p_value']:.4f})"
    )
    print(
        f"  {system2_name}: {'Normal' if result['system2_normality']['is_normal'] else 'Not Normal'} "
        f"(W={result['system2_normality']['statistic']:.4f}, p={result['system2_normality']['p_value']:.4f})"
    )

    print(f"\nDescriptive Statistics:")
    print(
        f"  {system1_name}: M={result['system1_mean']:.4f}, SD={result['system1_std']:.4f}, "
        f"Mdn={result['system1_median']:.4f}, n={result['system1_n']}"
    )
    print(
        f"  {system2_name}: M={result['system2_mean']:.4f}, SD={result['system2_std']:.4f}, "
        f"Mdn={result['system2_median']:.4f}, n={result['system2_n']}"
    )

    print(f"\nComparison Test ({result['test_used']}):")
    print(f"  Statistic={result['test_statistic']:.4f}, p={result['p_value']:.4f}")
    print(
        f"  Result: {'SIGNIFICANT' if result['is_significant'] else 'NOT SIGNIFICANT'} difference"
    )

    effect_interpretation = interpret_effect_size(
        result["effect_size"], result["effect_size_type"]
    )
    print(
        f"  Effect size ({result['effect_size_type']}): {result['effect_size']:.4f} ({effect_interpretation})"
    )


if __name__ == "__main__":
    # Load and compute metrics
    menu_select_metrics, drag_drop_metrics, keyboard_input_metrics = (
        load_and_compute_metrics()
    )

    # Perform statistical analysis
    statistical_results = analyze_metrics_statistically(
        menu_select_metrics, drag_drop_metrics, keyboard_input_metrics
    )

    # Summary
    print_divider("SUMMARY")
    print("\nSignificant differences found in:")
    for task, metrics in statistical_results.items():
        print(f"\n{task.upper()}:")
        for metric, result in metrics.items():
            if isinstance(result, dict) and "is_significant" in result:
                if result["is_significant"]:
                    print(f"  ✓ {metric}")
                else:
                    print(f"  ✗ {metric}")
