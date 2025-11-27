# defining different task types and their configurations

from data_collection.src.ui import ArrowElement, DotElement
from abc import ABC, abstractmethod
import random
from enum import Enum

dot_radius = 50


class TrueTaskType(Enum):
    BA_LEFT_CLICK = 0
    BA_RIGHT_CLICK = 1
    BA_SCROLL = 2
    MENU_NAVIGATION = 3
    DRAGGING = 4
    POINT_N_CLICK = 5


def return_tclass(ttype: TrueTaskType):
    for tclass in [
        BasicLeftCLickTask,
        BasicRightClickTask,
        BasicScrollTask,
        MenuNavigationTask,
        DraggingTask,
        PointAndClickTask,
    ]:
        if tclass.ttype == ttype:
            return tclass

    raise ValueError("Unsupported task type")


class Task(ABC):
    name: str
    ttype: TrueTaskType
    instruction: str

    @staticmethod
    @abstractmethod
    def generate_configs(
        count: int, canva_bound: tuple[int, int, int, int]
    ) -> list[tuple]:
        pass

    @staticmethod
    @abstractmethod
    def generate_elements(
        config: tuple,
    ) -> list[DotElement] | list[ArrowElement] | list[DotElement | ArrowElement]:
        pass


class BasicLeftCLickTask:
    name = "Basic Left Click Task"
    ttype = TrueTaskType.BA_LEFT_CLICK
    instruction = "Pinch with your thumb and index finger to left click."

    @staticmethod
    def generate_configs(count, canva_bound):
        configs = []
        for _ in range(count):
            x = random.randrange(canva_bound[0], canva_bound[1] + 1, step=10)
            y = random.randrange(canva_bound[2], canva_bound[3] + 1, step=10)
            configs.append((x, y))
        return configs

    @staticmethod
    def generate_elements(config):
        x, y = config
        return [
            DotElement(x, y, dot_radius, "transparent", label="left click"),
        ]


class BasicRightClickTask:
    name = "Basic Right Click Task"
    ttype = TrueTaskType.BA_RIGHT_CLICK
    instruction = "Pinch with your thumb and middle finger to right click."

    @staticmethod
    def generate_configs(count, canva_bound):
        configs = []
        for _ in range(count):
            x = random.randrange(canva_bound[0], canva_bound[1] + 1, step=10)
            y = random.randrange(canva_bound[2], canva_bound[3] + 1, step=10)
            configs.append((x, y))
        return configs

    @staticmethod
    def generate_elements(config):
        x, y = config
        return [
            DotElement(x, y, dot_radius, "transparent", label="right click"),
        ]


class BasicScrollTask:
    name = "Basic Scroll Task"
    ttype = TrueTaskType.BA_SCROLL
    instruction = "Swing your index and middle fingers up and down, repeat 5 times."

    @staticmethod
    def generate_configs(count, canva_bound):
        configs = []
        line_length = 600
        for _ in range(count):
            x1 = (canva_bound[0] + canva_bound[1]) // 2
            y1 = (canva_bound[2] + canva_bound[3]) // 2 + (line_length // 2)
            x2 = x1
            y2 = y1 - line_length
            configs.append((x1, y1, x2, y2))
        return configs

    @staticmethod
    def generate_elements(config):
        x1, y1, x2, y2 = config
        return [
            ArrowElement(x1, y1, x2, y2),
            ArrowElement(x2, y2, x1, y1),
        ]


class MenuNavigationTask:
    name = "Menu Navigation Task"
    ttype = TrueTaskType.MENU_NAVIGATION
    instruction = "Right click at dot 1, then left click at dot 2."

    @staticmethod
    def generate_configs(count, canva_bound):
        configs = []
        for _ in range(count):
            menu_width = random.randrange(100, 200 + 1, step=10)
            menu_height = random.randrange(150, 300 + 1, step=10)

            x1 = random.randrange(
                canva_bound[0], canva_bound[1] - menu_width + 1, step=10
            )
            y1 = random.randrange(
                canva_bound[2], canva_bound[3] - menu_height + 1, step=10
            )
            x2 = x1 + menu_width
            y2 = y1 + menu_height
            configs.append((x1, y1, x2, y2))
        return configs

    @staticmethod
    def generate_elements(config):
        x1, y1, x2, y2 = config
        return [
            ArrowElement(x1, y1, x2, y2, dashed=True),
            DotElement(
                x1, y1, dot_radius, "transparent", label="right", inner_label="1"
            ),
            DotElement(
                x2, y2, dot_radius, "transparent", label="left", inner_label="2"
            ),
        ]


class DraggingTask:
    name = "Dragging Task"
    ttype = TrueTaskType.DRAGGING
    instruction = "Left press on dot 1, then dragging to dot 2 and release."

    @staticmethod
    def generate_configs(count, canva_bound):
        configs = []
        mid_x = (canva_bound[0] + canva_bound[1]) // 2
        gap = 200
        for _ in range(count):
            lx = random.randrange(canva_bound[0], mid_x - gap + 1, step=10)
            ly = random.randrange(canva_bound[2], canva_bound[3] + 1, step=10)
            rx = random.randrange(mid_x + gap, canva_bound[1] + 1, step=10)
            ry = random.randrange(canva_bound[2], canva_bound[3] + 1, step=10)

            if random.random() < 0.5:
                configs.append((lx, ly, rx, ry))
            else:
                configs.append((rx, ry, lx, ly))

        return configs

    @staticmethod
    def generate_elements(config):
        x1, y1, x2, y2 = config
        return [
            ArrowElement(x1, y1, x2, y2),
            DotElement(x1, y1, dot_radius, "solid", label="press", inner_label="1"),
            DotElement(x2, y2, dot_radius, "hollow", label="release", inner_label="2"),
        ]


class PointAndClickTask:
    name = "Point And Click Task"
    ttype = TrueTaskType.POINT_N_CLICK
    instruction = "Left click on dot 1~3 in order."

    @staticmethod
    def generate_configs(count, canva_bound):
        configs = []

        mid1_x = (canva_bound[0] + canva_bound[1]) // 3
        mid2_x = (canva_bound[0] + canva_bound[1]) * 2 // 3
        mid1_y = (canva_bound[2] + canva_bound[3]) // 3
        mid2_y = (canva_bound[2] + canva_bound[3]) * 2 // 3
        gap = 100

        for _ in range(count):
            x1 = random.randrange(canva_bound[0], mid1_x - gap + 1, step=10)
            x2 = random.randrange(mid1_x + gap, mid2_x - gap + 1, step=10)
            x3 = random.randrange(mid2_x + gap, canva_bound[1] + 1, step=10)

            x1, x2, x3 = random.sample([x1, x2, x3], 3)

            y1 = random.randrange(canva_bound[2], mid1_y - gap + 1, step=10)
            y2 = random.randrange(mid1_y + gap, mid2_y - gap + 1, step=10)
            y3 = random.randrange(mid2_y + gap, canva_bound[3] + 1, step=10)
            y1, y2, y3 = random.sample([y1, y2, y3], 3)

            configs.append((x1, y1, x2, y2, x3, y3))

        return configs

    @staticmethod
    def generate_elements(config):
        x1, y1, x2, y2, x3, y3 = config
        return [
            ArrowElement(x1, y1, x2, y2, dashed=True),
            ArrowElement(x2, y2, x3, y3, dashed=True),
            DotElement(x1, y1, dot_radius, "transparent", inner_label="1"),
            DotElement(x2, y2, dot_radius, "transparent", inner_label="2"),
            DotElement(x3, y3, dot_radius, "transparent", inner_label="3"),
        ]
