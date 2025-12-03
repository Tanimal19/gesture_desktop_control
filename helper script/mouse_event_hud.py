# a hud that displays real-time mouse event information (only works on main desktop)

import sys
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt, QTimer
from pynput import mouse

pos = (0, 0)
event = "none"
state = "pressed"


def on_move(x, y):
    global pos, event
    pos = (int(x), int(y))
    event = "move"


def on_click(x, y, button, pressed):
    global pos, event, state
    pos = (int(x), int(y))
    if pressed:
        event = f"{button.name}_press"
    else:
        event = f"{button.name}_release"
    state = "pressed" if pressed else "released"


def on_scroll(x, y, dx, dy):
    global pos, event
    pos = (int(x), int(y))
    event = "scroll" + ("_up" if dy > 0 else "_down")


listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
listener.start()


class MouseHUD(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(
            """
            background-color: rgba(0, 0, 0, 150);
            border-radius: 10px;
            """
        )

        self.label = QLabel("waiting for mouse events...", self)
        self.label.setStyleSheet("color: white; font-size: 20px;")

        layout = QVBoxLayout()
        layout.addWidget(self.label)

        self.setLayout(layout)
        self.resize(400, 100)
        self._position_window()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_label)
        self.timer.start(30)

    def _position_window(self, hud_size=(400, 100), margin=20):
        screen = app.primaryScreen().availableGeometry()
        screen_width = screen.width()
        screen_height = screen.height()

        self.move(
            screen_width - hud_size[0] - margin, screen_height - hud_size[1] - margin
        )

    def update_label(self):
        hud_text = f"{event}\nstate: {state}\tposition: {pos}"
        self.label.setText(hud_text)


app = QApplication(sys.argv)
window = MouseHUD()
window.show()
sys.exit(app.exec())
listener.stop()
