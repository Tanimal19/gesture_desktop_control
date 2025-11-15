# utils.py
import numpy as np
import logging
from mediapipe.framework.formats import landmark_pb2
from mediapipe.python.solutions import drawing_utils, hands, drawing_styles
from numpy.typing import NDArray as Mat

logger = logging.getLogger(__name__)


def draw_landmarks_on_frame(frame: Mat, landmarks) -> np.ndarray:

    if (
        type(landmarks) is not list[landmark_pb2.NormalizedLandmark]  # type: ignore
        and len(landmarks) != 21
    ):
        logger.warning("Unsupport format")
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


def landmark_to_np(landmarks):
    return np.array([[lm.x, lm.y, lm.z] for lm in landmarks])


def np_to_normalized_landmark(arr):
    return [landmark_pb2.NormalizedLandmark(x=x, y=y, z=z) for x, y, z in arr]  # type: ignore


def np_to_world_landmark(arr):
    return [landmark_pb2.Landmark(x=x, y=y, z=z) for x, y, z in arr]  # type: ignore
