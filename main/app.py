import sys
import argparse
from PySide6.QtWidgets import QApplication
from main.controller import MainAppController
from main.view import MainAppView
from share.datapath import GTCN_BASE_FOLDER
from share.utils import setup_logging
from share.gesture_model.gtcn import GTCNModel


def main(log_path=None, model_path=None):
    setup_logging(log_path)

    if model_path is None:
        model_path = f"{GTCN_BASE_FOLDER}/models/best_model_win10-weight01-labeled.pth"

    app = QApplication(sys.argv)
    MainAppController(GTCNModel(), model_path)
    sys.exit(app.exec())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run gesture mouse control app")
    parser.add_argument(
        "--modelpath",
        type=str,
        help="Model file full path (.pth)",
    )
    parser.add_argument(
        "--logpath",
        type=str,
        help="Log file full path (.log)",
    )
    args = parser.parse_args()

    main(log_path=args.logpath, model_path=args.modelpath)
