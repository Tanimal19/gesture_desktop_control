from datapath import DC_FINAL_LABEL_CSV, DC_AUTO_LABEL_CSV, DC_MANUAL_LABEL_CSV
import pandas as pd


manual = pd.read_csv(DC_MANUAL_LABEL_CSV)
auto = pd.read_csv(DC_AUTO_LABEL_CSV)

# concatenate manual and auto
combined = pd.concat([manual, auto], ignore_index=True)

# remove duplicates, keep manual labels over auto labels
final = combined.drop_duplicates(
    subset=["participant_id", "timestamp", "task", "trail"], keep="first"
)

final.to_csv(DC_FINAL_LABEL_CSV, index=False)
