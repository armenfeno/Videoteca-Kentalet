from src.settings import (
    PAPER_WIDTH_MM,
    PAPER_WIDTH,
    PAPER_HEIGHT_MM,
    PAPER_HEIGHT,
)

def mm_to_pixels_x(mm):
    return int(mm * PAPER_WIDTH / PAPER_WIDTH_MM)

def mm_to_pixels_y(mm):
    return int(mm * PAPER_HEIGHT / PAPER_HEIGHT_MM)