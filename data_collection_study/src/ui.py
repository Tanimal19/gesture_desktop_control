from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication, QSizePolicy
from PySide6.QtGui import (
    QPainter,
    QPen,
    QFont,
    QPolygonF,
    QBrush,
    QColor,
    QImage,
    QPixmap,
)
from PySide6.QtCore import Qt, QPointF, QRect
import cv2
import math
import logging

color_background = (238, 238, 238, 255)
color_foregorund_dark = (20, 20, 20, 255)
color_foreground_light = (200, 200, 200, 255)
color_primary = (245, 72, 66, 255)
color_primary_transparent = (245, 72, 66, 120)
color_secondary = (66, 135, 245, 255)
color_secondary_transparent = (66, 135, 245, 120)

logger = logging.getLogger(__name__)


class Canva(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: rgba{color_background};")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.elements = []

    def add_element(self, comp):
        if comp.__class__ not in [ArrowElement, DotElement]:
            raise ValueError("Unsupported component type")
        self.elements.append(comp)

    def clean(self):
        self.elements = []
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for ele in self.elements:
            ele.paint(painter, self)


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


class ArrowElement:
    def __init__(self, x1, y1, x2, y2, width=5, dashed=False):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.width = width
        self.color = QColor(*color_foregorund_dark)
        self.dashed = dashed

    def paint(self, painter, canva):
        pen = (
            QPen(self.color, self.width)
            if not self.dashed
            else QPen(self.color, self.width, Qt.PenStyle.DashLine)
        )
        painter.setPen(pen)

        # convert global to screen coordinates
        p1 = canva.mapFromGlobal(QPointF(self.x1, self.y1))
        p2 = canva.mapFromGlobal(QPointF(self.x2, self.y2))
        x1, y1, x2, y2 = p1.x(), p1.y(), p2.x(), p2.y()

        # shorten the drawn line so the arrow head doesn't overlap the line
        delta = 60
        dx, dy = x2 - x1, y2 - y1
        length = (dx**2 + dy**2) ** 0.5
        head_scale = delta / length
        tail_scale = 1 - head_scale

        new_x1 = x1 + dx * head_scale
        new_y1 = y1 + dy * head_scale
        new_x2 = x1 + dx * tail_scale
        new_y2 = y1 + dy * tail_scale

        painter.drawLine(new_x1, new_y1, new_x2, new_y2)

        front, left, right = self._calc_arrow_head(
            new_x1, new_y1, new_x2, new_y2, self.width
        )
        polygon = QPolygonF([QPointF(*front), QPointF(*left), QPointF(*right)])
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color)
        painter.drawPolygon(polygon)

        logger.info(
            f"drawing line: setting={(self.x1, self.y1, self.x2, self.y2)} screen={(new_x1, new_y1, new_x2, new_y2)}"
        )

    @staticmethod
    def _calc_arrow_head(x1, y1, x2, y2, linewidth):
        size = linewidth * 4
        angle_deg = 30
        angle = math.atan2(y2 - y1, x2 - x1)

        front = (x2 + size / 2 * math.cos(angle), y2 + size / 2 * math.sin(angle))
        left = (
            front[0] - size * math.cos(angle - math.radians(angle_deg)),
            front[1] - size * math.sin(angle - math.radians(angle_deg)),
        )
        right = (
            front[0] - size * math.cos(angle + math.radians(angle_deg)),
            front[1] - size * math.sin(angle + math.radians(angle_deg)),
        )
        return front, left, right


class DotElement:
    def __init__(self, x, y, radius, type, label=None, inner_label=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.type = type
        self.label = label
        self.inner_label = inner_label

    def paint(self, painter, canva, active=False):
        color_p = color_primary if not active else color_secondary
        color_pt = (
            color_primary_transparent if not active else color_secondary_transparent
        )

        if self.type == "solid":
            painter.setBrush(QBrush(QColor(*color_p)))

        elif self.type == "transparent":
            pen = QPen(QColor(*color_p))
            pen.setWidth(4)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(*color_pt)))

        elif self.type == "hollow":
            pen = QPen(QColor(*color_p))
            pen.setWidth(4)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)

        else:
            raise ValueError("Unsupported dot type")

        # convert global to screen coordinates
        p = canva.mapFromGlobal(QPointF(self.x, self.y))
        x, y = p.x(), p.y()

        painter.drawEllipse(
            x - self.radius, y - self.radius, self.radius * 2, self.radius * 2
        )

        if self.label:
            font = QFont("Arial", 24)
            painter.setFont(font)
            painter.setPen(QPen(QColor(*color_foregorund_dark)))
            text_rect = painter.fontMetrics().boundingRect(self.label)
            padding = 4
            text_w = text_rect.width()
            text_h = text_rect.height()
            tx = int(x - text_w / 2)
            ty = int(y - self.radius - text_h - padding)
            painter.drawText(
                QRect(tx, ty, text_w, text_h), Qt.AlignmentFlag.AlignCenter, self.label
            )

        if self.inner_label:
            font = QFont("Arial", 24)
            painter.setFont(font)
            painter.setPen(QPen(QColor(*color_foregorund_dark)))
            text_rect = painter.fontMetrics().boundingRect(self.inner_label)
            padding = 4
            text_w = text_rect.width()
            text_h = text_rect.height()
            tx = int(x - text_w / 2)
            ty = int(y - text_h / 2)
            painter.drawText(
                QRect(tx, ty, text_w, text_h),
                Qt.AlignmentFlag.AlignCenter,
                self.inner_label,
            )

        logger.info(f"drawing dot: setting={(self.x, self.y)} screen={(x, y)}")
