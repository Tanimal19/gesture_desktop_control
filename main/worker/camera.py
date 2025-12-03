# using opencv to capture camera frame
import cv2
import time
from PySide6.QtCore import QThread, Signal
import logging


logger = logging.getLogger(__name__)


class CameraSingleton(QThread):
    """
    A singleton thread to capture camera frames and emit them via signal.
    """

    frame_ready = Signal(object)

    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        if not self.cap.isOpened():
            logger.error("Cannot open camera")
            return

        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        logger.debug(f"camera fps: {self.fps}")

        self.video_writer = None
        self.recording = False
        self.running = True

    def run(self):
        timestamp_start = time.time()
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            timestamp = int((time.time() - timestamp_start) * 1000)
            logger.debug(f"Captured frame at timestamp: {timestamp}")
            self.frame_ready.emit((timestamp, frame))

            if self.recording and self.video_writer is not None:
                try:
                    self.video_writer.write(frame)
                except Exception as e:
                    logger.error(f"Unable to write frame: {e}")

        self.cap.release()

    def start_recording(self, output_video: str):
        self.recording = True
        self.video_writer = cv2.VideoWriter(
            output_video,
            cv2.VideoWriter_fourcc(*"mp4v"),  # type: ignore
            self.fps,
            (
                int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            ),
        )
        logger.debug(f"Started recording to {output_video}")

    def stop_recording(self):
        self.recording = False
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
        logger.debug("Stopped recording")

    def stop(self):
        self.running = False
        if self.recording:
            self.stop_recording()


_camera_singleton = None


def get_camera_singleton():
    global _camera_singleton
    if _camera_singleton is None:
        _camera_singleton = CameraSingleton()
        _camera_singleton.start()
        logger.debug("CameraSingleton started.")
    return _camera_singleton


def close_camera_singleton():
    global _camera_singleton
    if _camera_singleton is not None:
        _camera_singleton.stop()
        _camera_singleton.wait()
        _camera_singleton = None
        logger.debug("CameraSingleton stopped.")
