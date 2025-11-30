from enum import Enum


class MyColor(Enum):
    white = (242, 242, 247)
    black = (28, 28, 30)
    gray = (229, 229, 234)
    gray_dark = (209, 209, 214)
    red = (255, 56, 60)
    green = (52, 199, 89)
    blue = (0, 122, 255)

    def to_css(self, transparency: float = 1) -> str:
        return (
            f"rgba({self.value[0]}, {self.value[1]}, {self.value[2]}, {transparency})"
        )


MAIN_WINDOW_HEIGHT = 800
MAIN_WINDOW_WIDTH = 1000

TITLE_FONT_SIZE = 24
INSTRUCTION_FONT_SIZE = 18
LABEL_FONT_SIZE = 14


class BUTTON_STYLE:
    @staticmethod
    def css_style(
        bg_color: MyColor = MyColor.blue, text_color: MyColor = MyColor.white
    ) -> str:
        return f"""
            QPushButton {{
                background-color: {bg_color.to_css()};
                color: {text_color.to_css()};
                border: none;
                border-radius: 8px;
                padding: 6px 30px;
                font-size: 14px;
                font-weight: bold;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {bg_color.to_css(0.8)};
            }}
        """


class PROGRESS_BAR_STYLE:
    height = 30

    @staticmethod
    def css_style() -> str:
        return f"""
            QProgressBar {{
                border: none;
                border-radius: 0px;
                text-align: center;
                font-size: 12px;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {MyColor.blue.to_css(0.4)};
            }}
        """


class INSTRUCTION_PANEL_STYLE:
    width = MAIN_WINDOW_WIDTH
    height = 120

    @staticmethod
    def css_style() -> str:
        return f"""
            QLabel {{
                background-color: {MyColor.white.to_css()};
                border-bottom: 2px solid {MyColor.gray_dark.to_css()};
                padding: 15px 20px;
                font-size: {INSTRUCTION_FONT_SIZE}px;
                font-weight: bold;
                color: {MyColor.red.to_css()};
                qproperty-wordWrap: true;
            }}
        """


class CENTRAL_WIDGET_STYLE:
    width = MAIN_WINDOW_WIDTH
    height = (
        MAIN_WINDOW_HEIGHT - INSTRUCTION_PANEL_STYLE.height - PROGRESS_BAR_STYLE.height
    )

    @staticmethod
    def css_style() -> str:
        return f"""
            QWidget {{
                background-color: {MyColor.white.to_css()};
            }}
        """
