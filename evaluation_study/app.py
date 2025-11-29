#!/usr/bin/env python3

import sys
import argparse
from PySide6.QtWidgets import QApplication
from evaluation_study.src.controller import EvaluationController
from evaluation_study.src.view import EvaluationView


def main():
    parser = argparse.ArgumentParser(description="Run evaluation study")
    parser.add_argument(
        "--pid", type=int, default=0, help="Participant ID (default: 0)"
    )
    args = parser.parse_args()

    app = QApplication(sys.argv)

    view = EvaluationView()
    controller = EvaluationController(args.pid, view)

    view.show()
    controller.start_study()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
