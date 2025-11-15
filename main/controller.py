import cv2
import logging
from PySide6.QtCore import Qt
from src.utils import (
    draw_landmarks_on_frame,
    merge_landmarks,
    np_to_normalized_landmark,
)
from src.task import return_tclass
from src.worker.camera import CameraThread
from src.worker.landmarker import Landmarker
from src.worker.smoother import EMASmoother
from src.worker.mapper import LandmarkMapper
from main.view import MainAppView


logger = logging.getLogger(__name__)


class MainAppController:
    def __init__(
        self,
        view: MainAppView,
    ):
        self.view = view

        self.camera = CameraThread()
        self.camera.frame_ready.connect(self._on_frame_ready)
        self.landmarker = Landmarker()
        self.landmarker.landmark_update.connect(self._on_landmark_update)
        self.smoother = EMASmoother()
        self.reset_after_undetect = 10
        self.undetected_count = 0

        self.mapper = LandmarkMapper(
            self.view.pointer_overlay.width(), self.view.pointer_overlay.height()
        )

        self.camera.start()

        self.update_view()

    def _on_frame_ready(self, payload):
        timestamp, frame = payload
        self.landmarker.detect_async(frame, timestamp)

    def _on_landmark_update(self, payload):
        timestamp, frame, result = payload
        self.timestamp = timestamp

        right_hand_detected = (
            len(result.hand_landmarks) > 0
            and result.handedness[0][0].category_name == "Right"
        )

        if right_hand_detected:
            if self.undetected_count > self.reset_after_undetect:
                self.smoother.reset()
                self.mapper.reset()
            self.undetected_count = 0

            # process landmarks
            landmarks = merge_landmarks(
                result.hand_landmarks[0], result.hand_world_landmarks[0]
            )
            smoothed_landmarks = self.smoother.update(landmarks)
            frame = draw_landmarks_on_frame(
                frame, np_to_normalized_landmark(smoothed_landmarks)
            )

            screen_pos = self.mapper.map_to_screen_pos(smoothed_landmarks)
            if screen_pos:
                self.view.pointer_overlay.update_pointer_position(screen_pos)

        else:
            self.undetected_count += 1

        frame = cv2.flip(frame, 1)
        self.view.cam_preview.update_camera_preview(frame)

    def update_state(self, key):
        prev_state = self.state

        if self.state == TaskState.BEGIN and key == Qt.Key.Key_Space:
            self.state = TaskState.BEFORE_TASK

        elif self.state == TaskState.BEFORE_TASK and key == Qt.Key.Key_Space:
            self.current_trial_idx = 0
            self.frame_in_trail = 0
            self.frame_landmark_detected = 0
            self.state = TaskState.IN_TRIAL

        elif self.state == TaskState.IN_TRIAL and key == Qt.Key.Key_Q:
            if self.current_trial_idx + 1 < len(
                self.tasks[self.current_task_idx]["configs"]
            ):
                if (
                    self._calculate_coverage_rate() > 0.7
                    and self.frame_in_trail >= 30
                    and self.frame_in_trail <= 300  # 1 to 10 seconds at 30 fps
                ):
                    self.state = TaskState.TRIAL_COMPLETED
                else:
                    self.state = TaskState.TRAIL_FAILED

            else:
                # all trials of current task done
                if self.current_task_idx + 1 < len(self.tasks):
                    self.state = TaskState.TASK_COMPLETED
                else:
                    self.state = TaskState.ALL_COMPLETED

        elif (
            self.state == TaskState.TRIAL_COMPLETED and key == Qt.Key.Key_Space
        ):  # start next trial
            self.current_trial_idx += 1
            self.frame_in_trail = 0
            self.frame_landmark_detected = 0
            self.state = TaskState.IN_TRIAL

        elif (
            self.state == TaskState.TRAIL_FAILED and key == Qt.Key.Key_Space
        ):  # restart current trial
            self.frame_in_trail = 0
            self.frame_landmark_detected = 0
            self.state = TaskState.IN_TRIAL

        elif (
            self.state == TaskState.TASK_COMPLETED and key == Qt.Key.Key_Space
        ):  # start next task
            self.current_task_idx += 1
            self.state = TaskState.BEFORE_TASK

        if prev_state != self.state:
            logger.info(
                f"Key pressed: {key}, Update {prev_state.name} -> {self.state.name}"
            )
            self.update_view()

    def update_view(self):

        # update view based on currrent state
        if self.state == TaskState.BEGIN:
            self.view.init_sidebar([(t["task"], len(t["configs"])) for t in self.tasks])
            self.view.show_hint("Welcome. Press 'Space' to start the first task.")

        elif self.state == TaskState.BEFORE_TASK:
            tclass = self._get_current_task_class()
            self.view.show_hint(
                f"Task: {tclass.name}\n{tclass.instruction}\nPress 'Space' to begin."
            )
            self.view.mark_task_start(self.tasks[self.current_task_idx]["task"])

        elif self.state == TaskState.IN_TRIAL:
            tclass = self._get_current_task_class()
            config = self._get_current_config()
            elements = tclass.generate_elements(config)
            self.view.show_elements(elements)
            self.view.show_hint(f"{tclass.instruction}\nPress 'Q' to end trail.")

        elif self.state == TaskState.TRIAL_COMPLETED:
            self.view.clear_elements()
            coverage = self._calculate_coverage_rate() * 100
            duration = self.frame_in_trail / 30
            self.view.show_hint(
                f"Trial completed with coverage: {coverage:.3f}%, time: {duration:.3f}s.\nPress 'Space' to continue."
            )
            self.view.increase_task_trial_count(
                self.tasks[self.current_task_idx]["task"],
                self.current_trial_idx + 1,
                len(self.tasks[self.current_task_idx]["configs"]),
            )

        elif self.state == TaskState.TRAIL_FAILED:
            self.view.clear_elements()
            coverage = self._calculate_coverage_rate() * 100
            duration = self.frame_in_trail / 30
            self.view.show_hint(
                f"Trial failed with coverage: {coverage:.3f}%, time: {duration:.3f}s.\nPress 'Space' to retry."
            )

        elif self.state == TaskState.TASK_COMPLETED:
            self.view.clear_elements()
            coverage = self._calculate_coverage_rate() * 100
            duration = self.frame_in_trail / 30
            self.view.show_hint(
                f"Trial completed with coverage: {coverage:.3f}%, time: {duration:.3f}s.\nAll trail completed.\nPress 'Space' to start the next task."
            )
            self.view.increase_task_trial_count(
                self.tasks[self.current_task_idx]["task"],
                self.current_trial_idx + 1,
                len(self.tasks[self.current_task_idx]["configs"]),
            )
            self.view.mark_task_complete(self.tasks[self.current_task_idx]["task"])

        elif self.state == TaskState.ALL_COMPLETED:
            self.view.clear_elements()
            coverage = self._calculate_coverage_rate() * 100
            duration = self.frame_in_trail / 30
            self.view.show_hint(
                f"Trial completed with coverage: {coverage:.3f}%, time: {duration:.3f}s.\nAll tasks completed. Thank you!"
            )
            self.view.increase_task_trial_count(
                self.tasks[self.current_task_idx]["task"],
                self.current_trial_idx + 1,
                len(self.tasks[self.current_task_idx]["configs"]),
            )

    def _calculate_coverage_rate(self):
        return self.frame_landmark_detected / self.frame_in_trail

    def _get_current_task_class(self):
        return return_tclass(self.tasks[self.current_task_idx]["task"])

    def _get_current_config(self):
        return self.tasks[self.current_task_idx]["configs"][self.current_trial_idx]

    def close(self):
        self.camera.stop()
        self.camera.wait()
        self.landmarker.close()
