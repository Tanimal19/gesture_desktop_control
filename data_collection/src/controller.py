import cv2
import logging
from enum import Enum
from PySide6.QtCore import Qt
from share.utils import (
    draw_landmarks_on_frame,
    merge_landmarks,
    np_to_normalized_landmark,
)
from data_collection.src.task import return_tclass, TrueTaskType, Task
from data_collection.task_generator import read_configs
from data_collection.src.view import DataCollectionView
from data_collection.src.recorder import DataCollectionRecorder
from share.worker.camera import CameraThread
from share.worker.landmarker import Landmarker
from share.worker.smoother import EMASmoother
from share.worker.mapper import LandmarkMapper


logger = logging.getLogger(__name__)


class TaskState(Enum):
    BEGIN = 0
    BEFORE_TASK = 1
    IN_TRIAL = 2
    TRIAL_COMPLETED = 3
    TRAIL_FAILED = 4
    TASK_COMPLETED = 5
    ALL_COMPLETED = 6


class DataCollectionController:
    def __init__(
        self,
        pid,
        view: DataCollectionView,
        recorder: DataCollectionRecorder,
        pointer_enabled=False,
    ):
        self.view = view
        self.recorder = recorder
        self.state = TaskState.BEGIN

        self.tasks = read_configs(pid)
        logger.info(f"Loaded tasks: {self.tasks}")
        self.current_task_idx = 0
        self.current_trial_idx = 0
        self.frame_in_trail = 0
        self.frame_landmark_detected = 0

        self.camera = CameraThread()
        self.camera.frame_ready.connect(self._on_frame_ready)
        self.landmarker = Landmarker(self.recorder.raw_landmarks_csv)
        self.landmarker.landmark_update.connect(self._on_landmark_update)
        self.smoother = EMASmoother()
        self.reset_after_undetect = 10
        self.undetected_count = 0

        self.pointer_enabled = pointer_enabled
        if self.pointer_enabled:
            self.mapper = LandmarkMapper(
                self.view.pointer_overlay.width(), self.view.pointer_overlay.height()
            )

        self.camera.start()
        self.camera.start_recording(self.recorder.camera_video_path)

        self.update_view()

    def _on_frame_ready(self, payload):
        timestamp, frame = payload
        self.landmarker.detect_async(frame, timestamp)

    def _on_landmark_update(self, payload):
        timestamp, frame, result = payload

        right_hand_detected = (
            len(result.hand_landmarks) > 0
            and result.handedness[0][0].category_name == "Right"
        )

        if self.state == TaskState.IN_TRIAL:
            self.frame_in_trail += 1

        if right_hand_detected:
            self.view.hide_warning()

            if self.undetected_count > self.reset_after_undetect:
                self.smoother.reset()
                if self.pointer_enabled:
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

            if self.pointer_enabled:
                screen_pos = self.mapper.map_to_screen_pos(smoothed_landmarks)
                if screen_pos:
                    self.view.pointer_overlay.update_pointer_position(screen_pos)

            if self.state == TaskState.IN_TRIAL:
                self.frame_landmark_detected += 1
                self.recorder.write_task_result(
                    timestamp,
                    self._get_current_task(),
                    self.current_trial_idx,
                    smoothed_landmarks,
                )

        else:
            self.undetected_count += 1

            if self.state == TaskState.IN_TRIAL:
                self.view.show_warning(
                    "Hand not detected! Please adjust your hand position."
                )

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
            if (
                self._calculate_coverage_rate() < 0.7
                or self.frame_in_trail < 30
                or self.frame_in_trail > 300
            ):
                self.state = TaskState.TRAIL_FAILED
            else:
                if self.current_trial_idx + 1 < len(
                    self.tasks[self.current_task_idx]["configs"]
                ):
                    self.state = TaskState.TRIAL_COMPLETED
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
            self.view.mark_task_start(self._get_current_task())

        elif self.state == TaskState.IN_TRIAL:
            tclass = self._get_current_task_class()
            config = self._get_current_config()
            elements = tclass.generate_elements(config)
            self.view.show_elements(elements)
            self.view.show_hint(f"{tclass.instruction}\nPress 'Q' to end trail.")
            self.recorder.mark_task_start(
                self._get_current_task(),
                self.current_trial_idx,
            )

        elif self.state == TaskState.TRIAL_COMPLETED:
            self.view.clear_elements()
            coverage = self._calculate_coverage_rate() * 100
            duration = self.frame_in_trail / 30
            self.view.show_hint(
                f"Trial completed with coverage: {coverage:.3f}%, time: {duration:.3f}s.\nPress 'Space' to continue."
            )
            self.view.increase_task_trial_count(
                self._get_current_task(),
                self.current_trial_idx + 1,
                self._get_current_config_length(),
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
                self._get_current_task(),
                self.current_trial_idx + 1,
                self._get_current_config_length(),
            )
            self.view.mark_task_complete(self._get_current_task())

        elif self.state == TaskState.ALL_COMPLETED:
            self.view.clear_elements()
            coverage = self._calculate_coverage_rate() * 100
            duration = self.frame_in_trail / 30
            self.view.show_hint(
                f"Trial completed with coverage: {coverage:.3f}%, time: {duration:.3f}s.\nAll tasks completed. Thank you!"
            )
            self.view.increase_task_trial_count(
                self._get_current_task(),
                self.current_trial_idx + 1,
                self._get_current_config_length(),
            )

    def _calculate_coverage_rate(self):
        return self.frame_landmark_detected / self.frame_in_trail

    def _get_current_task(self) -> TrueTaskType:
        return self.tasks[self.current_task_idx]["task"]

    def _get_current_task_class(self) -> Task:
        return return_tclass(self._get_current_task())

    def _get_current_config_length(self):
        return len(self.tasks[self.current_task_idx]["configs"])

    def _get_current_config(self):
        return self.tasks[self.current_task_idx]["configs"][self.current_trial_idx]

    def close(self):
        self.camera.stop()
        self.camera.wait()
        self.landmarker.close()
