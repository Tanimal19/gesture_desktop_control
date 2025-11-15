from enum import Enum


class GestureType(Enum):
    NONE = 0
    POINT = 1
    LEFT_PRESS = 2
    LEFT_RELEASE = 3
    RIGHT_PRESS = 4
    RIGHT_RELEASE = 5
    SCROLL_UP = 6
    SCROLL_DOWN = 7


class GestureClassificationRule:
    def __init__(self):

        self.sequence_min_length = 5
        pass

    def apply_rule(self, landmarks_sequence):

        if len(landmarks_sequence) < self.sequence_min_length:
            return GestureType.NONE

        last_landmark = landmarks_sequence[-1]

        # Example rule: If the last landmark indicates a pointing gesture
        if self.is_pointing_gesture(last_landmark):
            return GestureType.POINT

        # Additional rules can be added here

        return GestureType.NONE
