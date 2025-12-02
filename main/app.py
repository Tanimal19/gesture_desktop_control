import sys
import logging
import argparse
from PySide6.QtWidgets import QApplication
from main.controller import MainAppController
from main.view import MainAppView
from gesture_model.gtcn import GTCNModel
from datapath import GTCN_BASE_FOLDER


def setup_logging(filepath):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(filepath, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(module)s.%(funcName)s(): %(message)s"
    )
    file_handler.setFormatter(file_fmt)
    logger.addHandler(file_handler)


def main():
    parser = argparse.ArgumentParser(description="Run aircursor")
    parser.add_argument("--silent", action="store_true", help="Run in slient mode")
    parser.add_argument(
        "--model",
        type=str,
        help="Model name (.pth)",
    )
    args = parser.parse_args()

    if not args.silent:
        setup_logging("main/app.log")

    model_name = args.model
    if not model_name:
        model_name = "best_model_win10-weight01.pth"
    model_path = GTCN_BASE_FOLDER + "models/" + model_name

    app = QApplication(sys.argv)
    view = MainAppView()
    controller = MainAppController(view, GTCNModel(), model_path)
    view.set_controller(controller)
    view.show()
    view.activateWindow()
    view.setFocus()
    view.raise_()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
