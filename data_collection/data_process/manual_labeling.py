import os
import pandas as pd
import matplotlib.pyplot as plt
from gesture_model.utils import split_landmark_columns
from gesture_model.share import GestureLabel
from data_collection.src.recorder import DataCollectionRecorder
from data_collection.data_process.utils import RESULT_CSV, update_label_csv
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmark


CONNECTIONS = [
    ("WRIST", "THUMB_CMC"),
    ("THUMB_CMC", "THUMB_MCP"),
    ("THUMB_MCP", "THUMB_IP"),
    ("THUMB_IP", "THUMB_TIP"),
    ("WRIST", "INDEX_FINGER_MCP"),
    ("INDEX_FINGER_MCP", "INDEX_FINGER_PIP"),
    ("INDEX_FINGER_PIP", "INDEX_FINGER_DIP"),
    ("INDEX_FINGER_DIP", "INDEX_FINGER_TIP"),
    ("WRIST", "MIDDLE_FINGER_MCP"),
    ("MIDDLE_FINGER_MCP", "MIDDLE_FINGER_PIP"),
    ("MIDDLE_FINGER_PIP", "MIDDLE_FINGER_DIP"),
    ("MIDDLE_FINGER_DIP", "MIDDLE_FINGER_TIP"),
]


df = pd.read_csv(RESULT_CSV)

participant = int(input("enter participant ID to annotate (0-12): "))
df = df[df["participant_id"] == participant].reset_index(drop=True)

df["label"] = ""  # add label column
df = split_landmark_columns(df, DataCollectionRecorder.RECORDED_LANDMARKS)


current_frame = int(input("enter frame index to start (0 - {}): ".format(len(df) - 1)))
trail_length = 10

# plot
fig, ax = plt.subplots(figsize=(7, 7))
drawn_points = []
drawn_lines = []
drawn_texts = []


def draw_frame(frame_idx):
    global drawn_points, drawn_lines, drawn_texts
    for obj in drawn_points + drawn_lines + drawn_texts:
        obj.remove()
    drawn_points = []
    drawn_lines = []
    drawn_texts = []

    # frames to render (current and up to 10 past)
    start = max(0, frame_idx - trail_length)
    frames = range(start, frame_idx + 1)

    for i in frames:
        row = df.iloc[i]

        is_current = i == frame_idx
        if is_current:
            line_color = "blue"
            point_color = "red"
            alpha = 1.0
        else:
            line_color = "#888888"
            point_color = "#444444"
            alpha = 0.3

        # draw skeleton lines
        for a, b in CONNECTIONS:
            x1, y1 = row[f"{a}_x"], row[f"{a}_y"]
            x2, y2 = row[f"{b}_x"], row[f"{b}_y"]
            line = ax.plot([x1, x2], [y1, y2], "-", color=line_color, alpha=alpha)[0]
            drawn_lines.append(line)

        # draw points
        for lm in DataCollectionRecorder.RECORDED_LANDMARKS:
            x = row[f"{lm.name}_x"]
            y = row[f"{lm.name}_y"]
            if (
                lm == HandLandmark.INDEX_FINGER_TIP
                or lm == HandLandmark.MIDDLE_FINGER_TIP
                or lm == HandLandmark.THUMB_TIP
            ):
                p = ax.plot(x, y, "o", color=point_color, alpha=alpha)[0]
            else:
                p = ax.plot(x, y, "o", color=line_color, alpha=alpha)[0]
            drawn_points.append(p)

        # only label current frame (not past frames)
        if is_current:
            for lm in ["THUMB_TIP", "INDEX_FINGER_TIP", "MIDDLE_FINGER_TIP"]:
                x, y, z = row[f"{lm}_x"], row[f"{lm}_y"], row[f"{lm}_z"]
                txt = ax.text(
                    x + 0.005,
                    y + 0.005,
                    f"{lm}\n({x:.3f}, {y:.3f}, {z:.3f})",
                    fontsize=6,
                    color="darkred",
                )
                drawn_texts.append(txt)

    row = df.iloc[frame_idx]
    ax.set_title(
        f"participant={row['participant_id']} task={row['task']}, trail={row['trail']}:\nframe {frame_idx}/{len(df)-1}, time={row['timestamp']}, label={row['label']}"
    )

    fig.canvas.draw_idle()


def on_key(event):
    global current_frame
    if event.key == "right":
        if current_frame < len(df) - 1:
            current_frame += 1
            draw_frame(current_frame)
    elif event.key == "left":
        if current_frame > 0:
            current_frame -= 1
            draw_frame(current_frame)

    elif event.key in list("1234567"):
        label = GestureLabel(int(event.key) - 1).name
        df.at[current_frame, "label"] = label
        print(f"frame {current_frame} -> '{label}'")

        # auto-advance to next frame after labeling
        if current_frame < len(df) - 1:
            current_frame += 1
            draw_frame(current_frame)


ax.set_xlim(df.filter(regex="_x$").min().min(), df.filter(regex="_x$").max().max())
ax.set_ylim(df.filter(regex="_y$").min().min(), df.filter(regex="_y$").max().max())
ax.invert_yaxis()

fig.canvas.mpl_connect("key_press_event", on_key)

draw_frame(current_frame)
plt.show()

# save annotated results
df = df[["participant_id", "timestamp", "task", "trail", "label"]]
df = df[df["label"] != ""]  # keep only labeled frames
update_label_csv(df)
