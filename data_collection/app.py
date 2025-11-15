import sys
from src.config import BASE_DIR
from data_collection.controller import DataCollectionController
from data_collection.view import DataCollectionView
from data_collection.recorder import DataCollectionRecorder
from PySide6.QtWidgets import QApplication

pid = 1  # change this
pointer_enabled = True

app = QApplication(sys.argv)
recorder = DataCollectionRecorder(BASE_DIR, pid)
view = DataCollectionView(pointer_enabled)
controller = DataCollectionController(pid, view, recorder, pointer_enabled)
view.set_controller(controller)
view.show()
view.activateWindow()
view.setFocus()
sys.exit(app.exec())
