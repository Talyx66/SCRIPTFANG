from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout
from PyQt6.QtGui import QMovie, QFont, QColor, QPalette
from PyQt6.QtCore import Qt
import sys
import os

class ScriptFangGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ScriptFang 🐉")
        self.setFixedSize(1280, 720)

        # Background GIF
        self.bg_label = QLabel(self)
        gif_path = os.path.join("assets", "dragonsscript.gif")
        self.movie = QMovie(gif_path)
        self.bg_label.setMovie(self.movie)
        self.movie.start()
        self.bg_label.setGeometry(0, 0, 1280, 720)

        # Overlay widgets
        self.title = QLabel("SCRIPTFANG", self)
        self.title.setStyleSheet("color: #00ff00;")  # toxic green
        self.title.setFont(QFont("Courier", 36, QFont.Weight.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setGeometry(0, 30, 1280, 60)

        self.button = QPushButton("Generate Payload", self)
        self.button.setGeometry(540, 600, 200, 50)
        self.button.setStyleSheet(
            "background-color: rgba(0,128,0,0.7); color: white; font-size: 16px; border-radius: 8px;"
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ScriptFangGUI()
    gui.show()
    sys.exit(app.exec())

