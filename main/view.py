from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QResizeEvent
from share.ui.camera_preview import CameraPreview

if TYPE_CHECKING:
    from main.controller import MainAppController

logger = logging.getLogger(__name__)


class MainAppView(QWidget):

    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setStyleSheet("background-color: rgba(0, 0, 0, 200);")

        # info label
        label_style = (
            "background-color: rgba(0, 0, 0, 0); color: white; font-size: 16px;"
        )
        self.gesture_label = QLabel("Gesture:")
        self.gesture_label.setStyleSheet(label_style)
        self.pointer_label = QLabel("Pointer:")
        self.pointer_label.setStyleSheet(label_style)
        self.event_label = QLabel("")
        self.event_label.setStyleSheet(label_style)
        self.event_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        label_layout = QHBoxLayout()
        label_layout.addWidget(self.gesture_label)
        label_layout.addWidget(self.pointer_label)
        label_layout.addWidget(self.event_label)
        label_layout.setStretch(0, 2)
        label_layout.setStretch(1, 2)
        label_layout.setStretch(2, 1)
        label_layout.setContentsMargins(10, 10, 10, 10)

        self.camera_preview = CameraPreview(600)
        self.camera_preview.setStyleSheet("background-color: rgba(0, 0, 0, 0);")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(label_layout)
        layout.addWidget(self.camera_preview)

        self.controller = None
        screen_geometry = QApplication.primaryScreen().geometry()
        self.screen_width = screen_geometry.width()
        self.screen_height = screen_geometry.height()
        self.raise_()

        self.is_visible = True

    def resizeEvent(self, event: QResizeEvent) -> None:
        margin = 20
        screen_geometry = QApplication.primaryScreen().geometry()
        self.move(
            margin,
            screen_geometry.height() - self.height() - margin,
        )
        super().resizeEvent(event)

    def set_controller(self, controller: MainAppController):
        self.controller = controller

    def toggle_visible(self):
        if self.is_visible:
            logger.info("Hiding view")
            self.setWindowOpacity(0)
            self.is_visible = False
        else:
            logger.info("Showing view")
            self.setWindowOpacity(1)
            self.is_visible = True

    def update_overlay_info(self, gesture=None, pointer_pos=None, mouse_event=None):
        if gesture is not None:
            self.gesture_label.setText(f"Gesture: {gesture}")
        if pointer_pos is not None:
            self.pointer_label.setText(f"Pointer: {pointer_pos}")
        if mouse_event is not None and mouse_event != "MOVE":
            self.event_label.setText(f"{mouse_event}")

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key.Key_Escape:  # exit app
            self.close()
        elif key == Qt.Key.Key_Space:  # toggle camera preview
            self.toggle_visible()

    def closeEvent(self, event):
        if self.controller:
            self.controller.close()
        event.accept()
