from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPixmap, QPen
from PySide6.QtCore import QRect, QSize
from src.layout import GridLayout
from src.settings import (
    PAPER_WIDTH,
    PAPER_HEIGHT,
    PAPER_COLOR,
    BACKGROUND_COLOR,
    SHADOW_OFFSET,
    SHADOW_COLOR,
    CARD_HEIGHT_MM,
    CARD_WIDTH_MM,
    POSTER_MARGIN_MM,
    CARD_SPACING_MM,
    CARDS_PER_COLUMN,
    CARDS_PER_ROW,
    MAX_CARDS,
    CARD_BORDER_RADIUS,
    CARD_BORDER_WIDTH
)
from src.units import (
    mm_to_pixels_x,
    mm_to_pixels_y,
)


class CardCanvas(QWidget):

    def __init__(self):
        """Inicializa el lienzo y carga el póster en memoria."""

        super().__init__()

        self.images = []
        self.workspace_margin = 80

    def sizeHint(self):
        """Tamaño preferido del lienzo."""

        return QSize(
            PAPER_WIDTH + self.workspace_margin * 2,
            PAPER_HEIGHT + self.workspace_margin * 2,
        )

    def set_images(self, images):
        """Actualiza las imágenes del lienzo y fuerza el repintado."""

        self.images = images
        self.update()

    def add_images(self, images):
        """
        Añade nuevas imágenes al canvas.
        """
        remaining_slots = MAX_CARDS - len(self.images)

        if remaining_slots <= 0:
            return

        self.images.extend(images[:remaining_slots])
        self.update()

    def clear_images(self):
        """
        Elimina todas las imágenes del canvas.
        """
        self.images.clear()
        self.update()

    def has_images(self):
        """
        Indica si el lienzo contiene imágenes.
        """
        return len(self.images) > 0

    def paintEvent(self, event):
        """Dibuja toda la escena."""

        painter = QPainter(self)
        
        # ------------------------------------------------------------
        # Crear los rectángulos principales
        # ------------------------------------------------------------

        paper_rect = self.prepare_paper()

        layout = self.prepare_grid(paper_rect)

        shadow_rect = self.prepare_shadow(paper_rect)
        
        # ------------------------------------------------------------
        # Dibujar la escena
        # ------------------------------------------------------------

        self.draw_shadow(painter, shadow_rect)
        self.draw_paper(painter, paper_rect)
        self.draw_grid(painter, layout)
        
    def prepare_paper(self):
        """Calcula la posición y tamaño de la hoja."""

        paper_x = max(
            self.workspace_margin,
            (self.width() - PAPER_WIDTH) // 2,
        )

        paper_y = max(
            self.workspace_margin,
            (self.height() - PAPER_HEIGHT) // 2,
        )

        return QRect(
            paper_x,
            paper_y,
            PAPER_WIDTH,
            PAPER_HEIGHT
        )

    def prepare_shadow(self, paper_rect):
        """Calcula la posición de la sombra."""

        return QRect(
            paper_rect.x() + SHADOW_OFFSET,
            paper_rect.y() + SHADOW_OFFSET,
            PAPER_WIDTH,
            PAPER_HEIGHT,
            )

    def prepare_grid(self, paper_rect):
        """Calcula la posición y tamaño de la cuadrícula."""

        card_width = mm_to_pixels_x(CARD_WIDTH_MM)
        card_height = mm_to_pixels_y(CARD_HEIGHT_MM)
        card_spacing = mm_to_pixels_x(CARD_SPACING_MM)

        grid_width = (
            CARDS_PER_ROW * card_width
            + (CARDS_PER_ROW - 1) * card_spacing
        )

        grid_height = (
            CARDS_PER_COLUMN * card_height
            + (CARDS_PER_COLUMN - 1) * card_spacing
        )

        free_width = paper_rect.width() - grid_width
        free_height = paper_rect.height() - grid_height

        grid_x = paper_rect.x() + free_width // 2
        grid_y = paper_rect.y() + free_height // 2

        return GridLayout(
            grid_x=grid_x,
            grid_y=grid_y,
            card_width=card_width,
            card_height=card_height,
            card_spacing=card_spacing,
        )

    def prepare_poster(self, image, card_rect):
        """
        Calcula el tamaño y la posición del póster dentro de la carta.

        El póster mantiene siempre su proporción original.
        Se fija un margen superior e inferior constante y el margen
        lateral se calcula automáticamente para centrar la imagen.
        """

        poster_margin = mm_to_pixels_y(POSTER_MARGIN_MM)

        poster_height = (
            card_rect.height()
            - (2 * poster_margin)
        )

        scaled_poster = image.scaledToHeight(
            poster_height
        )

        poster_width = scaled_poster.width()

        poster_x = (
            card_rect.x()
            + (card_rect.width() - poster_width) // 2
        )

        poster_y = (
            card_rect.y()
            + poster_margin
        )

        return (
            poster_x,
            poster_y,
            scaled_poster,
        )

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

    def draw_grid(self, painter, layout):
        """Dibuja todas las cartas de la cuadrícula."""

        for index, image in enumerate(self.images):

            row = index // CARDS_PER_ROW
            column = index % CARDS_PER_ROW

            card_x = (
                layout.grid_x
                + column * (
                    layout.card_width + layout.card_spacing
                )
            )

            card_y = (
                layout.grid_y
                + row * (
                    layout.card_height + layout.card_spacing
                )
            )

            card_rect = QRect(
                card_x,
                card_y,
                layout.card_width,
                layout.card_height,
            )

            self.draw_card_layout(
                painter,
                image,
                card_rect,
            )

    def draw_poster(
        self,
        painter,
        poster_x,
        poster_y,
        scaled_poster,
    ):
        """Dibuja el póster escalado en la posición calculada."""

        painter.drawPixmap(
            poster_x,
            poster_y,
            scaled_poster
        )

    def draw_card(self, painter, card_rect):
        """Dibuja el borde de la carta."""

        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(CARD_BORDER_WIDTH)

        painter.setPen(pen)

        painter.drawRoundedRect(
            card_rect,
            CARD_BORDER_RADIUS,
            CARD_BORDER_RADIUS,
        )

    def draw_card_layout(self, painter, image, card_rect):
        """
        Dibuja una carta completa dentro del rectángulo indicado.
        """
        # ------------------------------------------------------------
        # Preparar el póster
        # ------------------------------------------------------------
        
        poster_x, poster_y, scaled_poster = self.prepare_poster(
            image,
            card_rect,
        )

        self.draw_poster(painter, poster_x, poster_y, scaled_poster)
        self.draw_card(painter, card_rect)
