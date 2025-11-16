import sys
from PySide6.QtWidgets import QApplication
from main.controller import MainAppController
from main.view import MainAppView
from gesture_model.dist_nn.model import DistNN

model = DistNN()
model_path = "./gesture_model/dist_nn/model_6.pth"


app = QApplication(sys.argv)
view = MainAppView()
controller = MainAppController(view, model, model_path)
view.set_controller(controller)
view.show()
view.activateWindow()
view.setFocus()
sys.exit(app.exec())
