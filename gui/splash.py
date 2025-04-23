#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

from config import APP_NAME, SLOGAN_EN, VERSION


class SplashScreen(QWidget):
    """A frameless splash screen displaying the application logo, name, slogan, and version."""

    def __init__(self) -> None:
        """Initialize the splash screen with centered logo, labels, and custom styling."""
        super().__init__()

        self.setWindowTitle(APP_NAME)
        self.setFixedSize(550, 450)
        self.setStyleSheet("background-color: #121212; color: white;")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Load and scale the splash image
        splash_path = os.path.join("assets", "images", "splash.png")
        pixmap = QPixmap(splash_path)
        scaled_pixmap = pixmap.scaledToWidth(300, Qt.SmoothTransformation)
        logo = QLabel()
        logo.setPixmap(scaled_pixmap)
        logo.setAlignment(Qt.AlignCenter)

        # Create application name label
        app_name_label = QLabel(APP_NAME)
        app_name_label.setFont(QFont("Arial", 25, QFont.Bold))
        app_name_label.setAlignment(Qt.AlignCenter)

        # Create slogan label
        slogan_label = QLabel(SLOGAN_EN)
        slogan_label.setFont(QFont("Arial", 15))
        slogan_label.setAlignment(Qt.AlignCenter)

        # Create version label
        version_label = QLabel(VERSION)
        version_label.setFont(QFont("Arial", 10))
        version_label.setStyleSheet("color: gray;")
        version_label.setAlignment(Qt.AlignCenter)

        # Add widgets to layout
        layout.addWidget(logo)
        layout.addWidget(app_name_label)
        layout.addWidget(slogan_label)
        layout.addWidget(version_label)

        self.setLayout(layout)