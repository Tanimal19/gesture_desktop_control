import sys
import argparse
from PySide6.QtWidgets import QApplication
from main.controller import MainAppController
from share.datapath import GTCN_BASE_FOLDER
from share.utils import setup_logging
from share.gesture_model.gtcn import GTCNModel


def main(
    log_path=None, model_path=None, rule_base_enable=False, camera_preview_disable=False
):
    setup_logging(log_path)

    if model_path is None:
        model_path = f"{GTCN_BASE_FOLDER}models/best_model_win10-weight01-manual.pth"

    app = QApplication(sys.argv)
    MainAppController(GTCNModel, model_path, rule_base_enable, camera_preview_disable)
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
    parser.add_argument(
        "--rulebase",
        action="store_true",
        help="use rule-based gesture model",
    )
    parser.add_argument(
        "--nocampreview",
        action="store_true",
        help="disable camera preview window",
    )
    args = parser.parse_args()

    main(
        log_path=args.logpath,
        model_path=args.modelpath,
        rule_base_enable=args.rulebase,
        camera_preview_disable=args.nocampreview,
    )
