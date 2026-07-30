from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QScrollArea,
)
from src.canvas import CardCanvas
from src.settings import BACKGROUND_COLOR
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


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

        # Botón temporal
        self.open_button = QPushButton("Abrir imágenes...")
        self.clear_button = QPushButton("Limpiar")

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

        layout.addWidget(self.open_button)
        layout.addWidget(self.clear_button)
        layout.addWidget(self.scroll_area)

        self.open_button.clicked.connect(self.open_images)
        self.clear_button.clicked.connect(self.clear_images)

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

    def load_images(self, file_paths):
        """Carga una lista de imágenes desde disco."""

        return [
            QPixmap(path)
            for path in file_paths
        ]
    def open_images(self):
        """Permite seleccionar imágenes y mostrarlas en el lienzo."""

        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar imágenes",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.webp *.bmp)"
        )

        if not file_paths:
            return

        self.canvas.set_images(
            self.load_images(file_paths)
        )
    def clear_images(self):
        self.canvas.clear_images()