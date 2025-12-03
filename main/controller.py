import logging
import numpy as np
from share.utils import merge_landmarks
from share.mediapipe_utils import np_to_normalized_landmark, draw_landmarks_on_frame
from share.worker.camera import get_camera_singleton, close_camera_singleton
from share.worker.landmarker import Landmarker
from share.worker.smoother import EMASmoother
from share.worker.landmark_mapper import LandmarkMapper
from share.worker.gesture_mapper import GestureMapper, MouseEvent
from share.mouse_server.client import MouseServerClient
from share.gesture_model.model_runner import GestureModelRunner
from share.gesture_model import AbstractGestureModel
from main.view import MainAppView


logger = logging.getLogger(__name__)


class MainAppController:
    def __init__(self, model: AbstractGestureModel, model_path: str):
        self.view = MainAppView()
        self.view.set_controller(self)

        # camera and hand landmarker
        self.camera = get_camera_singleton()
        self.camera.frame_ready.connect(self._on_frame_ready)
        self.landmarker = Landmarker()
        self.landmarker.landmark_update.connect(self._on_landmark_update)
        self.smoother = EMASmoother()
        self.reset_after_undetect = 10
        self.undetected_count = 0

        # landmark mapper to screen position
        self.landmark_mapper = LandmarkMapper(
            self.view.screen_width, self.view.screen_height
        )

        # gesture model
        self.model = model
        self.gesture_model = GestureModelRunner(self.model, model_path, "cpu")
        self.gesture_mapper = GestureMapper()
        self.landmarks_queue = []
        self.max_queue_length = self.model.WINDOW_LENGTH + 5  # some buffer

        # mouse server client
        self.mouse_cilent = MouseServerClient()
        if not self.mouse_cilent.connect():
            logger.error("Failed to connect to mouse server client")
            self.close()
            raise ConnectionError("Cannot connect to mouse server")

        self.mouse_control_enabled = False

        # show view
        self.view.show()
        self.view.setFocus()
        self.view.raise_()

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
            self.view.update_overlay_info(
                gesture=gesture_label.name,
                pointer_pos=screen_pos,
                mouse_event=mouse_event.name,
            )

        else:
            self.undetected_count += 1

        # frame = cv2.flip(frame, 1)
        # self.view.camera_preview.update_camera_preview(frame)

    def toggle_mouse_control(self):
        self.mouse_control_enabled = not self.mouse_control_enabled
        logger.info(
            f"Mouse control {'enabled' if self.mouse_control_enabled else 'disabled'}"
        )

    def perform_mouse_event(
        self, mouse_event: MouseEvent, pointer_pos: tuple[int, int]
    ):
        if not self.mouse_control_enabled:
            return

        self.mouse_cilent.move_mouse(*pointer_pos)

        if mouse_event == MouseEvent.LEFT_PRESS:
            self.mouse_cilent.button_event(*pointer_pos, down=True, button="left")
        elif mouse_event == MouseEvent.LEFT_RELEASE:
            self.mouse_cilent.button_event(*pointer_pos, down=False, button="left")
        elif mouse_event == MouseEvent.RIGHT_PRESS:
            self.mouse_cilent.button_event(*pointer_pos, down=True, button="right")
        elif mouse_event == MouseEvent.RIGHT_RELEASE:
            self.mouse_cilent.button_event(*pointer_pos, down=False, button="right")

    def close(self):
        close_camera_singleton()
        self.landmarker.close()
        self.mouse_cilent.disconnect()
