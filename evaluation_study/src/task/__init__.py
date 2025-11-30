from enum import Enum
from evaluation_study.src.task.abstract_task_widget import AbstractTaskWidget
from evaluation_study.src.task.menu_select import MenuSelectTaskWidget
from evaluation_study.src.task.dragdrop import DragDropTaskWidget
from evaluation_study.src.task.keyboard_input import KeyboardInputTaskWidget


class TrueTaskType(Enum):
    MenuSelect = "Menu Selection"
    DragDrop = "Drag and Drop"
    KeyboardInput = "Keyboard Input"


TASK_WIDGET_MAP: dict[TrueTaskType, type[AbstractTaskWidget]] = {
    TrueTaskType.MenuSelect: MenuSelectTaskWidget,
    TrueTaskType.DragDrop: DragDropTaskWidget,
    TrueTaskType.KeyboardInput: KeyboardInputTaskWidget,
}
