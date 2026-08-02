from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QScrollArea,
    QCheckBox,
    QStyle
)
from src.canvas import CardCanvas
from src.settings import (
    BACKGROUND_COLOR,
    BUTTON_STYLE
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from src.pdf_exporter import PdfExporter


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Videoteca Kentalet")
        self.resize(1000, 700)

        # Widget principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        layout = QVBoxLayout(central_widget)
        buttons_layout = QHBoxLayout()

        # Botón temporal
        self.new_selection_button = QPushButton("Nueva selección")
        self.add_images_button = QPushButton("Añadir imágenes")
        self.clear_button = QPushButton("Limpiar")
        self.export_pdf_button = QPushButton("Exportar PDF")
        self.print_mode_checkbox = QCheckBox("Modo impresión")
        self.print_mode_checkbox.toggled.connect(
            self.toggle_print_mode
        )

        style = self.style()

        self.new_selection_button.setIcon(
            style.standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        )

        self.add_images_button.setIcon(
            style.standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder)
        )

        self.clear_button.setIcon(
            style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
        )

        self.export_pdf_button.setIcon(
            style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)
        )

        for button in (
            self.new_selection_button,
            self.add_images_button,
            self.clear_button,
            self.export_pdf_button,
            self.print_mode_checkbox,
        ):
            button.setStyleSheet(BUTTON_STYLE)

        # Canvas
        self.canvas = CardCanvas()

        # Área con scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.canvas)
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.viewport().setStyleSheet(
            f"background-color: rgb({BACKGROUND_COLOR[0]}, {BACKGROUND_COLOR[1]}, {BACKGROUND_COLOR[2]});"
        )

        buttons_layout.addWidget(self.new_selection_button)
        buttons_layout.addWidget(self.add_images_button)
        buttons_layout.addWidget(self.clear_button)

        buttons_layout.addStretch()

        buttons_layout.addWidget(
            self.print_mode_checkbox
        )

        buttons_layout.addSpacing(20)

        buttons_layout.addWidget(
            self.export_pdf_button
        )


        buttons_layout.addWidget(self.export_pdf_button)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.scroll_area)

        self.new_selection_button.clicked.connect(self.new_selection)
        self.add_images_button.clicked.connect(self.add_images)
        self.clear_button.clicked.connect(self.clear_images)
        self.export_pdf_button.clicked.connect(
            self.export_pdf
        )

        self.canvas.set_images(
            self.load_images([
                "input/ice age.webp",
                "input/flow.webp",
                "input/el viaje de arlo.webp",
                "input/la tortuga roja.webp",
                "input/super mario bros la pelicula.webp",
                "input/toy story 1.webp",
                "input/toy story 2.webp",
                "input/toy story 3.webp",
                "input/walle.webp",
            ])
        )

        self.update_buttons()

    def load_images(self, file_paths):
        """Carga una lista de imágenes desde disco."""

        return [
            QPixmap(path)
            for path in file_paths
        ]
    
    def select_images(self):
        """Permite seleccionar imágenes y mostrarlas en el lienzo."""

        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar imágenes",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.webp *.bmp)"
        )

        if not file_paths:
            return []

        return self.load_images(file_paths)

    def new_selection(self):
        images = self.select_images()

        if not images:
            return

        self.canvas.set_images(images)

        self.update_buttons()

    def add_images(self):
        images = self.select_images()

        if not images:
            return

        self.canvas.add_images(images)

        self.update_buttons()
    
    def clear_images(self):
        self.canvas.clear_images()
        self.update_buttons()

    def export_pdf(self):
        """Exporta el proyecto actual a un archivo PDF."""

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar PDF",
            "cartas.pdf",
            "PDF (*.pdf)",
        )

        if not filename:
            return

        exporter = PdfExporter()

        old_mode = self.canvas.print_mode

        self.canvas.print_mode = True

        exporter.export(
            self.canvas,
            filename,
        )

        self.canvas.print_mode = old_mode

        self.canvas.update()
        
    def update_buttons(self):
        """Actualiza el estado de los botones según el proyecto actual."""

        has_images = self.canvas.has_images()

        self.clear_button.setEnabled(has_images)
        self.export_pdf_button.setEnabled(has_images)

    def toggle_print_mode(self):
        """Activa o desactiva el modo impresión."""

        self.canvas.print_mode = (
            self.print_mode_checkbox.isChecked()
        )

        self.canvas.update()