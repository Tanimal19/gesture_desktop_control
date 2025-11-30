#!/usr/bin/env python3

import sys
import argparse
from PySide6.QtWidgets import QApplication
from evaluation_study.src.controller import EvaluationController
from evaluation_study.src.view import EvaluationView
from evaluation_study.src.recorder import EvaluationRecorder
from evaluation_study.task_generator import read_configs
from datapath import EVA_DATASET_FOLDER


def main():
    parser = argparse.ArgumentParser(description="Run evaluation study")
    parser.add_argument(
        "--pid", type=int, default=0, help="Participant ID (default: 0)"
    )
    args = parser.parse_args()

    # read config
    try:
        task_configs = read_configs(args.pid)
    except Exception as e:
        return

    app = QApplication(sys.argv)

    recorder = EvaluationRecorder(args.pid)
    view = EvaluationView(
        [(task_type, trial_num) for task_type, trial_num, _ in task_configs]
    )
    controller = EvaluationController(view, recorder, task_configs)

    view.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
