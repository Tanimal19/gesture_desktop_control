from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
)
from src.config import color_foregorund_dark


class TopBar(QLabel):
    def __init__(self, height, parent=None):
        super().__init__(parent)
        self.setFixedHeight(height)
        self.setContentsMargins(10, 0, 10, 0)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setWordWrap(True)
        self.setStyleSheet(f"color: rgba{color_foregorund_dark}; font-size: 24px;")

    def set_instruction(self, text, color=None):
        self.setText(text)
        if color is not None:
            self.setStyleSheet(f"color: rgba{color}; font-size: 24px;")


class SideBar(QWidget):
    def __init__(self, width, parent=None):
        super().__init__(parent)
        self.setFixedWidth(width)

        self.mlayout = QVBoxLayout()
        self.mlayout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.mlayout)

        self.info_labels = {}

    def add_label(self, key, text):
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet(f"color: rgba{color_foregorund_dark}; font-size: 16px;")
        self.mlayout.addWidget(label)
        self.info_labels[key] = label

    def update_label(self, key, text=None, color=None):
        if key in self.info_labels:
            if color is not None:
                self.info_labels[key].setStyleSheet(
                    f"color: rgba{color}; font-size: 16px;"
                )
            if text is not None:
                self.info_labels[key].setText(text)


class HintOverlay(QWidget):
    def __init__(self, parent, bg_color, text_color):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setStyleSheet(f"background-color: rgba{bg_color};")
        self.setGeometry(parent.rect())

        # 加文字 label
        self.label = QLabel(self)
        self.label.setText("")

        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(
            f"""
            color: rgba{text_color};
            font-size: 30px;
            font-weight: bold;
            background-color: transparent;
            """
        )
        self.label.setGeometry(self.rect())

        self.hide()

    def set_hint(self, text):
        self.label.setText(text)
        self.show()
