from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QPushButton, QTextEdit, QLineEdit, QFileDialog
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
        self.setWindowTitle("SCRIPTFANG")
        self.setFixedSize(1024, 600)  # Resized window

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
        self.title.setGeometry(0, 20, self.width(), 50)

        # Target URL input - centered horizontally
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter target URL (e.g. https://victim.com/search?q=)")
        input_width = 600
        input_height = 35
        self.url_input.setGeometry(
            (self.width() - input_width) // 2,
            90,
            input_width,
            input_height
        )
        self.url_input.setStyleSheet(
            "background-color: rgba(0,0,0,0.6); color: #00ff00; font-size: 14px; border: 2px solid #00ff00; border-radius: 10px;"
        )
        self.url_input.setFont(QFont("Courier", 12))

        # Payload output box - centered horizontally
        output_width = 700
        output_height = 110
        self.output = QTextEdit(self)
        self.output.setGeometry(
            (self.width() - output_width) // 2,
            150,
            output_width,
            output_height
        )
        self.output.setReadOnly(True)
        self.output.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0.6); color: #00ff00; font-size: 14px; border: 2px solid #00ff00; border-radius: 10px;"
        )
        self.output.setFont(QFont("Courier", 12))
        self.output.setText("// XSS Payload will appear here\n")

        # Feedback label - centered horizontally
        self.feedback = QLabel("", self)
        self.feedback.setGeometry(
            0,
            270,
            self.width(),
            30
        )
        self.feedback.setStyleSheet("color: #00ff00; background: transparent; font-size: 14px;")
        self.feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        btn_width = 140
        btn_height = 35
        spacing = 15
        buttons_per_row = 4

        # Starting positions for button grid
        start_x = (self.width() - (btn_width * buttons_per_row + spacing * (buttons_per_row - 1))) // 2
        start_y = 320

        # Create first row buttons
        for idx, (label, filename) in enumerate(self.payload_buttons[:buttons_per_row]):
            x = start_x + idx * (btn_width + spacing)
            btn = QPushButton(label, self)
            btn.setGeometry(x, start_y, btn_width, btn_height)
            btn.setStyleSheet(
                "background-color: rgba(0,128,0,0.7); color: white; font-size: 13px; border-radius: 6px;"
            )
            btn.clicked.connect(lambda checked, f=filename: self.generate_payload_from_file(f))
            self.buttons[label] = btn

        # Second row buttons
        second_row_y = start_y + btn_height + 12
        for idx, (label, filename) in enumerate(self.payload_buttons[buttons_per_row:buttons_per_row*2]):
            x = start_x + idx * (btn_width + spacing)
            btn = QPushButton(label, self)
            btn.setGeometry(x, second_row_y, btn_width, btn_height)
            btn.setStyleSheet(
                "background-color: rgba(0,128,0,0.7); color: white; font-size: 13px; border-radius: 6px;"
            )
            btn.clicked.connect(lambda checked, f=filename: self.generate_payload_from_file(f))
            self.buttons[label] = btn

        # Group the three buttons below payload buttons and center them as a block
        multi_btn_width, multi_btn_height = 140, 40
        test_btn_width, test_btn_height = 140, 40
        export_btn_width, export_btn_height = 140, 40
        btn_spacing = 15

        total_width = multi_btn_width + test_btn_width + export_btn_width + btn_spacing * 2
        multi_btn_y = second_row_y + btn_height + 25
        start_x = (self.width() - total_width) // 2

        self.multi_button = QPushButton("Generate Mult- Payloads", self)
        self.multi_button.setGeometry(start_x, multi_btn_y, multi_btn_width, multi_btn_height)
        self.multi_button.setStyleSheet(
            "background-color: rgba(0,100,0,0.7); color: white; font-size: 12px; border-radius: 8px;"
        )
        self.multi_button.clicked.connect(self.generate_multiple_payloads)

        self.test_button = QPushButton("Test Payload", self)
        self.test_button.setGeometry(start_x + multi_btn_width + btn_spacing, multi_btn_y, test_btn_width, test_btn_height)
        self.test_button.setStyleSheet(
            "background-color: rgba(128,0,0,0.7); color: white; font-size: 15px; border-radius: 8px;"
        )
        self.test_button.clicked.connect(self.test_payload)

        self.export_button = QPushButton("Export Payload(s)", self)
        self.export_button.setGeometry(
            start_x + multi_btn_width + btn_spacing + test_btn_width + btn_spacing,
            multi_btn_y,
            export_btn_width,
            export_btn_height
        )
        self.export_button.setStyleSheet(
            "background-color: rgba(128,128,0,0.7); color: white; font-size: 15px; border-radius: 8px;"
        )
        self.export_button.clicked.connect(self.export_payloads)

        # Footer label (GitHub + credit) at the bottom center
        footer_height = 26
        self.footer = QLabel("GitHub: Github.com/Talyx66  |  Made by Talyx", self)
        self.footer.setStyleSheet("color: #00ff00; background: transparent;")
        self.footer.setFont(QFont("Courier", 13))
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer.setGeometry(0, self.height() - footer_height, self.width(), footer_height)

        # Store current payloads
        self.current_payloads = []

    def resizeEvent(self, event):
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        if self.movie and self.movie.isValid():
            self.movie.setScaledSize(QSize(self.width(), self.height()))
        # Re-center input, output, feedback, buttons, footer on resize
        input_width = 600
        output_width = 700
        btn_width = 140
        btn_height = 35
        spacing = 15
        buttons_per_row = 4

        self.url_input.setGeometry(
            (self.width() - input_width) // 2,
            90,
            input_width,
            35
        )
        self.output.setGeometry(
            (self.width() - output_width) // 2,
            150,
            output_width,
            110
        )
        self.feedback.setGeometry(
            0,
            270,
            self.width(),
            30
        )

        start_x = (self.width() - (btn_width * buttons_per_row + spacing * (buttons_per_row - 1))) // 2
        start_y = 320

        for idx, label in enumerate(list(self.buttons.keys())[:buttons_per_row]):
            x = start_x + idx * (btn_width + spacing)
            self.buttons[label].setGeometry(x, start_y, btn_width, btn_height)

        second_row_y = start_y + btn_height + 12
        for idx, label in enumerate(list(self.buttons.keys())[buttons_per_row:buttons_per_row*2]):
            x = start_x + idx * (btn_width + spacing)
            self.buttons[label].setGeometry(x, second_row_y, btn_width, btn_height)

        multi_btn_width, multi_btn_height = 140, 40
        test_btn_width, test_btn_height = 140, 40
        export_btn_width, export_btn_height = 140, 40
        btn_spacing = 15

        total_width = multi_btn_width + test_btn_width + export_btn_width + btn_spacing * 2
        multi_btn_y = second_row_y + btn_height + 25
        start_x = (self.width() - total_width) // 2

        self.multi_button.setGeometry(start_x, multi_btn_y, multi_btn_width, multi_btn_height)
        self.test_button.setGeometry(start_x + multi_btn_width + btn_spacing, multi_btn_y, test_btn_width, test_btn_height)
        self.export_button.setGeometry(
            start_x + multi_btn_width + btn_spacing + test_btn_width + btn_spacing,
            multi_btn_y,
            export_btn_width,
            export_btn_height
        )

        footer_height = 25
        self.footer.setGeometry(0, self.height() - footer_height, self.width(), footer_height)

        super().resizeEvent(event)

    # ... rest of your methods unchanged (generate_payload_from_file, generate_multiple_payloads, etc.) ...

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

    def export_payloads(self):
        if not self.current_payloads:
            self.feedback.setText("⚠️ No payloads to export.")
            return

        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Save Payloads", "", "Text Files (*.txt)", options=options)
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write("\n\n".join(self.current_payloads))
                self.feedback.setStyleSheet("color: #00ff00;")
                self.feedback.setText(f"✅ Payloads exported to {filename}")
            except Exception as e:
                self.feedback.setStyleSheet("color: #ff5555;")
                self.feedback.setText(f"❌ Failed to export: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ScriptFangGUI()
    gui.show()
    sys.exit(app.exec())
