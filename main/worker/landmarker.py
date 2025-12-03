import csv
from PySide6.QtCore import QObject, Signal
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python.vision.hand_landmarker import (
    HandLandmarker,
    HandLandmarkerOptions,
    HandLandmarkerResult,
)
from mediapipe.tasks.python.vision.core.vision_task_running_mode import (
    VisionTaskRunningMode as RunningMode,
)
from numpy.typing import NDArray as Mat
from main.utils import HandLandmark
import logging


logger = logging.getLogger(__name__)


class Landmarker(QObject):
    """
    Detect hand landmarks from video frames asynchronously using MediaPipe HandLandmarker.\n
    Usage:\n
        landmarker = Landmarker()
        landmarker.landmark_update.connect(your_callback_function)
        landmarker.detect_async(frame, timestamp)
    """

    landmark_update = Signal(object)

    def __init__(self, output_csv=None):
        super().__init__()
        self._active = False

        try:
            options = HandLandmarkerOptions(
                base_options=mp.tasks.BaseOptions(
                    model_asset_path="hand_landmarker.task"
                ),
                running_mode=RunningMode.LIVE_STREAM,
                num_hands=1,
                min_hand_detection_confidence=0.4,
                min_hand_presence_confidence=0.4,
                min_tracking_confidence=0.4,
                result_callback=self.process_result,
            )
            self.landmarker = HandLandmarker.create_from_options(options)
            self._warm_up()
            self._active = True
            logger.info("HandLandmarker started successfully")

        except Exception as e:
            logger.error(f"Failed to create HandLandmarker: {e}")
            return

        self.output_csv = output_csv
        if self.output_csv:
            with open(self.output_csv, "w") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["timestamp"]
                    + [lm.name for lm in HandLandmark]
                    + [("WORLD_" + lm.name) for lm in HandLandmark]
                )

    def _warm_up(self):
        import numpy as np

        dummy = np.zeros((10, 10, 3), dtype=np.uint8)
        img = mp.Image(image_format=mp.ImageFormat.SRGB, data=dummy)

        try:
            self.landmarker.detect(img)
        except Exception as e:
            logger.error("Warm-up failed:", e)

    def process_result(
        self, result: HandLandmarkerResult, frame: mp.Image, timestamp: int
    ):
        if not self._active:
            return

        self.landmark_update.emit((timestamp, frame.numpy_view(), result))

        if self.output_csv:
            with open(self.output_csv, "a", newline="") as f:
                writer = csv.writer(f)
                if result.hand_landmarks:
                    landmarks = result.hand_landmarks[0]
                    world_landmarks = result.hand_world_landmarks[0]
                    row = [str(timestamp)]
                    for lm in landmarks + world_landmarks:
                        row.append(f"{lm.x}_{lm.y}_{lm.z}")
                    writer.writerow(row)

    def detect_async(self, frame: Mat, timestamp: int):
        if not self._active:
            return

        frame = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        try:
            self.landmarker.detect_async(frame, timestamp)
        except Exception as e:
            logger.error(f"Failed to detect landmarks: {e}")

    def close(self):
        self._active = False
        self.landmarker.close()


class LandmarkSmoother:
    """
    Smooth landmarks using Exponential Moving Average (EMA) filter.
    """

    def __init__(self, alpha=0.5, jump_thresh=1.5):
        self.alpha = alpha
        self.jump_thresh = jump_thresh
        self.prev = None

    def update(self, landmarks: np.ndarray) -> np.ndarray:
        assert landmarks.shape == (len(HandLandmark), 3)

        if self.prev is None:
            self.prev = landmarks
            return landmarks

        vel = np.linalg.norm(landmarks - self.prev)
        logger.debug(f"velocity={vel}")
        if vel > self.jump_thresh:
            logger.debug("jump detected")
            return self.prev

        smoothed = self.alpha * landmarks + (1 - self.alpha) * self.prev
        self.prev = smoothed.copy()

        return smoothed

    def reset(self):
        self.prev = None
