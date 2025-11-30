from PySide6.QtCore import QThread
from pynput import mouse
import math
import logging


logger = logging.getLogger(__name__)


class MouseListenerSingleton(QThread):
    def __init__(self):
        super().__init__()
        self.listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click)
        self.recording_distance = False
        self.last_pos = (0, 0)
        self.total_distance = 0

    def run(self):
        self.listener.start()
        self.listener.join()

    def stop(self):
        self.listener.stop()
        self.listener.join()

    def start_record_distance(self):
        self.total_distance = 0
        self.recording_distance = True
        logger.debug("Started recording mouse movement distance.")

    def stop_record_distance(self):
        self.recording_distance = False
        logger.debug(
            f"Stopped recording mouse movement distance. Total distance: {self.total_distance}"
        )
        return self.total_distance

    def on_move(self, x, y):
        logger.debug(f"Mouse moved to ({x}, {y})")
        if self.recording_distance:
            dx = x - self.last_pos[0]
            dy = y - self.last_pos[1]
            dist = math.hypot(dx, dy)  # sqrt(dx^2 + dy^2)
            self.total_distance += dist

        self.last_pos = (x, y)

    def on_click(self, x, y, button, pressed):
        pos = (int(x), int(y))
        if pressed:
            event = f"{button.name}_press"
        else:
            event = f"{button.name}_release"
        logger.debug(f"{event} at {pos}")


_mouse_listener_singleton = None


def get_mouse_listener():
    global _mouse_listener_singleton
    if _mouse_listener_singleton is None:
        _mouse_listener_singleton = MouseListenerSingleton()
        _mouse_listener_singleton.start()
        logger.debug("Started MouseListenerSingleton thread.")
    return _mouse_listener_singleton


def close_mouse_listener():
    global _mouse_listener_singleton
    if _mouse_listener_singleton is not None:
        _mouse_listener_singleton.stop()
        _mouse_listener_singleton = None
        logger.debug("Stopped MouseListenerSingleton thread.")
