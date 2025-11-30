#!/usr/bin/env python3
"""
Test script for the evaluation study UI
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from evaluation_study.src.view import EvaluationView
from evaluation_study.src.task_widget import TrueTaskType, TASK_WIDGET_MAP


def test_view():
    """Test the evaluation view with sample data"""
    app = QApplication(sys.argv)

    # Create the main view
    view = EvaluationView()

    # Create sample task list
    tasks = [
        ("Menu Selection", 1),
        ("Menu Selection", 2),
        ("Drag and Drop", 1),
        ("Drag and Drop", 2),
        ("Keyboard Input", 1),
        ("Keyboard Input", 2),
    ]

    # Initialize the view with tasks
    view.init_view(tasks)

    # Set up test progression
    current_task = 0

    def progress_test():
        nonlocal current_task

        if current_task == 0:
            # Show first task type
            view.show_task_view(TrueTaskType.MenuSelect)
            current_task += 1
        elif current_task == 1:
            # Show trial view
            config = {"menu_length": 5, "target_index": 2}
            widget_class = TASK_WIDGET_MAP[TrueTaskType.MenuSelect]
            task_widget = widget_class(config, view)
            view.show_trial_view(task_widget)
            current_task += 1
        elif current_task == 2:
            # Show completion view
            view.show_completion_view()
            current_task += 1
        else:
            QTimer.singleShot(2000, app.quit)

    # Connect signals for testing
    view.on_study_start.connect(progress_test)
    view.on_next_trial.connect(progress_test)

    # Auto-progress for demonstration
    QTimer.singleShot(1000, progress_test)

    view.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(test_view())
