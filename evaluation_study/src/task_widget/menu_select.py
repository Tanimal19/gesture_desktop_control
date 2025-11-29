import random
from evaluation_study.src.config import (
    TrueTaskType,
    TaskWidget,
    MyColor,
)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from share.singleton.mouse_listener import get_mouse_listener
import logging

logger = logging.getLogger(__name__)


class MenuSelectTaskWidget(TaskWidget):
    ttype = TrueTaskType.MenuSelect
    payload_header = [
        "menu_length",
        "target_index",
        "selected_index",
        "error_distance",  # pixels between clicked point and target item
        "target_distance",  # pixels between start point and target item
        "moving_distance",  # pixels moving during the trial
    ]
    on_completed = Signal(object)

    @staticmethod
    def generate_configs(count: int) -> list[dict]:
        configs = []
        for _ in range(count):
            menu_length = random.randint(5, 10)
            target_index = random.randint(0, menu_length - 1)
            config = {"menu_length": menu_length, "target_index": target_index}
            configs.append(config)
        return configs

    def check_config_valid(self, config: dict):
        assert "menu_length" in config and "target_index" in config
        assert 0 <= config["target_index"] < config["menu_length"]

    def init(self, config: dict):
        self.setFixedSize(800, 600)
        self.setStyleSheet(f"background-color: {MyColor.white.value};")

        layout = QVBoxLayout(self)

        # menu trigger area
        self.trigger_area = QLabel("right-click here to open menu")
        self.trigger_area.setFixedHeight(400)
        self.trigger_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.trigger_area.setStyleSheet(
            f"""
            background-color: {MyColor.white.value};
            border: 2px dashed {MyColor.gray_dark.value};
            color: {MyColor.black.value};
            font-size: 18px;
            border-radius: 10px;
        """
        )
        layout.addWidget(self.trigger_area)

        # setup context menu
        menu_items = [f"Item {i+1}" for i in range(config["menu_length"])]
        self.menu_widget = MenuWidget(menu_items, config["target_index"], self)
        self.menu_widget.item_clicked.connect(self.on_menu_item_selected)
        self.menu_widget.hide()

        # prevent default context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position: QPoint):
        logger.debug(f"show context menu at {position}")

        global_pos = self.mapToGlobal(position)
        self.menu_widget.move(global_pos)
        self.menu_widget.show()

        self.start_pos = (global_pos.x(), global_pos.y())
        listener = get_mouse_listener()
        listener.start_record_distance()

    def on_menu_item_selected(self, selected_idx: int):
        logger.debug(f"item idx {selected_idx} is selected")

        listener = get_mouse_listener()
        click_pos = listener.last_pos
        target_pos = self.menu_widget.get_target_item_position()

        error_distance = calculate_distance(click_pos, target_pos)
        target_distance = calculate_distance(self.start_pos, target_pos)
        moving_distance = listener.stop_record_distance()

        payload = {
            "menu_length": len(self.menu_widget.items),
            "target_index": self.menu_widget.target_idx,
            "selected_index": selected_idx,
            "error_distance": error_distance,
            "target_distance": target_distance,
            "moving_distance": moving_distance,
        }
        self.on_completed.emit(payload)

        self.menu_widget.close()


class MenuWidget(QWidget):
    item_clicked = Signal(object)

    def __init__(self, items: list[str], target_idx: int, parent=None):
        super().__init__(parent)
        self.items = items
        self.target_idx = target_idx
        self.setupUI()

    def setupUI(self):
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {MyColor.gray.value};
                border: 1px solid {MyColor.gray_dark.value};
                border-radius: 2px;
            }}
            QPushButton {{
                text-align: left;
                padding: 8px 16px;
                border: none;
                font-size: 14px;
                color: {MyColor.black.value};
            }}
            QPushButton:hover {{
                background-color: {MyColor.blue.value};
                color: {MyColor.gray.value};
            }}
        """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        for i, item in enumerate(self.items):
            btn = QPushButton(item)
            btn.clicked.connect(lambda checked, i=i: self.item_clicked.emit(i))

            if i == self.target_idx:
                btn.setStyleSheet(
                    """
                    QPushButton {
                        font-weight: bold;
                    }
                """
                )

            layout.addWidget(btn)

        self.setFixedSize(150, len(self.items) * 35)

    def get_target_item_position(self) -> tuple[int, int]:
        for btn in self.findChildren(QPushButton):
            if btn.text() == self.items[self.target_idx]:
                pos = btn.mapToGlobal(btn.rect().center())
                return (pos.x(), pos.y())
        return (0, 0)


def calculate_distance(pos1: tuple[int, int], pos2: tuple[int, int]) -> float:
    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]
    return (dx**2 + dy**2) ** 0.5
