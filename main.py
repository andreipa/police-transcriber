#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

import ctypes
import logging
import os
import sys
import warnings

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from config import SUPPRESS_QT_WARNINGS
from gui.main_window import MainWindow
from gui.splash import SplashScreen


def configure_logging():
    """Configure logging to capture warnings and errors in a log file."""
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        filename="logs/app.log",
        level=logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )


def suppress_system_warnings():
    """Suppress system-specific warnings for a cleaner application runtime."""
    if SUPPRESS_QT_WARNINGS:
        sys.stderr = open(os.devnull, 'w')
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        try:
            ctypes.CDLL(None).objc_getClass(b"NSWindow")
        except Exception:
            pass


def load_stylesheet(app: QApplication) -> None:
    """Load and apply the global stylesheet to the application."""
    with open("assets/styles/styles.qss", "r") as f:
        style = f.read()
        app.setStyleSheet(style)


def show_main_window(splash: SplashScreen) -> None:
    """Initialize and display the main application window, closing the splash screen."""
    global main_window
    try:
        splash.close()
        main_window = MainWindow()
        main_window.show()
    except Exception as e:
        logging.error("Error initializing main window", exc_info=True)


def main():
    """Initialize the application, display the splash screen, and start the main event loop."""
    configure_logging()
    suppress_system_warnings()

    app = QApplication(sys.argv)
    load_stylesheet(app)

    splash = SplashScreen()
    splash.show()

    # Schedule the main window to appear after a 2.5-second delay
    QTimer.singleShot(2500, lambda: show_main_window(splash))

    try:
        sys.exit(app.exec_())
    except Exception as e:
        logging.error("Unhandled exception in application loop", exc_info=True)


if __name__ == "__main__":
    main()
