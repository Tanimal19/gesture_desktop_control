import Quartz
import logging
from enum import Enum
from gesture_model.model import GestureLabel
from share.worker.mouse_controller import MouseController

logger = logging.getLogger(__name__)


class MouseEvent(Enum):
    MOVE = 1
    LEFT_PRESS = 2
    LEFT_RELEASE = 3
    RIGHT_PRESS = 4
    RIGHT_RELEASE = 5
    SCROLL_UP = 6
    SCROLL_DOWN = 7


class GestureMapper:
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
        event = MouseEvent.MOVE
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

        return event

    def _is_valid_gesture(self, gesture: GestureLabel, consecutive_frame: int) -> bool:
        if gesture == GestureLabel.NONE:
            return False

        if consecutive_frame >= self.GESTURE_CONFIRMATION_THRESHOLD[gesture]:
            return True
        else:
            return False

    def _perform_gesture(self, gesture: GestureLabel) -> MouseEvent:
        if gesture == GestureLabel.LEFT_PRESS:
            return MouseEvent.LEFT_PRESS

        elif gesture == GestureLabel.LEFT_RELEASE:
            return MouseEvent.LEFT_RELEASE

        elif gesture == GestureLabel.RIGHT_PRESS:
            return MouseEvent.RIGHT_PRESS

        elif gesture == GestureLabel.RIGHT_RELEASE:
            return MouseEvent.RIGHT_RELEASE

        elif gesture == GestureLabel.SCROLL_UP:
            if self.scroll_direction is None:
                self.scroll_direction = "UP"
            if self.scroll_direction == "UP":
                return MouseEvent.SCROLL_UP

        elif gesture == GestureLabel.SCROLL_DOWN:
            if self.scroll_direction is None:
                self.scroll_direction = "DOWN"
            if self.scroll_direction == "DOWN":
                return MouseEvent.SCROLL_DOWN

        return MouseEvent.MOVE
