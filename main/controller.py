import cv2
import logging
import numpy as np
from PySide6.QtCore import Qt
from share.utils import merge_landmarks
from share.mediapipe_utils import np_to_normalized_landmark, draw_landmarks_on_frame
from share.singleton.camera import get_camera_singleton, close_camera_singleton
from share.worker.landmarker import Landmarker
from share.worker.smoother import EMASmoother
from share.worker.landmark_mapper import LandmarkMapper
from share.worker.gesture_mapper import GestureMapper, MouseEvent
from share.worker.mouse_controller import MouseController
from gesture_model.model_runner import GestureModelRunner
from gesture_model import AbstractGestureModel
from main.view import MainAppView


logger = logging.getLogger(__name__)


class MainAppController:
    def __init__(self, view: MainAppView, model: AbstractGestureModel, model_path: str):
        self.view = view

        self.camera = get_camera_singleton()
        self.camera.frame_ready.connect(self._on_frame_ready)
        self.landmarker = Landmarker()
        self.landmarker.landmark_update.connect(self._on_landmark_update)
        self.smoother = EMASmoother()
        self.reset_after_undetect = 10
        self.undetected_count = 0

        self.landmark_mapper = LandmarkMapper(
            self.view.pointer_overlay.width(), self.view.pointer_overlay.height()
        )
        self.model = model
        self.gesture_model = GestureModelRunner(self.model, model_path, "cpu")
        self.gesture_mapper = GestureMapper()
        self.landmarks_queue = []
        self.max_queue_length = self.model.WINDOW_LENGTH + 5  # some buffer

    def _on_frame_ready(self, payload):
        timestamp, frame = payload
        self.landmarker.detect_async(frame, timestamp)

    def _on_landmark_update(self, payload):
        timestamp, frame, result = payload

        right_hand_detected = (
            len(result.hand_landmarks) > 0
            and result.handedness[0][0].category_name == "Right"
        )

        if right_hand_detected:
            if self.undetected_count > self.reset_after_undetect:
                self.smoother.reset()
                self.landmark_mapper.reset()
            self.undetected_count = 0

            # process landmarks
            landmarks = merge_landmarks(
                result.hand_landmarks[0], result.hand_world_landmarks[0]
            )
            smoothed_landmarks = self.smoother.update(landmarks)
            frame = draw_landmarks_on_frame(
                frame, np_to_normalized_landmark(smoothed_landmarks)
            )
            self.landmarks_queue.append(smoothed_landmarks)
            if len(self.landmarks_queue) > self.max_queue_length:
                self.landmarks_queue.pop(0)

            # pointer mapping
            screen_pos = self.landmark_mapper.mapping_use_palm(smoothed_landmarks)
            logger.debug(f"Pointer mapped to screen position: {screen_pos}")

            # gesture recognition
            if len(self.landmarks_queue) < self.model.WINDOW_LENGTH:
                return
            landmarks_window = self.landmarks_queue[
                -self.model.WINDOW_LENGTH :
            ]  # get last WINDOW_LENGTH frames
            landmarks_window = np.stack(landmarks_window, axis=0)
            gesture_label = self.gesture_model.inference(landmarks_window)
            logger.debug(f"Gesture detected: {gesture_label.name}")

            mouse_event = self.gesture_mapper.update(gesture_label)
            self.perform_mouse_event(mouse_event, screen_pos)
            self.view.set_overlay_text(
                f"Pointer: {screen_pos}\t\tGesture: {gesture_label.name}\t\tMouse Event: {mouse_event.name}"
            )

        else:
            self.undetected_count += 1

        frame = cv2.flip(frame, 1)
        self.view.cam_preview.update_camera_preview(frame)

    def perform_mouse_event(
        self, mouse_event: MouseEvent, pointer_pos: tuple[int, int]
    ):
        if mouse_event == MouseEvent.MOVE:
            MouseController.mouse_move(*pointer_pos)
            self.view.pointer_overlay.update_pointer_position(pointer_pos)
        elif mouse_event == MouseEvent.LEFT_PRESS:
            MouseController.mouse_button_event(*pointer_pos, down=True, button="left")
        elif mouse_event == MouseEvent.LEFT_RELEASE:
            MouseController.mouse_button_event(*pointer_pos, down=False, button="left")
        elif mouse_event == MouseEvent.RIGHT_PRESS:
            MouseController.mouse_button_event(*pointer_pos, down=True, button="right")
        elif mouse_event == MouseEvent.RIGHT_RELEASE:
            MouseController.mouse_button_event(*pointer_pos, down=False, button="right")

    def keyPressEvent(self, key):
        if key == Qt.Key.Key_Escape:  # exit app
            logger.debug("Escape key pressed. Exiting application.")
            self.view.close()

    def close(self):
        close_camera_singleton()
        self.landmarker.close()
