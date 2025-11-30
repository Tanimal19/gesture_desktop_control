from abc import abstractmethod
from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import Signal


class AbstractTaskWidget(QWidget):
    payload_header: list[str]
    on_completed: Signal
    description: str

    @staticmethod
    @abstractmethod
    def generate_configs_str(count: int) -> str:
        """Generate a list of configurations for the task."""
        pass

    @staticmethod
    @abstractmethod
    def parse_configs(configs_str: str) -> list[dict]:
        """Parse the configuration string into a list of configuration dictionaries."""
        pass

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setup(config)

    @abstractmethod
    def setup(self, config: dict):
        pass
