# TODO: return none if clicked outside the menu

import random
from evaluation_study.src.task_widget.abstract_task_widget import AbstractTaskWidget
from evaluation_study.src.styles import MyColor, get_instruction_style
from evaluation_study.src.utils import calculate_distance
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from share.singleton.mouse_listener import get_mouse_listener
import logging

logger = logging.getLogger(__name__)


class MenuSelectTaskWidget(AbstractTaskWidget):
    payload_header = [
        "is_correct",
        "menu_length",
        "target_index",
        "selected_index",
        "error_distance",  # pixels between clicked point and target item
        "target_distance",  # pixels between start point and target item
        "moving_distance",  # pixels of pointer moving between menu open and item click
    ]
    on_completed = Signal(object)
    description = """
    This task has 5 trials.\n
    For each trial, right-click to open the context menu (contains 6 options), then left-click on the specified option.\n
    You could only perform each trial once. The current trial ends when any option is selected."""
    _menu_length = 6

    @staticmethod
    def generate_configs_str(count: int) -> str:
        configs = []
        for _ in range(count):
            target_index = random.randint(0, MenuSelectTaskWidget._menu_length - 1)
            config = {"target_index": target_index}
            configs.append(config)
        return str(configs)

    @staticmethod
    def parse_configs(configs_str: str) -> list[dict]:
        import ast

        configs = ast.literal_eval(configs_str)
        assert isinstance(configs, list)
        for config in configs:
            assert "target_index" in config
            assert 0 <= config["target_index"] < MenuSelectTaskWidget._menu_length
        return configs

    def setup(self, config: dict):
        self.target_index = config["target_index"]
        menu_items = [f"Option {i+1}" for i in range(MenuSelectTaskWidget._menu_length)]

        # setup context menu
        self.menu_widget = MenuWidget(menu_items, self)
        self.menu_widget.item_clicked.connect(self.on_menu_item_selected)
        self.menu_widget.hide()

        # prevent default context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.has_opened = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        instruction = f"Please right-click and select <b>{menu_items[self.target_index]}</b> from the context menu."
        instruction_label = QLabel(instruction)
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction_label.setStyleSheet(get_instruction_style())
        layout.addWidget(instruction_label)

    def show_context_menu(self, position: QPoint):
        if self.has_opened:
            return
        self.has_opened = True

        logger.debug(f"show context menu at {position}")

        global_pos = self.mapToGlobal(position)
        self.menu_widget.move(global_pos)
        self.menu_widget.show()

        self.start_pos = (global_pos.x(), global_pos.y())
        listener = get_mouse_listener()
        listener.start_record_distance()

    def on_menu_item_selected(self, selected_index: int):
        logger.debug(f"item idx {selected_index} is selected")
        self.menu_widget.close()

        listener = get_mouse_listener()
        click_pos = listener.last_pos
        target_pos = self.menu_widget.get_item_position(self.target_index)

        error_distance = calculate_distance(click_pos, target_pos)
        target_distance = calculate_distance(self.start_pos, target_pos)
        moving_distance = listener.stop_record_distance()

        payload = {
            "is_correct": int(selected_index == self.target_index),
            "menu_length": MenuSelectTaskWidget._menu_length,
            "target_index": self.target_index,
            "selected_index": selected_index,
            "error_distance": error_distance,
            "target_distance": target_distance,
            "moving_distance": moving_distance,
        }

        logger.debug(f"MenuSelect completed: {payload}")
        self.on_completed.emit(payload)


class MenuWidget(QWidget):
    item_clicked = Signal(object)

    def __init__(self, items: list[str], parent=None):
        super().__init__(parent)
        self.items = items

        # STYLE: menu appearance
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {MyColor.gray.to_css()};
                border: 1px solid {MyColor.gray_dark.to_css()};
                border-radius: 8px;
            }}
        """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.btn = []
        for i, item in enumerate(self.items):
            btn = QPushButton(item)
            btn.clicked.connect(lambda checked, i=i: self.item_clicked.emit(i))

            # STYLE: menu item appearance
            btn.setFixedSize(200, 50)
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {MyColor.gray.to_css()};
                    color: {MyColor.black.to_css()};
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 14px;
                    font-weight: bold;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {MyColor.blue.to_css()};
                    color: {MyColor.white.to_css()};
                }}
            """
            )

            layout.addWidget(btn)
            self.btn.append(btn)

    def get_item_position(self, index) -> tuple[int, int]:
        btn = self.btn[index]
        btn_pos = btn.mapToGlobal(btn.rect().center())
        return (btn_pos.x(), btn_pos.y())
