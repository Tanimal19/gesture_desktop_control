import random
from evaluation_study.src.task_widget.abstract_task_widget import AbstractTaskWidget
from evaluation_study.src.utils import calculate_distance
from evaluation_study.src.styles import CENTRAL_WIDGET_STYLE, MyColor
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QApplication,
)
from PySide6.QtGui import QMouseEvent
from share.singleton.mouse_listener import get_mouse_listener
import logging

logger = logging.getLogger(__name__)


class DragDropTaskWidget(AbstractTaskWidget):
    payload_header = [
        "target_area",
        "dropped_area",
        "error_distance",  # pixels between dropped point and target area center
        "target_distance",  # pixels between start point and target area center
        "drag_distance",  # pixels between drag start point and drop point
        "moving_distance",  # pixels of pointer moving bewteen drag start and drop
    ]
    on_completed = Signal(object)
    description = """
        Drag the dark square to the highlighted target area.
        Release the mouse button when over the target area.
    """
    AREAS = ["A", "B", "C"]

    @staticmethod
    def generate_configs(count: int) -> str:
        configs = []
        for _ in range(count):
            target_area = random.choice(DragDropTaskWidget.AREAS)
            config = {
                "target_area": target_area,
            }
            configs.append(config)

        configs_str = str(configs)
        return configs_str

    @staticmethod
    def parse_configs(configs_str: str) -> list[dict]:
        import ast

        try:
            configs = ast.literal_eval(configs_str)
            assert isinstance(configs, list)
            for config in configs:
                assert "target_area" in config
                assert config["target_area"] in DragDropTaskWidget.AREAS
            return configs
        except (ValueError, SyntaxError, AssertionError) as e:
            logger.error(f"Failed to parse configs: {e}")
            return []

    @staticmethod
    def compute_correctness(payload: dict) -> bool:
        return payload["dropped_area"] == payload["target_area"]

    def get_instructions(self) -> str:
        return f"Drag the black square to area [{self.target_area}]\n"

    def custom_init(self, config: dict):
        self.setFixedSize(CENTRAL_WIDGET_STYLE.width, CENTRAL_WIDGET_STYLE.height)

        self.target_area = config["target_area"]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(40)

        # Create three drop areas
        self.drop_areas: list[DropArea] = []
        for i, label in enumerate(DragDropTaskWidget.AREAS):
            is_target = label == self.target_area
            area = DropArea(label, is_target, self)
            self.drop_areas.append(area)
            layout.addWidget(area, alignment=Qt.AlignmentFlag.AlignRight)

            if is_target:
                self.target_area_widget = area

        # Create draggable square
        self.draggable_square = DraggableSquare(self)
        self.draggable_square.move(
            50, CENTRAL_WIDGET_STYLE.height // 2 - DraggableSquare.SIZE // 2
        )
        self.draggable_square.dragged.connect(self.on_drag)
        self.draggable_square.dropped.connect(self.on_drop)

    def on_drag(self):
        logger.debug("Drag started")
        listener = get_mouse_listener()
        listener.start_record_distance()

    def on_drop(self, dropped_area):
        logger.debug(
            f"Dropped in area: {dropped_area.area_label if dropped_area else 'None'}"
        )

        listener = get_mouse_listener()

        target_area_pos = self.target_area_widget.geometry().center()

        error_distance = calculate_distance(
            self.draggable_square.drag_end_pos, target_area_pos
        )
        target_distance = calculate_distance(
            self.draggable_square.drag_start_pos, target_area_pos
        )
        drag_distance = calculate_distance(
            self.draggable_square.drag_start_pos, self.draggable_square.drag_end_pos
        )
        moving_distance = listener.stop_record_distance()

        payload = {
            "target_area": self.target_area,
            "dropped_area": dropped_area.area_label if dropped_area else "None",
            "error_distance": error_distance,
            "target_distance": target_distance,
            "drag_distance": drag_distance,
            "moving_distance": moving_distance,
        }

        self.on_completed.emit(payload)


class DropArea(QLabel):
    SIZE = 160

    def __init__(self, label: str, is_target: bool, parent=None):
        super().__init__(label, parent)
        self.area_label = label

        self.setFixedSize(DropArea.SIZE, DropArea.SIZE)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if is_target:
            # Highlight target drop area
            self.setStyleSheet(
                f"""
                QLabel {{
                    background-color: {MyColor.green.to_css(0.3)};
                    border: 2px solid {MyColor.black.to_css()};
                    border-radius: 12px;
                    font-size: 24px;
                    font-weight: bold;
                    color: {MyColor.black.to_css()};
                }}
            """
            )
        else:
            self.setStyleSheet(
                f"""
                QLabel {{
                    background-color: {MyColor.gray.to_css()};
                    border: 2px solid {MyColor.black.to_css()};
                    border-radius: 12px;
                    font-size: 24px;
                    color:  {MyColor.black.to_css()};
                }}
            """
            )


class DraggableSquare(QLabel):
    dragged = Signal()
    dropped = Signal(object)
    SIZE = 80

    def __init__(self, parent=None):
        super().__init__(parent)

        self.drag_start_pos = QPoint()
        self.drag_end_pos = QPoint()
        self.is_dragging = False
        self.can_drag = True

        self.setFixedSize(DraggableSquare.SIZE, DraggableSquare.SIZE)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
        if event.button() == Qt.MouseButton.LeftButton and self.can_drag:
            self.drag_start_pos = event.position().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if not (event.buttons() & Qt.MouseButton.LeftButton) or not self.can_drag:
            return

        if (
            event.position().toPoint() - self.drag_start_pos
        ).manhattanLength() < QApplication.startDragDistance():
            return

        if not self.is_dragging:
            self.is_dragging = True
            self.dragged.emit()

        # Move the widget
        self.move(self.mapToParent(event.position().toPoint() - self.drag_start_pos))

    def mouseReleaseEvent(self, event: QMouseEvent):
        if not self.is_dragging or not self.can_drag:
            return

        self.drag_end_pos = event.position().toPoint()
        self.is_dragging = False
        self.can_drag = False  # Disable further dragging

        # Check if dropped in any target area
        parent = self.parent()
        if parent and hasattr(parent, "drop_areas"):
            from typing import cast

            widget = cast(DragDropTaskWidget, parent)
            square_center = self.geometry().center()
            for area in widget.drop_areas:
                if area.geometry().contains(square_center):
                    self.dropped.emit(area)
                    return

            # If not dropped in any area, emit empty string or handle as miss
            self.dropped.emit(None)
