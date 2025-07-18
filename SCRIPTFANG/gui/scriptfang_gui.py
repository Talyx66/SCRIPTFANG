

from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QTextEdit
from PyQt6.QtGui import QMovie, QFont
from PyQt6.QtCore import Qt
import sys
import os

class ScriptFangGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ScriptFang 🐉")
        self.setFixedSize(1280, 720)

        # Load the GIF background
        self.bg_label = QLabel(self)
        gif_path = os.path.abspath("dragonsscript.gif")
        print("GIF path:", gif_path)

        self.movie = QMovie(gif_path)
        if not self.movie.isValid():
            print(f"❌ Failed to load GIF from {gif_path}")
            return

        self.movie.setScaledSize(self.size())
        self.bg_label.setMovie(self.movie)
        self.bg_label.setGeometry(0, 0, 1280, 720)
        self.bg_label.lower()  # Send background to back

        self.movie.setParent(self)  # Prevent garbage collection
        self.movie.start()

        # Title label
        self.title = QLabel("SCRIPTFANG", self)
        self.title.setStyleSheet("color: #00ff00; background: transparent;")
        self.title.setFont(QFont("Courier", 36, QFont.Weight.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setGeometry(0, 30, 1280, 60)

        # Generate Button
        self.button = QPushButton("Generate Payload", self)
        self.button.setGeometry(540, 600, 200, 50)
        self.button.setStyleSheet(
            "background-color: rgba(0,128,0,0.7); color: white; font-size: 16px; border-radius: 8px;"
        )

        # Payload output in the center (as if created by dragon's flame)
        self.output = QTextEdit(self)
        self.output.setGeometry(390, 300, 500, 120)
        self.output.setReadOnly(True)
        self.output.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0.6); color: #00ff00; font-size: 14px; border: 2px solid #00ff00; border-radius: 10px;"
        )
        self.output.setFont(QFont("Courier", 12))
        self.output.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.output.setText("// XSS Payload will appear here\n// Created by the dragon's flame")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ScriptFangGUI()
    gui.show()
    sys.exit(app.exec())
