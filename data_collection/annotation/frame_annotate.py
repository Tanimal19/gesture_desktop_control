import pandas as pd
import os
import matplotlib.pyplot as plt
from gesture_model.utils import index_to_label

csv_file = "./data_collection/datasets/p0/task_result.csv"
df = pd.read_csv(csv_file)
df["label"] = ""  # add label column


# init landmark settings
meta_cols = ["timestamp", "task", "trail", "label"]
LANDMARKS = [c for c in df.columns if c not in meta_cols]
for lm in LANDMARKS:
    df[[f"{lm}_x", f"{lm}_y", f"{lm}_z"]] = (
        df[lm].str.split("_", expand=True).astype(float)
    )

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

# display settings
current_frame = int(input("Enter frame index to start (0 - {}): ".format(len(df) - 1)))
trail_length = 20

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
        for lm in LANDMARKS:
            x = row[f"{lm}_x"]
            y = row[f"{lm}_y"]
            p = ax.plot(x, y, "o", color=point_color, alpha=alpha)[0]
            drawn_points.append(p)

        # only label current frame (not past frames)
        if is_current:
            for lm in LANDMARKS:
                x, y, z = row[f"{lm}_x"], row[f"{lm}_y"], row[f"{lm}_z"]
                txt = ax.text(
                    x + 0.005,
                    y + 0.005,
                    f"{lm}\n({x:.2f}, {y:.2f}, {z:.2f})",
                    fontsize=6,
                    color="darkred",
                )
                drawn_texts.append(txt)

    row = df.iloc[frame_idx]
    ax.set_title(
        f"task={row['task']}, trail={row['trail']}:\nframe {frame_idx}/{len(df)-1}, time={row['timestamp']}, label={row['label']}"
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

    elif event.key in list("12345678"):
        label = index_to_label(int(event.key) - 1)
        df.at[current_frame, "label"] = label
        print("frame {} labeled as '{}'".format(current_frame, label))

        # auto-advance to next frame after labeling
        if current_frame < len(df) - 1:
            current_frame += 1
            draw_frame(current_frame)


# --------------------------------------------------
# initialize plot space
# --------------------------------------------------
ax.set_xlim(df.filter(regex="_x$").min().min(), df.filter(regex="_x$").max().max())
ax.set_ylim(df.filter(regex="_y$").min().min(), df.filter(regex="_y$").max().max())
ax.invert_yaxis()
ax.set_aspect("equal")

fig.canvas.mpl_connect("key_press_event", on_key)

draw_frame(current_frame)
plt.show()

# save annotated results
output_csv = "./data_collection/datasets/p0/labels_temp.csv"
df = df[df["label"] != ""]
write_header = not os.path.exists(output_csv)
df.to_csv(output_csv, columns=meta_cols, index=False, mode="a", header=write_header)
