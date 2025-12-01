import Quartz
import logging

logger = logging.getLogger(__name__)


class MouseController:
    _left_pressed = False

    def move(self, x, y):
        if self._left_pressed:
            # dragging
            btn = Quartz.kCGMouseButtonLeft
            ev_type = Quartz.kCGEventLeftMouseDragged
            event = Quartz.CGEventCreateMouseEvent(None, ev_type, (x, y), btn)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
            logger.debug(f"Dragged mouse to ({x}, {y})")

        else:
            self._left_pressed = False
            Quartz.CGWarpMouseCursorPosition((x, y))
            Quartz.CGAssociateMouseAndMouseCursorPosition(True)
            logger.debug(f"Moved mouse to ({x}, {y})")

    def button_event(self, x, y, down=True, button="left"):
        if button == "left":
            btn = Quartz.kCGMouseButtonLeft
            if down:
                ev_type = Quartz.kCGEventLeftMouseDown
            else:
                ev_type = Quartz.kCGEventLeftMouseUp
        elif button == "right":
            btn = Quartz.kCGMouseButtonRight
            if down:
                ev_type = Quartz.kCGEventRightMouseDown
            else:
                ev_type = Quartz.kCGEventRightMouseUp
        else:
            raise ValueError(f"Unsupported button: {button}")

        if button == "left" and down:
            self._left_pressed = True
        else:
            self._left_pressed = False

        event = Quartz.CGEventCreateMouseEvent(None, ev_type, (x, y), btn)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)

        logger.debug(f"{"Press" if down else "Release"} {button} button at {(x, y)}")
