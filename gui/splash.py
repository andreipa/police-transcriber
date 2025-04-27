#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

"""Frameless splash screen for the Police Transcriber application."""

import os

from PyQt5.QtCore import QCoreApplication, QEventLoop, Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QLabel, QProgressBar, QSpacerItem, QSizePolicy, QVBoxLayout, QWidget

from config import APP_NAME, SLOGAN_EN, VERSION, app_logger, debug_logger


class SplashScreen(QWidget):
    """A frameless splash screen displaying the application logo, name, slogan, version, and download progress."""

    def __init__(self) -> None:
        """Initialize the splash screen with centered logo, labels, and progress bar."""
        super().__init__()
        app_logger.debug("Initializing SplashScreen")
        debug_logger.debug("Starting SplashScreen setup")

        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(550, 500)
        self.setObjectName("SplashScreen")  # For stylesheet targeting
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Load and scale the splash image
        splash_path = os.path.join("assets", "images", "splash.png")
        pixmap = QPixmap(splash_path)
        scaled_pixmap = pixmap.scaledToWidth(300, Qt.SmoothTransformation)
        logo = QLabel()
        logo.setPixmap(scaled_pixmap)
        logo.setAlignment(Qt.AlignCenter)
        logo.setObjectName("SplashLogo")
        if not os.path.exists(splash_path):
            app_logger.error(f"Splash image not found: {splash_path}")
            debug_logger.debug(f"Missing splash image: {splash_path}")
            logo.setText("Logo não encontrado")

        # Application name label
        app_name_label = QLabel(APP_NAME)
        app_name_label.setFont(QFont("Arial", 25, QFont.Bold))
        app_name_label.setAlignment(Qt.AlignCenter)
        app_name_label.setObjectName("SplashAppName")

        # Slogan label
        slogan_label = QLabel(SLOGAN_EN)
        slogan_label.setFont(QFont("Arial", 15))
        slogan_label.setAlignment(Qt.AlignCenter)
        slogan_label.setObjectName("SplashSlogan")

        # Version label
        version_label = QLabel(VERSION)
        version_label.setFont(QFont("Arial", 10))
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setObjectName("SplashVersion")

        # Progress bar for download
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedWidth(300)
        self.progress_bar.setObjectName("SplashProgressBar")

        # Message label
        self.message_label = QLabel("Inicializando...")
        self.message_label.setFont(QFont("Arial", 11))
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setObjectName("SplashMessage")

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
        app_logger.debug("SplashScreen initialization completed")
        debug_logger.debug("SplashScreen setup finished")

    def setMessage(self, message: str) -> None:
        """Update the message shown on the splash screen.

        Args:
            message: The message to display.
        """
        self.message_label.setText(message)
        QCoreApplication.processEvents(QEventLoop.AllEvents, 100)
        app_logger.debug(f"Splash screen message updated: {message}")
        debug_logger.debug(f"Set splash message to: {message}")

    def setProgress(self, value: int) -> None:
        """Set the progress bar value.

        Args:
            value: The progress percentage (0-100).
        """
        self.progress_bar.setValue(value)
        QCoreApplication.processEvents(QEventLoop.AllEvents, 100)
        app_logger.debug(f"Splash screen progress updated: {value}%")
        debug_logger.debug(f"Set splash progress to: {value}")
