#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

"""Main entry point for the Police Transcriber application."""

import sys
import traceback
from datetime import datetime

from PyQt5.QtCore import QTimer, QtMsgType, qInstallMessageHandler
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog

from config import (
    app_logger,
    debug_logger,
    VERBOSE,
    LOG_FOLDER,
    OUTPUT_FOLDER,
    load_config,
    save_config,
)
from core.model_downloader import ensure_model_available
from gui.main_window import MainWindow
from gui.splash import SplashScreen


def rotate_log_file(log_file: str, max_size: int = 10 * 1024 * 1024) -> None:
    """Rotate the log file if it exceeds the maximum size.

    Args:
        log_file: Path to the log file.
        max_size: Maximum file size in bytes (default: 10MB).
    """
    if not os.path.exists(log_file) or os.path.getsize(log_file) <= max_size:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    new_file = os.path.join(os.path.dirname(log_file), f"app_{timestamp}.log")
    try:
        os.rename(log_file, new_file)
        debug_logger.debug(f"Rotated log file {log_file} to {new_file} due to size exceeding {max_size} bytes")
    except Exception as e:
        app_logger.error(f"Failed to rotate log file {log_file}: {e}")


def qt_message_handler(msg_type: QtMsgType, context: object, msg: str) -> None:
    """Handle Qt messages and log them using configured loggers.

    Args:
        msg_type: Type of Qt message.
        context: Message context (unused).
        msg: The message content.
    """
    msg = f"Qt Message: {msg}"
    if msg_type == QtMsgType.QtDebugMsg:
        debug_logger.debug(msg)
    elif msg_type == QtMsgType.QtInfoMsg:
        app_logger.info(msg)
    elif msg_type == QtMsgType.QtWarningMsg:
        app_logger.warning(msg)
    elif msg_type == QtMsgType.QtCriticalMsg:
        app_logger.error(msg)
    elif msg_type == QtMsgType.QtFatalMsg:
        app_logger.critical(msg)
    else:
        app_logger.info(msg)


def prompt_output_folder(parent) -> str:
    """Prompt the user to select an output folder on first run.

    Args:
        parent: The parent widget for the file dialog.

    Returns:
        The selected folder path or the default OUTPUT_FOLDER if cancelled.
    """
    folder = QFileDialog.getExistingDirectory(
        parent,
        "Selecionar Pasta de Saída para Transcrições",
        OUTPUT_FOLDER or os.path.expanduser("~"),
        QFileDialog.ShowDirsOnly
    )
    if folder:
        app_logger.info(f"Selected output folder on first run: {folder}")
        debug_logger.debug(f"First-run output folder set to: {folder}")
        return folder
    app_logger.info("No output folder selected, using default")
    debug_logger.debug(f"Using default output folder: {OUTPUT_FOLDER}")
    return OUTPUT_FOLDER


def main() -> None:
    """Initialize the application, check model availability, and display the main window."""
    # Load configuration
    config = load_config()
    app_logger.info("Starting Police Transcriber application")
    debug_logger.debug(f"Loaded configuration: {config}")

    # Rotate log files
    rotate_log_file(os.path.join(LOG_FOLDER, "app.log"))
    if VERBOSE:
        rotate_log_file(os.path.join(LOG_FOLDER, "debug.log"))

    # Initialize QApplication and load stylesheet
    app = QApplication(sys.argv)
    try:
        with open("styles.qss", "r") as f:
            app.setStyleSheet(f.read())
        debug_logger.debug("Loaded styles.qss")
    except Exception as e:
        app_logger.error(f"Failed to load styles.qss: {e}")
        debug_logger.debug(f"Stylesheet loading error: {str(e)}")
    debug_logger.debug("QApplication initialized")

    # Configure Qt logging for debugging
    os.environ["QT_LOGGING_RULES"] = "qt5.debug=true"
    debug_logger.debug("Qt logging rules set")

    # Redirect Qt messages to logger
    qInstallMessageHandler(qt_message_handler)
    debug_logger.debug("Qt message handler installed")

    # Prompt for output folder on first run
    if not os.path.exists(OUTPUT_FOLDER):
        debug_logger.debug("Output folder does not exist, prompting user")
        splash = SplashScreen()
        splash.show()
        splash.setMessage("Configurando pasta de saída...")
        output_folder = prompt_output_folder(splash)
        save_config(
            selected_model=config["selected_model"],
            logging_level=config["logging_level"],
            verbose=config["verbose"],
            output_folder=output_folder,
            check_for_updates=config["check_for_updates"],
        )
        splash.close()
        debug_logger.debug("Initial output folder prompt completed")
    else:
        # Show splash screen
        splash = SplashScreen()
        splash.show()
        splash.setMessage("Verificando modelo...")
        debug_logger.debug("Splash screen displayed with message: Verificando modelo...")

    # Keep a global reference to MainWindow to prevent garbage collection
    global main_window
    main_window = None

    def continue_after_model() -> None:
        """Open the main window if the model is available, or exit on failure."""
        debug_logger.debug("Entering continue_after_model")
        try:
            if ensure_model_available():
                app_logger.info("Model available, loading interface")
                debug_logger.debug("Model verification successful")
                splash.setMessage("Carregando interface...")
                debug_logger.debug("Splash message updated: Carregando interface...")
                global main_window
                main_window = MainWindow()
                debug_logger.debug("MainWindow created")
                splash.close()
                debug_logger.debug("Splash screen closed")
                main_window.show()
                app_logger.info("Main window displayed")
                debug_logger.debug("MainWindow shown")
            else:
                app_logger.error("Model download failed")
                debug_logger.debug("Model download failed, showing error message")
                QMessageBox.critical(
                    splash,
                    "Modelo Não Disponível",
                    "Falha ao baixar o modelo de transcrição. Verifique sua conexão com a internet e tente novamente."
                )
                splash.close()
                debug_logger.debug("Splash screen closed after error")
                sys.exit(1)
        except Exception as e:
            app_logger.error(f"Error in continue_after_model: {e}", exc_info=True)
            debug_logger.debug(f"Exception in continue_after_model: {traceback.format_exc()}")
            splash.close()
            debug_logger.debug("Splash screen closed after exception")
            sys.exit(1)

    def run_model_download() -> None:
        """Trigger model download and proceed to main window."""
        debug_logger.debug("Starting model download")
        success = ensure_model_available(
            on_status=splash.setMessage,
            on_progress=splash.setProgress
        )
        app_logger.info(f"Model download result: {success}")
        debug_logger.debug(f"Model download completed with success: {success}")
        QTimer.singleShot(0, continue_after_model)

    # Schedule model download
    QTimer.singleShot(100, run_model_download)
    debug_logger.debug("Scheduled model download")

    try:
        app_logger.info("Entering Qt event loop")
        debug_logger.debug("Starting Qt event loop")
        result = app.exec_()
        app_logger.info(f"Qt event loop exited with code: {result}")
        debug_logger.debug(f"Application event loop exited with code: {result}")
        sys.exit(result)
    except Exception as e:
        app_logger.error(f"Unhandled exception in application loop: {e}", exc_info=True)
        debug_logger.debug(f"Unhandled exception in application loop: {traceback.format_exc()}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()