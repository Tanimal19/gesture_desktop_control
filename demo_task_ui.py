#!/usr/bin/env python3
"""
Demo script showing how to use the task UI components.
Run this script to see all three task UIs in action.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QTabWidget, QMainWindow
from evluation_study.src.task_ui import (
    MenuNavigationUI,
    DragDropUI,
    KeyboardInputUI,
    create_task_ui,
)


def main():
    """Main function to run the demo."""
    app = QApplication(sys.argv)

    # Create main window with tabs
    window = QMainWindow()
    window.setWindowTitle("Study Task UI Demo")
    window.setGeometry(100, 100, 900, 700)

    # Create tab widget
    tabs = QTabWidget()
    window.setCentralWidget(tabs)

    # Task 1: Menu Navigation
    print("Creating Menu Navigation task...")
    menu_task = MenuNavigationUI(
        target_item="Tools",
        menu_items=["File", "Edit", "View", "Insert", "Format", "Tools", "Help"],
    )
    menu_task.item_selected.connect(
        lambda item: print(f"✓ Menu Navigation: Selected '{item}'")
    )
    tabs.addTab(menu_task, "1. Menu Navigation")

    # Task 2: Drag and Drop
    print("Creating Drag & Drop task...")
    dragdrop_task = DragDropUI(
        objects=["A", "B", "C"], target_arrangement=["C", "A", "B"]
    )
    dragdrop_task.arrangement_completed.connect(
        lambda arrangement: print(f"✓ Drag & Drop: Final arrangement {arrangement}")
    )
    tabs.addTab(dragdrop_task, "2. Drag & Drop")

    # Task 3: Keyboard Input
    print("Creating Keyboard Input task...")
    keyboard_task = KeyboardInputUI(target_text="HELLO WORLD")
    keyboard_task.text_completed.connect(
        lambda text: print(f"✓ Keyboard Input: Completed text '{text}'")
    )
    tabs.addTab(keyboard_task, "3. Keyboard Input")

    # Alternative way using the factory function
    print("\nYou can also create tasks using the factory function:")
    print("menu_ui = create_task_ui('menu_navigation', target_item='Edit')")
    print(
        "dragdrop_ui = create_task_ui('drag_drop', objects=['A', 'B', 'C'], target_arrangement=['C', 'A', 'B'])"
    )
    print("keyboard_ui = create_task_ui('keyboard_input', target_text='Test123')")

    # Show window
    window.show()
    print("\\nDemo window opened! Try the different tasks in the tabs.")
    print("Task instructions:")
    print(
        "1. Menu Navigation: Right-click in the area to open menu, select target item"
    )
    print("2. Drag & Drop: Drag the colored objects to match the target arrangement")
    print("3. Keyboard Input: Click the virtual keys to type the target text")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
