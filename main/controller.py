import cv2
import logging
from share.utils import merge_landmarks
from share.mediapipe_utils import np_to_normalized_landmark, draw_landmarks_on_frame
from share.worker.camera import get_camera_singleton, close_camera_singleton
from share.worker.landmarker import Landmarker, LandmarkSmoother
from share.worker.pointer_mapper import PointerLandmarkMapper
from share.worker.mouse_event_mapper import (
    MouseEventGestureMapper,
    MouseEventRuleBaseMapper,
    MouseEvent,
)
from share.gesture_model.model_runner import GestureModelRunner
from share.gesture_model import AbstractGestureModel
from share.mouse_server.client import MouseServerClient
from main.view import MainAppView


logger = logging.getLogger(__name__)


class MainAppController:
    def __init__(
        self,
        model_class: type[AbstractGestureModel],
        model_path: str,
        rule_base_enable: bool,
    ):
        self.view = MainAppView()
        self.view.set_controller(self)

        # camera and hand landmarker
        self.camera = get_camera_singleton()
        self.camera.frame_ready.connect(self._on_frame_ready)
        self.landmarker = Landmarker()
        self.landmarker.landmark_update.connect(self._on_landmark_update)
        self.smoother = LandmarkSmoother()
        self.reset_after_undetect = 10
        self.undetected_count = 0

        # landmark mapper to screen position
        self.landmark_mapper = PointerLandmarkMapper(
            self.view.screen_width, self.view.screen_height
        )

        self.rule_base_enable = rule_base_enable
        if not rule_base_enable:
            # gesture model
            self.model_class = model_class
            self.gesture_model = GestureModelRunner(self.model_class, model_path, "cpu")
            self.mouse_mapper_gesture = MouseEventGestureMapper()
        else:
            self.mouse_mapper_rulebase = MouseEventRuleBaseMapper()
            logger.info("Using rule-based mapper")

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

            # pointer mapping
            screen_pos = self.landmark_mapper.mapping_use_palm(smoothed_landmarks)
            logger.debug(f"Pointer mapped to screen position: {screen_pos}")

            # mouse event mapping
            if not self.rule_base_enable:
                # gesture recognition
                gesture_label = self.gesture_model.update_and_inference(
                    smoothed_landmarks
                )
                logger.debug(f"Gesture detected: {gesture_label.name}")
                mouse_event = self.mouse_mapper_gesture.update(gesture_label)
                self.view.update_overlay_info(
                    gesture=gesture_label,
                    pointer_pos=screen_pos,
                    mouse_event=mouse_event.name,
                )
            else:
                mouse_event = self.mouse_mapper_rulebase.update(smoothed_landmarks)
                self.view.update_overlay_info(
                    pointer_pos=screen_pos,
                    mouse_event=mouse_event.name,
                )
            logger.debug(f"Mouse event deteced: {mouse_event.name}")
            self.perform_mouse_event(mouse_event, screen_pos)

        else:
            self.undetected_count += 1

        frame = cv2.flip(frame, 1)
        self.view.camera_preview.update_camera_preview(frame)

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
            self.mouse_cilent.button_event(
                *pointer_pos, button="left", event_type="down"
            )
        elif mouse_event == MouseEvent.LEFT_RELEASE:
            self.mouse_cilent.button_event(*pointer_pos, button="left", event_type="up")
        elif mouse_event == MouseEvent.LEFT_CLICK:
            self.mouse_cilent.button_event(
                *pointer_pos, button="left", event_type="click"
            )
        elif mouse_event == MouseEvent.RIGHT_PRESS:
            self.mouse_cilent.button_event(
                *pointer_pos, button="right", event_type="down"
            )
        elif mouse_event == MouseEvent.RIGHT_RELEASE:
            self.mouse_cilent.button_event(
                *pointer_pos, button="right", event_type="up"
            )
        elif mouse_event == MouseEvent.RIGHT_CLICK:
            self.mouse_cilent.button_event(
                *pointer_pos, button="right", event_type="click"
            )

    def close(self):
        close_camera_singleton()
        self.landmarker.close()
        self.mouse_cilent.disconnect()
