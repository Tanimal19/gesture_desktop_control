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

    def button_event(self, x, y, button, event_type):
        if button == "left":
            down_event = Quartz.CGEventCreateMouseEvent(
                None, Quartz.kCGEventLeftMouseDown, (x, y), Quartz.kCGMouseButtonLeft
            )
            up_event = Quartz.CGEventCreateMouseEvent(
                None, Quartz.kCGEventLeftMouseUp, (x, y), Quartz.kCGMouseButtonLeft
            )

            if event_type == "down":
                self._left_pressed = True
            else:
                self._left_pressed = False

        elif button == "right":
            down_event = Quartz.CGEventCreateMouseEvent(
                None, Quartz.kCGEventRightMouseDown, (x, y), Quartz.kCGMouseButtonRight
            )
            up_event = Quartz.CGEventCreateMouseEvent(
                None, Quartz.kCGEventRightMouseUp, (x, y), Quartz.kCGMouseButtonRight
            )
        else:
            raise ValueError(f"Unsupported button: {button}")

        if event_type == "down":
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, down_event)
        elif event_type == "up":
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, up_event)
        elif event_type == "click":
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, down_event)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, up_event)
        else:
            raise ValueError(f"Unsupported event type: {event_type}")

        logger.debug(f"Performed {event_type} event for {button} button at ({x}, {y})")
