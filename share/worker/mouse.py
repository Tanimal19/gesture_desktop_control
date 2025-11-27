import Quartz
import logging
from enum import Enum
from gesture_model.model import GestureLabel

logger = logging.getLogger(__name__)


class MouseEvent(Enum):
    NONE = 0
    LEFT_PRESS = 1
    LEFT_RELEASE = 2
    RIGHT_PRESS = 3
    RIGHT_RELEASE = 4
    SCROLL_UP = 5
    SCROLL_DOWN = 6


class MouseController:
    """A class to control mouse actions based on gesture labels."""

    GESTURE_CONFIRMATION_THRESHOLD = (
        {  # Number of consecutive frames to confirm a gesture
            GestureLabel.LEFT_PRESS: 5,
            GestureLabel.LEFT_RELEASE: 5,
            GestureLabel.RIGHT_PRESS: 5,
            GestureLabel.RIGHT_RELEASE: 5,
            GestureLabel.SCROLL_UP: 7,
            GestureLabel.SCROLL_DOWN: 7,
        }
    )

    SCROLL_RESET_THRESHOLD = 5  # Number of non-scroll frames to reset scroll direction

    def __init__(self):
        self.current_gesture = GestureLabel.NONE
        self.current_consecutive_count = 0
        self.current_start_pos = (0, 0)

        self.scroll_direction = None
        self.non_scroll_count = 0

    def update(
        self, new_label: GestureLabel, pointer_pos: tuple[int, int]
    ) -> MouseEvent:

        # ------ scroll logic ------
        if new_label not in [GestureLabel.SCROLL_DOWN, GestureLabel.SCROLL_UP]:
            self.non_scroll_count += 1
            if self.non_scroll_count >= self.SCROLL_RESET_THRESHOLD:
                self.scroll_direction = None
        else:
            self.non_scroll_count = 0

        # ------ gesture transition ------
        event = MouseEvent.NONE
        if new_label != self.current_gesture:
            prev_gesture = self.current_gesture
            prev_count = self.current_consecutive_count

            self.current_gesture = new_label
            self.current_consecutive_count = 1
            self.current_start_pos = pointer_pos

            if self._is_valid_gesture(prev_gesture, prev_count):
                event = self._perform_gesture(prev_gesture)
        else:
            self.current_consecutive_count += 1

        if event == MouseEvent.NONE:
            self._move_mouse(*pointer_pos)

        return event

    def _is_valid_gesture(self, gesture: GestureLabel, consecutive_frame: int) -> bool:
        if gesture == GestureLabel.NONE:
            return False

        if consecutive_frame >= self.GESTURE_CONFIRMATION_THRESHOLD[gesture]:
            return True
        else:
            return False

    def _perform_gesture(self, gesture: GestureLabel) -> MouseEvent:
        event = MouseEvent.NONE

        if gesture == GestureLabel.LEFT_PRESS:
            self._left_press(*self.current_start_pos)
            event = MouseEvent.LEFT_PRESS

        elif gesture == GestureLabel.LEFT_RELEASE:
            self._left_release()
            event = MouseEvent.LEFT_RELEASE

        elif gesture == GestureLabel.RIGHT_PRESS:
            self._right_press(*self.current_start_pos)
            event = MouseEvent.RIGHT_PRESS

        elif gesture == GestureLabel.RIGHT_RELEASE:
            self._right_release()
            event = MouseEvent.RIGHT_RELEASE

        elif gesture == GestureLabel.SCROLL_UP:
            if self.scroll_direction is None:
                self.scroll_direction = "UP"
            if self.scroll_direction == "UP":
                self._scroll_up()
                event = MouseEvent.SCROLL_UP

        elif gesture == GestureLabel.SCROLL_DOWN:
            if self.scroll_direction is None:
                self.scroll_direction = "DOWN"
            if self.scroll_direction == "DOWN":
                self._scroll_down()
                event = MouseEvent.SCROLL_DOWN

        return event

    @staticmethod
    def _move_mouse(x, y):
        logger.info(f"Moving mouse to ({x}, {y})")
        mouse_move(x, y)

    @staticmethod
    def _left_press(x, y):
        logger.info("Left mouse button pressed")
        # pyautogui.mouseDown(x, y, button="left")

    @staticmethod
    def _left_release():
        logger.info("Left mouse button released")
        # pyautogui.mouseUp(button="left")

    @staticmethod
    def _right_press(x, y):
        logger.info("Right mouse button pressed")
        # pyautogui.mouseDown(x, y, button="right")

    @staticmethod
    def _right_release():
        logger.info("Right mouse button released")
        # pyautogui.mouseUp(button="right")

    @staticmethod
    def _scroll_up(amount=100):
        logger.info("Scrolling up")
        # pyautogui.scroll(amount)

    @staticmethod
    def _scroll_down(amount=100):
        logger.info("Scrolling down")
        # pyautogui.scroll(-amount)


def mouse_move(x, y):
    # macOS coordinate: origin bottom-left; need convert
    # Get screen height to flip coordinate
    screen = Quartz.CGDisplayBounds(Quartz.CGMainDisplayID())

    Quartz.CGWarpMouseCursorPosition((x, y))
    Quartz.CGAssociateMouseAndMouseCursorPosition(True)


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


def mouse_scroll(amount):
    # Positive = up, negative = down
    event = Quartz.CGEventCreateScrollWheelEvent(
        None,
        Quartz.kCGScrollEventUnitLine,
        1,  # number of wheels (vertical only)
        amount,  # positive = up
    )
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
