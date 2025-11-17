import sys
from PySide6.QtWidgets import QApplication
from main.controller import MainAppController
from main.view import MainAppView
from gesture_model.graph_tcn.model import GTCNModel

model = GTCNModel()
model_path = "./gesture_model/graph_tcn/model.pth"


app = QApplication(sys.argv)
view = MainAppView()
controller = MainAppController(view, model, model_path)
view.set_controller(controller)
view.show()
view.activateWindow()
view.setFocus()
sys.exit(app.exec())
