from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QStackedWidget,
)
from PySide6.QtCore import Qt, Signal, SignalInstance
from evaluation_study.src.task import (
    TrueTaskType,
    AbstractTaskWidget,
    TASK_WIDGET_MAP,
)
from evaluation_study.src.styles import MyColor


class EvaluationView(QMainWindow):
    on_study_start = Signal()
    on_task_start = Signal()
    on_trail_completed = Signal()

    def __init__(self, tasks: list[tuple]):
        super().__init__()
        self.setWindowTitle("Evaluation Study")
        self.setGeometry(100, 100, 1200, 700)
        # self.showFullScreen()

        main_widget = QWidget()
        main_widget.setStyleSheet(
            f"""
            QWidget {{
                background-color: {MyColor.white.to_css()};
            }}
        """
        )
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # top bar
        self.topbar = QLabel()
        self.topbar.setFixedHeight(60)
        self.topbar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.topbar.setStyleSheet(
            f"""
            QLabel {{
                background-color: {MyColor.gray.to_css()};
                border-bottom: 2px solid {MyColor.gray_dark.to_css()};
                padding: 15px 20px;
                font-size: 20px;
                font-weight: bold;
                color: {MyColor.black.to_css()};
            }}
        """
        )
        layout.addWidget(self.topbar)

        # Central content area (stacked widget for different views)
        self.central_stack = QStackedWidget()
        self.central_stack.setContentsMargins(50, 50, 50, 50)
        layout.addWidget(self.central_stack)

        self.welcome_view = CentralWidgetView(
            "Welcome to the Evaluation Study",
            "participant: 0, condition: A",
            "Start Study",
            self.on_study_start,
        )
        self.central_stack.addWidget(self.welcome_view)
        self.completion_view = CentralWidgetView(
            "Thank you for participating!",
            "Please inform the experimenter.",
        )
        self.central_stack.addWidget(self.completion_view)
        self.task_view = CentralWidgetView(
            "Task View",
            "",
            "Start Trial",
            self.on_task_start,
        )
        self.central_stack.addWidget(self.task_view)

        # Progress bar at bottom
        self.progress_bar = ProgressBarContainer(tasks)
        layout.addWidget(self.progress_bar)

        self.central_stack.setCurrentWidget(self.welcome_view)

    def show_task_view(self, ttype: TrueTaskType):
        tclass = TASK_WIDGET_MAP[ttype]
        self.task_view.title.setText(f"Task: {ttype.value}")
        self.task_view.description.setText(tclass.description)
        self.central_stack.setCurrentWidget(self.task_view)

    def show_trial_view(self, task_widget: AbstractTaskWidget):
        self.central_stack.addWidget(task_widget)
        self.central_stack.setCurrentWidget(task_widget)

    def show_completion_view(self):
        self.central_stack.setCurrentWidget(self.completion_view)

    def update_topbar(self, text: str):
        self.topbar.setText(text)

    def update_progress(self, ttype: TrueTaskType, trials_completed: int):
        self.progress_bar.update_progress(ttype, trials_completed)


class CentralWidgetView(QWidget):
    def __init__(
        self,
        title: str,
        description: str,
        button_label: str | None = None,
        on_button_click: SignalInstance | None = None,
    ):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 100, 0, 100)
        layout.setSpacing(40)

        # title
        self.title = QLabel(title)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 30px;
                font-weight: bold;
                color: {MyColor.black.to_css()};
            }}
        """
        )
        layout.addWidget(self.title)

        # Task description
        self.description = QLabel(description)
        self.description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.description.setWordWrap(True)
        self.description.setStyleSheet(
            f"""
            QLabel {{
                font-size: 20px;
                color: {MyColor.black.to_css()};
            }}
        """
        )
        layout.addWidget(self.description)

        layout.addStretch()

        # Button
        if button_label and on_button_click:
            self.button = QPushButton(button_label)
            self.button.setStyleSheet(
                f"""
            QPushButton {{
                background-color: {MyColor.gray.to_css()};
                color: {MyColor.black.to_css()};
                border: 1px solid {MyColor.gray_dark.to_css()};
                border-radius: 8px;
                padding: 6px 60px;
                font-size: 14px;
                font-weight: bold;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {MyColor.blue.to_css()};
                color: {MyColor.white.to_css()};s
            }}
        """
            )
            self.button.clicked.connect(on_button_click.emit)
            layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignCenter)


class ProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.setStyleSheet(
            f"""
            QProgressBar {{
                border-top: 2px solid {MyColor.gray_dark.to_css()};
                border-radius: 0px;
                text-align: center;
                font-size: 12px;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {MyColor.blue.to_css(0.5)};
            }}
        """
        )
        self.setTextVisible(True)


class ProgressBarContainer(QWidget):
    def __init__(self, tasks: list[tuple], parent=None):
        """
        tasks: list of (task_type: TrueTasktype, trial_num: int)
        """
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.progress_bars = {}
        for task_type, trial_num in tasks:
            self.progress_bars[task_type] = ProgressBar()
            self.progress_bars[task_type].setRange(0, trial_num)
            self.progress_bars[task_type].setValue(0)
            self.progress_bars[task_type].setFormat(f"{task_type.value}: 0/{trial_num}")
            layout.addWidget(self.progress_bars[task_type])

    def update_progress(self, task_type: TrueTaskType, trials_completed: int):
        if task_type in self.progress_bars:
            bar = self.progress_bars[task_type]
            bar.setValue(trials_completed)
            bar.setFormat(f"{task_type.value}: {trials_completed}/{bar.maximum()}")
