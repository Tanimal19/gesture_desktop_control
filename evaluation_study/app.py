import sys
import argparse
from PySide6.QtWidgets import QApplication
from evaluation_study.src.controller import EvaluationController
from evaluation_study.src.view import EvaluationView
from evaluation_study.src.recorder import EvaluationRecorder
from evaluation_study.task_generator import read_configs, NUM_PARTICIPANT
import logging

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Run evaluation study")
    parser.add_argument(
        "--pid", type=int, default=0, help="Participant ID (default: 0)"
    )
    parser.add_argument(
        "--condition",
        type=str,
        default="mouse",
        help="Condition type: mouse or hand (default: mouse)",
    )
    args = parser.parse_args()

    pid = args.pid
    if pid not in range(NUM_PARTICIPANT):
        logger.error(f"Invalid participant ID: {pid}")
        return
    condition = args.condition.lower()
    if condition not in ["mouse", "hand"]:
        logger.error(f"Invalid condition type: {condition}")
        return

    recorder = EvaluationRecorder(pid, condition)

    try:
        task_configs = read_configs(pid)
        logger.info(f"Loaded task configs {task_configs}")
    except Exception as e:
        logger.error(f"Failed to read task configs for pid {pid}: {e}")
        return

    app = QApplication(sys.argv)

    view = EvaluationView(
        [(task_type, trial_num) for task_type, trial_num, _ in task_configs],
        pid,
        condition,
    )
    controller = EvaluationController(view, recorder, task_configs)
    view.set_controller(controller)
    view.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
