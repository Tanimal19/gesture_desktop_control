import csv
from PySide6.QtCore import QObject, Signal
import mediapipe as mp
from mediapipe.tasks.python.vision.hand_landmarker import (
    HandLandmarker,
    HandLandmarkerOptions,
    HandLandmarkerResult,
    HandLandmark,
)
from mediapipe.tasks.python.vision.core.vision_task_running_mode import (
    VisionTaskRunningMode as RunningMode,
)
from numpy.typing import NDArray as Mat
import logging


logger = logging.getLogger(__name__)


class Landmarker(QObject):
    landmark_update = Signal(object)

    def __init__(self, output_csv=None):
        super().__init__()

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

    def process_result(
        self, result: HandLandmarkerResult, frame: mp.Image, timestamp: int
    ):
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
        frame = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        try:
            self.landmarker.detect_async(frame, timestamp)
        except Exception as e:
            logger.error(f"Failed to detect landmarks: {e}")

    def close(self):
        self.landmarker.close()
