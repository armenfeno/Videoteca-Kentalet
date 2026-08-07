from dataclasses import dataclass
from PySide6.QtCore import QRect

@dataclass
class GridLayout:

    grid_x: int
    grid_y: int

    card_width: int
    card_height: int

    card_spacing: int

    paper_rect: QRect