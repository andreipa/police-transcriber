#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

import logging
import os
import sys
import traceback

from PyQt5.QtCore import QTimer, QtMsgType, qInstallMessageHandler
from PyQt5.QtWidgets import QApplication, QMessageBox

from config import AVAILABLE_MODELS, SELECTED_MODEL, HF_TOKEN
from core.model_downloader import ensure_model_available
from gui.main_window import MainWindow
from gui.splash import SplashScreen


def configure_logging() -> None:
    """Configure logging to capture debug, warnings, and errors in a log file."""
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        filename="logs/app.log",
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    logging.debug("Logging configured")


def qt_message_handler(msg_type: QtMsgType, context: object, msg: str) -> None:
    """Handle Qt messages and log them."""
    if msg_type == QtMsgType.QtDebugMsg:
        logging.debug(f"Qt Debug: {msg}")
    elif msg_type == QtMsgType.QtInfoMsg:
        logging.info(f"Qt Info: {msg}")
    elif msg_type == QtMsgType.QtWarningMsg:
        logging.warning(f"Qt Warning: {msg}")
    elif msg_type == QtMsgType.QtCriticalMsg:
        logging.error(f"Qt Critical: {msg}")
    elif msg_type == QtMsgType.QtFatalMsg:
        logging.critical(f"Qt Fatal: {msg}")
    else:
        logging.info(f"Qt Unknown: {msg}")


def main() -> None:
    """Initialize the application, check model availability, and display the main window."""
    configure_logging()
    logging.debug("Starting application")

    # Disable SUPPRESS_QT_WARNINGS for debugging
    os.environ["QT_LOGGING_RULES"] = "qt5.debug=true"
    logging.debug("Qt logging rules set")

    # Redirect Qt messages to logger
    qInstallMessageHandler(qt_message_handler)
    logging.debug("Qt message handler installed")

    app = QApplication(sys.argv)
    logging.debug("QApplication initialized")

    splash = SplashScreen()
    splash.show()
    splash.setMessage("Verificando modelo...")
    logging.debug("Splash screen displayed")

    # Keep a global reference to MainWindow to prevent garbage collection
    global main_window
    main_window = None

    def continue_after_model() -> None:
        """Open the main window if the model is available, or exit on failure."""
        logging.debug("Entering continue_after_model")
        try:
            if ensure_model_available():
                logging.debug("Model available, loading interface")
                splash.setMessage("Carregando interface...")
                global main_window
                main_window = MainWindow()
                logging.debug("MainWindow created")
                splash.close()
                logging.debug("Splash screen closed")
                main_window.show()
                logging.debug("MainWindow shown")
            else:
                logging.error("Model download failed")
                QMessageBox.critical(
                    splash,
                    "Modelo Não Disponível",
                    "Falha ao baixar o modelo de transcrição. Verifique sua conexão com a internet e tente novamente."
                )
                splash.close()
                logging.debug("Splash screen closed after error")
                sys.exit(1)
        except Exception as e:
            logging.error(f"Error in continue_after_model: {e}", exc_info=True)
            splash.close()
            sys.exit(1)

    def run_model_download() -> None:
        """Trigger model download and proceed to main window."""
        logging.debug("Starting model download")
        token = HF_TOKEN if AVAILABLE_MODELS[SELECTED_MODEL]["requires_token"] else None
        success = ensure_model_available(
            on_status=splash.setMessage,
            on_progress=splash.setProgress,
            token=token
        )
        logging.debug(f"Model download result: {success}")
        QTimer.singleShot(0, continue_after_model)

    QTimer.singleShot(100, run_model_download)

    try:
        logging.debug("Entering Qt event loop")
        result = app.exec_()
        logging.debug(f"Qt event loop exited with code: {result}")
        sys.exit(result)
    except Exception as e:
        logging.error(f"Unhandled exception in application loop: {e}", exc_info=True)
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()