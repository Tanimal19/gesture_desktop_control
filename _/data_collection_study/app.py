import sys
from data_collection_study.src.controller import DataCollectionController
from data_collection_study.src.view import DataCollectionView
from data_collection_study.src.recorder import DataCollectionRecorder
from PySide6.QtWidgets import QApplication
from data_collection_study.task_generator import NUM_PARTICIPANT


pid = int(input(f"Enter the participant ID (0 for testing, 1-{NUM_PARTICIPANT-1}): "))
if pid not in range(0, NUM_PARTICIPANT):
    sys.exit(1)

pointer_enabled = True

app = QApplication(sys.argv)
recorder = DataCollectionRecorder(pid)
view = DataCollectionView(pointer_enabled)
controller = DataCollectionController(pid, view, recorder, pointer_enabled)
view.set_controller(controller)
view.show()
view.activateWindow()
view.setFocus()
sys.exit(app.exec())
