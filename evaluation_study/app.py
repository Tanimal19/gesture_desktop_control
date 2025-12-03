import sys
import argparse
from PySide6.QtWidgets import QApplication
from evaluation_study.src.controller import EvaluationController
from log_util import setup_logging
import logging


def main(log_path=None, pid=0, condition="touchpad"):
    setup_logging(log_path)
    logger = logging.getLogger(__name__)

    if condition not in ["touchpad", "gesture"]:
        logger.error(f"Invalid condition type: {condition}")
        return

    app = QApplication(sys.argv)
    EvaluationController(pid, condition)
    sys.exit(app.exec())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run evaluation study")
    parser.add_argument("--pid", type=int, help="Participant id")
    parser.add_argument(
        "--condition",
        type=str,
        help="Condition: touchpad/gesture",
    )
    parser.add_argument(
        "--logpath",
        type=str,
        help="Log file full path (.log)",
    )
    args = parser.parse_args()

    main(log_path=args.logpath, pid=args.pid, condition=args.condition)
