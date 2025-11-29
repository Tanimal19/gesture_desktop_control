import random
import time
from typing import List
from evaluation_study.src.config import (
    TrueTaskType,
    TaskWidget,
    MyColor,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
)
from PySide6.QtGui import QFont
from share.singleton.mouse_listener import get_mouse_listener
import logging

logger = logging.getLogger(__name__)


class KeyboardInputTaskWidget(TaskWidget):
    ttype = TrueTaskType.KeyboardInput
    payload_header = [
        "target_text",
        "entered_text",
        "is_correct",
        "completion_time",
        "character_accuracy",
        "total_distance",
        "num_keystrokes",
        "num_backspaces",
    ]
    on_completed = Signal(object)

    @staticmethod
    def generate_configs(count: int) -> list[dict]:
        configs = []
        text_options = [
            "Hello",
            "World",
            "Python",
            "Code",
            "Test",
            "Quick",
            "Brown",
            "Fox",
            "Jumps",
            "Over",
            "The",
            "Lazy",
            "Dog",
        ]

        for _ in range(count):
            target_text = random.choice(text_options)
            config = {"target_text": target_text}
            configs.append(config)
        return configs

    def check_config_valid(self, config: dict):
        assert "target_text" in config
        assert isinstance(config["target_text"], str)
        assert len(config["target_text"]) > 0

    def init(self, config: dict):
        self.target_text = config["target_text"]
        self.current_text = ""
        self.start_time = None
        self.keystroke_count = 0
        self.backspace_count = 0

        self.setFixedSize(800, 600)
        self.setStyleSheet(f"background-color: rgb{MyColor.white.value};")

        layout = QVBoxLayout(self)

        # Instruction
        instruction = QLabel(f"Type the target text: '{self.target_text}'")
        instruction.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction.setStyleSheet(f"color: rgb{MyColor.black.value}; padding: 20px;")
        layout.addWidget(instruction)

        # Text input display
        self.text_display = QLineEdit()
        self.text_display.setFont(QFont("Arial", 18))
        self.text_display.setFixedHeight(50)
        self.text_display.setPlaceholderText("Click keys below to type...")
        self.text_display.setReadOnly(True)
        self.text_display.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: white;
                border: 2px solid rgb{MyColor.gray_dark.value};
                border-radius: 5px;
                padding: 10px;
            }}
        """
        )
        layout.addWidget(self.text_display)

        # Progress indicator
        self.progress_label = QLabel("Progress: 0%")
        self.progress_label.setFont(QFont("Arial", 12))
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet(
            f"color: rgb{MyColor.black.value}; padding: 10px;"
        )
        layout.addWidget(self.progress_label)

        # Virtual keyboard
        self.keyboard = VirtualKeyboard(self)
        self.keyboard.key_pressed.connect(self.on_key_pressed)
        layout.addWidget(self.keyboard)

        # Control buttons
        btn_layout = QHBoxLayout()

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFont(QFont("Arial", 12))
        self.clear_btn.setFixedHeight(40)
        self.clear_btn.clicked.connect(self.clear_text)

        self.backspace_btn = QPushButton("Backspace")
        self.backspace_btn.setFont(QFont("Arial", 12))
        self.backspace_btn.setFixedHeight(40)
        self.backspace_btn.clicked.connect(self.backspace)

        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setFont(QFont("Arial", 12))
        self.submit_btn.setFixedHeight(40)
        self.submit_btn.clicked.connect(self.submit_text)

        for btn in [self.clear_btn, self.backspace_btn, self.submit_btn]:
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: rgb{MyColor.blue.value};
                    color: white;
                    border: none;
                    border-radius: 5px;
                }}
                QPushButton:hover {{
                    background-color: rgb{MyColor.gray_dark.value};
                }}
            """
            )

        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.backspace_btn)
        btn_layout.addWidget(self.submit_btn)
        layout.addLayout(btn_layout)

    def start_next_trail(self):
        # Reset for new trial
        self.current_text = ""
        self.start_time = None
        self.keystroke_count = 0
        self.backspace_count = 0
        self.text_display.setText("")
        self.progress_label.setText("Progress: 0%")
        self.progress_label.setStyleSheet(
            f"color: rgb{MyColor.black.value}; padding: 10px;"
        )

    def on_key_pressed(self, key: str):
        """Handle virtual key press."""
        if self.start_time is None:
            self.start_time = time.time()
            listener = get_mouse_listener()
            listener.start_record_distance()

        if key == "SPACE":
            key = " "
        self.current_text += key
        self.keystroke_count += 1
        self.text_display.setText(self.current_text)
        self.update_progress()

        # Auto-submit if text matches target exactly
        if self.current_text == self.target_text:
            self.submit_text()

    def clear_text(self):
        """Clear the current text."""
        self.current_text = ""
        self.text_display.setText("")
        self.update_progress()

    def backspace(self):
        """Remove the last character."""
        if self.current_text:
            if self.start_time is None:
                self.start_time = time.time()
                listener = get_mouse_listener()
                listener.start_record_distance()

            self.current_text = self.current_text[:-1]
            self.backspace_count += 1
            self.text_display.setText(self.current_text)
            self.update_progress()

    def submit_text(self):
        """Submit the current text."""
        completion_time = time.time() - self.start_time if self.start_time else 0
        listener = get_mouse_listener()
        total_distance = listener.stop_record_distance()

        is_correct = self.current_text == self.target_text

        # Calculate character accuracy
        correct_chars = 0
        for i in range(min(len(self.current_text), len(self.target_text))):
            if self.current_text[i] == self.target_text[i]:
                correct_chars += 1

        accuracy = (
            (correct_chars / len(self.target_text)) * 100 if self.target_text else 0
        )

        payload = {
            "target_text": self.target_text,
            "entered_text": self.current_text,
            "is_correct": is_correct,
            "completion_time": completion_time,
            "character_accuracy": accuracy,
            "total_distance": total_distance,
            "num_keystrokes": self.keystroke_count,
            "num_backspaces": self.backspace_count,
        }

        self.on_completed.emit(payload)

        if is_correct:
            self.progress_label.setText("✓ Text completed successfully!")
            self.progress_label.setStyleSheet(
                f"color: rgb{MyColor.green.value}; font-weight: bold; padding: 10px;"
            )
        else:
            self.progress_label.setText("✗ Text does not match target")
            self.progress_label.setStyleSheet(
                f"color: rgb{MyColor.red.value}; font-weight: bold; padding: 10px;"
            )

    def update_progress(self):
        """Update the progress indicator."""
        if not self.target_text:
            return

        # Calculate character-by-character accuracy
        correct_chars = 0
        for i, char in enumerate(self.current_text):
            if i < len(self.target_text) and char == self.target_text[i]:
                correct_chars += 1
            else:
                break

        progress = (correct_chars / len(self.target_text)) * 100
        self.progress_label.setText(f"Progress: {progress:.0f}%")


