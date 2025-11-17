import sys
from data_collection.src.controller import DataCollectionController
from data_collection.src.view import DataCollectionView
from data_collection.src.recorder import DataCollectionRecorder
from data_collection.task_generator import base_dir
from PySide6.QtWidgets import QApplication

pid = 1  # change this
pointer_enabled = True

app = QApplication(sys.argv)
recorder = DataCollectionRecorder(base_dir, pid)
view = DataCollectionView(pointer_enabled)
controller = DataCollectionController(pid, view, recorder, pointer_enabled)
view.set_controller(controller)
view.show()
view.activateWindow()
view.setFocus()
sys.exit(app.exec())
