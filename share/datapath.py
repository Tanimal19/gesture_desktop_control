# data paths that are used across studies and modules

DC_DATASET_FOLDER = "./data_collection_study/datasets/"
DC_PARTICIPANT_FOLDER_TEMPLATE = DC_DATASET_FOLDER + "p{pid}/"
DC_RESULT_CSV = DC_DATASET_FOLDER + "result_merged.csv"
DC_MANUAL_LABEL_CSV = DC_DATASET_FOLDER + "labeled_manual.csv"  # for manual labeling
DC_AUTO_LABEL_CSV = DC_DATASET_FOLDER + "labeled_auto.csv"  # for auto labeling
DC_FINAL_LABEL_CSV = DC_DATASET_FOLDER + "labeled_final.csv"

ANNOTATOR_BASE_FOLDER = "./share/gesture_model/task_annotator/"
ANNOTATOR_MODEL_FOLDER_TEMPLATE = ANNOTATOR_BASE_FOLDER + "models/{task}/"
GTCN_BASE_FOLDER = "./share/gesture_model/gtcn/"


EVA_DATASET_FOLDER = "./evaluation_study/datasets/"
EVA_PARTICIPANT_FOLDER_TEMPLATE = EVA_DATASET_FOLDER + "p{pid}/"
