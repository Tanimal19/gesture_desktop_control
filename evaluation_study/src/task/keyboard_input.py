import random
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)
from evaluation_study.src.task.abstract_task_widget import AbstractTaskWidget
from evaluation_study.src.styles import (
    MyColor,
    get_instruction_style,
)
from share.singleton.mouse_listener import get_mouse_listener
import logging

logger = logging.getLogger(__name__)


class KeyboardInputTaskWidget(AbstractTaskWidget):
    payload_header = [
        "is_correct",
        "target_word",
        "entered_word",
        "num_key_clicks",
        "num_backspaces",
        "moving_distance",  # pixels of pointer moving between first click and submit
    ]
    on_completed = Signal(object)
    description = """
    This task has 5 trials.\n
    For each trial, use the virtual keyboard to type the specified word.\n
    You could only perform each trial once. The current trial ends when you submit your input.
    """
    _word_list = [
        "keyboard",
        "computer",
        "practice",
        "algorithm",
        "education",
        "language",
        "typing",
        "monitor",
        "network",
    ]

    @staticmethod
    def generate_configs_str(count: int) -> str:
        configs = []
        word_list = KeyboardInputTaskWidget._word_list.copy()
        selected_words = random.sample(word_list, count)
        for target_word in selected_words:
            config = {"target_word": target_word.upper()}
            configs.append(config)
        return str(configs)

    @staticmethod
    def parse_configs(configs_str: str) -> list[dict]:
        import ast

        configs = ast.literal_eval(configs_str)
        assert isinstance(configs, list)
        for config in configs:
            assert "target_word" in config
            assert config["target_word"].lower() in KeyboardInputTaskWidget._word_list
            config["target_word"] = config["target_word"].upper()
        return configs

    def setup(self, config: dict):
        self.target_word = config["target_word"]
        self.num_key_clicks = 0
        self.num_backspaces = 0
        self.first_click = True
        self.current_word = ""

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.addStretch()

        # instruction
        instruction = f"Please enter: <b>{self.target_word}</b>."
        instruction_label = QLabel(instruction)
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction_label.setStyleSheet(get_instruction_style())
        layout.addWidget(instruction_label)

        # text display
        self.text_display = QLabel()
        self.text_display.setFixedHeight(60)
        self.text_display.setStyleSheet(
            f"""
            QLabel {{
                font-size: 20px;
                color: {MyColor.black.to_css()};
                background-color: {MyColor.white.to_css()};
                border: 2px solid {MyColor.gray.to_css()};
                border-radius: 4px;
                padding: 6px;
                qproperty-wordWrap: true;
            }}
        """
        )
        layout.addWidget(self.text_display)

        # Virtual keyboard
        self.keyboard = self.create_virtual_keyboard()
        layout.addWidget(self.keyboard)

        layout.addStretch()

    def create_virtual_keyboard(self) -> QWidget:
        left_layout = QVBoxLayout()
        left_layout.setSpacing(8)

        # Define keyboard rows
        rows = [
            ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
            ["z", "x", "c", "v", "b", "n", "m"],
        ]

        # Create letter keys
        for row in rows:
            row_layout = QHBoxLayout()
            row_layout.setSpacing(6)
            row_layout.addStretch()
            for char in row:
                btn = self.create_key_button(char.upper(), char.upper())
                row_layout.addWidget(btn)
            row_layout.addStretch()
            left_layout.addLayout(row_layout)

        # Create backspace key and enter key column
        right_layout = QVBoxLayout()

        backspace_btn = self.create_key_button("backspace", "backspace", width=120)
        submit_btn = self.create_key_button("submit", "submit", width=140)

        right_layout.addWidget(backspace_btn, alignment=Qt.AlignmentFlag.AlignRight)
        right_layout.addStretch()
        right_layout.addWidget(submit_btn, alignment=Qt.AlignmentFlag.AlignRight)

        keyboard_layout = QHBoxLayout()
        keyboard_layout.addStretch()
        keyboard_layout.setSpacing(20)
        keyboard_layout.addLayout(left_layout)
        keyboard_layout.addLayout(right_layout)
        keyboard_layout.addStretch()

        keyboard_widget = QWidget()
        keyboard_widget.setLayout(keyboard_layout)
        keyboard_widget.setFixedHeight(300)
        return keyboard_widget

    def create_key_button(
        self, display_text: str, value: str, width: int = 60
    ) -> QPushButton:
        btn = QPushButton(display_text)

        # STYLE: key button appearance
        btn.setFixedSize(width, 60)
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {MyColor.white.to_css()};
                color: {MyColor.black.to_css()};
                border: 2px solid {MyColor.gray.to_css()};
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {MyColor.blue.to_css()};
                color: {MyColor.white.to_css()};
                border-color: {MyColor.blue.to_css()};
            }}
            QPushButton:pressed {{
                background-color: {MyColor.blue.to_css(0.8)};
            }}
        """
        )
        btn.clicked.connect(lambda: self.on_key_click(value))
        return btn

    def on_key_click(self, value: str):
        # Track first click for mouse movement recording
        if self.first_click:
            listener = get_mouse_listener()
            listener.start_record_distance()
            self.first_click = False

        self.num_key_clicks += 1

        if value == "submit":
            self.on_submit()
        elif value == "backspace":
            if self.current_word:
                self.current_word = self.current_word[:-1]
                self.num_backspaces += 1
        else:
            self.current_word += value

        # Update display
        self.text_display.setText(f"{self.current_word}")

    def on_submit(self):
        listener = get_mouse_listener()
        moving_distance = listener.stop_record_distance() if not self.first_click else 0

        payload = {
            "is_correct": int(self.current_word == self.target_word),
            "target_word": self.target_word,
            "entered_word": self.current_word,
            "num_key_clicks": self.num_key_clicks,
            "num_backspaces": self.num_backspaces,
            "moving_distance": moving_distance,
        }

        logger.debug(f"KeyboardInput completed: {payload}")
        self.on_completed.emit(payload)
