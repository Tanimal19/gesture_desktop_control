import sys
import argparse
from PySide6.QtWidgets import QApplication
from main.controller import MainAppController
from share.utils import setup_logging


def main(log_path=None, camera_preview_disable=False):
    setup_logging(log_path)

    app = QApplication(sys.argv)
    MainAppController(camera_preview_disable)
    sys.exit(app.exec())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run gesture mouse control app")
    parser.add_argument(
        "--logpath",
        type=str,
        help="Log file full path (.log)",
    )
    parser.add_argument(
        "--nocampreview",
        action="store_true",
        help="disable camera preview window",
    )
    args = parser.parse_args()

    main(
        log_path=args.logpath,
        camera_preview_disable=args.nocampreview,
    )
