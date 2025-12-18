from __future__ import annotations
from typing import TYPE_CHECKING
import time
import cv2
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QApplication
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QResizeEvent, QImage, QPixmap
import logging

if TYPE_CHECKING:
    from main.controller import MainAppController

logger = logging.getLogger(__name__)


class MainAppView(QWidget):

    def __init__(self, camera_preview_disable):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setStyleSheet("background-color: rgba(0, 0, 0, 150);")

        # info label
        label_style = (
            "background-color: rgba(0, 0, 0, 0); color: white; font-size: 16px;"
        )
        self.gesture_label = QLabel("Gesture:")
        self.gesture_label.setStyleSheet(label_style)
        self.gesture_label.setFixedSize(180, 20)
        self.pointer_label = QLabel("Pointer:")
        self.pointer_label.setStyleSheet(label_style)
        self.pointer_label.setFixedSize(180, 20)
        self.event_label = QLabel("")
        self.event_label.setStyleSheet(label_style)
        self.event_label.setFixedSize(120, 20)
        self.event_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.consectuive_move_count = 0

        label_layout = QHBoxLayout()
        label_layout.addWidget(self.gesture_label)
        label_layout.addWidget(self.pointer_label)
        label_layout.addWidget(self.event_label)
        label_layout.setContentsMargins(10, 10, 10, 10)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(label_layout)

        if not camera_preview_disable:
            self.camera_preview = CameraPreview(500, 300)
            main_layout.addWidget(self.camera_preview)

        self.setLayout(main_layout)

        self.controller = None
        screen_geometry = QApplication.primaryScreen().geometry()
        self.screen_width = screen_geometry.width()
        self.screen_height = screen_geometry.height()

        self.is_visible = True

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.move(
            20,
            60,
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
        if mouse_event is not None:
            # reset label if move event sustained, (otherwise it clutters the UI)
            if mouse_event == "MOVE":
                self.consectuive_move_count += 1
                if self.consectuive_move_count >= 10:
                    self.event_label.setText("")
            else:
                self.consectuive_move_count = 0
                self.event_label.setText(f"{mouse_event}")

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key.Key_Escape:  # exit app
            self.close()

        elif key == Qt.Key.Key_Space:  # toggle camera preview
            self.toggle_visible()

        elif key == Qt.Key.Key_E:
            if self.controller:
                self.controller.toggle_mouse_control()

    def closeEvent(self, event):
        if self.controller:
            self.controller.close()
            QCoreApplication.processEvents()  # drain queued callbacks
            time.sleep(0.05)

        super().closeEvent(event)


class CameraPreview(QLabel):
    def __init__(self, width, height):
        super().__init__()
        self.setFixedSize(width, height)
        self.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)

    def update_camera_preview(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg).scaled(
            self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatio
        )
        self.setPixmap(pixmap)
