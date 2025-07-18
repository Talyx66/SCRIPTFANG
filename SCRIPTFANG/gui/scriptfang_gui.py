

from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QTextEdit
from PyQt6.QtGui import QMovie, QFont, QTextCursor
from PyQt6.QtCore import Qt, QSize
import sys
import os

class ScriptFangGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCRIPTFANG")
        self.setFixedSize(1500, 720)

        # Calculate GIF path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        gif_path = os.path.join(base_dir, "assets", "dragons.gif")
        print("Resolved GIF path:", gif_path)

        # Background label for GIF
        self.bg_label = QLabel(self)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.bg_label.setStyleSheet("background: black;")
        self.bg_label.lower()

        self.movie = QMovie(gif_path)
        if not self.movie.isValid():
            print(f"❌ Failed to load GIF from {gif_path}")
            self.bg_label.setText("Failed to load GIF")
            self.bg_label.setStyleSheet("color: red; background: black; font-size: 24px;")
        else:
            self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
            self.movie.setSpeed(100)
            self.movie.setScaledSize(QSize(self.width(), self.height()))
            self.bg_label.setMovie(self.movie)
            self.movie.start()

        # Title
        self.title = QLabel("SCRIPTFANG", self)
        self.title.setStyleSheet("color: #00ff00; background: transparent;")
        self.title.setFont(QFont("Courier", 55, QFont.Weight.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setGeometry(0, 30, 1280, 60)

        # Generate Button
        self.button = QPushButton("Generate Payload", self)
        self.button.setGeometry(540, 600, 200, 50)
        self.button.setStyleSheet(
            "background-color: rgba(0,128,0,0.7); color: white; font-size: 16px; border-radius: 8px;"
        )
        self.button.clicked.connect(self.generate_payload)

        # Payload output box
        self.output = QTextEdit(self)
        self.output.setGeometry(390, 440, 500, 120)
        self.output.setReadOnly(True)
        self.output.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0.6); color: #00ff00; font-size: 14px; border: 2px solid #00ff00; border-radius: 10px;"
        )
        self.output.setFont(QFont("Courier", 12))
        self.output.setText("// XSS Payload will appear here\n")

        # Footer credit label
        self.credit = QLabel("Made by Talyx · GitHub.com/Talyx66", self)
        self.credit.setStyleSheet("color: #00ff00; background: transparent; font-size: 14px;")
        self.credit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.credit.setGeometry(0, 680, 1280, 20)

    def resizeEvent(self, event):
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        if self.movie and self.movie.isValid():
            self.movie.setScaledSize(QSize(self.width(), self.height()))
        super().resizeEvent(event)

    def generate_payload(self):
        payload = "<script>alert('ScriptFang 🔥 Payload!')</script>"
        self.output.setPlainText(payload)
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.output.setTextCursor(cursor)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ScriptFangGUI()
    gui.show()
    sys.exit(app.exec())