class VirtualKeyboard(QWidget):
    """Virtual keyboard widget."""

    key_pressed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()

    def setupUI(self):
        """Initialize the virtual keyboard."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Define keyboard layout
        rows = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
            ["Z", "X", "C", "V", "B", "N", "M"],
        ]

        # Create key rows
        for row in rows:
            row_layout = QHBoxLayout()
            row_layout.setSpacing(5)

            for key in row:
                btn = KeyButton(key)
                btn.clicked.connect(lambda checked, k=key: self.key_pressed.emit(k))
                row_layout.addWidget(btn)

            layout.addLayout(row_layout)

        # Space bar row
        space_layout = QHBoxLayout()
        space_btn = KeyButton("SPACE", width=300)
        space_btn.clicked.connect(lambda: self.key_pressed.emit("SPACE"))
        space_layout.addWidget(space_btn)
        layout.addLayout(space_layout)


class KeyButton(QPushButton):
    """Individual key button for the virtual keyboard."""

    def __init__(self, text: str, width: int = 50, height: int = 50, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(width, height)
        self.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: white;
                color: rgb{MyColor.black.value};
                border: 2px solid rgb{MyColor.gray_dark.value};
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: rgb{MyColor.gray.value};
            }}
            QPushButton:pressed {{
                background-color: rgb{MyColor.blue.value};
                color: white;
            }}
        """
        )
