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
        self.setFixedSize(1280, 780)  # Added height for extra buttons

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.payload_dir = os.path.join(base_dir, "tools", "payloads")

        gif_path = os.path.join(base_dir, "assets", "dragons.gif")
        print("Resolved GIF path:", gif_path)

        # Background GIF label
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

        # Target URL input
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter target URL (e.g. https://victim.com/search?q=)")
        self.url_input.setGeometry(390, 110, 500, 40)
        self.url_input.setStyleSheet(
            "background-color: rgba(0,0,0,0.6); color: #00ff00; font-size: 14px; border: 2px solid #00ff00; border-radius: 10px;"
        )
        self.url_input.setFont(QFont("Courier", 12))

        # Payload output box
        self.output = QTextEdit(self)
        self.output.setGeometry(250, 290, 660, 120)
        self.output.setReadOnly(True)
        self.output.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0.6); color: #00ff00; font-size: 14px; border: 2px solid #00ff00; border-radius: 10px;"
        )
        self.output.setFont(QFont("Courier", 12))
        self.output.setText("// XSS Payload will appear here\n")

        # Feedback label
        self.feedback = QLabel("", self)
        self.feedback.setGeometry(390, 420, 660, 30)
        self.feedback.setStyleSheet("color: #00ff00; background: transparent; font-size: 14px;")
        self.feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # GitHub + credit label
        self.footer = QLabel("GitHub: github.com/Talyx66  |  Made by Talyx", self)
        self.footer.setStyleSheet("color: #00ff00; background: transparent;")
        self.footer.setFont(QFont("Courier", 10))
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer.setGeometry(0, 740, 1280, 30)

        # Buttons config: (label, file_name)
        self.payload_buttons = [
            ("XSS Payload", "xss.txt"),
            ("WAF Bypass", "waf_bypass.txt"),
            ("Angular Payload", "angular.txt"),
            ("href Payload", "href.txt"),
            ("Script Breakout", "script_breakout.txt"),
            ("ScriptSneaky", "scriptsneaky.txt"),
            ("Body Payload", "body.txt"),
            ("Div Payload", "div.txt"),
            ("Cloudflare Bypass", "cloudflare.txt")
        ]

        self.buttons = {}
        button_width = 150
        button_height = 35
        spacing = 20
        total_buttons_first_row = 4
        total_buttons_second_row = len(self.payload_buttons) - total_buttons_first_row

        # Calculate starting x to center first row
        total_width_first_row = total_buttons_first_row * button_width + (total_buttons_first_row - 1) * spacing
        start_x_first_row = (self.width() - total_width_first_row) // 2
        y_pos_first_row = 450

        # First row buttons
        for i, (label, filename) in enumerate(self.payload_buttons[:total_buttons_first_row]):
            x_pos = start_x_first_row + i * (button_width + spacing)
            btn = QPushButton(label, self)
            btn.setGeometry(x_pos, y_pos_first_row, button_width, button_height)
            btn.setStyleSheet(
                "background-color: rgba(0,128,0,0.7); color: white; font-size: 13px; border-radius: 7px;"
            )
            btn.clicked.connect(lambda _, f=filename: self.generate_payload_from_file(f))
            self.buttons[label] = btn

        # Calculate starting x to center second row
        total_width_second_row = total_buttons_second_row * button_width + (total_buttons_second_row - 1) * spacing
        start_x_second_row = (self.width() - total_width_second_row) // 2
        y_pos_second_row = 495

        # Second row buttons
        for i, (label, filename) in enumerate(self.payload_buttons[total_buttons_first_row:]):
            x_pos = start_x_second_row + i * (button_width + spacing)
            btn = QPushButton(label, self)
            btn.setGeometry(x_pos, y_pos_second_row, button_width, button_height)
            btn.setStyleSheet(
                "background-color: rgba(0,128,0,0.7); color: white; font-size: 13px; border-radius: 7px;"
            )
            btn.clicked.connect(lambda _, f=filename: self.generate_payload_from_file(f))
            self.buttons[label] = btn

        # Generate Multiple Payloads button
        self.multi_button = QPushButton("Generate Multiple Payloads", self)
        multi_button_width = 220
        multi_button_height = 45

        # Test Payload button
        self.test_button = QPushButton("Test Payload", self)
        test_button_width = 180
        test_button_height = 45

        # Center multi and test buttons below the payload buttons
        total_width_bottom = multi_button_width + 30 + test_button_width
        start_x_bottom = (self.width() - total_width_bottom) // 2
        y_pos_bottom = 550

        self.multi_button.setGeometry(start_x_bottom, y_pos_bottom, multi_button_width, multi_button_height)
        self.multi_button.setStyleSheet(
            "background-color: rgba(0,100,0,0.7); color: white; font-size: 16px; border-radius: 8px;"
        )
        self.multi_button.clicked.connect(self.generate_multiple_payloads)

        self.test_button.setGeometry(start_x_bottom + multi_button_width + 30, y_pos_bottom, test_button_width, test_button_height)
        self.test_button.setStyleSheet(
            "background-color: rgba(128,0,0,0.7); color: white; font-size: 16px; border-radius: 8px;"
        )
        self.test_button.clicked.connect(self.test_payload)

        # Current payloads storage
        self.current_payloads = []

    def resizeEvent(self, event):
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        if self.movie and self.movie.isValid():
            self.movie.setScaledSize(QSize(self.width(), self.height()))
        super().resizeEvent(event)

    def generate_payload_from_file(self, filename):
        try:
            path = os.path.join(self.payload_dir, filename)
            with open(path, 'r', encoding='utf-8') as f:
                payloads = [line.strip() for line in f if line.strip()]
            if not payloads:
                self.output.setPlainText(f"// No payloads found in {filename}.")
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
            self.output.setPlainText(f"⚠️ Error loading {filename}: {e}")
            self.current_payloads = []
            self.feedback.setText("")

    def generate_multiple_payloads(self):
        try:
            path = os.path.join(self.payload_dir, "xss.txt")
            with open(path, 'r', encoding='utf-8') as f:
                payloads = [line.strip() for line in f if line.strip()]
            if not payloads:
                self.output.setPlainText("// No payloads found in xss.txt.")
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
            self.output.setPlainText(f"⚠️ Error loading xss.txt: {e}")
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
