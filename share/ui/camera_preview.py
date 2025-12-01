from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
import cv2


class CameraPreview(QLabel):
    def __init__(self, width=300, ratio=2):
        super().__init__()
        self.setFixedSize(width, int(width // ratio))
        self.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)

    def update_camera_preview(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg).scaled(
            self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatio
        )
        self.setPixmap(pixmap)
