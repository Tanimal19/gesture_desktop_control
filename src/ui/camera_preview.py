from PySide6.QtWidgets import QWidget, QLabel, QApplication, QVBoxLayout
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
import cv2


class CameraPreview(QWidget):
    def __init__(self, width=600, ratio=1.5):
        super().__init__()
        self.camera_preview = QLabel()

        screen_geometry = QApplication.primaryScreen().geometry()

        height = int(width // ratio)
        x = screen_geometry.width() - width - 20
        y = screen_geometry.height() - height - 20

        self.setGeometry(x, y, width, height)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.camera_preview)
        self.setLayout(layout)

    def update_camera_preview(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg).scaled(
            self.camera_preview.width(),
            self.camera_preview.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
        )
        self.camera_preview.setPixmap(pixmap)


class CameraPreviewLabel(QLabel):
    def __init__(self, width=300, ratio=1.5):
        super().__init__()
        self.setFixedSize(width, int(width // ratio))

    def update_camera_preview(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg).scaled(
            self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatio
        )
        self.setPixmap(pixmap)
