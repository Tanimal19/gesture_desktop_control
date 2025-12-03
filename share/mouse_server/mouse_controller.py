# to control mouse on macOS

import Quartz
import logging

logger = logging.getLogger(__name__)


class MouseController:
    def __init__(self):
        self._left_pressed = False

    def move(self, x, y):
        if self._left_pressed:
            ev_type = Quartz.kCGEventLeftMouseDragged
        else:
            ev_type = Quartz.kCGEventMouseMoved

        btn = Quartz.kCGMouseButtonLeft
        event = Quartz.CGEventCreateMouseEvent(None, ev_type, (x, y), btn)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
        logger.debug(f"Moved mouse to ({x}, {y})")

    def button_event(self, x, y, down, button):
        if button == "left":
            btn = Quartz.kCGMouseButtonLeft
            ev_type = (
                Quartz.kCGEventLeftMouseDown if down else Quartz.kCGEventLeftMouseUp
            )
        elif button == "right":
            btn = Quartz.kCGMouseButtonRight
            ev_type = (
                Quartz.kCGEventRightMouseDown if down else Quartz.kCGEventRightMouseUp
            )
        else:
            raise ValueError(f"Unsupported button: {button}")

        if button == "left" and down:
            self._left_pressed = True
        else:
            self._left_pressed = False

        event = Quartz.CGEventCreateMouseEvent(None, ev_type, (x, y), btn)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)

        logger.debug(f"{"Press" if down else "Release"} {button} button at {(x, y)}")
