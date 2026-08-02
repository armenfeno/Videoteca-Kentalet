from src.units import (
    mm_to_pixels_x,
    mm_to_pixels_y,
)


class Geometry:
    """Calcula todas las medidas físicas para un DPI determinado."""

    def __init__(self, dpi):

        self.dpi = dpi

    def mm_x(self, mm):

        return mm_to_pixels_x(
            mm,
            self.dpi,
        )

    def mm_y(self, mm):

        return mm_to_pixels_y(
            mm,
            self.dpi,
        )