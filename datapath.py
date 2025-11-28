# data paths that are used across studies and modules

DC_DATASET_FOLDER = "./data_collection_study/datasets/"
DC_PARTICIPANT_FOLDER_TEMPLATE = DC_DATASET_FOLDER + "p{pid}/"
DC_RESULT_CSV = DC_DATASET_FOLDER + "merged.csv"
DC_FULL_LABEL_CSV = DC_DATASET_FOLDER + "labeled_full.csv"  # for auto labeling
DC_P0_LABEL_CSV = DC_DATASET_FOLDER + "labeled_p0.csv"  # for manual labeling

ANNOTATOR_BASE_FOLDER = "./gesture_model/task_annotator/"
GTCN_BASE_FOLDER = "./gesture_model/gtcn/"
DISTNN_BASE_FOLDER = "./gesture_model/dist_nn/"


EVA_DATASET_FOLDER = "./evaluation_study/datasets/"
