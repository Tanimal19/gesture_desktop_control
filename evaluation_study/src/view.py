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
from PySide6.QtGui import QFont
from evaluation_study.src.task_widget import (
    TrueTaskType,
    AbstractTaskWidget,
    TASK_WIDGET_MAP,
)
from evaluation_study.src.styles import (
    MyColor,
    MAIN_WINDOW_HEIGHT,
    MAIN_WINDOW_WIDTH,
    TITLE_FONT_SIZE,
    INSTRUCTION_FONT_SIZE,
    INSTRUCTION_PANEL_STYLE,
    CENTRAL_WIDGET_STYLE,
    PROGRESS_BAR_STYLE,
    BUTTON_STYLE,
)


class EvaluationView(QMainWindow):
    on_study_start = Signal()
    on_task_start = Signal()

    def __init__(self, tasks: list[tuple]):
        super().__init__()
        self.setWindowTitle("Evaluation Study")
        self.setFixedSize(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Instruction panel at top
        self.instruction_label = QLabel()
        self.instruction_label.setFixedHeight(INSTRUCTION_PANEL_STYLE.height)
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction_label.setStyleSheet(INSTRUCTION_PANEL_STYLE.css_style())
        layout.addWidget(self.instruction_label)

        # Central content area (stacked widget for different views)
        self.central_stack = QStackedWidget()
        self.central_stack.setFixedHeight(CENTRAL_WIDGET_STYLE.height)
        self.central_stack.setStyleSheet(CENTRAL_WIDGET_STYLE.css_style())
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
        self.central_stack.addWidget(self.welcome_view)
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
        self.instruction_label.setText("")

    def show_trial_view(self, trail_idx, task_widget: AbstractTaskWidget):
        self.central_stack.addWidget(task_widget)
        self.central_stack.setCurrentWidget(task_widget)
        self.instruction_label.setText(
            f"Trail {trail_idx}\n\n" + task_widget.get_instructions()
        )

    def show_completion_view(self):
        self.central_stack.setCurrentWidget(self.completion_view)
        self.instruction_label.setText("")

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

        self.setFixedSize(CENTRAL_WIDGET_STYLE.width, CENTRAL_WIDGET_STYLE.height)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(40)
        layout.addStretch()

        # title
        self.title = QLabel(title)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet(
            f"""
            QLabel {{
                font-size: {TITLE_FONT_SIZE}px;
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
                font-size: {INSTRUCTION_FONT_SIZE}px;
                color: {MyColor.black.to_css()};
            }}
        """
        )
        layout.addWidget(self.description)

        # Button
        if button_label and on_button_click:
            self.button = QPushButton(button_label)
            self.button.setStyleSheet(BUTTON_STYLE.css_style())
            self.button.clicked.connect(on_button_click.emit)
            layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()


class ProgressBar(QProgressBar):
    def __init__(self, width, parent=None):
        super().__init__(parent)
        self.setFixedSize(width, PROGRESS_BAR_STYLE.height)
        self.setStyleSheet(PROGRESS_BAR_STYLE.css_style())
        self.setTextVisible(True)


class ProgressBarContainer(QWidget):
    def __init__(self, tasks: list[tuple], parent=None):
        """
        tasks: list of (task_type: TrueTasktype, trial_num: int)
        """

        super().__init__(parent)
        self.setFixedHeight(PROGRESS_BAR_STYLE.height)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.progress_bars = {}
        bar_width = MAIN_WINDOW_WIDTH // len(tasks)
        for task_type, trial_num in tasks:
            self.progress_bars[task_type] = ProgressBar(bar_width)
            self.progress_bars[task_type].setRange(0, trial_num)
            self.progress_bars[task_type].setValue(0)
            self.progress_bars[task_type].setFormat(f"{task_type.value}: 0/{trial_num}")
            layout.addWidget(self.progress_bars[task_type])

    def update_progress(self, task_type: TrueTaskType, trials_completed: int):
        if task_type in self.progress_bars:
            bar = self.progress_bars[task_type]
            bar.setValue(trials_completed)
            bar.setFormat(f"{task_type.value}: {trials_completed}/{bar.maximum()}")
