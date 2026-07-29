from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPixmap
from PySide6.QtCore import QRect

from src.settings import (
    PAPER_WIDTH_MM,
    PAPER_HEIGHT_MM,
    PAPER_COLOR,
    BACKGROUND_COLOR,
    SHADOW_OFFSET,
    SHADOW_COLOR,
)


class CardCanvas(QWidget):

    def __init__(self):
        super().__init__()
        self.poster = QPixmap("input/ice age.webp")

    def paintEvent(self, event):

        painter = QPainter(self)

        # Calcular la posición de la hoja
        paper_x = (self.width() - PAPER_WIDTH_MM) // 2
        paper_y = (self.height() - PAPER_HEIGHT_MM) // 2

        # Crear los rectángulos
        paper_rect = QRect(
            paper_x,
            paper_y,
            PAPER_WIDTH_MM,
            PAPER_HEIGHT_MM
        )

        shadow_rect = QRect(
            paper_x + SHADOW_OFFSET,
            paper_y + SHADOW_OFFSET,
            PAPER_WIDTH_MM,
            PAPER_HEIGHT_MM
        )

        # Dibujar la escena
        self.draw_background(painter)
        self.draw_shadow(painter, shadow_rect)
        self.draw_paper(painter, paper_rect)
        #self.draw_poster(painter, paper_rect)

    def draw_background(self, painter):
        """Dibuja el fondo de la aplicación."""

        painter.fillRect(
            self.rect(),
            QColor(*BACKGROUND_COLOR)
        )

    def draw_shadow(self, painter, shadow_rect):
        """Dibuja la sombra de la hoja."""

        painter.fillRect(
            shadow_rect,
            QColor(*SHADOW_COLOR)
        )

    def draw_paper(self, painter, paper_rect):
        """Dibuja la hoja de trabajo."""

        painter.fillRect(
            paper_rect,
            QColor(*PAPER_COLOR)
        )
    def draw_poster(self, painter, paper_rect):
        painter.drawPixmap(
            paper_rect.x(),
            paper_rect.y(),
            self.poster
        )