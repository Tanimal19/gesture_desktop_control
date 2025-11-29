import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from main.controller import MainAppController
from main.view import MainAppView
from share.logger import setup_logging
from gesture_model.gtcn.model import GTCNModel
from gesture_model.dist_nn.model import DistNN
from datapath import GTCN_BASE_FOLDER, DISTNN_BASE_FOLDER

model = GTCNModel()
model_path = GTCN_BASE_FOLDER + "models/" + "best_model_win10-weight01.pth"

setup_logging("./main/app.log")

app = QApplication(sys.argv)
view = MainAppView()
controller = MainAppController(view, model, model_path)
view.set_controller(controller)
view.show()
view.activateWindow()
view.setFocus()
sys.exit(app.exec())
