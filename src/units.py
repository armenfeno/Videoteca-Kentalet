from src.settings import (
    PAPER_WIDTH_MM,
    PAPER_HEIGHT_MM,
)


def mm_to_pixels_x(
    mm,
    dpi,
):
    """Convierte milímetros a píxeles horizontales."""

    return int(
        mm * dpi / 25.4
    )


def mm_to_pixels_y(
    mm,
    dpi,
):
    """Convierte milímetros a píxeles verticales."""

    return int(
        mm * dpi / 25.4
    )