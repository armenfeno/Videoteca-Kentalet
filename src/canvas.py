from PySide6.QtWidgets import QWidget
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPixmap,
    QPen,
    QPainterPath,
    QBrush,
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
    FRAME_TEXTURE_OPACITY,
    CUT_MARK_INNER_OVERLAP_MM,
    CUT_MARK_OUTER_EXTENSION_MM
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
        #print("Canvas DPI:", self.dpi)
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

    def prepare_grid(
        self,
        paper_rect,
        card_spacing,
    ):
        """
        Calcula la cuadrícula de cartas para cualquier modo.
        """

        card_width = self.mm_x(CARD_WIDTH_MM)
        card_height = self.mm_y(CARD_HEIGHT_MM)

        grid_width = (
            CARDS_PER_ROW * card_width
            + (CARDS_PER_ROW - 1) * card_spacing
        )

        grid_height = (
            CARDS_PER_COLUMN * card_height
            + (CARDS_PER_COLUMN - 1) * card_spacing
        )

        grid_x = (
            paper_rect.x()
            + (paper_rect.width() - grid_width) // 2
        )

        grid_y = (
            paper_rect.y()
            + (paper_rect.height() - grid_height) // 2
        )

        return GridLayout(
            grid_x=grid_x,
            grid_y=grid_y,
            card_width=card_width,
            card_height=card_height,
            card_spacing=card_spacing,
            paper_rect=paper_rect,
        )

    def prepare_preview_grid(
        self,
        paper_rect,
    ):
        return self.prepare_grid(
            paper_rect,
            self.mm_x(CARD_SPACING_MM),
        )

    def prepare_print_grid(
        self,
        paper_rect,
    ):
        return self.prepare_grid(
            paper_rect,
            self.mm_x(CARD_SPACING_MM),
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

    def create_bleed_frame_path(
        self,
        card_rect,
        poster_rect,
    ):
        """Genera el marco exterior utilizado como bleed."""

        bleed = self.mm_x(BLEED_MM)

        bleed_rect = QRect(
            card_rect.left() - bleed,
            card_rect.top() - bleed,
            card_rect.width() + bleed * 2,
            card_rect.height() + bleed * 2,
        )

        radius = self.mm_x(CARD_BORDER_RADIUS_MM)

        outer = QPainterPath()
        outer.addRoundedRect(
            bleed_rect,
            radius + bleed,
            radius + bleed,
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
        frame_path,
    ):
        """Aplica la textura únicamente al marco."""

        painter.save()

        painter.setOpacity(
            FRAME_TEXTURE_OPACITY
        )

        painter.setCompositionMode(
            QPainter.CompositionMode_Multiply
        )

        brush = QBrush(
            self.paper_texture
        )

        painter.fillPath(
            frame_path,
            brush,
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

    def prepare_cards(self, layout):
        """
        Calcula la geometría real de todas las cartas.
        """

        cards = []

        pitch_x = (
            layout.card_width
            + layout.card_spacing
        )

        pitch_y = (
            layout.card_height
            + layout.card_spacing
        )

        for row in range(CARDS_PER_COLUMN):

            for column in range(CARDS_PER_ROW):

                x = (
                    layout.grid_x
                    + column * pitch_x
                )

                y = (
                    layout.grid_y
                    + row * pitch_y
                )

                cards.append(
                    QRect(
                        x,
                        y,
                        layout.card_width,
                        layout.card_height,
                    )
                )

        return cards

    def draw_mark(
        self,
        painter,
        x,
        y,
        size,
        gap,
        up=True,
        down=True,
        left=True,
        right=True,
    ):
        """Dibuja una marca de corte configurable."""

        if up:
            self.draw_line(
    painter,
                x,
                y - size,
                x,
                y - gap,
            )

        if down:
            self.draw_line(
    painter,
                x,
                y + gap,
                x,
                y + size,
            )

        if left:
            self.draw_line(
    painter,
                x - size,
                y,
                x - gap,
                y,
            )

        if right:
            self.draw_line(
    painter,
                x + gap,
                y,
                x + size,
                y,
            )

    def draw_line(
        self,
        painter,
        x1,
        y1,
        x2,
        y2,
    ):
        """Dibuja una línea usando coordenadas enteras."""

        painter.drawLine(
            int(x1),
            int(y1),
            int(x2),
            int(y2),
        )

    def draw_card_corner_marks(
        self,
        painter,
        card,
        paper_rect,
    ):
        """Dibuja las marcas correspondientes a una única carta."""

        mark_length_x = self.mm_x(
            CUT_MARK_LENGTH_MM
        )

        mark_length_y = self.mm_y(
            CUT_MARK_LENGTH_MM
        )

        inner_x = self.mm_x(
            CUT_MARK_INNER_OVERLAP_MM
        )

        inner_y = self.mm_y(
            CUT_MARK_INNER_OVERLAP_MM
        )

        outer_x = self.mm_x(
            CUT_MARK_OUTER_EXTENSION_MM
        )

        outer_y = self.mm_y(
            CUT_MARK_OUTER_EXTENSION_MM
        )

        left = card.left()
        right = card.right()

        top = card.top()
        bottom = card.bottom()

        paper_left = paper_rect.left()
        paper_right = paper_rect.right()

        paper_top = paper_rect.top()
        paper_bottom = paper_rect.bottom()

        # ---------- Superior ----------

        if top == paper_top:

            self.draw_line(
                painter,
                left,
                top + inner_y,
                left,
                paper_top,
            )

            self.draw_line(
                painter,
                right,
                top + inner_y,
                right,
                paper_top,
            )

        else:

            self.draw_line(
                painter,
                left,
                top + inner_y,
                left,
                top - mark_length_y - outer_y,
            )

            self.draw_line(
                painter,
                right,
                top + inner_y,
                right,
                top - mark_length_y - outer_y,
            )

        # ---------- Inferior ----------

        if bottom == paper_bottom:

            self.draw_line(
                painter,
                left,
                bottom - inner_y,
                left,
                paper_bottom,
            )

            self.draw_line(
                painter,
                right,
                bottom - inner_y,
                right,
                paper_bottom,
            )

        else:

            self.draw_line(
                painter,
                left,
                bottom - inner_y,
                left,
                bottom - inner_y + mark_length_y + outer_y,
            )

            self.draw_line(
                painter,
                right,
                bottom - inner_y,
                right,
                bottom - inner_y + mark_length_y + outer_y,
            )

        # ---------- Izquierda ----------

        if left == paper_left:

            self.draw_line(
                painter,
                left + inner_x,
                top,
                paper_left,
                top,
            )

            self.draw_line(
                painter,
                left + inner_x,
                bottom,
                paper_left,
                bottom,
            )

        else:

            self.draw_line(
                painter,
                left + inner_x,
                top,
                left - mark_length_x - outer_x,
                top,
            )

            self.draw_line(
                painter,
                left + inner_x,
                bottom,
                left - mark_length_x - outer_x,
                bottom,
            )

        # ---------- Derecha ----------

        if right == paper_right:

            self.draw_line(
                painter,
                right - inner_x,
                top,
                paper_right,
                top,
            )

            self.draw_line(
                painter,
                right - inner_x,
                bottom,
                paper_right,
                bottom,
            )

        else:

            self.draw_line(
                painter,
                right - inner_x,
                top,
                right + mark_length_x + outer_x,
                top,
            )

            self.draw_line(
                painter,
                right - inner_x,
                bottom,
                right + mark_length_x + outer_x,
                bottom,
            )

    def draw_cut_marks(
        self,
        painter,
        layout,
    ):
        """Dibuja las marcas de corte del modo impresión."""

        cards = self.prepare_cards(
            layout,
        )

        pen = QPen(QColor(255, 0, 0))

        pen.setWidthF(
            self.mm_x(CUT_MARK_WIDTH_MM)
        )

        painter.setPen(pen)

        for card in cards:

            self.draw_card_corner_marks(
                painter,
                card,
                layout.paper_rect,
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

        # Poster
        self.draw_poster(
            painter,
            poster_x,
            poster_y,
            scaled_poster,
        )

        poster_rect = QRect(
            poster_x,
            poster_y,
            scaled_poster.width(),
            scaled_poster.height(),
        )

        frame_path = self.create_frame_path(
            card_rect,
            poster_rect,
        )

        if self.print_mode:

            bleed_path = self.create_bleed_frame_path(
                card_rect,
                poster_rect,
            )

            self.draw_frame_texture(
                painter,
                bleed_path,
            )

        # Marco marfil
        self.draw_overlay_frame(
            painter,
            card_rect,
        )

        # Textura SOLO sobre el marco
        self.draw_frame_texture(
            painter,
            frame_path,
        )

        # Brillos
        self.draw_overlay_fx(
            painter,
            card_rect,
        )

    