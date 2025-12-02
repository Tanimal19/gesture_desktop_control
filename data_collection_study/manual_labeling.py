import pandas as pd
import matplotlib.pyplot as plt
from gesture_model import GestureLabel
from data_collection_study.src.recorder import DataCollectionRecorder
from data_collection_study.post_process import update_labeled_csv
from share.utils import HandLandmark
from datapath import DC_DATASET_FOLDER, DC_MANUAL_LABEL_CSV


CONNECTIONS = [
    (HandLandmark.WRIST, HandLandmark.THUMB_CMC),
    (HandLandmark.THUMB_CMC, HandLandmark.THUMB_MCP),
    (HandLandmark.THUMB_MCP, HandLandmark.THUMB_IP),
    (HandLandmark.THUMB_IP, HandLandmark.THUMB_TIP),
    (HandLandmark.WRIST, HandLandmark.INDEX_FINGER_MCP),
    (HandLandmark.INDEX_FINGER_MCP, HandLandmark.INDEX_FINGER_PIP),
    (HandLandmark.INDEX_FINGER_PIP, HandLandmark.INDEX_FINGER_DIP),
    (HandLandmark.INDEX_FINGER_DIP, HandLandmark.INDEX_FINGER_TIP),
    (HandLandmark.WRIST, HandLandmark.MIDDLE_FINGER_MCP),
    (HandLandmark.MIDDLE_FINGER_MCP, HandLandmark.MIDDLE_FINGER_PIP),
    (HandLandmark.MIDDLE_FINGER_PIP, HandLandmark.MIDDLE_FINGER_DIP),
    (HandLandmark.MIDDLE_FINGER_DIP, HandLandmark.MIDDLE_FINGER_TIP),
]

csv_file = input("Enter original CSV path: ")
df = pd.read_csv(DC_DATASET_FOLDER + csv_file)

# split landmark columns into x, y, z
landmarks_name = [lm.name for lm in DataCollectionRecorder.RECORDED_LANDMARKS]
for lm in landmarks_name:
    df[[f"{lm}_x", f"{lm}_y", f"{lm}_z"]] = (
        df[lm].str.split("_", expand=True).astype(float)
    )
df = df.drop(columns=landmarks_name)  # drop original columns

current_frame = int(input("Select frame index (0 - {}): ".format(len(df) - 1)))
trail_length = 6

# plot
fig, ax = plt.subplots(figsize=(7, 7))
drawn_points = []
drawn_lines = []
drawn_texts = []

# frame jumping state
space_pressed = False
frame_number_buffer = ""


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
            x1, y1 = row[f"{a.name}_x"], row[f"{a.name}_y"]
            x2, y2 = row[f"{b.name}_x"], row[f"{b.name}_y"]
            line = ax.plot([x1, x2], [y1, y2], "-", color=line_color, alpha=alpha)[0]
            drawn_lines.append(line)

        # draw points
        for lm in DataCollectionRecorder.RECORDED_LANDMARKS:
            x = row[f"{lm.name}_x"]
            y = row[f"{lm.name}_y"]
            if (
                lm == HandLandmark.THUMB_TIP
                or lm == HandLandmark.INDEX_FINGER_TIP
                or lm == HandLandmark.MIDDLE_FINGER_TIP
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
    global current_frame, space_pressed, frame_number_buffer

    if event.key == " ":  # space key pressed
        space_pressed = True
        frame_number_buffer = ""
        print("Frame jump mode: Enter frame number...")
        return

    # if space was pressed and we get a number
    if space_pressed and event.key.isdigit():
        frame_number_buffer += event.key
        print(f"Frame number: {frame_number_buffer}")
        return

    # if space was pressed and we get enter/return, jump to frame
    if space_pressed and event.key == "enter":
        if frame_number_buffer:
            try:
                target_frame = int(frame_number_buffer)
                if 0 <= target_frame < len(df):
                    current_frame = target_frame
                    print(f"Jumped to frame {current_frame}")
                    draw_frame(current_frame)
                else:
                    print(f"Frame {target_frame} out of range (0-{len(df)-1})")
            except ValueError:
                print("Invalid frame number")
        space_pressed = False
        frame_number_buffer = ""
        return

    # if space was pressed and we get escape, cancel jump mode
    if space_pressed and event.key == "escape":
        space_pressed = False
        frame_number_buffer = ""
        print("Frame jump cancelled")
        return

    # reset space mode if any other key is pressed
    if space_pressed:
        space_pressed = False
        frame_number_buffer = ""

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
        print(f"> frame {current_frame} set to '{label}'")

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

df = df[df["label"] != "-1"]  # keep only labeled frames
update_labeled_csv(DC_MANUAL_LABEL_CSV, df)
