import random
import time
from typing import List, Optional
from evaluation_study.src.config import (
    TrueTaskType,
    TaskWidget,
    MyColor,
)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QApplication,
)
from PySide6.QtGui import QFont, QMouseEvent
from share.singleton.mouse_listener import get_mouse_listener
import logging

logger = logging.getLogger(__name__)


class DragDropTaskWidget(TaskWidget):
    ttype = TrueTaskType.DragDrop
    payload_header = [
        "num_objects",
        "target_arrangement",
        "initial_arrangement",
        "final_arrangement",
        "is_correct",
        "completion_time",
        "total_distance",
        "num_moves",
    ]
    on_completed = Signal(object)

    @staticmethod
    def generate_configs(count: int) -> list[dict]:
        configs = []
        object_sets = [
            ["A", "B", "C"],
            ["X", "Y", "Z"],
            ["1", "2", "3"],
            ["P", "Q", "R", "S"],
            ["M", "N", "O", "P", "Q"],
        ]

        for _ in range(count):
            objects = random.choice(object_sets)
            target_arrangement = objects.copy()
            random.shuffle(target_arrangement)

            config = {"objects": objects, "target_arrangement": target_arrangement}
            configs.append(config)
        return configs

    def check_config_valid(self, config: dict):
        assert "objects" in config and "target_arrangement" in config
        assert len(config["objects"]) == len(config["target_arrangement"])
        assert set(config["objects"]) == set(config["target_arrangement"])

    def init(self, config: dict):
        self.objects = config["objects"]
        self.target_arrangement = config["target_arrangement"]
        self.current_arrangement = self.objects.copy()
        random.shuffle(self.current_arrangement)
        self.initial_arrangement = self.current_arrangement.copy()

        self.start_time = None
        self.move_count = 0

        self.setFixedSize(800, 600)
        self.setStyleSheet(f"background-color: rgb{MyColor.white.value};")

        layout = QVBoxLayout(self)

        # Instruction
        instruction = QLabel(
            f"Arrange objects in this order: {' → '.join(self.target_arrangement)}"
        )
        instruction.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction.setStyleSheet(f"color: rgb{MyColor.black.value}; padding: 20px;")
        layout.addWidget(instruction)

        # Current arrangement display
        self.arrangement_label = QLabel(
            f"Current: {' → '.join(self.current_arrangement)}"
        )
        self.arrangement_label.setFont(QFont("Arial", 14))
        self.arrangement_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.arrangement_label.setStyleSheet(
            f"color: rgb{MyColor.black.value}; padding: 10px;"
        )
        layout.addWidget(self.arrangement_label)

        # Drag area
        self.drag_area = DragArea(self.current_arrangement, self)
        self.drag_area.arrangement_changed.connect(self.on_arrangement_changed)
        self.drag_area.drag_started.connect(self.on_drag_started)
        layout.addWidget(self.drag_area)

        # Check button
        self.check_btn = QPushButton("Submit Arrangement")
        self.check_btn.setFont(QFont("Arial", 14))
        self.check_btn.setFixedHeight(50)
        self.check_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgb{MyColor.blue.value};
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgb{MyColor.gray_dark.value};
            }}
        """
        )
        self.check_btn.clicked.connect(self.check_arrangement)
        layout.addWidget(self.check_btn)

    def start_next_trail(self):
        # Reset for new trial
        random.shuffle(self.current_arrangement)
        self.initial_arrangement = self.current_arrangement.copy()
        self.move_count = 0
        self.start_time = None

        self.arrangement_label.setText(
            f"Current: {' → '.join(self.current_arrangement)}"
        )
        self.arrangement_label.setStyleSheet(
            f"color: rgb{MyColor.black.value}; padding: 10px;"
        )

        self.drag_area.update_objects(self.current_arrangement)

    def on_drag_started(self):
        if self.start_time is None:
            self.start_time = time.time()
            listener = get_mouse_listener()
            listener.start_record_distance()

    def on_arrangement_changed(self, new_arrangement: List[str]):
        """Handle arrangement changes."""
        self.current_arrangement = new_arrangement
        self.move_count += 1
        self.arrangement_label.setText(
            f"Current: {' → '.join(self.current_arrangement)}"
        )

    def check_arrangement(self):
        """Check if the current arrangement matches the target."""
        completion_time = time.time() - self.start_time if self.start_time else 0
        listener = get_mouse_listener()
        total_distance = listener.stop_record_distance()

        is_correct = self.current_arrangement == self.target_arrangement

        payload = {
            "num_objects": len(self.objects),
            "target_arrangement": str(self.target_arrangement),
            "initial_arrangement": str(self.initial_arrangement),
            "final_arrangement": str(self.current_arrangement),
            "is_correct": is_correct,
            "completion_time": completion_time,
            "total_distance": total_distance,
            "num_moves": self.move_count,
        }

        self.on_completed.emit(payload)

        if is_correct:
            self.arrangement_label.setText("✓ Correct arrangement!")
            self.arrangement_label.setStyleSheet(
                f"color: rgb{MyColor.green.value}; font-weight: bold; padding: 10px;"
            )
        else:
            self.arrangement_label.setText("✗ Incorrect arrangement")
            self.arrangement_label.setStyleSheet(
                f"color: rgb{MyColor.red.value}; font-weight: bold; padding: 10px;"
            )


class DragArea(QWidget):
    """Drag area for the drag-and-drop task."""

    arrangement_changed = Signal(list)
    drag_started = Signal()

    def __init__(self, objects: List[str], parent=None):
        super().__init__(parent)
        self.objects = objects
        self.draggables = []
        self.setupUI()

    def setupUI(self):
        """Initialize the drag area."""
        self.setFixedHeight(300)
        self.setAcceptDrops(True)
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: rgb{MyColor.gray.value};
                border: 2px dashed rgb{MyColor.gray_dark.value};
                border-radius: 10px;
            }}
        """
        )

        # Create draggable objects
        for i, obj in enumerate(self.objects):
            draggable = DraggableObject(obj, self)
            draggable.move(100 + i * 120, 100)
            draggable.drag_started.connect(self.drag_started.emit)
            self.draggables.append(draggable)

    def update_objects(self, objects: List[str]):
        """Update the draggable objects."""
        # Clear existing draggables
        for draggable in self.draggables:
            draggable.deleteLater()
        self.draggables.clear()

        self.objects = objects
        # Create new draggable objects
        for i, obj in enumerate(self.objects):
            draggable = DraggableObject(obj, self)
            draggable.move(100 + i * 120, 100)
            draggable.drag_started.connect(self.drag_started.emit)
            self.draggables.append(draggable)

    def update_arrangement(self):
        """Update the arrangement based on object positions."""
        # Sort objects by x position
        sorted_objects = sorted(self.draggables, key=lambda d: d.x())
        new_arrangement = [d.object_text for d in sorted_objects]
        self.arrangement_changed.emit(new_arrangement)


