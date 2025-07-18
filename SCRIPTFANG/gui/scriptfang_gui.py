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
        self.title.setFont(QFont("Courier", 45, QFont.Weight.Bold))
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

        # Context selector combo box - placed right of URL input
        combo_width = 180
        combo_x = (self.width() + input_width) // 2 + 10  # 10px right to url input
        self.context_combo = QComboBox(self)
        self.context_combo.setGeometry(combo_x, 90, combo_width, input_height)
        self.context_combo.setStyleSheet(
            "background-color: rgba(0,0,0,0.6); color: #00ff00; font-size: 13px; border: 2px solid #00ff00; border-radius: 10px;"
        )
        self.context_combo.setFont(QFont("Courier", 11))
        self.context_combo.addItems([
            "General", "HTML Context", "Attribute Context", "JavaScript Context"
        ])

        # WAF Bypass checkbox - right of combo box
        cb_width = 120
        cb_x2 = combo_x + combo_width + 10
        self.waf_checkbox = QCheckBox("WAF Bypass", self)
        self.waf_checkbox.setGeometry(cb_x2, 90, cb_width, input_height)
        self.waf_checkbox.setStyleSheet(
            "color: #00ff00; font-size: 13px;"
        )
        self.waf_checkbox.setFont(QFont("Courier", 11))

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
            btn.clicked.connect(lambda _, f=filename: self.generate_payload_from_file(f))
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
            btn.clicked.connect(lambda _, f=filename: self.generate_payload_from_file(f))
            self.buttons[label] = btn

        # Generate Multiple Payloads button centered below payload buttons
        multi_btn_width = 200
        multi_btn_height = 40
        multi_btn_y = second_row_y + btn_height + 25
        self.multi_button = QPushButton("Generate Multiple Payloads", self)
        self.multi_button.setGeometry(
            (self.width() - multi_btn_width) // 2,
            multi_btn_y,
            multi_btn_width,
            multi_btn_height
        )
        self.multi_button.setStyleSheet(
            "background-color: rgba(0,100,0,0.7); color: white; font-size: 15px; border-radius: 8px;"
        )
        self.multi_button.clicked.connect(self.generate_multiple_payloads)

        # Test Payload button next to multi_button
        test_btn_width = 140
        test_btn_height = 40
        test_btn_x = (self.width() + multi_btn_width) // 2 + 15
        self.test_button = QPushButton("Test Payload", self)
        self.test_button.setGeometry(
            test_btn_x,
            multi_btn_y,
            test_btn_width,
            test_btn_height
        )
        self.test_button.setStyleSheet(
            "background-color: rgba(128,0,0,0.7); color: white; font-size: 15px; border-radius: 8px;"
        )
        self.test_button.clicked.connect(self.test_payload)

        # Footer label (GitHub + credit) at the bottom center
        footer_height = 25
        self.footer = QLabel("GitHub: github.com/Talyx66  |  Made by Talyx", self)
        self.footer.setStyleSheet("color: #00ff00; background: transparent;")
        self.footer.setFont(QFont("Courier", 10))
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer.setGeometry(0, self.height() - footer_height, self.width(), footer_height)

        # Store current payloads
        self.current_payloads = []

    def resizeEvent(self, event):
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        if self.movie and self.movie.isValid():
            self.movie.setScaledSize(QSize(self.width(), self.height()))

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

        # Reposition context combo box and checkbox based on url_input geometry
        combo_x = (self.width() + input_width) // 2 + 10
        self.context_combo.setGeometry(combo_x, 90, 180, 35)
        self.waf_checkbox.setGeometry(combo_x + 180 + 10, 90, 120, 35)

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

        multi_btn_width = 200
        multi_btn_height = 40
        multi_btn_y = second_row_y + btn_height + 25
        self.multi_button.setGeometry(
            (self.width() - multi_btn_width) // 2,
            multi_btn_y,
            multi_btn_width,
            multi_btn_height
        )

        test_btn_width = 140
        test_btn_height = 40
        test_btn_x = (self.width() + multi_btn_width) // 2 + 15
        self.test_button.setGeometry(
            test_btn_x,
            multi_btn_y,
            test_btn_width,
            test_btn_height
        )

        footer_height = 25
        self.footer.setGeometry(0, self.height() - footer_height, self.width(), footer_height)

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

            # Check WAF Bypass toggle: if checked and filename != waf_bypass.txt, append waf bypass payloads
            waf_enabled = self.waf_checkbox.isChecked()
            if waf_enabled and filename != "waf_bypass.txt":
                waf_path = os.path.join(self.payload_dir, "waf_bypass.txt")
                with open(waf_path, 'r', encoding='utf-8') as waf_file:
                    waf_payloads = [line.strip() for line in waf_file if line.strip()]
                # Mix waf payloads with original payloads
                payloads.extend(waf_payloads)

            # Apply context-based payload filtering or modification
            context = self.context_combo.currentText()

            # For example: you could filter or tweak payloads based on context, here just a dummy example
            if context == "HTML Context":
                payloads = [p for p in payloads if "<script" not in p.lower()]
            elif context == "Attribute Context":
                payloads = [p for p in payloads if "onerror" in p.lower() or "onload" in p.lower()]
            elif context == "JavaScript Context":
                payloads = [p for p in payloads if "<script" in p.lower()]

            if not payloads:
                self.output.setPlainText("// No payloads found after applying context filter.")
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

            # If WAF bypass enabled, append waf bypass payloads to the list
            if self.waf_checkbox.isChecked():
                waf_path = os.path.join(self.payload_dir, "waf_bypass.txt")
                with open(waf_path, 'r', encoding='utf-8') as waf_file:
                    waf_payloads = [line.strip() for line in waf_file if line.strip()]
                payloads.extend(waf_payloads)

            # Context filtering (same as single payload)
            context = self.context_combo.currentText()
            if context == "HTML Context":
                payloads = [p for p in payloads if "<script" not in p.lower()]
            elif context == "Attribute Context":
                payloads = [p for p in payloads if "onerror" in p.lower() or "onload" in p.lower()]
            elif context == "JavaScript Context":
                payloads = [p for p in payloads if "<script" in p.lower()]

            if not payloads:
                self.output.setPlainText("// No payloads found after applying context filter.")
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
           
