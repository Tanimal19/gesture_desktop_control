import sys
import logging
from PySide6.QtWidgets import QApplication
from main.controller import MainAppController
from main.view import MainAppView
from gesture_model import AbstractGestureModel
from gesture_model.gtcn.model import GTCNModel


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


def main(model: type[AbstractGestureModel], model_path: str | None = None):
    setup_logging("app.log")

    app = QApplication(sys.argv)
    view = MainAppView()
    controller = MainAppController(
        view, model(), model.DEFAULT_PATH if model_path is None else model_path
    )
    view.set_controller(controller)
    view.show()
    view.activateWindow()
    view.setFocus()
    sys.exit(app.exec())


if __name__ == "__main__":
    main(GTCNModel)
