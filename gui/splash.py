# gui/splash.py

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
import os

from config import APP_NAME, VERSION, SLOGAN_EN

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()

        splash_path = os.path.join("assets","images","splash.png")
        pixmap = QPixmap(splash_path)
        max_logo_width = 550  # or tweak this value if needed
        scaled_pixmap = pixmap.scaledToWidth(max_logo_width, Qt.SmoothTransformation)

        logo = QLabel()
        logo.setPixmap(scaled_pixmap)
        logo.setAlignment(Qt.AlignCenter)

        self.setWindowTitle(APP_NAME)
        self.setFixedSize(550, 450)
        self.setStyleSheet("background-color: #121212; color: white;")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Load splash image
        splash_path = os.path.join("assets", "images","splash.png")
        pixmap = QPixmap(splash_path)
        logo = QLabel()
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)

        # App name
        app_name_label = QLabel(APP_NAME)
        app_name_label.setFont(QFont("Arial", 25, QFont.Bold))
        app_name_label.setAlignment(Qt.AlignCenter)

        # Slogan
        slogan_label = QLabel(SLOGAN_EN)
        slogan_label.setFont(QFont("Arial", 15))
        slogan_label.setAlignment(Qt.AlignCenter)

        # Version at the bottom
        version_label = QLabel(VERSION)
        version_label.setFont(QFont("Arial", 10))
        version_label.setStyleSheet("color: gray;")
        version_label.setAlignment(Qt.AlignCenter)

        # Add all to layout
        layout.addWidget(logo)
        layout.addWidget(app_name_label)
        layout.addWidget(slogan_label)
        layout.addWidget(version_label)

        self.setLayout(layout)