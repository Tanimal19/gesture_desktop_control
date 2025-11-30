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


def get_instruction_style():
    return f"""
        QLabel {{
            font-size: 20px;
            color: {MyColor.red.to_css()};
        }}
    """
