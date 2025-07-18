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
        self.setFixedSize(1024, 600)

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.payload_dir = os.path.join(base_dir, "tools", "payloads")

        gif_path = os.path.join(base_dir, "assets", "dragons.gif")

        self.bg_label = QLabel(self)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.bg_label.setStyleSheet("background: black;")
        self.bg_label.lower()

        self.movie = QMovie(gif_path)
        if not self.movie.isValid():
            self.bg_label.setText("Failed to load GIF")
            self.bg_label.setStyleSheet("color: red; background: black; font-size: 24px;")
        else:
            self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
            self.movie.setSpeed(100)
            self.movie.setScaledSize(QSize(self.width(), self.height()))
            self.bg_label.setMovie(self.movie)
            self.movie.start()

        self.title = QLabel("SCRIPTFANG", self)
        self.title.setStyleSheet("color: #00ff00; background: transparent;")
        self.title.setFont(QFont("Courier", 45, QFont.Weight.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setGeometry(0, 20, self.width(), 50)

        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter target URL (e.g. https://victim.com/search?q=)")
        input_width = 600
        input_height = 35
        self.url_input.setGeometry((self.width() - input_width) // 2, 90, input_width, input_height)
        self.url_input.setStyleSheet(
            "background-color: rgba(0,0,0,0.6); color: #00ff00; font-size: 14px; border: 2px solid #00ff00; border-radius: 10px;"
        )
        self.url_input.setFont(QFont("Courier", 12))

        output_width = 700
        output_height = 110
        self.output = QTextEdit(self)
        self.output.setGeometry((self.width() - output_width) // 2, 150, output_width, output_height)
        self.output.setReadOnly(True)
        self.output.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0.6); color: #00ff00; font-size: 14px; border: 2px solid #00ff00; border-radius: 10px;"
        )
        self.output.setFont(QFont("Courier", 12))
        self.output.setText("// XSS Payload will appear here\n")

        self.feedback = QLabel("", self)
        self.feedback.setGeometry(0, 270, self.width(), 30)
        self.feedback.setStyleSheet("color: #00ff00; background: transparent; font-size: 14px;")
        self.feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        start_y = 320

        for idx, (label, filename) in enumerate(self.payload_buttons[:buttons_per_row]):
            x = start_x + idx * (btn_width + spacing)
            btn = QPushButton(label, self)
            btn.setGeometry(x, start_y, btn_width, btn_height)
            btn.setStyleSheet("background-color: rgba(0,128,0,0.7); color: white; font-size: 13px; border-radius: 6px;")
            btn.clicked.connect(lambda checked, f=filename: self.generate_payload_from_file(f))
            self.buttons[label] = btn

        second_row_y = start_y + btn_height + 12
        for idx, (label, filename) in enumerate(self.payload_buttons[buttons_per_row:buttons_per_row*2]):
            x = start_x + idx * (btn_width + spacing)
            btn = QPushButton(label, self)
            btn.setGeometry(x, second_row_y, btn_width, btn_height)
            btn.setStyleSheet("background-color: rgba(0,128,0,0.7); color: white; font-size: 13px; border-radius: 6px;")
            btn.clicked.connect(lambda checked, f=filename: self.generate_payload_from_file(f))
            self.buttons[label] = btn

        multi_btn_width = 200
        multi_btn_height = 40
        multi_btn_y = second_row_y + btn_height + 25
        self.multi_button = QPushButton("Generate Multiple Payloads", self)
        self.multi_button.setGeometry((self.width() - multi_btn_width) // 2, multi_btn_y, multi_btn_width, multi_btn_height)
        self.multi_button.setStyleSheet("background-color: rgba(0,100,0,0.7); color: white; font-size: 15px; border-radius: 8px;")
        self.multi_button.clicked.connect(self.generate_multiple_payloads)

        test_btn_width = 140
        test_btn_height = 40
        test_btn_x = (self.width() + multi_btn_width) // 2 + 15
        self.test_button = QPushButton("Test Payload", self)
        self.test_button.setGeometry(test_btn_x, multi_btn_y, test_btn_width, test_btn_height)
        self.test_button.setStyleSheet("background-color: rgba(128,0,0,0.7); color: white; font-size: 15px; border-radius: 8px;")
        self.test_button.clicked.connect(self.test_payload)

        # --- Added Buttons for Auto Mutation and WAF Evasion ---
        mutate_btn = QPushButton("Mutate Payload", self)
        mutate_btn.setGeometry((self.width() - 300) // 2, multi_btn_y + 60, 140, 35)
        mutate_btn.setStyleSheet("background-color: rgba(0,80,150,0.7); color: white; font-size: 13px; border-radius: 8px;")
        mutate_btn.clicked.connect(self.auto_mutate_payload)
        self.mutate_button = mutate_btn

        waf_btn = QPushButton("WAF Evasion", self)
        waf_btn.setGeometry((self.width() + 20) // 2, multi_btn_y + 60, 140, 35)
        waf_btn.setStyleSheet("background-color: rgba(150,50,0,0.7); color: white; font-size: 13px; border-radius: 8px;")
        waf_btn.clicked.connect(self.apply_waf_evasion)
        self.waf_button = waf_btn

        self.footer = QLabel("GitHub: github.com/Talyx66  |  Made by Talyx", self)
        self.footer.setStyleSheet("color: #00ff00; background: transparent;")
        self.footer.setFont(QFont("Courier", 10))
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer.setGeometry(0, self.height() - 25, self.width(), 25)

        self.current_payloads = []

    def auto_mutate_payload(self):
        if not self.current_payloads:
            self.feedback.setText("\u26a0\ufe0f Generate payload first to mutate.")
            return
        mutated = []
        for payload in self.current_payloads:
            version = ''.join(random.choice([c.upper(), c.lower()]) for c in payload)
            version = version.replace("<", "%3C").replace(">", "%3E")
            version = version.replace("script", "script")
            mutated.append(version)
        self.current_payloads = mutated
        self.output.setPlainText("\n\n".join(mutated))
        self.feedback.setText("\ud83d\udd01 Payloads mutated.")

    def apply_waf_evasion(self):
        if not self.current_payloads:
            self.feedback.setText("\u26a0\ufe0f Generate payload first to apply WAF evasion.")
            return
        evaded = []
        for payload in self.current_payloads:
            version = payload.replace("<script>", "<scr\0ipt>")
            version = version.replace("onerror", "onerror%00")
            version = version.replace("=", "%3D")
            version = version.replace("alert", "alert")
            evaded.append(version)
        self.current_payloads = evaded
        self.output.setPlainText("\n\n".join(evaded))
        self.feedback.setText("\ud83d\udee1\ufe0f WAF evasion applied.")

    # The rest of your existing methods go here, unchanged...

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ScriptFangGUI()
    gui.show()
    sys.exit(app.exec())
