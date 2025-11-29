from PySide6.QtCore import QPoint


def calculate_distance(
    pos1: tuple[int, int] | QPoint, pos2: tuple[int, int] | QPoint
) -> float:
    if isinstance(pos1, QPoint):
        pos1 = (pos1.x(), pos1.y())
    if isinstance(pos2, QPoint):
        pos2 = (pos2.x(), pos2.y())

    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]
    return (dx**2 + dy**2) ** 0.5
