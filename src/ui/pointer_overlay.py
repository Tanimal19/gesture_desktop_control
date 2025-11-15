# Qt widgets for ui
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QColor, QPainter
from PySide6.QtCore import Qt, QPointF


class PointerOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)

        self.dot_radius = 10
        self.dot_pos = None

    def update_pointer_position(self, pos):
        self.dot_pos = pos
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.dot_pos is not None:
            painter.setBrush(QColor(255, 0, 0))
            p = self.mapFromGlobal(QPointF(self.dot_pos[0], self.dot_pos[1]))
            x, y = p.x(), p.y()

            painter.drawEllipse(
                int(x - self.dot_radius),
                int(y - self.dot_radius),
                self.dot_radius * 2,
                self.dot_radius * 2,
            )

        painter.end()
