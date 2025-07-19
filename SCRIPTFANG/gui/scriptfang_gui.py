import sys
import os
import random
import time
import requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QTextEdit, QPushButton,
                             QVBoxLayout, QWidget, QComboBox, QFileDialog, QLineEdit)
from PyQt6.QtGui import QMovie, QFont, QColor
from PyQt6.QtCore import Qt
from bs4 import BeautifulSoup

class ScriptFangGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ScriptFang - XSS Payload Generator & Fuzzer")
        self.setGeometry(100, 100, 850, 600)
        self.setStyleSheet("background-color: black; color: white;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.bg_label = QLabel(self)
        self.bg_movie = QMovie("assets/dragonss.gif")
        self.bg_label.setMovie(self.bg_movie)
        self.bg_movie.start()

        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        self.output_area.setStyleSheet("background-color: black; color: #00FF00; font-family: Consolas; font-size: 13px;")
        self.output_area.setFont(QFont("Consolas", 12))

        self.category_dropdown = QComboBox(self)
        self.category_dropdown.setStyleSheet("background-color: #222; color: white; font-size: 12px;")
        self.load_categories()

        self.target_input = QLineEdit(self)
        self.target_input.setPlaceholderText("Enter target URL (e.g., https://site.com?q=)")
        self.target_input.setStyleSheet("background-color: #222; color: white; padding: 5px;")

        self.multi_payload_btn = QPushButton("Generate Mult- Payloads")
        self.multi_payload_btn.clicked.connect(self.generate_multiple_payloads)
        self.multi_payload_btn.setFixedWidth(180)

        self.test_button = QPushButton("Test Payload")
        self.test_button.clicked.connect(self.test_payload)
        self.test_button.setFixedWidth(140)

        self.export_button = QPushButton("Export Payload(s)")
        self.export_button.clicked.connect(self.export_payloads)
        self.export_button.setFixedWidth(160)

        self.fuzz_button = QPushButton("Fuzz Target")
        self.fuzz_button.clicked.connect(self.fuzz_target)
        self.fuzz_button.setFixedWidth(140)

        self.multi_payload_btn.setStyleSheet("background-color: #2f2f2f; color: white;")
        self.test_button.setStyleSheet("background-color: #3f3f3f; color: white;")
        self.export_button.setStyleSheet("background-color: #4f4f4f; color: white;")
        self.fuzz_button.setStyleSheet("background-color: #5f5f5f; color: white;")

        self.multi_payload_btn.setParent(self)
        self.test_button.setParent(self)
        self.export_button.setParent(self)
        self.fuzz_button.setParent(self)

    def resizeEvent(self, event):
        self.bg_label.resize(self.width(), self.height())
        self.output_area.resize(self.width() - 80, self.height() - 300)
        self.output_area.move(40, 30)
        self.category_dropdown.resize(240, 30)
        self.category_dropdown.move((self.width() - self.category_dropdown.width()) // 2, self.height() - 240)
        self.target_input.resize(self.width() - 160, 30)
        self.target_input.move(80, self.height() - 200)

        btn_spacing = 12
        multi_btn_width = self.multi_payload_btn.width()
        test_btn_width = self.test_button.width()
        export_btn_width = self.export_button.width()
        fuzz_btn_width = self.fuzz_button.width()

        total_width = multi_btn_width + test_btn_width + export_btn_width + fuzz_btn_width + btn_spacing * 3
        start_x = (self.width() - total_width) // 2
        y = self.height() - 130

        self.multi_payload_btn.move(start_x, y)
        self.test_button.move(start_x + multi_btn_width + btn_spacing, y)
        self.export_button.move(start_x + multi_btn_width + test_btn_width + btn_spacing * 2, y)
        self.fuzz_button.move(start_x + multi_btn_width + test_btn_width + export_btn_width + btn_spacing * 3, y)

    def load_categories(self):
        payload_path = os.path.join("tools", "payloads")
        if os.path.exists(payload_path):
            for file in os.listdir(payload_path):
                if file.endswith(".txt"):
                    self.category_dropdown.addItem(file)

    def generate_multiple_payloads(self):
        payload_path = os.path.join("tools", "payloads")
        all_payloads = []
        for file in os.listdir(payload_path):
            if file.endswith(".txt"):
                with open(os.path.join(payload_path, file), "r", encoding="utf-8") as f:
                    all_payloads.extend(f.read().splitlines())
        random.shuffle(all_payloads)
        self.output_area.clear()
        for payload in all_payloads[:50]:
            self.output_area.append(payload)

    def export_payloads(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Payloads", "payloads.txt", "Text Files (*.txt)")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.output_area.toPlainText())

    def test_payload(self):
        url = self.target_input.text()
        payload = self.output_area.toPlainText()

        if not url or not payload:
            self.output_area.append("❌ Missing target URL or payload.")
            return

        try:
            test_url = url + payload
            response = requests.get(test_url, timeout=6)
            soup = BeautifulSoup(response.text, "html.parser")

            if payload in response.text:
                self.output_area.append("✅ Payload reflected in response!")
            else:
                self.output_area.append("❌ Payload not reflected.")
        except Exception as e:
            self.output_area.append(f"❌ Error testing payload: {e}")

    def fuzz_target(self):
        url = self.target_input.text()
        if not url:
            self.output_area.append("❌ No target URL provided for fuzzing.")
            return

        payload_path = os.path.join("tools", "payloads")
        all_payloads = []
        for file in os.listdir(payload_path):
            if file.endswith(".txt"):
                with open(os.path.join(payload_path, file), "r", encoding="utf-8") as f:
                    all_payloads.extend(f.read().splitlines())

        self.output_area.append(f"🔍 Fuzzing {url} with {len(all_payloads)} payloads...")
        for payload in all_payloads:
            test_url = url + payload
            try:
                response = requests.get(test_url, timeout=6)
                if payload in response.text:
                    self.output_area.append(f"✅ Reflected: {payload}")
                elif response.status_code == 403:
                    self.output_area.append(f"🚫 Blocked (403): {payload}")
                else:
                    self.output_area.append(f"❌ Not reflected: {payload}")
            except Exception as e:
                self.output_area.append(f"⚠️ Error with payload: {payload} | {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ScriptFangGUI()
    gui.show()
    sys.exit(app.exec())
