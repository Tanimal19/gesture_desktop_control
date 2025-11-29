import random
from PySide6.QtCore import Signal
from evaluation_study.src.task_widget.abstract_task_widget import AbstractTaskWidget
from evaluation_study.src.styles import MyColor
import logging

logger = logging.getLogger(__name__)


class KeyboardInputTaskWidget(AbstractTaskWidget):
    payload_header = [
        "target_text",
        "entered_text",
        "num_keystrokes",
        "num_backspaces",
        "moving_distance",  # pixels of pointer moving between first click and submit
    ]
    on_completed = Signal(object)

    sentences = [
        "The quick brown fox jumps over the lazy dog.",
        "Pack my box with five dozen liquor jugs.",
        "Sphinx of black quartz, judge my vow.",
        "How vexingly quick daft zebras jump!",
        "Bright vixens jump; dozy fowl quack.",
        "Jackdaws love my big sphinx of quartz.",
        "The five boxing wizards jump quickly.",
        "Quick zephyrs blow, vexing daft Jim.",
        "Two driven jocks help fax my big quiz.",
        "Five quacking zephyrs jolt my wax bed.",
    ]

    @staticmethod
    def generate_configs(count: int) -> str:
        configs = []
        for _ in range(count):
            target_text = random.choice(KeyboardInputTaskWidget.sentences)
            config = {"target_text": target_text}
            configs.append(config)
        return str(configs)

    @staticmethod
    def parse_configs(configs_str: str) -> list[dict]:
        import ast

        try:
            configs = ast.literal_eval(configs_str)
            assert isinstance(configs, list)
            for config in configs:
                assert "target_text" in config
                assert config["target_text"] in KeyboardInputTaskWidget.sentences
            return configs
        except (ValueError, SyntaxError, AssertionError) as e:
            logger.error(f"Failed to parse KeyboardInput configs: {e}")
            return []

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)

        # TODO: Implement the UI and logic for the keyboard input task
