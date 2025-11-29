from enum import Enum


class MyColor(Enum):
    white = (242, 242, 247, 255)
    black = (28, 28, 30, 255)
    gray = (229, 229, 234, 255)
    gray_dark = (209, 209, 214, 255)
    red = (255, 56, 60, 255)
    red_translucent = (255, 56, 60, 160)
    green = (52, 199, 89, 255)
    green_translucent = (52, 199, 89, 160)
    blue = (0, 122, 255, 255)
    blue_translucent = (0, 122, 255, 160)


INSTURCTION_PANEL_HEIGHT = 100
CENTRAL_WIDGET_HEIGHT = 600
PROGRESS_BAR_HEIGHT = 30

MAIN_WINDOW_HEIGHT = (
    INSTURCTION_PANEL_HEIGHT + CENTRAL_WIDGET_HEIGHT + PROGRESS_BAR_HEIGHT
)
MAIN_WINDOW_WIDTH = 1000
