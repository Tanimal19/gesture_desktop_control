import random
from evaluation_study.src.task.abstract_task_widget import AbstractTaskWidget
from evaluation_study.src.utils import calculate_distance
from evaluation_study.src.styles import MyColor, get_instruction_style
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QApplication,
    QLayout,
)
from PySide6.QtGui import QMouseEvent, QResizeEvent
from share.singleton.mouse_listener import get_mouse_listener
import logging

logger = logging.getLogger(__name__)


class DragDropTaskWidget(AbstractTaskWidget):
    payload_header = [
        "is_correct",
        "target_area",
        "dropped_area",
        "error_distance",  # pixels between dropped point and target area center
        "target_distance",  # pixels between start point and target area center
        "drag_distance",  # pixels between start point and drop point
        "moving_distance",  # pixels of pointer moving bewteen drag start and drop
    ]
    on_completed = Signal(object)
    description = """
    This task has 5 trials.\n
    For each trial, drag the black square to the specified target area (A, B, C, or D) and drop it there.\n
    You could only perform each trial once. The current trial ends when the square is dropped.
    """
    _areas = ["A", "B", "C", "D"]

    @staticmethod
    def generate_configs_str(count: int) -> str:
        configs = []
        prev_area = None
        for _ in range(count):
            choices = [area for area in DragDropTaskWidget._areas if area != prev_area]
            target_area = random.choice(choices)
            config = {
                "target_area": target_area,
            }
            configs.append(config)
            prev_area = target_area

        configs_str = str(configs)
        return configs_str

    @staticmethod
    def parse_configs(configs_str: str) -> list[dict]:
        import ast

        configs = ast.literal_eval(configs_str)
        assert isinstance(configs, list)
        for config in configs:
            assert "target_area" in config
            assert config["target_area"] in DragDropTaskWidget._areas
        return configs

    def setup(self, config: dict):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        left_layout = QVBoxLayout()
        instruction = f"Please drag the square to area <b>{config["target_area"]}</b>."
        instruction_label = QLabel(instruction)
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction_label.setStyleSheet(get_instruction_style())
        left_layout.addWidget(instruction_label)
        layout.addLayout(left_layout, stretch=1)

        # create drop areas
        self.drop_areas: list[DropArea] = []
        for i, label in enumerate(DragDropTaskWidget._areas):
            area = DropArea(label, self)
            self.drop_areas.append(area)
            if label == config["target_area"]:
                self.target_area_idx = i

        right_layout = QGridLayout()
        right_layout.setSpacing(40)
        right_layout.addWidget(self.drop_areas[0], 0, 0)
        right_layout.addWidget(self.drop_areas[1], 0, 1)
        right_layout.addWidget(self.drop_areas[2], 1, 0)
        right_layout.addWidget(self.drop_areas[3], 1, 1)
        layout.addLayout(right_layout)

        # create draggable square
        self.draggable_square = DraggableSquare(self)
        self.draggable_square.on_drag.connect(self.on_drag)
        self.draggable_square.on_drop.connect(self.on_drop)
        self.draggable_square.position_changed.connect(self.on_position_changed)

        self.currently_highlighted_area = None

    def resizeEvent(self, event: QResizeEvent) -> None:
        # move draggable square to left center
        height = self.height()
        self.draggable_square.move(50, height // 2 - DraggableSquare._size // 2)

    def on_drag(self):
        logger.debug("Drag started")
        listener = get_mouse_listener()
        listener.start_record_distance()

    def on_drop(self, dropped_area):
        logger.debug(
            f"Dropped in area: {dropped_area.area_label if dropped_area else 'None'}"
        )

        target_area = self.drop_areas[self.target_area_idx]
        target_pos = target_area.geometry().center()

        error_distance = calculate_distance(
            self.draggable_square.drag_end_pos, target_pos
        )
        target_distance = calculate_distance(
            self.draggable_square.drag_start_pos, target_pos
        )
        drag_distance = calculate_distance(
            self.draggable_square.drag_start_pos, self.draggable_square.drag_end_pos
        )

        listener = get_mouse_listener()
        moving_distance = listener.stop_record_distance()

        payload = {
            "is_correct": int(
                dropped_area.area_label == target_area.area_label
                if dropped_area
                else False
            ),
            "target_area": target_area.area_label,
            "dropped_area": dropped_area.area_label if dropped_area else "None",
            "error_distance": error_distance,
            "target_distance": target_distance,
            "drag_distance": drag_distance,
            "moving_distance": moving_distance,
        }

        logger.debug(f"DragDrop completed: {payload}")
        self.on_completed.emit(payload)

    def on_position_changed(self, position):
        if not self.draggable_square.is_dragging:
            return

        square_center = self.draggable_square.geometry().center()
        hovering_area = None

        # Check which area the square is hovering over
        for area in self.drop_areas:
            if area.geometry().contains(square_center):
                hovering_area = area
                break

        # Update highlights
        if self.currently_highlighted_area != hovering_area:
            # Remove highlight from previous area
            if self.currently_highlighted_area:
                self.currently_highlighted_area.set_highlighted(False)

            # Add highlight to new area
            if hovering_area:
                hovering_area.set_highlighted(True)

            self.currently_highlighted_area = hovering_area


class DropArea(QLabel):
    _size = 250

    def __init__(self, label: str, parent=None):
        super().__init__(label, parent)
        self.area_label = label
        self.is_highlighted = False

        self.setFixedSize(DropArea._size, DropArea._size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_appearance()

    def update_appearance(self):
        # STYLE: drop area appearance
        bg_color = (
            MyColor.blue.to_css(0.3) if self.is_highlighted else MyColor.gray.to_css()
        )
        border_color = (
            MyColor.blue.to_css() if self.is_highlighted else MyColor.black.to_css()
        )

        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 12px;
                font-size: 24px;
                color: {MyColor.black.to_css()};
            }}
        """
        )

    def set_highlighted(self, highlighted: bool):
        if self.is_highlighted != highlighted:
            self.is_highlighted = highlighted
            self.update_appearance()


class DraggableSquare(QLabel):
    on_drag = Signal()
    on_drop = Signal(object)
    position_changed = Signal(QPoint)
    _size = 150

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_dragging = False
        self.has_dragged = False

        # STYLE: draggable square appearance
        self.setFixedSize(DraggableSquare._size, DraggableSquare._size)
        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: {MyColor.black.to_css()};
                border-radius: 6px;
            }}
            QLabel:hover {{
                background-color: {MyColor.black.to_css(0.8)};
            }}
        """
        )

    def mousePressEvent(self, event: QMouseEvent):
        if self.has_dragged:
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.position().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if not (event.buttons() & Qt.MouseButton.LeftButton) or self.has_dragged:
            return

        if (
            event.position().toPoint() - self.drag_start_pos
        ).manhattanLength() < QApplication.startDragDistance():
            return

        if not self.is_dragging:
            self.is_dragging = True
            self.on_drag.emit()

        # Move the widget
        new_pos = self.mapToParent(event.position().toPoint() - self.drag_start_pos)
        self.move(new_pos)

        # Emit position change for hover detection
        self.position_changed.emit(self.geometry().center())

    def mouseReleaseEvent(self, event: QMouseEvent):
        if not self.is_dragging or self.has_dragged:
            return

        self.drag_end_pos = event.position().toPoint()
        self.is_dragging = False
        self.has_dragged = True

        # Check if dropped in any target area
        parent = self.parent()
        if parent and hasattr(parent, "drop_areas"):
            from typing import cast

            widget = cast(DragDropTaskWidget, parent)
            square_center = self.geometry().center()
            for area in widget.drop_areas:
                if area.geometry().contains(square_center):
                    self.on_drop.emit(area)
                    return

            # If not dropped in any area, emit empty string or handle as miss
            self.on_drop.emit(None)
