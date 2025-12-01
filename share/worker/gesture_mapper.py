import logging
from enum import Enum
from gesture_model import GestureLabel

logger = logging.getLogger(__name__)


class MouseEvent(Enum):
    MOVE = 1
    LEFT_PRESS = 2
    LEFT_RELEASE = 3
    RIGHT_PRESS = 4
    RIGHT_RELEASE = 5


class GestureMapper:
    GESTURE_CONFIRMATION_THRESHOLD = (
        {  # Number of consecutive frames to confirm a gesture
            GestureLabel.LEFT_PRESS: 3,
            GestureLabel.LEFT_RELEASE: 3,
            GestureLabel.RIGHT_PRESS: 3,
            GestureLabel.RIGHT_RELEASE: 3,
        }
    )
    SCROLL_RESET_THRESHOLD = 5  # Number of non-scroll frames to reset scroll direction

    def __init__(self):
        self.current_gesture = GestureLabel.NONE
        self.current_consecutive_count = 0

        self.scroll_direction = None
        self.non_scroll_count = 0

    def update(self, new_label: GestureLabel) -> MouseEvent:
        # ------ gesture transition ------
        event = MouseEvent.MOVE
        if new_label != self.current_gesture:
            prev_gesture = self.current_gesture
            prev_count = self.current_consecutive_count

            self.current_gesture = new_label
            self.current_consecutive_count = 1

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

        return MouseEvent.MOVE
