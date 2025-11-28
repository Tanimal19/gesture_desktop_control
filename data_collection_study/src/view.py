from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
from data_collection_study.src.ui import Canva, SideBar, HintOverlay
from data_collection_study.src.ui import (
    color_background,
    color_primary,
    color_foreground_light,
)
from share.ui.camera_preview import CameraPreview
from share.ui.pointer_overlay import PointerOverlay

if TYPE_CHECKING:
    from data_collection_study.src.controller import DataCollectionController

logger = logging.getLogger(__name__)


class DataCollectionView(QWidget):

    def __init__(self, pointer_enabled=False):
        super().__init__()
        self.setWindowTitle("Data Collection")
        self.showFullScreen()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet(f"background-color: rgba{color_background};")

        left_vbox_width = 300
        self.canva = Canva()
        self.hint_overlay = HintOverlay(self, (0, 0, 0, 0), (160, 160, 160, 180))
        self.warning_overlay = HintOverlay(self, (0, 0, 0, 0), (255, 20, 20, 255))
        self.sidebar = SideBar(left_vbox_width)
        self.cam_preview = CameraPreview(left_vbox_width)

        self.left_vbox = QVBoxLayout()
        self.left_vbox.setContentsMargins(0, 0, 0, 0)
        self.left_vbox.addWidget(self.sidebar, 0, Qt.AlignmentFlag.AlignTop)
        self.left_vbox.addWidget(self.cam_preview, 0, Qt.AlignmentFlag.AlignBottom)

        self.mlayout = QHBoxLayout(self)
        self.mlayout.setContentsMargins(0, 0, 0, 0)
        self.mlayout.addLayout(self.left_vbox, 0)
        self.mlayout.addWidget(self.canva, 1)
        self.setLayout(self.mlayout)

        self.hint_overlay.hide()
        self.warning_overlay.hide()

        if pointer_enabled:
            self.pointer_overlay = PointerOverlay()
            self.pointer_overlay.show()

        self.controller = None

    def set_controller(self, controller: DataCollectionController):
        self.controller = controller

    def keyPressEvent(self, event):
        if self.controller:
            self.controller.update_state(event.key())

    def closeEvent(self, event):
        if self.controller:
            self.controller.close()
        event.accept()

    # sidebar
    def init_sidebar(self, tasks):
        self.sidebar.add_label("header", "Task Progress")
        for t, count in tasks:
            self.sidebar.add_label(t, f"{t.name:<40}\t0/{count}")

    def increase_task_trial_count(self, t, trail, count):
        self.sidebar.update_label(t, f"{t.name:<40}\t{trail}/{count}")

    def mark_task_start(self, t):
        self.sidebar.update_label(t, color=color_primary)

    def mark_task_complete(self, t):
        self.sidebar.update_label(t, color=color_foreground_light)

    # hint overlay
    def show_hint(self, text):
        self.hint_overlay.set_hint(text)

    def hide_hint(self):
        self.hint_overlay.hide()

    def show_warning(self, text):
        self.warning_overlay.set_hint(text)

    def hide_warning(self):
        self.warning_overlay.hide()

    # canva
    def show_elements(self, elements):
        for ele in elements:
            self.canva.add_element(ele)
        self.canva.update()

    def clear_elements(self):
        self.canva.clean()
