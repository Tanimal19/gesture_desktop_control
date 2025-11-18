from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QApplication
from PySide6.QtGui import QPainter, QFont
from share.ui.camera_preview import CameraPreview
from share.ui.pointer_overlay import PointerOverlay

if TYPE_CHECKING:
    from main.controller import MainAppController

logger = logging.getLogger(__name__)


class MainAppView(QWidget):

    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.cam_preview = CameraPreview(600)
        self.mlayout = QVBoxLayout(self)
        self.mlayout.setContentsMargins(0, 0, 0, 0)
        self.mlayout.addWidget(self.cam_preview)
        self.setLayout(self.mlayout)

        # place at bottom-left
        screen_geometry = QApplication.primaryScreen().geometry()
        x = 20
        y = screen_geometry.height() - self.height() - 20
        self.move(x, y)

        self.overlay_text = ""

        self.pointer_overlay = PointerOverlay()
        self.pointer_overlay.show()

        self.controller = None

    def set_controller(self, controller: MainAppController):
        self.controller = controller

    def set_overlay_text(self, text: str):
        self.overlay_text = text
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.overlay_text:
            painter = QPainter(self)
            painter.setPen(Qt.GlobalColor.red)
            painter.setFont(QFont("Arial", 16))
            painter.drawText(10, 30, self.overlay_text)
            painter.end()

    def keyPressEvent(self, event):
        if self.controller:
            self.controller.keyPressEvent(event.key())

    def closeEvent(self, event):
        if self.controller:
            self.controller.close()
        event.accept()
