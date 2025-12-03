import numpy as np
from numpy.typing import NDArray as Mat
from enum import Enum
import logging
from mediapipe.python.solutions import drawing_utils, hands, drawing_styles


def setup_logging(filepath=None):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    if filepath:
        file_handler = logging.FileHandler(filepath, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(module)s.%(funcName)s(): %(message)s"
        )
        file_handler.setFormatter(file_fmt)
        logger.addHandler(file_handler)


def np_to_normalized_landmark(arr):
    return [landmark_pb2.NormalizedLandmark(x=x, y=y, z=z) for x, y, z in arr]  # type: ignore


# simulate mediapipe.tasks.python.vision.hand_landmarker.HandLandmark
class HandLandmark(Enum):
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_FINGER_MCP = 5
    INDEX_FINGER_PIP = 6
    INDEX_FINGER_DIP = 7
    INDEX_FINGER_TIP = 8
    MIDDLE_FINGER_MCP = 9
    MIDDLE_FINGER_PIP = 10
    MIDDLE_FINGER_DIP = 11
    MIDDLE_FINGER_TIP = 12
    RING_FINGER_MCP = 13
    RING_FINGER_PIP = 14
    RING_FINGER_DIP = 15
    RING_FINGER_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20


def merge_landmarks(hand_landmarks, world_landmarks):
    return np.array(
        [
            [norm.x, norm.y, world.z]
            for norm, world in zip(
                hand_landmarks,
                world_landmarks,
            )
        ]
    )


def draw_landmarks_on_frame(frame: Mat, landmarks) -> np.ndarray:

    if (
        type(landmarks) is not list[landmark_pb2.NormalizedLandmark]  # type: ignore
        and len(landmarks) != 21
    ):
        return frame

    annotated_frame = np.copy(frame)

    hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()  # type: ignore
    hand_landmarks_proto.landmark.extend(
        [
            landmark_pb2.NormalizedLandmark(  # type: ignore
                x=landmark.x, y=landmark.y, z=0
            )
            for landmark in landmarks
        ]
    )
    drawing_utils.draw_landmarks(
        annotated_frame,
        hand_landmarks_proto,
        list(hands.HAND_CONNECTIONS),
        drawing_styles.get_default_hand_landmarks_style(),
        drawing_styles.get_default_hand_connections_style(),
    )

    return annotated_frame
