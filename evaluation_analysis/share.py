DATASET_FOLDER = "./evaluation_analysis/"
QUALITATIVE_RESULT_FOLDER = DATASET_FOLDER + "qualitative_results/"
QUANTITATIVE_RESULT_FOLDER = DATASET_FOLDER + "quantitative_results/"

SYSTEM = ["gesture", "touchpad"]
TASK = ["menu-selection", "dragdrop", "keyboard-input"]

SHEET_HEADER = {
    "pid": "B",
    # NASA-TLX system 1
    "s1-mental-demand": "F",
    "s1-physical-demand": "G",
    "s1-temporal-demand": "H",
    "s1-performance": "I",
    "s1-effort": "J",
    "s1-frustration": "K",
    # NASA-TLX system 2
    "s2-mental-demand": "L",
    "s2-physical-demand": "M",
    "s2-temporal-demand": "N",
    "s2-performance": "O",
    "s2-effort": "P",
    "s2-frustration": "Q",
    # Preferences
    "menu-selection-preference": "R",
    "dragdrop-preference": "S",
    "keyboard-input-preference": "T",
    # SUS Questions
    "sus-q1": "U",
    "sus-q2": "V",
    "sus-q3": "W",
    "sus-q4": "X",
    "sus-q5": "Y",
    "sus-q6": "Z",
    "sus-q7": "AA",
    "sus-q8": "AB",
    "sus-q9": "AC",
    "sus-q10": "AD",
}

NASA_TLX_SUBSCALES = [
    "mental-demand",
    "physical-demand",
    "temporal-demand",
    "performance",
    "effort",
    "frustration",
]


COLOR = ["#FF6B6B", "#4ECDC4"]  # Gesture: red, Touchpad: teal


def print_divider(title: str):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
