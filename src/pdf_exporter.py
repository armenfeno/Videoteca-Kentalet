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
        writer.setResolution(1200)

        painter = QPainter()
        painter.begin(writer)

        # -----------------------------
        # Cambiar DPI temporalmente
        # -----------------------------

        old_dpi = canvas.dpi
        canvas.dpi = writer.resolution()

        print("Canvas DPI:", canvas.dpi)

        canvas.render(
            painter,
            painter.viewport(),
        )

        # -----------------------------
        # Restaurar DPI
        # -----------------------------

        canvas.dpi = old_dpi

        painter.end()