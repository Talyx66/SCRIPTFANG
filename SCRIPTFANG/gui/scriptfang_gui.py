
from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QPushButton, QTextEdit, QLineEdit
)
from PyQt6.QtGui import QMovie, QFont, QTextCursor
from PyQt6.QtCore import Qt, QSize
import sys
import os
import random
import re
import requests

class ScriptFangGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ScriptFang")
        self.setFixedSize(1280, 720)

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

        # Title label
        self.title = QLabel("SCRIPTFANG", self)
        self.title.setStyleSheet("color: #00ff00; background: transparent;")
        self.title.setFont(QFont("Courier", 55, QFont.Weight.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setGeometry(0, 30, 1280, 60)

        # Target URL input
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter target URL (e.g. https://victim.com/search?q=)")
        self.url_input.setGeometry(390, 360, 500, 40)
        self.url_input.setStyleSheet(
            "background-color: rgba(0,0,0,0.6); color: #00ff00; font-size: 14px; border: 2px solid #00ff00; border-radius: 10px;"
        )
        self.url_input.setFont(QFont("Courier", 12))

        # Generate Payload Button
        self.button = QPushButton("Generate Payload", self)
        self.button.setGeometry(390, 600, 200, 50)
        self.button.setStyleSheet(
            "background-color: rgba(0,128,0,0.7); color: white; font-size: 16px; border-radius: 8px;"
        )
        self.button.clicked.connect(self.generate_payload)

        # Test Payload Button
        self.test_button = QPushButton("Test Payload", self)
        self.test_button.setGeometry(700, 600, 200, 50)
        self.test_button.setStyleSheet(
            "background-color: rgba(128,0,0,0.7); color: white; font-size: 16px; border-radius: 8px;"
        )
        self.test_button.clicked.connect(self.test_payload)

        # Payload output box
        self.output = QTextEdit(self)
        self.output.setGeometry(390, 430, 500, 120)
        self.output.setReadOnly(True)
        self.output.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0.6); color: #00ff00; font-size: 14px; border: 2px solid #00ff00; border-radius: 10px;"
        )
        self.output.setFont(QFont("Courier", 12))
        self.output.setText("// XSS Payload will appear here\n")

        # Feedback label
        self.feedback = QLabel("", self)
        self.feedback.setGeometry(390, 560, 510, 30)
        self.feedback.setStyleSheet("color: #00ff00; background: transparent; font-size: 14px;")
        self.feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # GitHub + credit label
        self.footer = QLabel("GitHub: github.com/Talyx66  |  Made by Talyx", self)
        self.footer.setStyleSheet("color: #00ff00; background: transparent;")
        self.footer.setFont(QFont("Courier", 10))
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer.setGeometry(0, 680, 1280, 30)

        # Store current payload (for testing)
        self.current_payload = ""

    def resizeEvent(self, event):
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        if self.movie and self.movie.isValid():
            self.movie.setScaledSize(QSize(self.width(), self.height()))
        super().resizeEvent(event)

    def generate_payload(self):
        try:
            payload_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools', 'payloads', 'xss.txt')
            with open(payload_path, 'r') as f:
                payloads = [line.strip() for line in f if line.strip()]
            self.current_payload = random.choice(payloads) if payloads else "<script>alert('xss')</script>"
            self.output.setPlainText(self.current_payload)
            cursor = self.output.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.output.setTextCursor(cursor)
            self.feedback.setText("")
        except Exception as e:
            self.output.setPlainText(f"⚠️ Error loading payloads: {e}")
            self.feedback.setText("")

    def test_payload(self):
        target_url = self.url_input.text().strip()
        if not target_url:
            self.feedback.setText("⚠️ Enter a valid target URL first.")
            return
        if not self.current_payload:
            self.feedback.setText("⚠️ Generate a payload first.")
            return

        # Inject payload into URL param — assumes the target URL ends with '=' or expects query param
        test_url = target_url + self.current_payload

        try:
            self.feedback.setText("⏳ Testing payload on target...")
            self.repaint()  # Update UI immediately

            resp = requests.get(test_url, timeout=10)

            # Simple regex checks for payload reflection or typical XSS triggers:
            patterns = [
                re.escape(self.current_payload),  # Exact payload reflection
                r"(?i)<script>alert\(",            # common alert signature
                r"(?i)onerror=",                  # common XSS attribute
                r"(?i)onload=",                   # another common event
                r"(?i)javascript:",               # javascript: in response
                r"(?i)document\.cookie",          # cookie access attempts
            ]

            content = resp.text

            # Check patterns
            for pattern in patterns:
                if re.search(pattern, content):
                    self.feedback.setStyleSheet("color: #00ff00;")
                    self.feedback.setText("✅ Payload likely successful — reflection detected.")
                    return

            # If no pattern matched, check HTTP status codes for possible blocking
            if resp.status_code in (403, 406):
                self.feedback.setStyleSheet("color: #ff5555;")
                self.feedback.setText(f"❌ Payload blocked — HTTP {resp.status_code}.")
            elif resp.status_code >= 500:
                self.feedback.setStyleSheet("color: #ffbb55;")
                self.feedback.setText(f"⚠️ Server error — HTTP {resp.status_code}.")
            else:
                self.feedback.setStyleSheet("color: #ffbb55;")
                self.feedback.setText(f"⚠️ No clear reflection detected (HTTP {resp.status_code}).")

        except requests.exceptions.Timeout:
            self.feedback.setStyleSheet("color: #ff5555;")
            self.feedback.setText("❌ Request timed out.")
        except requests.exceptions.RequestException as e:
            self.feedback.setStyleSheet("color: #ff5555;")
            self.feedback.setText(f"❌ Request error: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ScriptFangGUI()
    gui.show()
    sys.exit(app.exec())

