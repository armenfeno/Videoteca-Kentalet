from PySide6.QtWidgets import QWidget
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPixmap,
    QPen,
    QPainterPath,
    QImage
)
from PySide6.QtCore import QRect, QSize, Qt
from src.layout import GridLayout
from src.settings import (
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
    BLEED_MM,
    CUT_MARK_LENGTH_MM,
    CUT_MARK_OVERLAP_MM,
    CUT_MARK_CROSS_SIZE_MM,
    PREVIEW_DPI,
    PAPER_HEIGHT_MM,
    PAPER_WIDTH_MM,
    CUT_MARK_WIDTH_MM,
    CUT_MARK_EXTENSION_MM,
    FRAME_TEXTURE_OPACITY
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
        self.dpi = PREVIEW_DPI
        self.overlay_frame = QPixmap(
            "resources/themes/peliculas/overlay_frame.png"
        )

        self.overlay_fx = QPixmap(
            "resources/themes/peliculas/overlay_fx.png"
        )
        self.paper_texture = QPixmap(
            "resources/themes/peliculas/texture.png"
        )

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

    def sizeHint(self):
        """Tamaño preferido del lienzo."""

        paper_width = self.mm_x(PAPER_WIDTH_MM)
        paper_height = self.mm_y(PAPER_HEIGHT_MM)

        return QSize(
            paper_width + self.workspace_margin * 2,
            paper_height + self.workspace_margin * 2,
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

        self.render(
            painter,
            self.rect(),
        )

    def render(
        self,
        painter,
        target_rect,
    ):
        """Dibuja toda la escena sobre cualquier QPainter."""
        print("Canvas DPI:", self.dpi)
        paper_rect = self.prepare_paper(
            target_rect,
        )

        if self.print_mode:

            layout = self.prepare_print_grid(
                paper_rect,
            )

        else:

            layout = self.prepare_preview_grid(
                paper_rect,
            )

        shadow_rect = self.prepare_shadow(
            paper_rect,
        )

        self.draw_shadow(
            painter,
            shadow_rect,
        )

        self.draw_paper(
            painter,
            paper_rect,
        )

        self.draw_grid(
            painter,
            layout,
        )

        if self.print_mode:

            self.draw_cut_marks(
                painter,
                layout,
            )
        
    def prepare_paper(
        self,
        target_rect,
    ):        
        """Calcula la posición y tamaño de la hoja."""

        paper_width = self.mm_x(PAPER_WIDTH_MM)
        paper_height = self.mm_y(PAPER_HEIGHT_MM)

        paper_x = max(
            target_rect.x() + self.workspace_margin,
            target_rect.x() + (target_rect.width() - paper_width) // 2,
        )

        paper_y = max(
            target_rect.y() + self.workspace_margin,
            target_rect.y() + (target_rect.height() - paper_height) // 2,
        )

        return QRect(
            paper_x,
            paper_y,
            paper_width,
            paper_height,
        )

    def prepare_shadow(self, paper_rect):
        """Calcula la posición de la sombra."""

        paper_width = self.mm_x(PAPER_WIDTH_MM)
        paper_height = self.mm_y(PAPER_HEIGHT_MM)

        return QRect(
            paper_rect.x() + SHADOW_OFFSET,
            paper_rect.y() + SHADOW_OFFSET,
            paper_width,
            paper_height,
        )

    def prepare_preview_grid(self, paper_rect):
        """Calcula la posición y tamaño de la cuadrícula."""

        card_width = self.mm_x(CARD_WIDTH_MM)
        card_height = self.mm_y(CARD_HEIGHT_MM)
        card_spacing = self.mm_x(CARD_SPACING_MM)

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

        card_width = self.mm_x(CARD_WIDTH_MM)
        card_height = self.mm_y(CARD_HEIGHT_MM)

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

    def prepare_poster(
        self,
        image,
        card_rect,
    ):
        """
        Calcula el tamaño y posición del póster utilizando
        medidas físicas (mm), para que Preview y PDF sean idénticos.
        """

        poster_margin = self.mm_x(POSTER_MARGIN_MM)

        poster_width = (
            card_rect.width()
            - poster_margin * 2
        )

        poster_height = (
            card_rect.height()
            - poster_margin * 2
        )

        scaled_poster = image.scaled(
            poster_width,
            poster_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        poster_x = (
            card_rect.x()
            + (card_rect.width() - scaled_poster.width()) // 2
        )

        poster_y = (
            card_rect.y()
            + (card_rect.height() - scaled_poster.height()) // 2
        )

        return (
            poster_x,
            poster_y,
            scaled_poster,
        )

    def create_frame_path(
        self,
        card_rect,
        poster_rect,
    ):

        radius = self.mm_x(CARD_BORDER_RADIUS_MM)

        outer = QPainterPath()
        outer.addRoundedRect(
            card_rect,
            radius,
            radius,
        )

        inner = QPainterPath()
        inner.addRoundedRect(
            poster_rect,
            radius,
            radius,
        )

        return outer.subtracted(inner)

    def draw_frame_texture(
        self,
        painter,
        card_rect,
        poster_rect,
    ):

        painter.save()

        painter.setClipPath(
            self.create_frame_path(
                card_rect,
                poster_rect,
            )
        )

        painter.setOpacity(
            FRAME_TEXTURE_OPACITY
        )

        painter.setCompositionMode(
            QPainter.CompositionMode_Multiply
        )

        tile_w = self.paper_texture.width()
        tile_h = self.paper_texture.height()

        for y in range(
            0,
            self.height(),
            tile_h,
        ):

            for x in range(
                0,
                self.width(),
                tile_w,
            ):

                painter.drawPixmap(
                    x,
                    y,
                    self.paper_texture,
                )

        painter.restore()

    def draw_overlay_frame(
        self,
        painter,
        card_rect,
    ):

        frame = self.overlay_frame.scaled(
            card_rect.size(),
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation,
        )

        painter.drawPixmap(
            card_rect.topLeft(),
            frame,
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

    def draw_paper_texture(
        self,
        painter,
        paper_rect,
    ):
        """Rellena la hoja utilizando una textura repetida."""
        painter.save()

        painter.setClipRect(
            paper_rect
        )
        tile_width = self.paper_texture.width()
        tile_height = self.paper_texture.height()

        for y in range(
            paper_rect.top(),
            paper_rect.bottom(),
            tile_height,
        ):

            for x in range(
                paper_rect.left(),
                paper_rect.right(),
                tile_width,
            ):

                painter.drawPixmap(
                    x,
                    y,
                    self.paper_texture,
                )
        painter.restore()

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

        radius = self.mm_x(CARD_BORDER_RADIUS_MM)

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

    def draw_overlay_fx(
        self,
        painter,
        card_rect,
    ):

        fx = self.overlay_fx.scaled(
            card_rect.size(),
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation,
        )

        painter.drawPixmap(
            card_rect.topLeft(),
            fx,
        )

    def prepare_cut_marks(self, layout):
        """Calcula las posiciones de las marcas de corte."""

        left = layout.grid_x

        right = (
            layout.grid_x
            + CARDS_PER_ROW * layout.card_width
        )

        top = layout.grid_y

        bottom = (
            layout.grid_y
            + CARDS_PER_COLUMN * layout.card_height
        )

        verticals = [
            left,
        ]

        for column in range(1, CARDS_PER_ROW):
            verticals.append(
                left + column * layout.card_width
            )

        verticals.append(right)

        horizontals = [
            top,
        ]

        for row in range(1, CARDS_PER_COLUMN):
            horizontals.append(
                top + row * layout.card_height
            )

        horizontals.append(bottom)

        return verticals, horizontals

    def draw_cut_marks(
        self,
        painter,
        layout,
    ):
        """Dibuja las marcas de corte del modo impresión."""

        verticals, horizontals = self.prepare_cut_marks(
            layout,
        )

        pen = QPen(QColor(255, 0, 0))

        pen.setWidthF(
            self.mm_x(CUT_MARK_WIDTH_MM)
        )

        painter.setPen(pen)

        mark_length = self.mm_y(CUT_MARK_LENGTH_MM)
        corner_overlap = self.mm_x(CUT_MARK_OVERLAP_MM)
        extension = self.mm_x(CUT_MARK_EXTENSION_MM)

        top = horizontals[0]
        bottom = horizontals[-1]
        left = verticals[0]
        right = verticals[-1]

        # --------------------------------------------------
        # Marcas superiores
        # --------------------------------------------------

        for i, x in enumerate(verticals):

            start_y = top
            end_y = top - mark_length

            if i == 0 or i == len(verticals) - 1:
                start_y += corner_overlap
            else:
                start_y += extension

            painter.drawLine(
                x,
                start_y,
                x,
                end_y,
            )

        # --------------------------------------------------
        # Marcas inferiores
        # --------------------------------------------------

        for i, x in enumerate(verticals):

            start_y = bottom
            end_y = bottom + mark_length

            if i == 0 or i == len(verticals) - 1:
                start_y -= corner_overlap
            else:
                start_y -= extension

            painter.drawLine(
                x,
                start_y,
                x,
                end_y,
            )

        mark_length = self.mm_x(CUT_MARK_LENGTH_MM)

        # --------------------------------------------------
        # Marcas izquierdas
        # --------------------------------------------------

        for i, y in enumerate(horizontals):

            start_x = left
            end_x = left - mark_length

            if i == 0 or i == len(horizontals) - 1:
                start_x += corner_overlap
            else:
                start_x += extension

            painter.drawLine(
                start_x,
                y,
                end_x,
                y,
            )

        # --------------------------------------------------
        # Marcas derechas
        # --------------------------------------------------

        for i, y in enumerate(horizontals):

            start_x = right
            end_x = right + mark_length

            if i == 0 or i == len(horizontals) - 1:
                start_x -= corner_overlap
            else:
                start_x -= extension

            painter.drawLine(
                start_x,
                y,
                end_x,
                y,
            )

        # --------------------------------------------------
        # Cruces interiores
        # --------------------------------------------------

        cross_size = self.mm_x(CUT_MARK_CROSS_SIZE_MM)
        cross_gap = 2

        for x in verticals[1:-1]:
            for y in horizontals[1:-1]:

                # Arriba
                painter.drawLine(
                    x,
                    y - cross_size,
                    x,
                    y - cross_gap,
                )

                # Abajo
                painter.drawLine(
                    x,
                    y + cross_gap,
                    x,
                    y + cross_size,
                )

                # Izquierda
                painter.drawLine(
                    x - cross_size,
                    y,
                    x - cross_gap,
                    y,
                )

                # Derecha
                painter.drawLine(
                    x + cross_gap,
                    y,
                    x + cross_size,
                    y,
                )

    def draw_card_layout(self, painter, image, card_rect):
        """
        Dibuja una carta completa dentro del rectángulo indicado.
        """

        poster_x, poster_y, scaled_poster = self.prepare_poster(
            image,
            card_rect,
        )

        if not hasattr(self, "_debug_done"):

            self._debug_done = True

            print("\n====================")
            print("CARD")
            print(card_rect)

            print("\nPOSTER")
            print(
                QRect(
                    poster_x,
                    poster_y,
                    scaled_poster.width(),
                    scaled_poster.height(),
                )
            )

            print("\nMARGINS")
            print("Left :", poster_x - card_rect.x())
            print("Top  :", poster_y - card_rect.y())
            print("Right:", card_rect.right() - (poster_x + scaled_poster.width()))
            print("Bottom:", card_rect.bottom() - (poster_y + scaled_poster.height()))
            print("====================\n")

        # Poster
        self.draw_poster(
            painter,
            poster_x,
            poster_y,
            scaled_poster,
        )

        frame_rect = card_rect

        # Marco marfil
        self.draw_overlay_frame(
            painter,
            card_rect,
        )

        poster_rect = QRect(
            poster_x,
            poster_y,
            scaled_poster.width(),
            scaled_poster.height(),
        )

        self.draw_frame_texture(
            painter,
            frame_rect,
            poster_rect,
        )

        # Brillos
        self.draw_overlay_fx(
            painter,
            frame_rect,
        )

    