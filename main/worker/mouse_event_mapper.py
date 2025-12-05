import numpy as np
from enum import Enum
from main.utils import HandLandmark
import logging

logger = logging.getLogger(__name__)


class MouseEvent(Enum):
    MOVE = 1
    LEFT_PRESS = 2
    LEFT_RELEASE = 3
    LEFT_CLICK = 4
    RIGHT_PRESS = 5
    RIGHT_RELEASE = 6
    RIGHT_CLICK = 7


class MouseEventMapper:
    """Directly map landmark windows to mouse events based on rules"""

    WINDOW_SIZE = 3  # number of frames to get average distance
    WINDOW_OVERLAP_SIZE = 0  # number of frames between current and past window
    WINDOW_LENGTH = WINDOW_SIZE + WINDOW_SIZE - WINDOW_OVERLAP_SIZE

    PRESS_DISTANCE_THRESHOLD = {"left": 0.11, "right": 0.16}
    CLICK_MERGE_THRESHOLD = (
        6  # number of frames to merge sequential press/release events
    )

    def __init__(self):
        self.landmarks_queue = []
        self.prev_detected_mouse_event = MouseEvent.MOVE
        self.onhold_frames = 0
        self.onhold_event = None
        self.current_button_context = None  # "left" or "right"

    @staticmethod
    def compute_distance(
        landmarks_window: np.ndarray, l1: HandLandmark, l2: HandLandmark
    ) -> np.ndarray:
        l1pos = landmarks_window[:, l1.value, :]
        l2pos = landmarks_window[:, l2.value, :]
        distances = np.linalg.norm(l1pos - l2pos, axis=1)
        return distances

    @staticmethod
    def is_press(current_distance, past_distance, btn):
        return (
            current_distance < MouseEventMapper.PRESS_DISTANCE_THRESHOLD[btn]
            and MouseEventMapper.PRESS_DISTANCE_THRESHOLD[btn] < past_distance
        )

    @staticmethod
    def is_release(current_distance, past_distance, btn):
        return (
            current_distance > MouseEventMapper.PRESS_DISTANCE_THRESHOLD[btn]
            and MouseEventMapper.PRESS_DISTANCE_THRESHOLD[btn] > past_distance
        )

    def detect(self, landmarks_window: np.ndarray) -> MouseEvent:
        ti_distances = MouseEventMapper.compute_distance(
            landmarks_window, HandLandmark.THUMB_TIP, HandLandmark.INDEX_FINGER_TIP
        )
        tm_distances = MouseEventMapper.compute_distance(
            landmarks_window, HandLandmark.THUMB_TIP, HandLandmark.MIDDLE_FINGER_TIP
        )

        current_ti_distance = np.mean(ti_distances[-3:])
        past_ti_distance = np.mean(ti_distances[0:3])
        current_tm_distance = np.mean(tm_distances[-3:])
        past_tm_distance = np.mean(tm_distances[0:3])

        logger.debug(f"thumb-index distances: {current_ti_distance}")
        logger.debug(f"thumb-middle distances: {current_tm_distance}")

        # detect press and release, right button events have higher priority, since we found that when middle finger approaches thumb, both index and middle distance decrease, but when index finger approaches thumb, only index distance decreases.
        if MouseEventMapper.is_press(current_tm_distance, past_tm_distance, "right"):
            return MouseEvent.RIGHT_PRESS
        if (
            MouseEventMapper.is_release(current_tm_distance, past_tm_distance, "right")
            and self.current_button_context != "left"
        ):
            return MouseEvent.RIGHT_RELEASE

        if MouseEventMapper.is_press(current_ti_distance, past_ti_distance, "left"):
            return MouseEvent.LEFT_PRESS
        if (
            MouseEventMapper.is_release(current_ti_distance, past_ti_distance, "left")
            and self.current_button_context != "right"
        ):
            return MouseEvent.LEFT_RELEASE

        return MouseEvent.MOVE

    def perform(self, detected_event: MouseEvent) -> MouseEvent:
        # we perform event only when we confirmed it ends
        if detected_event != self.prev_detected_mouse_event:
            # context switching, perform previously detected event
            performed_event = self.prev_detected_mouse_event
            self.prev_detected_mouse_event = detected_event

            # however, if the performed event is press, we see if the release comes in few frames
            if performed_event in [MouseEvent.LEFT_PRESS, MouseEvent.RIGHT_PRESS]:
                self.onhold_frames = 0
                self.onhold_event = performed_event
                performed_event = MouseEvent.MOVE  # do not perform press yet
        else:
            self.onhold_frames += 1
            performed_event = MouseEvent.MOVE

        # if release comes in few frames after press, merge to click
        if self.onhold_frames <= MouseEventMapper.CLICK_MERGE_THRESHOLD:
            if detected_event in [MouseEvent.LEFT_RELEASE, MouseEvent.RIGHT_RELEASE]:
                # merge press and release to click
                if self.onhold_event == MouseEvent.LEFT_PRESS:
                    performed_event = MouseEvent.LEFT_CLICK
                elif self.onhold_event == MouseEvent.RIGHT_PRESS:
                    performed_event = MouseEvent.RIGHT_CLICK
                self.onhold_event = None
        else:
            # release the onhold press event
            if self.onhold_event == MouseEvent.LEFT_PRESS:
                performed_event = MouseEvent.LEFT_PRESS
            elif self.onhold_event == MouseEvent.RIGHT_PRESS:
                performed_event = MouseEvent.RIGHT_PRESS
            self.onhold_event = None

        return performed_event

    def update(self, landmarks: np.ndarray) -> MouseEvent:
        assert landmarks.shape[0] == len(HandLandmark) and landmarks.shape[1] == 3

        # update
        self.landmarks_queue.append(landmarks)
        if len(self.landmarks_queue) > MouseEventMapper.WINDOW_LENGTH:
            self.landmarks_queue.pop(0)

        # build landmarks window
        if len(self.landmarks_queue) < MouseEventMapper.WINDOW_LENGTH:
            return MouseEvent.MOVE
        landmarks_window = self.landmarks_queue[-MouseEventMapper.WINDOW_LENGTH :]
        landmarks_window = np.stack(landmarks_window, axis=0)

        detected_event = self.detect(landmarks_window)
        logger.debug(f"detected mouse event: {detected_event}")
        performed_event = self.perform(detected_event)
        logger.debug(f"performed mouse event: {performed_event}")

        if performed_event in [
            MouseEvent.LEFT_PRESS,
            MouseEvent.LEFT_CLICK,
        ]:
            self.current_button_context = "left"
            logger.debug(f"Current button context set to LEFT")
        elif performed_event in [
            MouseEvent.RIGHT_PRESS,
            MouseEvent.RIGHT_CLICK,
        ]:
            self.current_button_context = "right"
            logger.debug(f"Current button context set to RIGHT")
        elif performed_event in [
            MouseEvent.LEFT_RELEASE,
            MouseEvent.RIGHT_RELEASE,
        ]:
            self.current_button_context = None

        return performed_event
