import Quartz
import logging

logger = logging.getLogger(__name__)


class MouseController:
    @staticmethod
    def mouse_move(x, y):
        # macOS coordinate: origin bottom-left; need convert
        # Get screen height to flip coordinate
        screen = Quartz.CGDisplayBounds(Quartz.CGMainDisplayID())

        Quartz.CGWarpMouseCursorPosition((x, y))
        Quartz.CGAssociateMouseAndMouseCursorPosition(True)

        logger.debug(f"Moving mouse to ({x}, {y})")

    @staticmethod
    def mouse_button_event(x, y, down, button="left"):
        screen = Quartz.CGDisplayBounds(Quartz.CGMainDisplayID())
        screen_height = screen.size.height
        pos = (x, screen_height - y)

        if button == "left":
            btn = Quartz.kCGMouseButtonLeft
            ev_type_down = Quartz.kCGEventLeftMouseDown
            ev_type_up = Quartz.kCGEventLeftMouseUp
        else:
            btn = Quartz.kCGMouseButtonRight
            ev_type_down = Quartz.kCGEventRightMouseDown
            ev_type_up = Quartz.kCGEventRightMouseUp

        event_type = ev_type_down if down else ev_type_up
        event = Quartz.CGEventCreateMouseEvent(None, event_type, pos, btn)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)

        logger.debug(
            f"{'Pressed' if down else 'Released'} {button} mouse button at ({x}, {y})"
        )

    # @staticmethod
    # def mouse_scroll(amount):
    #     # Positive = up, negative = down
    #     event = Quartz.CGEventCreateScrollWheelEvent(
    #         None,
    #         Quartz.kCGScrollEventUnitLine,
    #         1,  # number of wheels (vertical only)
    #         amount,  # positive = up
    #     )
    #     Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)

    #     logger.debug(f"Scrolled mouse by amount: {amount}")
