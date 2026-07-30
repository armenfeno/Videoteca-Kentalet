from dataclasses import dataclass


@dataclass
class GridLayout:
    """Información necesaria para dibujar la cuadrícula."""

    grid_x: int
    grid_y: int

    card_width: int
    card_height: int

    card_spacing: int