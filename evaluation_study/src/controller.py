import time
import logging
from typing import Optional
from PySide6.QtCore import QObject, QTimer
from evaluation_study.task_generator import read_configs
from evaluation_study.src.recorder import EvaluationRecorder
from evaluation_study.src.view import EvaluationView
from evaluation_study.src.task_widget import TrueTaskType, TASK_WIDGET_MAP

logger = logging.getLogger(__name__)


class EvaluationController(QObject):
    def __init__(self, pid: int, view: EvaluationView):
        super().__init__()
        self.pid = pid
        self.view = view
        self.recorder = EvaluationRecorder(pid)

        # Study state
        try:
            self.task_configs = read_configs(self.pid)
            logger.info(f"loaded task: {self.task_configs}")
        except Exception as e:
            logger.error(f"Error loading task configurations: {e}")
            return

        # Connect view signals
        self.view.on_study_start.connect(self.start_study)
        self.view.on_next_trial.connect(self.start_next_trial)
        self.view.on_study_complete.connect(self.finish_study)

        self.view.init_view(
            [
                (task_type.value, trial_num)
                for task_type, trial_num, _ in self.task_configs
            ]
        )

    def start_study(self):
        self.current_task_index = 0
        self.start_current_task()

    def start_current_task(self):
        if self.current_task_index >= len(self.task_configs):
            self.finish_study()
            return

        task_type, trial_num, configs = self.task_configs[self.current_task_index]
        self.current_task_type = task_type
        self.current_trial_configs = configs
        self.current_trial_index = 0

        self.view.show_task_view(self.current_task_type)

    def start_next_trial(self):
        if self.current_trial_index >= len(self.current_trial_configs):
            # move to next task
            self.current_task_index += 1
            self.start_current_task()
            return

        trial_config = self.current_trial_configs[self.current_trial_index]

        task_widget = TASK_WIDGET_MAP[self.current_task_type]
        self.current_task_widget = task_widget(trial_config)
        self.current_task_widget.on_completed.connect(self.on_trial_completed)

        self.view.show_trial_view(self.current_task_widget)
        self.trial_start_time = time.time()

        logger.info(
            f"Started trial {self.current_trial_index + 1} of task {self.current_task_type.name}"
        )

    def on_trial_completed(self, payload: dict):
        complete_time = time.time() - self.trial_start_time
        correctness = self.current_task_widget.compute_correctness(payload)

        self.recorder.write_trial_result(
            self.current_task_type,
            self.current_trial_index,
            complete_time,
            correctness,
            payload,
        )

        logger.info(f"Current trail completed in {complete_time:.2f}s")

        # move to next trial
        self.current_trial_index += 1

    def finish_study(self):
        logger.info(f"Evaluation study completed.")
        self.view.show_completion_view()
