import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

csv_file = "./data_collection/datasets/p0/task_result.csv"
df = pd.read_csv(csv_file)


# === 2. 解析 landmarks ===
meta_cols = ["timestamp", "task", "trail"]
LANDMARKS = [c for c in df.columns if c not in meta_cols]

# 拆分 x, y, z
for col in LANDMARKS:
    df[[f"{col}_x", f"{col}_y", f"{col}_z"]] = (
        df[col].str.split("_", expand=True).astype(float)
    )

for lm in LANDMARKS:
    if lm != "WRIST":
        for dim in ["x", "y", "z"]:
            df[f"{lm}_{dim}"] = df[f"{lm}_{dim}"] - df[f"WRIST_{dim}"]

for dim in ["x", "y", "z"]:
    df[f"WRIST_{dim}"] = 0.0


# === 3. 指定骨架連接關係 ===
# 參考 MediaPipe hand model 的 21 點拓撲結構
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

# === 4. 選擇某個 task 來動畫化 ===
task_name = df["task"].unique()[0]
task_df = df[df["task"] == task_name].reset_index(drop=True)

print(task_df)

# === 5. 建立 2D 動畫 ===
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_title(f"2D Hand landmarks - {task_name}")
ax.set_xlabel("X")
ax.set_ylabel("Y")

# 初始化散點與骨架線
scat = ax.scatter([], [], c="blue", s=40)
lines = [ax.plot([], [], c="gray", lw=2)[0] for _ in CONNECTIONS]
trail_id = ax.text(
    0.05, 0.95, "", transform=ax.transAxes, fontsize=12, color="red", va="top"
)

# 設定座標範圍（可依資料調整）
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.invert_yaxis()  # 適配攝影機座標系（y 向下）


def update(frame):
    row = task_df.iloc[frame]
    xs = [row[f"{col}_x"] for col in LANDMARKS]
    ys = [row[f"{col}_y"] for col in LANDMARKS]
    scat.set_offsets(list(zip(xs, ys)))

    # 更新線條
    for i, (a, b) in enumerate(CONNECTIONS):
        xline = [row[f"{a}_x"], row[f"{b}_x"]]
        yline = [row[f"{a}_y"], row[f"{b}_y"]]
        lines[i].set_data(xline, yline)

    ax.set_title(f"Frame {frame+1}/{len(task_df)} - {task_name}")
    trail_id.set_text(f"trail: {int(row['trail'] + 1)}")

    return scat, *lines, trail_id


ani = FuncAnimation(fig, update, frames=len(task_df), interval=33, blit=False)
# ani.save("right_click.mp4", writer="ffmpeg", fps=30)
plt.show()
