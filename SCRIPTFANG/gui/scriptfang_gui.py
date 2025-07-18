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
        self.button.setGeometry(390, 600, 180, 50)
        self.button.setStyleSheet(
            "background-color: rgba(0,128,0,0.7); color: white; font-size: 16px; border-radius: 8px;"
        )
        self.button.clicked.connect(self.generate_payload)

        # Generate Multiple Payloads Button
        self.multi_button = QPushButton("Generate Multiple Payloads", self)
        self.multi_button.setGeometry(590, 600, 250, 50)
        self.multi_button.setStyleSheet(
            "background-color: rgba(0,100,0,0.7); color: white; font-size: 16px; border-radius: 8px;"
        )
        self.multi_button.clicked.connect(self.generate_multiple_payloads)

        # Test Payload Button
        self.test_button = QPushButton("Test Payload", self)
        self.test_button.setGeometry(870, 600, 180, 50)
        self.test_button.setStyleSheet(
            "background-color: rgba(128,0,0,0.7); color: white; font-size: 16px; border-radius: 8px;"
        )
        self.test_button.clicked.connect(self.test_payload)

        # Payload output box
        self.output = QTextEdit(self)
        self.output.setGeometry(390, 430, 660, 120)
        self.output.setReadOnly(True)
        self.output.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0.6); color: #00ff00; font-size: 14px; border: 2px solid #00ff00; border-radius: 10px;"
        )
        self.output.setFont(QFont("Courier", 12))
        self.output.setText("// XSS Payload will appear here\n")

        # Feedback label
        self.feedback = QLabel("", self)
        self.feedback.setGeometry(390, 560, 660, 30)
        self.feedback.setStyleSheet("color: #00ff00; background: transparent; font-size: 14px;")
        self.feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # GitHub + credit label
        self.footer = QLabel("GitHub: github.com/Talyx66  |  Made by Talyx", self)
        self.footer.setStyleSheet("color: #00ff00; background: transparent;")
        self.footer.setFont(QFont("Courier", 10))
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer.setGeometry(0, 680, 1280, 30)

        # Store current payloads for testing (list)
        self.current_payloads = []

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
            if not payloads:
                self.output.setPlainText("// No payloads found in file.")
                self.current_payloads = []
                self.feedback.setText("")
                return
            payload = random.choice(payloads)
            self.current_payloads = [payload]
            self.output.setPlainText(payload)
            cursor = self.output.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.output.setTextCursor(cursor)
            self.feedback.setText("")
        except Exception as e:
            self.output.setPlainText(f"⚠️ Error loading payloads: {e}")
            self.current_payloads = []
            self.feedback.setText("")

    def generate_multiple_payloads(self):
        try:
            payload_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools', 'payloads', 'xss.txt')
            with open(payload_path, 'r') as f:
                payloads = [line.strip() for line in f if line.strip()]
            if not payloads:
                self.output.setPlainText("// No payloads found in file.")
                self.current_payloads = []
                self.feedback.setText("")
                return
            selected = random.sample(payloads, min(5, len(payloads)))
            self.current_payloads = selected
            self.output.setPlainText("\n\n".join(selected))
            cursor = self.output.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.output.setTextCursor(cursor)
            self.feedback.setText("")
        except Exception as e:
            self.output.setPlainText(f"⚠️ Error loading payloads: {e}")
            self.current_payloads = []
            self.feedback.setText("")

    def test_payload(self):
        target_url = self.url_input.text().strip()
        if not target_url:
            self.feedback.setText("⚠️ Enter a valid target URL first.")
            return
        if not self.current_payloads:
            self.feedback.setText("⚠️ Generate payload(s) first.")
            return

        self.feedback.setText("⏳ Testing payload(s) on target...")
        self.repaint()  # Force UI update

        results = []

        for payload in self.current_payloads:
            test_url = target_url + payload
            try:
                resp = requests.get(test_url, timeout=10)
                content = resp.text

                patterns = [
                    re.escape(payload),
                    r"(?i)<script>alert\(",
                    r"(?i)onerror=",
                    r"(?i)onload=",
                    r"(?i)javascript:",
                    r"(?i)document\.cookie",
                ]

                matched = any(re.search(pattern, content) for pattern in patterns)

                if matched:
                    results.append(f"✅ Payload reflected: {payload[:40]}...")
                else:
                    if resp.status_code in (403, 406):
                        results.append(f"❌ Blocked (HTTP {resp.status_code}): {payload[:40]}...")
                    elif resp.status_code >= 500:
                        results.append(f"⚠️ Server error (HTTP {resp.status_code}): {payload[:40]}...")
                    else:
                        results.append(f"⚠️ No reflection (HTTP {resp.status_code}): {payload[:40]}...")

            except requests.exceptions.Timeout:
                results.append(f"❌ Timeout: {payload[:40]}...")
            except requests.exceptions.RequestException as e:
                results.append(f"❌ Request error: {e}")

        self.feedback.setStyleSheet("color: #00ff00;" if any(r.startswith("✅") for r in results) else "color: #ffbb55;")
        self.feedback.setText("\n".join(results))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ScriptFangGUI()
    gui.show()
    sys.exit(app.exec())
