from PySide6.QtGui import (
    QPainter,
    QPdfWriter,
    QPageLayout,
    QPageSize,
)

from PySide6.QtCore import (
    QMarginsF,
)


class PdfExporter:
    """Se encarga de exportar el contenido del canvas a un PDF."""

    def export(
        self,
        canvas,
        filename,
    ):

        writer = QPdfWriter(filename)

        writer.setPageSize(QPageSize(QPageSize.A4))
        writer.setPageMargins(
            QMarginsF(0, 0, 0, 0)
        )
        writer.setResolution(1200)

        painter = QPainter()
        painter.begin(writer)

        # -----------------------------
        # Cambiar DPI temporalmente
        # -----------------------------

        old_dpi = canvas.dpi
        canvas.dpi = writer.resolution()

        print("Canvas DPI:", canvas.dpi)

        page_rect = writer.pageLayout().paintRectPixels(
            writer.resolution()
        )

        print(page_rect)

        canvas.render(
            painter,
            page_rect,
        )

        print("Viewport :", painter.viewport())
        print("PaintRect:", page_rect)

        # -----------------------------
        # Restaurar DPI
        # -----------------------------

        canvas.dpi = old_dpi

        painter.end()