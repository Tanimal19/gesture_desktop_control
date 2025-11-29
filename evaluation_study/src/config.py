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
    green = (52, 199, 89)
    blue = (0, 122, 255)


class TrueTaskType(Enum):
    Tutorial = 0
    MenuSelect = 1
    DragDrop = 2
    KeyboardInput = 3


class TaskWidget(QWidget, ABC):
    ttype: TrueTaskType
    payload_header: list[str]
    on_completed: Signal

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.check_config_valid(config)
        self.init(config)

    @staticmethod
    @abstractmethod
    def generate_configs(count: int) -> list[dict]:
        """Generate a list of configurations for the task."""
        pass

    @abstractmethod
    def check_config_valid(self, config: dict):
        """Check whether the provided config are valid for this task type, use assertion error"""
        pass

    @abstractmethod
    def init(self, config: dict):
        """Initialize the UI components and properties."""
        pass

    @abstractmethod
    def start_next_trail(self):
        """Update the UI components to the next trail configuration."""
        pass
