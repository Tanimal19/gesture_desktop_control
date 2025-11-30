import random
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QVBoxLayout, QLabel, QTextEdit, QPushButton, QWidget
from PySide6.QtGui import QFont, QKeyEvent
from evaluation_study.src.task_widget.abstract_task_widget import AbstractTaskWidget
from evaluation_study.src.styles import MyColor, CENTRAL_WIDGET_STYLE
from share.singleton.mouse_listener import get_mouse_listener
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

    @staticmethod
    def compute_correctness(payload: dict) -> bool:
        return payload["entered_text"].strip() == payload["target_text"].strip()

    def get_instructions(self) -> str:
        return (
            f"Type the following text exactly as shown:\n"
            f"'{self.target_text}'\n"
            "Click in the text area below and type the sentence. Click Submit when done."
        )

    def custom_init(self, config: dict):
        self.setFixedSize(CENTRAL_WIDGET_STYLE.width, CENTRAL_WIDGET_STYLE.height)

        self.target_text = config["target_text"]
        self.num_keystrokes = 0
        self.num_backspaces = 0
        self.first_click = True

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        # Target text display
        target_label = QLabel("Target text:")
        target_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {MyColor.black.to_css()};
            }}
        """
        )
        layout.addWidget(target_label)

        self.target_display = QLabel(f'"{self.target_text}"')
        self.target_display.setStyleSheet(
            f"""
            QLabel {{
                font-size: 14px;
                color: {MyColor.black.to_css()};
                background-color: {MyColor.gray_light.to_css()};
                border: 2px solid {MyColor.blue.to_css()};
                border-radius: 8px;
                padding: 15px;
                qproperty-wordWrap: true;
            }}
        """
        )
        layout.addWidget(self.target_display)

        # Input area
        input_label = QLabel("Type here:")
        input_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {MyColor.black.to_css()};
            }}
        """
        )
        layout.addWidget(input_label)

        self.text_input = QTextEdit()
        self.text_input.setFixedHeight(120)
        self.text_input.setStyleSheet(
            f"""
            QTextEdit {{
                font-size: 14px;
                color: {MyColor.black.to_css()};
                background-color: {MyColor.white.to_css()};
                border: 2px solid {MyColor.gray.to_css()};
                border-radius: 8px;
                padding: 10px;
            }}
            QTextEdit:focus {{
                border-color: {MyColor.blue.to_css()};
            }}
        """
        )
        self.text_input.mousePressEvent = self.on_text_area_click
        self.text_input.textChanged.connect(self.on_text_changed)
        self.text_input.installEventFilter(self)
        layout.addWidget(self.text_input)

        # Submit button
        self.submit_button = QPushButton("Submit")
        self.submit_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {MyColor.blue.to_css()};
                color: {MyColor.white.to_css()};
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {MyColor.blue.to_css(0.8)};
            }}
        """
        )
        self.submit_button.clicked.connect(self.on_submit)
        self.submit_button.setEnabled(False)  # Disabled until text is entered
        layout.addWidget(self.submit_button, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

    def on_text_area_click(self, event):
        # Track first click for mouse movement recording
        if self.first_click:
            listener = get_mouse_listener()
            listener.start_record_distance()
            self.first_click = False

        # Call the original mousePressEvent
        QTextEdit.mousePressEvent(self.text_input, event)

    def on_text_changed(self):
        # Enable submit button when text is entered
        has_text = len(self.text_input.toPlainText().strip()) > 0
        self.submit_button.setEnabled(has_text)

    def eventFilter(self, obj, event):
        if obj == self.text_input and event.type() == event.Type.KeyPress:
            key_event = QKeyEvent(event)
            self.num_keystrokes += 1

            if key_event.key() == Qt.Key.Key_Backspace:
                self.num_backspaces += 1

        return super().eventFilter(obj, event)

    def on_submit(self):
        entered_text = self.text_input.toPlainText()

        listener = get_mouse_listener()
        moving_distance = listener.stop_record_distance() if not self.first_click else 0

        payload = {
            "target_text": self.target_text,
            "entered_text": entered_text,
            "num_keystrokes": self.num_keystrokes,
            "num_backspaces": self.num_backspaces,
            "moving_distance": moving_distance,
        }

        logger.debug(f"Keyboard input completed: {payload}")
        self.on_completed.emit(payload)
