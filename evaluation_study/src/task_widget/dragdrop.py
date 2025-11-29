import random
from evaluation_study.src.config import (
    TrueTaskType,
    TaskWidget,
    MyColor,
)
from evaluation_study.src.utils import calculate_distance
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QApplication,
)
from PySide6.QtGui import QFont, QMouseEvent
from share.singleton.mouse_listener import get_mouse_listener
import logging

logger = logging.getLogger(__name__)


class DragDropTaskWidget(TaskWidget):
    payload_header = [
        "target_area",
        "dropped_area",
        "error_distance",  # pixels between dropped point and target area center
        "target_distance",  # pixels between start point and target area center
        "drag_distance",  # pixels between drag start point and drop point
        "moving_distance",  # pixels moving bewteen drag start and drop
    ]
    on_completed = Signal(object)

    AREAS = ["A", "B", "C"]
    AREA_SIZE = 150

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

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.target_area = config["target_area"]

        self.setFixedSize(800, 600)
        self.setStyleSheet(f"background-color: rgb{MyColor.white.value};")
        layout = QVBoxLayout(self)

        # Drag area
        self.drag_area = DragArea(self)
        layout.addWidget(self.drag_area)

        # Create three drop areas
        self.drop_areas: list[DropArea] = []
        for i, label in enumerate(DragDropTaskWidget.AREAS):
            color = (
                MyColor.blue_translucent if label == self.target_area else MyColor.gray
            )
            area = DropArea(label, color, self)
            x = 50 + i * 200
            y = 50
            area.setGeometry(
                x,
                y,
                DragDropTaskWidget.AREA_SIZE,
                DragDropTaskWidget.AREA_SIZE,
            )
            self.drop_areas.append(area)

            if label == self.target_area:
                self.target_pos = (
                    x + DragDropTaskWidget.AREA_SIZE // 2,
                    y + DragDropTaskWidget.AREA_SIZE // 2,
                )

        # Create draggable square
        self.draggable_square = DraggableSquare(self)
        self.draggable_square.move(350, 250)
        self.draggable_square.drag_started.connect(self.on_drag_started)
        self.draggable_square.dropped_in_area.connect(self.on_object_dropped)

    def on_drag_started(self):
        listener = get_mouse_listener()
        listener.start_record_distance()

    def on_object_dropped(self, dropped_area):

        listener = get_mouse_listener()

        error_distance = calculate_distance(
            self.draggable_square.drag_end_pos, self.target_pos
        )
        target_distance = calculate_distance(
            self.draggable_square.drag_start_pos, self.target_pos
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


class DragArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draggable_square = None

        self.setFixedHeight(400)
        self.setAcceptDrops(True)
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: rgb{MyColor.white.value};
                border: 2px solid rgb{MyColor.gray_dark.value};
                border-radius: 10px;
            }}
        """
        )


class DropArea(QLabel):
    def __init__(self, label: str, color: MyColor, parent=None):
        super().__init__(label, parent)
        self.area_label = label

        self.setFixedSize(150, 150)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: rgb{color.value};
                color: white;
                border: 3px solid rgb{MyColor.black.value};
                border-radius: 15px;
                opacity: 0.7;
            }}
        """
        )


class DraggableSquare(QLabel):
    drag_started = Signal()
    dropped_in_area = Signal(object)

    def __init__(self, parent=None):
        super().__init__("■", parent)

        self.drag_start_pos = QPoint()
        self.drag_end_pos = QPoint()
        self.is_dragging = False
        self.can_drag = True

        self.setFixedSize(60, 60)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Arial", 40, QFont.Weight.Bold))
        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: rgb{MyColor.gray_dark.value};
                color: white;
                border: 2px solid rgb{MyColor.black.value};
                border-radius: 10px;
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
            self.drag_started.emit()

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
                    self.dropped_in_area.emit(area)
                    return

            # If not dropped in any area, emit empty string or handle as miss
            self.dropped_in_area.emit(None)
