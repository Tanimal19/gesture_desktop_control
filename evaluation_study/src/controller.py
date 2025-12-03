import time
import logging
from PySide6.QtCore import QObject
from evaluation_study.src.recorder import EvaluationResultRecorder
from evaluation_study.src.view import EvaluationView
from mouse_server.client import MouseServerClient
from evaluation_study.src.task import TASK_WIDGET_MAP
from evaluation_study.task_generator import read_configs

logger = logging.getLogger(__name__)


class EvaluationController(QObject):
    def __init__(self, pid: int, condition: str):
        super().__init__()

        # load task configs
        try:
            self.task_configs = read_configs(pid)
            logger.info(f"Loaded task configs {self.task_configs}")
        except Exception as e:
            logger.error(f"Failed to read task configs for pid {pid}: {e}")
            raise e

        # recorder
        self.recorder = EvaluationResultRecorder(pid, condition)

        # view
        self.view = EvaluationView()
        self.view.set_controller(self)
        self.view.setup_ui(
            [(task_type, trial_num) for task_type, trial_num, _ in self.task_configs],
            pid,
            condition,
        )
        self.view.on_study_start.connect(self.start_study)
        self.view.on_task_start.connect(self.start_next_trial)

        # mouse server client
        self.mouse_cilent = MouseServerClient()
        if not self.mouse_cilent.connect():
            logger.error("Failed to connect to mouse server client")
            self.close()
            raise ConnectionError("Cannot connect to mouse server")

        # show view
        self.view.show()

    def start_study(self):
        logger.info("Study started.")
        self.current_task_index = 0
        self.start_next_task()

    def start_next_task(self):
        self.view.update_topbar("")

        if self.current_task_index >= len(self.task_configs):
            logger.info("All tasks completed.")
            self.view.show_completion_view()
            return

        task_type, trial_num, configs = self.task_configs[self.current_task_index]
        self.current_task_type = task_type
        self.current_trial_configs = configs
        self.current_trial_index = 0

        self.view.show_task_view(self.current_task_type)

    def start_next_trial(self):
        self.view.update_progress(self.current_task_type, self.current_trial_index)

        if self.current_trial_index >= len(self.current_trial_configs):
            # move to next task
            logger.info("All trials for current task completed. Moving to next task.")
            self.current_task_index += 1
            self.start_next_task()
            return

        trial_config = self.current_trial_configs[self.current_trial_index]

        task_widget = TASK_WIDGET_MAP[self.current_task_type]
        self.current_task_widget = task_widget(trial_config, self.mouse_cilent)
        self.current_task_widget.on_completed.connect(self.on_trial_completed)

        self.view.show_trial_view(self.current_task_widget)
        self.view.update_topbar(
            f"{self.current_task_type.value}, Trial {self.current_trial_index + 1} of {len(self.current_trial_configs)}"
        )
        self.trial_start_time = time.time()

        logger.info(
            f"Start trial {self.current_trial_index + 1} of task {self.current_task_type.name}"
        )

    def on_trial_completed(self, payload: dict):
        complete_time = time.time() - self.trial_start_time

        self.recorder.write_trial_result(
            self.current_task_type,
            self.current_trial_index,
            complete_time,
            payload["is_correct"],
            payload,
        )

        logger.info(f"Current trail completed in {complete_time:.2f}s")

        # move to next trial
        self.current_trial_index += 1
        self.start_next_trial()

    def close(self):
        self.mouse_cilent.disconnect()
