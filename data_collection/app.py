import sys
from data_collection.src.controller import DataCollectionController
from data_collection.src.view import DataCollectionView
from data_collection.src.recorder import DataCollectionRecorder
from data_collection.data_process.utils import DATASET_DIR
from PySide6.QtWidgets import QApplication

pid = int(input("Enter the participant ID (0-12): "))
if pid not in range(0, 13):
    sys.exit(1)

pointer_enabled = True

app = QApplication(sys.argv)
recorder = DataCollectionRecorder(DATASET_DIR, pid)
view = DataCollectionView(pointer_enabled)
controller = DataCollectionController(pid, view, recorder, pointer_enabled)
view.set_controller(controller)
view.show()
view.activateWindow()
view.setFocus()
sys.exit(app.exec())
