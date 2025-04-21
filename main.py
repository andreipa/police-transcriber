# main.py

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from gui.splash import SplashScreen
from gui.main_window import MainWindow
from config import SUPPRESS_QT_WARNINGS

# NEW: Suppress macOS native stderr output (e.g., NSOpenPanel warning)
if SUPPRESS_QT_WARNINGS:
    sys.stderr = open(os.devnull, 'w')  # <- This hides Cocoa (macOS) errors too

    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    import ctypes
    try:
        ctypes.CDLL(None).objc_getClass(b"NSWindow")
    except Exception:
        pass

# Setup logging for warnings and errors
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/app.log",
    level=logging.WARNING,  # Logs WARNING and ERROR
    format="%(asctime)s [%(levelname)s] %(message)s"
)

app = QApplication(sys.argv)
# Load global stylesheet
with open("assets/styles/styles.qss", "r") as f:
    style = f.read()
    app.setStyleSheet(style)

# Show splash screen
splash = SplashScreen()
splash.show()

# Main window instance declared globally to prevent garbage collection
main_window = None

def show_main_window():
    global main_window
    try:
        splash.close()
        main_window = MainWindow()
        main_window.show()
    except Exception as e:
        logging.error("Error initializing main window", exc_info=True)

# Delay showing the main window for 2.5 seconds
QTimer.singleShot(2500, show_main_window)

# Run the main application loop
try:
    sys.exit(app.exec_())
except Exception as e:
    logging.error("Unhandled exception in application loop", exc_info=True)
