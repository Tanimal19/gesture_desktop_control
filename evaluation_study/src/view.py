from PySide6.QtWidgets import QMainWindow, QWidget
from PySide6.QtCore import Signal
from evaluation_study.src.task_widget import TrueTaskType, AbstractTaskWidget


class EvaluationView(QMainWindow):
    on_study_start = Signal()
    on_next_trial = Signal()
    on_study_complete = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Evaluation Study")

    def init_view(self, tasks: list[tuple]):
        """tasks: list of (task_name: str, trial_num: int)"""
        # initialize the central widget, progress bar
        pass

    def show_task_view(self, ttype: TrueTaskType):
        # update central widget to show task descript for ttype and a start button
        pass

    def show_trial_view(self, task_widget: AbstractTaskWidget):
        # update central widget to task_widget, update instructions
        pass

    def show_completion_view(self):
        # update central widget to show study completion message
        pass
