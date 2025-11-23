import sys
from PySide6.QtWidgets import QApplication
from main.controller import MainAppController
from main.view import MainAppView
from gesture_model.graph_tcn.model import GTCNModel
from gesture_model.dist_nn.model import DistNN
from config import GTCN_BASE_FOLDER, DISTNN_BASE_FOLDER

model = DistNN()
model_path = DISTNN_BASE_FOLDER + "model_weighted.pth"


app = QApplication(sys.argv)
view = MainAppView()
controller = MainAppController(view, model, model_path)
view.set_controller(controller)
view.show()
view.activateWindow()
view.setFocus()
sys.exit(app.exec())
