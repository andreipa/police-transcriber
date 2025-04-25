#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

import os

from PyQt5.QtCore import QCoreApplication, QEventLoop, Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QLabel, QProgressBar, QSpacerItem, QSizePolicy, QVBoxLayout, QWidget

from config import APP_NAME, SLOGAN_EN, VERSION


class SplashScreen(QWidget):
    """A frameless splash screen displaying the application logo, name, slogan, version, and download progress."""

    def __init__(self) -> None:
        """Initialize the splash screen with centered logo, labels, and progress bar."""
        super().__init__()

        self.setWindowTitle(APP_NAME)
        self.setFixedSize(550, 500)
        self.setStyleSheet("background-color: #121212; color: white;")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)

        # Load and scale the splash image
        splash_path = os.path.join("assets", "images", "splash.png")
        pixmap = QPixmap(splash_path)
        scaled_pixmap = pixmap.scaledToWidth(300, Qt.SmoothTransformation)
        logo = QLabel()
        logo.setPixmap(scaled_pixmap)
        logo.setAlignment(Qt.AlignCenter)

        # Application name label
        app_name_label = QLabel(APP_NAME)
        app_name_label.setFont(QFont("Arial", 25, QFont.Bold))
        app_name_label.setAlignment(Qt.AlignCenter)

        # Slogan label
        slogan_label = QLabel(SLOGAN_EN)
        slogan_label.setFont(QFont("Arial", 15))
        slogan_label.setAlignment(Qt.AlignCenter)

        # Version label
        version_label = QLabel(VERSION)
        version_label.setFont(QFont("Arial", 10))
        version_label.setStyleSheet("color: gray;")
        version_label.setAlignment(Qt.AlignCenter)

        # Progress bar for download
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedWidth(300)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #444;
                border-radius: 5px;
                background-color: #222;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00cc66;
                border-radius: 5px;
            }
            """
        )

        # Message label
        self.message_label = QLabel("Inicializando...")
        self.message_label.setFont(QFont("Arial", 11))
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("color: #ccc;")

        # Add widgets to layout
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addWidget(logo)
        layout.addWidget(app_name_label)
        layout.addWidget(slogan_label)
        layout.addWidget(version_label)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)
        layout.addWidget(self.message_label, alignment=Qt.AlignCenter)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(layout)

    def setMessage(self, message: str) -> None:
        """Update the message shown on the splash screen.

        Args:
            message: The message to display.
        """
        self.message_label.setText(message)
        QCoreApplication.processEvents(QEventLoop.AllEvents, 100)

    def setProgress(self, value: int) -> None:
        """Set the progress bar value.

        Args:
            value: The progress percentage (0-100).
        """
        self.progress_bar.setValue(value)
        QCoreApplication.processEvents(QEventLoop.AllEvents, 100)
