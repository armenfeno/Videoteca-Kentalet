from PySide6.QtWidgets import QMainWindow
from src.canvas import CardCanvas


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Videoteca Kentalet")
        self.resize(1000, 700)

        self.canvas = CardCanvas()

        self.setCentralWidget(self.canvas)