class DraggableObject(QLabel):
    """Draggable object for the drag-and-drop task."""

    drag_started = Signal()

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.object_text = text
        self.drag_start_position = QPoint()
        self.is_dragging = False
        self.setupUI()

    def setupUI(self):
        """Initialize the draggable object."""
        self.setFixedSize(80, 80)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Arial", 20, QFont.Weight.Bold))

        colors = {
            "A": MyColor.red,
            "B": MyColor.green,
            "C": MyColor.blue,
            "X": MyColor.red,
            "Y": MyColor.green,
            "Z": MyColor.blue,
            "1": MyColor.red,
            "2": MyColor.green,
            "3": MyColor.blue,
        }
        bg_color = colors.get(self.object_text, MyColor.gray)

        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: rgb{bg_color.value};
                color: white;
                border: 2px solid rgb{MyColor.black.value};
                border-radius: 10px;
            }}
        """
        )

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for drag initiation."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.position().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for dragging."""
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        if (
            event.position().toPoint() - self.drag_start_position
        ).manhattanLength() < QApplication.startDragDistance():
            return

        if not self.is_dragging:
            self.is_dragging = True
            self.drag_started.emit()

        # Move the widget
        self.move(
            self.mapToParent(event.position().toPoint() - self.drag_start_position)
        )
        parent = self.parent()
        if parent and hasattr(parent, "update_arrangement"):
            from typing import cast

            cast(DragArea, parent).update_arrangement()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release to stop dragging."""
        self.is_dragging = False
