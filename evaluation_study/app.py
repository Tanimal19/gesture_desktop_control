import sys
import os
import csv
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QInputDialog,
    QMessageBox,
    QProgressBar,
    QTextEdit,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from evaluation_study.src.config import TrueTaskType, MyColor
from evaluation_study.src.task_widget.menu_select import MenuSelectTaskWidget
from evaluation_study.src.task_widget.dragdrop import DragDropTaskWidget
from evaluation_study.task_generator import read_configs
from datapath import EVA_DATASET_FOLDER, EVA_PARTICIPANT_FOLDER_TEMPLATE


class TaskRunner(QMainWindow):
    """Main application window for running evaluation tasks."""

    def __init__(self):
        super().__init__()
        self.participant_id = None
        self.task_configs = []
        self.current_task_index = 0
        self.current_widget = None
        self.results = []

        # Task type to widget class mapping
        self.task_widgets = {
            TrueTaskType.MenuSelect: MenuSelectTaskWidget,
            TrueTaskType.DragDrop: DragDropTaskWidget,
        }

        self.init_ui()
        self.get_participant_info()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("AirCursor Evaluation Study")
        self.setFixedSize(900, 700)
        self.setStyleSheet(f"background-color: rgb{MyColor.white.value};")

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        self.main_layout = QVBoxLayout(central_widget)

        # Header section
        self.create_header()

        # Task area (will be replaced with actual task widgets)
        self.task_area = QWidget()
        self.task_area.setFixedSize(800, 600)
        self.main_layout.addWidget(
            self.task_area, alignment=Qt.AlignmentFlag.AlignCenter
        )

        # Control buttons
        self.create_controls()

    def create_header(self):
        """Create the header section with participant info and progress."""
        header_layout = QVBoxLayout()

        # Title
        title = QLabel("AirCursor Evaluation Study")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: rgb{MyColor.black.value}; padding: 10px;")
        header_layout.addWidget(title)

        # Participant info and progress
        info_layout = QHBoxLayout()

        self.participant_label = QLabel("Participant: Not set")
        self.participant_label.setFont(QFont("Arial", 12))

        self.progress_label = QLabel("Progress: 0/0")
        self.progress_label.setFont(QFont("Arial", 12))

        info_layout.addWidget(self.participant_label)
        info_layout.addStretch()
        info_layout.addWidget(self.progress_label)

        header_layout.addLayout(info_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        header_layout.addWidget(self.progress_bar)

        self.main_layout.addLayout(header_layout)

    def create_controls(self):
        """Create control buttons."""
        control_layout = QHBoxLayout()

        self.prev_btn = QPushButton("Previous Task")
        self.prev_btn.setFixedHeight(40)
        self.prev_btn.clicked.connect(self.previous_task)
        self.prev_btn.setEnabled(False)

        self.next_btn = QPushButton("Next Task")
        self.next_btn.setFixedHeight(40)
        self.next_btn.clicked.connect(self.next_task)
        self.next_btn.setEnabled(False)

        self.restart_btn = QPushButton("Restart Current Task")
        self.restart_btn.setFixedHeight(40)
        self.restart_btn.clicked.connect(self.restart_current_task)
        self.restart_btn.setEnabled(False)

        for btn in [self.prev_btn, self.next_btn, self.restart_btn]:
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: rgb{MyColor.blue.value};
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: rgb{MyColor.gray_dark.value};
                }}
                QPushButton:disabled {{
                    background-color: rgb{MyColor.gray.value};
                    color: rgb{MyColor.gray_dark.value};
                }}
            """
            )

        control_layout.addWidget(self.prev_btn)
        control_layout.addStretch()
        control_layout.addWidget(self.restart_btn)
        control_layout.addStretch()
        control_layout.addWidget(self.next_btn)

        self.main_layout.addLayout(control_layout)

    def get_participant_info(self):
        """Get participant ID from user input."""
        while self.participant_id is None:
            pid, ok = QInputDialog.getInt(
                self, "Participant ID", "Enter participant ID (0-7):", value=0
            )

            if ok and 0 <= pid <= 7:
                self.participant_id = pid
                self.participant_label.setText(f"Participant: {pid}")
                self.load_task_configs()
            elif ok:
                QMessageBox.warning(
                    self,
                    "Invalid Input",
                    "Please enter a participant ID between 0 and 7.",
                )
            else:
                # User cancelled, exit application
                sys.exit(0)

    def load_task_configs(self):
        """Load task configurations for the participant."""
        if self.participant_id is None:
            return

        self.task_configs = read_configs(self.participant_id)

        if not self.task_configs:
            QMessageBox.warning(
                self,
                "No Configurations",
                f"No task configurations found for participant {self.participant_id}.\n"
                "Please run task_generator.py first to generate configurations.",
            )
            self.get_participant_info()  # Ask for participant ID again
            return

        self.progress_bar.setMaximum(len(self.task_configs))
        self.update_progress()
        self.load_current_task()

    def load_current_task(self):
        """Load the current task based on current_task_index."""
        if self.current_task_index >= len(self.task_configs):
            self.show_completion_screen()
            return

        # Remove previous task widget if exists
        if self.current_widget:
            self.current_widget.setParent(None)
            self.current_widget = None

        # Get current task configuration
        task_type, trial_number, config = self.task_configs[self.current_task_index]

        # Create appropriate task widget
        widget_class = self.task_widgets[task_type]
        self.current_widget = widget_class(config, self.task_area)
        self.current_widget.on_completed.connect(self.on_task_completed)

        # Position widget in task area
        self.current_widget.move(0, 0)
        self.current_widget.show()

        # Update UI state
        self.update_progress()
        self.prev_btn.setEnabled(self.current_task_index > 0)
        self.next_btn.setEnabled(False)  # Enabled only after task completion
        self.restart_btn.setEnabled(True)

    def on_task_completed(self, payload):
        """Handle task completion."""
        # Get current task info
        task_type, trial_number, config = self.task_configs[self.current_task_index]

        # Create result record
        result = {
            "participant_id": self.participant_id,
            "task_type": task_type.name,
            "trial_number": trial_number,
            "timestamp": datetime.now().isoformat(),
            **payload,  # Add all payload data
        }

        self.results.append(result)

        # Save result immediately
        self.save_results()

        # Enable next button
        self.next_btn.setEnabled(True)

        # Show completion message
        QMessageBox.information(
            self, "Task Completed", f"Task completed! Click 'Next Task' to continue."
        )

    def save_results(self):
        """Save results to CSV file."""
        if not self.results:
            return

        # Ensure participant folder exists
        participant_folder = EVA_PARTICIPANT_FOLDER_TEMPLATE.format(
            pid=self.participant_id
        )
        os.makedirs(participant_folder, exist_ok=True)

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results_p{self.participant_id}_{timestamp}.csv"
        filepath = os.path.join(participant_folder, filename)

        # Write results to CSV
        if self.results:
            with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = list(self.results[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.results)

    def next_task(self):
        """Move to next task."""
        self.current_task_index += 1
        self.next_btn.setEnabled(False)
        self.load_current_task()

    def previous_task(self):
        """Move to previous task."""
        if self.current_task_index > 0:
            self.current_task_index -= 1
            self.next_btn.setEnabled(True)  # Can go forward again
            self.load_current_task()

    def restart_current_task(self):
        """Restart the current task."""
        # Remove the last result if it exists for this task
        if self.results and len(self.results) > self.current_task_index:
            self.results = self.results[: self.current_task_index]

        # Reload current task
        self.load_current_task()

    def update_progress(self):
        """Update progress indicators."""
        current = self.current_task_index + 1
        total = len(self.task_configs)

        self.progress_label.setText(f"Progress: {self.current_task_index}/{total}")
        self.progress_bar.setValue(self.current_task_index)

        if self.current_task_index < total:
            task_type, trial_number, _ = self.task_configs[self.current_task_index]
            self.setWindowTitle(
                f"AirCursor Study - {task_type.name} (Trial {trial_number + 1})"
            )

    def show_completion_screen(self):
        """Show completion screen when all tasks are done."""
        # Remove current widget
        if self.current_widget:
            self.current_widget.setParent(None)

        # Create completion widget
        completion_widget = QWidget(self.task_area)
        completion_widget.setFixedSize(800, 600)

        layout = QVBoxLayout(completion_widget)

        # Completion message
        message = QLabel(
            "🎉 All tasks completed!\n\nThank you for participating in the study."
        )
        message.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setStyleSheet(f"color: rgb{MyColor.green.value}; padding: 50px;")
        layout.addWidget(message)

        # Results summary
        summary = QLabel(f"Completed {len(self.results)} tasks")
        summary.setFont(QFont("Arial", 16))
        summary.setAlignment(Qt.AlignmentFlag.AlignCenter)
        summary.setStyleSheet(f"color: rgb{MyColor.black.value};")
        layout.addWidget(summary)

        # Exit button
        exit_btn = QPushButton("Exit Application")
        exit_btn.setFixedSize(200, 50)
        exit_btn.setFont(QFont("Arial", 14))
        exit_btn.clicked.connect(self.close)
        exit_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgb{MyColor.blue.value};
                color: white;
                border: none;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: rgb{MyColor.gray_dark.value};
            }}
        """
        )
        layout.addWidget(exit_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        completion_widget.move(0, 0)
        completion_widget.show()

        # Disable control buttons
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        self.restart_btn.setEnabled(False)

        self.setWindowTitle("AirCursor Study - Completed")

        # Final save
        self.save_results()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)

    window = TaskRunner()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
