# Statistical Analysis Summary

## Overview
This analysis compares two input systems: **gesture** vs **touchpad** across three tasks: Menu Select, Drag Drop, and Keyboard Input.

## Methodology

### Statistical Tests Applied

1. **Normality Testing**: Shapiro-Wilk test (α = 0.05)
   - Used to determine if data follows normal distribution
   
2. **Comparison Tests**:
   - **Independent t-test**: Used when both groups show normal distribution
   - **Mann-Whitney U test**: Used when at least one group is non-normal (non-parametric alternative)

3. **Categorical Data**:
   - **Chi-square test**: Used for accuracy rates (correct/incorrect proportions)

4. **Effect Sizes**:
   - **Cohen's d**: For parametric tests (small: 0.2-0.5, medium: 0.5-0.8, large: >0.8)
   - **Rank-biserial correlation**: For non-parametric tests (small: 0.1-0.3, medium: 0.3-0.5, large: >0.5)

---

## Results by Task

### 1. MENU SELECT TASK

#### Accuracy (Chi-square test)
- **Gesture**: 55.00% correct rate
- **Touchpad**: 100.00% correct rate
- **Result**: χ²=9.18, p=0.0025 ✅ **SIGNIFICANT**
- **Interpretation**: Touchpad significantly more accurate than gesture

#### Efficiency (Independent t-test)
- **Gesture**: M=1.72, SD=0.35 (n=13)
- **Touchpad**: M=0.81, SD=0.35 (n=20)
- **Normality**: Both groups normal
- **Result**: t=7.20, p<0.001, Cohen's d=2.57 (large) ✅ **SIGNIFICANT**
- **Interpretation**: Gesture required significantly MORE movement to reach target (lower efficiency is better, 1.0 = perfect)

#### Complete Time (Mann-Whitney U test)
- **Gesture**: Mdn=4.47s (M=6.12, SD=3.19)
- **Touchpad**: Mdn=2.79s (M=3.46, SD=2.38)
- **Normality**: Both groups non-normal
- **Result**: U=222, p=0.0007, r=-0.71 (large) ✅ **SIGNIFICANT**
- **Interpretation**: Touchpad significantly faster than gesture

#### Moving Distance (Mann-Whitney U test)
- **Gesture**: Mdn=329.43 (M=368.55, SD=178.63)
- **Touchpad**: Mdn=146.65 (M=172.17, SD=108.62)
- **Normality**: Gesture non-normal, Touchpad normal
- **Result**: U=215, p=0.0019, r=-0.65 (large) ✅ **SIGNIFICANT**
- **Interpretation**: Gesture required significantly more cursor movement

---

### 2. DRAG DROP TASK

#### Accuracy (Chi-square test)
- **Gesture**: 70.00% correct rate
- **Touchpad**: 100.00% correct rate
- **Result**: χ²=4.90, p=0.0268 ✅ **SIGNIFICANT**
- **Interpretation**: Touchpad significantly more accurate than gesture

#### Efficiency (Mann-Whitney U test)
- **Gesture**: Mdn=1.05 (M=1.03, SD=0.12)
- **Touchpad**: Mdn=0.92 (M=0.94, SD=0.17)
- **Normality**: Touchpad non-normal
- **Result**: U=211, p=0.0136, r=-0.51 (large) ✅ **SIGNIFICANT**
- **Interpretation**: Gesture less efficient (more movement than necessary)

#### Complete Time (Mann-Whitney U test)
- **Gesture**: Mdn=5.75s (M=6.08, SD=1.93)
- **Touchpad**: Mdn=2.12s (M=2.95, SD=2.84)
- **Normality**: Touchpad non-normal
- **Result**: U=256, p=0.0001, r=-0.83 (large) ✅ **SIGNIFICANT**
- **Interpretation**: Touchpad significantly faster than gesture

#### Moving Distance (Mann-Whitney U test)
- **Gesture**: Mdn=913.67 (M=912.29, SD=216.54)
- **Touchpad**: Mdn=811.93 (M=854.55, SD=234.41)
- **Normality**: Touchpad non-normal
- **Result**: U=170, p=0.3019, r=-0.21 (small) ❌ **NOT SIGNIFICANT**
- **Interpretation**: No significant difference in total movement distance

---

### 3. KEYBOARD INPUT TASK

#### Accuracy (Independent t-test)
- **Gesture**: M=1.00, SD=0.00 (n=19)
- **Touchpad**: M=1.00, SD=0.00 (n=20)
- **Normality**: Both groups normal (but zero variance)
- **Result**: Cannot compute meaningful comparison ❌ **NOT SIGNIFICANT**
- **Interpretation**: Both systems achieved 100% accuracy (perfect word entry)

#### Efficiency (Mann-Whitney U test)
- **Gesture**: Mdn=1.53 (M=1.68, SD=0.69)
- **Touchpad**: Mdn=1.13 (M=1.15, SD=0.08)
- **Normality**: Touchpad non-normal
- **Result**: U=332.5, p=0.0003, r=-0.66 (large) ✅ **SIGNIFICANT**
- **Interpretation**: Gesture required significantly more key clicks per character (more backspaces/corrections)

#### Complete Time (Mann-Whitney U test)
- **Gesture**: Mdn=44.05s (M=50.02, SD=28.21)
- **Touchpad**: Mdn=8.31s (M=9.24, SD=2.42)
- **Normality**: Touchpad non-normal
- **Result**: U=380, p<0.001, r=-0.90 (large) ✅ **SIGNIFICANT**
- **Interpretation**: Touchpad dramatically faster than gesture

#### Moving Distance (Independent t-test)
- **Gesture**: M=7372.18, SD=3956.47 (n=20)
- **Touchpad**: M=2397.21, SD=452.33 (n=20)
- **Normality**: Both groups normal
- **Result**: t=5.59, p<0.001, Cohen's d=1.77 (large) ✅ **SIGNIFICANT**
- **Interpretation**: Gesture required significantly more cursor movement

---

## Key Findings Summary

### Overall Pattern
**Touchpad consistently outperforms gesture across nearly all metrics:**

1. **Accuracy**: Touchpad more accurate in Menu Select (100% vs 55%) and Drag Drop (100% vs 70%)
2. **Speed**: Touchpad faster in all tasks
3. **Efficiency**: Touchpad more efficient (less wasted movement/effort)
4. **Movement**: Gesture requires more cursor movement

### Significant Differences Found

| Task           | Accuracy | Efficiency | Time | Distance |
| -------------- | -------- | ---------- | ---- | -------- |
| Menu Select    | ✅        | ✅          | ✅    | ✅        |
| Drag Drop      | ✅        | ✅          | ✅    | ❌        |
| Keyboard Input | ❌*       | ✅          | ✅    | ✅        |

*Both achieved 100% accuracy

### Effect Sizes
Most significant differences showed **large effect sizes** (Cohen's d > 0.8 or |r| > 0.5), indicating substantial practical differences between systems.

### Non-significant Results
1. **Drag Drop - Moving Distance**: Similar total movement (p=0.30)
2. **Keyboard Input - Accuracy**: Both perfect (100%)

---

## Recommendations

Based on the statistical analysis:

1. **For precision tasks** (menu selection, drag-drop): Touchpad is significantly more accurate
2. **For speed**: Touchpad is 2-5x faster across all tasks
3. **For efficiency**: Touchpad requires less movement and fewer corrections
4. **Gesture system improvements needed**: Focus on accuracy and reducing wasted movement

The statistical evidence strongly suggests touchpad superiority in current implementation, with large and consistent effects across multiple independent metrics.
