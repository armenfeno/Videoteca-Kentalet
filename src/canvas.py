from PySide6.QtWidgets import QWidget
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPixmap,
    QPen,
    QPainterPath,
)
from PySide6.QtCore import QRect, QSize, Qt
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
    CARD_BORDER_RADIUS_MM,
    CARD_BORDER_WIDTH,
    CARD_BORDER_COLOR,
    BLEED_MM,
    BUTTON_STYLE
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
        self.print_mode = False

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

        if self.print_mode:

            layout = self.prepare_print_grid(
                paper_rect,
            )

        else:

            layout = self.prepare_preview_grid(
                paper_rect,
            )

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

    def prepare_preview_grid(self, paper_rect):
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

    def prepare_print_grid(self, paper_rect):
        """Calcula el layout para impresión."""

        card_width = mm_to_pixels_x(CARD_WIDTH_MM)
        card_height = mm_to_pixels_y(CARD_HEIGHT_MM)

        card_spacing = 0

        grid_width = (
            CARDS_PER_ROW * card_width
        )

        grid_height = (
            CARDS_PER_COLUMN * card_height
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

        color = PAPER_COLOR

        if self.print_mode:
            color = (255, 255, 255)

        painter.fillRect(
            paper_rect,
            QColor(*color)
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
        """Dibuja el póster con esquinas redondeadas."""

        radius = mm_to_pixels_x(CARD_BORDER_RADIUS_MM)

        poster_rect = QRect(
            poster_x,
            poster_y,
            scaled_poster.width(),
            scaled_poster.height(),
        )

        path = QPainterPath()
        path.addRoundedRect(
            poster_rect,
            radius,
            radius,
        )

        painter.save()

        painter.setClipPath(path)

        painter.drawPixmap(
            poster_rect,
            scaled_poster,
        )

        painter.restore()

    def draw_card_background(self, painter, card_rect):
        """Dibuja el fondo de la carta."""

        painter.setBrush(QColor(*PAPER_COLOR))
        painter.setPen(Qt.NoPen)

        radius = mm_to_pixels_x(CARD_BORDER_RADIUS_MM)

        painter.drawRoundedRect(
            card_rect,
            radius,
            radius,
        )

    def draw_card_bleed(self, painter, card_rect):
        """Dibuja el sangrado de impresión."""

        if not self.print_mode:
            return

        bleed = mm_to_pixels_x(BLEED_MM)

        bleed_rect = QRect(
            card_rect.x() - bleed,
            card_rect.y() - bleed,
            card_rect.width() + bleed * 2,
            card_rect.height() + bleed * 2,
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(*PAPER_COLOR))

        radius = mm_to_pixels_x(CARD_BORDER_RADIUS_MM)

        painter.drawRoundedRect(
            bleed_rect,
            radius + bleed,
            radius + bleed,
        )

    def draw_card_border(self, painter, card_rect):
        """Dibuja el borde de la carta."""

        pen = QPen(QColor(*CARD_BORDER_COLOR))
        pen.setWidth(CARD_BORDER_WIDTH)

        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        radius = mm_to_pixels_x(CARD_BORDER_RADIUS_MM)

        painter.drawRoundedRect(
            card_rect,
            radius,
            radius,
        )

    def draw_cut_mark(
        self,
        painter,
        x1,
        y1,
        x2,
        y2,
    ):
        """Dibuja una única marca de corte."""

        #pen = QPen(QColor(140, 140, 140))
        #pen.setWidth(1)
        pen = QPen(QColor(0, 0, 255))
        pen.setWidth(4)

        painter.setPen(pen)

        painter.drawLine(
            x1,
            y1,
            x2,
            y2,
        )

    def draw_card_layout(self, painter, image, card_rect):
        """
        Dibuja una carta completa dentro del rectángulo indicado.
        """

        poster_x, poster_y, scaled_poster = self.prepare_poster(
            image,
            card_rect,
        )

        self.draw_card_bleed(
            painter,
            card_rect,
        )

        self.draw_card_background(
            painter,
            card_rect,
        )

        self.draw_poster(
            painter,
            poster_x,
            poster_y,
            scaled_poster,
        )

        self.draw_card_border(
            painter,
            card_rect,
        )
