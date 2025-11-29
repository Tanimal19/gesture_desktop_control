from enum import Enum
from abc import ABC, abstractmethod
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal


class MyColor(Enum):
    white = (242, 242, 247)
    black = (28, 28, 30)
    gray = (229, 229, 234)
    gray_dark = (209, 209, 214)
    red = (255, 56, 60)
    red_translucent = (255, 56, 60, 180)
    green = (52, 199, 89)
    green_translucent = (52, 199, 89, 180)
    blue = (0, 122, 255)
    blue_translucent = (0, 122, 255, 180)


class TrueTaskType(Enum):
    Tutorial = 0
    MenuSelect = 1
    DragDrop = 2
    KeyboardInput = 3


class TaskWidget(QWidget):
    payload_header: list[str]
    on_completed: Signal

    @staticmethod
    @abstractmethod
    def generate_configs(count: int) -> str:
        """Generate a list of configurations for the task."""
        pass

    @staticmethod
    @abstractmethod
    def parse_configs(configs_str: str) -> list[dict]:
        """Parse the configuration string into a list of configuration dictionaries."""
        pass
