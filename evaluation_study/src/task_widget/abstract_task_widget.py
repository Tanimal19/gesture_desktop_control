from abc import abstractmethod
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal
from evaluation_study.src.styles import (
    CENTRAL_WIDGET_HEIGHT,
    MAIN_WINDOW_WIDTH,
)


class AbstractTaskWidget(QWidget):
    payload_header: list[str]
    on_completed: Signal
    HEIGHT = CENTRAL_WIDGET_HEIGHT
    WIDTH = MAIN_WINDOW_WIDTH

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

    @staticmethod
    @abstractmethod
    def compute_correctness(payload: dict) -> bool:
        """Compute whether the task was completed correctly based on the payload."""
        pass

    @abstractmethod
    def get_instructions(self) -> str:
        """Return the instructions for the task."""
        pass

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.custom_init(config)

    @abstractmethod
    def custom_init(self, config: dict):
        pass
