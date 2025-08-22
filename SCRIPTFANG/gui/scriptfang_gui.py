from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QPushButton, QTextEdit, QLineEdit, QFileDialog
)
from PyQt6.QtGui import QMovie, QFont, QTextCursor, QColor, QTextCharFormat
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal
import sys
import os
import random
import re
import requests
import datetime


# Fuzzer thread to avoid freezing GUI
class FuzzThread(QThread):
    update_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, urls, payloads):
        super().__init__()
        self.urls = urls
        self.payloads = payloads

    def run(self):
        for url in self.urls:
            for payload in self.payloads:
                test_url = url + payload
                try:
                    resp = requests.get(test_url, timeout=5)
                    if payload in resp.text:
                        result = f"✅ Reflected: {payload[:40]}..."
                    elif resp.status_code in (403, 406):
                        result = f"❌ Blocked (HTTP {resp.status_code}): {payload[:40]}..."
                    else:
                        result = f"⚠️ No reflection (HTTP {resp.status_code}): {payload[:40]}..."
                except Exception as e:
                    result = f"❌ Error: {str(e)}"
                self.update_signal.emit(f"{url} -> {result}")
        self.finished_signal.emit()


class ScriptFangGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCRIPTFANG")
        self.setFixedSize(1024, 600)

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.payload_dir = os.path.join(base_dir, "tools", "payloads")
        gif_path = os.path.join(base_dir, "assets", "Fangvenom1")

        # Background GIF
        self.bg_label = QLabel(self)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.bg_label.setStyleSheet("background: black;")
        self.bg_label.lower()
        self.movie = QMovie(gif_path)
        if self.movie.isValid():
            self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
            self.movie.setSpeed(100)
            self.movie.setScaledSize(QSize(self.width(), self.height()))
            self.bg_label.setMovie(self.movie)
            self.movie.start()
        else:
            self.bg_label.setText("Failed to load GIF")
            self.bg_label.setStyleSheet("color: red; background: black; font-size: 24px;")

        # Title
        self.title = QLabel("SCRIPTFANG", self)
        self.title.setStyleSheet("color: #00ff00; background: transparent;")
        self.title.setFont(QFont("Courier", 55, QFont.Weight.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setGeometry(0, 20, self.width(), 50)

        # GitHub link top-left
        self.github_link = QLabel("Github.com/Talyx66", self)
        self.github_link.setStyleSheet("color: #00ff00; background: transparent;")
        self.github_link.setFont(QFont("Courier", 13))
        self.github_link.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.github_link.setGeometry(10, 10, 250, 25)

        # Credit top-right
        self.made_by = QLabel("Made by Talyx", self)
        self.made_by.setStyleSheet("color: #00ff00; background: transparent;")
        self.made_by.setFont(QFont("Courier", 13))
        self.made_by.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.made_by.setGeometry(self.width() - 260, 10, 250, 25)

        # Target URL input
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter target URL or file path (e.g. https://victim.com/search?q=)")
        self.url_input.setGeometry((self.width() - 600) // 2, 90, 600, 35)
        self.url_input.setStyleSheet(
            "background-color: rgba(0,0,0,0.6); color: #00ff00; font-size: 14px; border: 2px solid #00ff00; border-radius: 10px;"
        )
        self.url_input.setFont(QFont("Courier", 12))

        # Payload output box
        self.output = QTextEdit(self)
        self.output.setGeometry((self.width() - 700) // 2, 150, 700, 110)
        self.output.setReadOnly(True)
        self.output.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0.6); color: #00ff00; font-size: 14px; border: 2px solid #00ff00; border-radius: 10px;"
        )
        self.output.setFont(QFont("Courier", 12))
        self.output.setText("// XSS Payload will appear here\n")

        # Feedback box
        self.feedback = QTextEdit(self)
        self.feedback.setGeometry((self.width() - 700) // 2, 270, 700, 150)
        self.feedback.setReadOnly(True)
        self.feedback.setStyleSheet(
            "background-color: rgba(0,0,0,0.6); color: #00ff00; font-size: 14px; border: 2px solid #00ff00; border-radius: 10px;"
        )
        self.feedback.setFont(QFont("Courier", 12))

        # Buttons
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
        start_x = (self.width() - (btn_width * buttons_per_row + spacing * (buttons_per_row - 1))) // 2
        start_y = 430

        # First row
        for idx, (label, filename) in enumerate(self.payload_buttons[:buttons_per_row]):
            x = start_x + idx * (btn_width + spacing)
            btn = QPushButton(label, self)
            btn.setGeometry(x, start_y, btn_width, btn_height)
            btn.setStyleSheet("background-color: rgba(0,128,0,0.7); color: white; font-size: 13px; border-radius: 6px;")
            btn.clicked.connect(lambda checked, f=filename: self.generate_payload_from_file(f))
            self.buttons[label] = btn

        # Second row
        second_row_buttons = self.payload_buttons[buttons_per_row:buttons_per_row*2]
        total_width = len(second_row_buttons) * btn_width + (len(second_row_buttons) - 1) * spacing
        start_x2 = (self.width() - total_width) // 2
        second_row_y = start_y + btn_height + 12
        for idx, (label, filename) in enumerate(second_row_buttons):
            x = start_x2 + idx * (btn_width + spacing)
            btn = QPushButton(label, self)
            btn.setGeometry(x, second_row_y, btn_width, btn_height)
            btn.setStyleSheet("background-color: rgba(0,128,0,0.7); color: white; font-size: 13px; border-radius: 6px;")
            btn.clicked.connect(lambda checked, f=filename: self.generate_payload_from_file(f))
            self.buttons[label] = btn

        # Multi/Test/Export/Fuzz buttons
        multi_buttons = [
            ("Generate Payloads", self.generate_multiple_payloads, "rgba(0,100,0,0.7)"),
            ("Test Payload", self.test_payload, "rgba(128,0,0,0.7)"),
            ("Export Payloads", self.export_payloads, "rgba(128,128,0,0.7)"),
            ("Export Report", self.export_report, "rgba(150,75,0,0.7)"),
            ("Fuzz Target", self.start_fuzzing, "rgba(0,0,150,0.7)")
        ]
        mb_width = 140
        mb_height = 40
        mb_spacing = 15
        total_mb_width = len(multi_buttons) * mb_width + (len(multi_buttons) - 1) * mb_spacing
        start_x_mb = (self.width() - total_mb_width) // 2
        mb_y = second_row_y + btn_height + 25

        for idx, (label, func, color) in enumerate(multi_buttons):
            x = start_x_mb + idx * (mb_width + mb_spacing)
            btn = QPushButton(label, self)
            btn.setGeometry(x, mb_y, mb_width, mb_height)
            btn.setStyleSheet(f"background-color: {color}; color: white; font-size: 13px; border-radius: 8px;")
            btn.setFont(QFont("Courier", 12))
            btn.clicked.connect(func)

        self.current_payloads = []

    def resizeEvent(self, event):
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        if self.movie and self.movie.isValid():
            self.movie.setScaledSize(QSize(self.width(), self.height()))
        super().resizeEvent(event)

    # --- PAYLOAD METHODS ---
    def generate_payload_from_file(self, filename):
        try:
            path = os.path.join(self.payload_dir, filename)
            with open(path, 'r', encoding='utf-8') as f:
                payloads = [line.strip() for line in f if line.strip()]
            if not payloads:
                self.output.setPlainText(f"// No payloads found in {filename}.")
                self.current_payloads = []
                return
            payload = random.choice(payloads)
            self.current_payloads = [payload]
            self.output.setPlainText(payload)
            self.output.moveCursor(QTextCursor.MoveOperation.Start)
        except Exception as e:
            self.output.setPlainText(f"⚠️ Error loading {filename}: {e}")
            self.current_payloads = []

    def generate_multiple_payloads(self):
        try:
            path = os.path.join(self.payload_dir, "xss.txt")
            with open(path, 'r', encoding='utf-8') as f:
                payloads = [line.strip() for line in f if line.strip()]
            if not payloads:
                self.output.setPlainText("// No payloads found in xss.txt.")
                self.current_payloads = []
                return
            selected = random.sample(payloads, min(5, len(payloads)))
            self.current_payloads = selected
            self.output.setPlainText("\n\n".join(selected))
            self.output.moveCursor(QTextCursor.MoveOperation.Start)
        except Exception as e:
            self.output.setPlainText(f"⚠️ Error loading xss.txt: {e}")
            self.current_payloads = []

    def test_payload(self):
        target_text = self.url_input.text().strip()
        if not target_text:
            self.feedback.setPlainText("⚠️ Enter a valid target URL or file path first.")
            return
        urls = [line.strip() for line in target_text.splitlines() if line.strip()]
        if not urls:
            urls = [target_text]
        if not self.current_payloads:
            self.feedback.setPlainText("⚠️ Generate payload(s) first.")
            return

        self.feedback.setPlainText("⏳ Testing payload(s) on target(s)...")
        self.repaint()

        results = []
        for url in urls:
            for payload in self.current_payloads:
                try:
                    resp = requests.get(url + payload, timeout=10)
                    content = resp.text
                    patterns = [
                        re.escape(payload),
                        r"(?i)<script>alert\(",
                        r"(?i)onerror=",
                        r"(?i)onload=",
                        r"(?i)javascript:",
                        r"(?i)document\.cookie",
                    ]
                    matched = any(re.search(p, content) for p in patterns)
                    if matched:
                        results.append(f"✅ [{url}] Reflected: {payload[:40]}...")
                    else:
                        if resp.status_code in (403, 406):
                            results.append(f"❌ [{url}] Blocked (HTTP {resp.status_code}): {payload[:40]}...")
                        elif resp.status_code >= 500:
                            results.append(f"⚠️ [{url}] Server error (HTTP {resp.status_code}): {payload[:40]}...")
                        else:
                            results.append(f"⚠️ [{url}] No reflection (HTTP {resp.status_code}): {payload[:40]}...")
                except requests.exceptions.Timeout:
                    results.append(f"❌ [{url}] Timeout: {payload[:40]}...")
                except requests.exceptions.RequestException as e:
                    results.append(f"❌ [{url}] Request error: {e}")

        self.feedback.clear()
        for line in results:
            self._append_colored_feedback(line)

    def _append_colored_feedback(self, text):
        fmt = QTextCharFormat()
        if text.startswith("✅"):
            fmt.setForeground(QColor("lime"))
        elif text.startswith("⚠️"):
            fmt.setForeground(QColor("orange"))
        else:
            fmt.setForeground(QColor("red"))
        cursor = self.feedback.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text + "\n", fmt)
        self.feedback.setTextCursor(cursor)

    def export_payloads(self):
        if not self.current_payloads:
            self.feedback.setPlainText("⚠️ No payloads to export.")
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Save Payloads", "", "Text Files (*.txt)")
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write("\n\n".join(self.current_payloads))
                self.feedback.setPlainText(f"✅ Payloads exported to {filename}")
            except Exception as e:
                self.feedback.setPlainText(f"❌ Failed to export: {e}")

    def export_report(self):
        if not self.current_payloads and not self.feedback.toPlainText().strip():
            self.feedback.setPlainText("⚠️ Nothing to report.")
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Save Report", "", "Text Files (*.txt)")
        if filename:
            try:
                report_lines = []
                report_lines.append("==== ScriptFang Report ====")
                report_lines.append(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                report_lines.append(f"Target(s): {self.url_input.text().strip()}")
                report_lines.append("")
                report_lines.append("=== Payloads Used ===")
                report_lines.extend(self.current_payloads if self.current_payloads else ["(None)"])
                report_lines.append("")
                report_lines.append("=== Feedback / Results ===")
                report_lines.append(self.feedback.toPlainText().strip() or "(No feedback)")
                report_text = "\n".join(report_lines)

                with open(filename, "w", encoding="utf-8") as f:
                    f.write(report_text)

                self.feedback.setPlainText(f"✅ Report exported to {filename}")
            except Exception as e:
                self.feedback.setPlainText(f"❌ Failed to export report: {e}")

    def start_fuzzing(self):
        target_text = self.url_input.text().strip()
        if not target_text:
            self.feedback.setPlainText("⚠ Enter a valid target URL first.")
            return
        urls = [line.strip() for line in target_text.splitlines() if line.strip()]
        if not urls:
            urls = [target_text]
        if not self.current_payloads:
            self.feedback.setPlainText("⚠ Generate payloads first.")
            return
        self.feedback.setPlainText("⏳ Starting fuzzing...\n")
        self.fuzz_thread = FuzzThread(urls, self.current_payloads)
        self.fuzz_thread.update_signal.connect(self._append_colored_feedback)
        self.fuzz_thread.finished_signal.connect(lambda: self.feedback.append("✅ Fuzzing completed"))
        self.fuzz_thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScriptFangGUI()
    window.show()
    sys.exit(app.exec())
