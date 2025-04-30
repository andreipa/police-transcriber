#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

"""Main application window for the Police Transcriber, providing a GUI for audio transcription."""

import os
import traceback
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

import requests
from PyQt5.QtCore import QPoint, Qt, QThread, QTimer, QUrl, pyqtSignal
from PyQt5.QtGui import QDesktopServices, QIcon, QPixmap
from PyQt5.QtWidgets import (
    QAction, QDialog, QDialogButtonBox, QFileDialog, QHBoxLayout, QLabel, QListWidget,
    QMenu, QMenuBar, QMessageBox, QProgressBar, QPushButton, QStatusBar, QVBoxLayout,
    QWidget, QApplication
)
from packaging import version

from config import (
    APP_NAME, GITHUB_RELEASES_URL, LOG_FOLDER, VERSION,
    is_model_downloaded, app_logger, debug_logger
)
from core.transcriber import transcribe_audio
from gui.settings_dialog import SettingsDialog
from gui.word_editor import WordEditorDialog


class TranscriptionThread(QThread):
    """A thread for transcribing multiple audio files sequentially."""
    progress = pyqtSignal(int)
    current_file = pyqtSignal(str)
    finished = pyqtSignal(str, list)
    failed = pyqtSignal(str)
    cancelled = False

    def __init__(self, files: list[str]) -> None:
        super().__init__()
        self.files = files

    def run(self) -> None:
        try:
            total_files = len(self.files)
            app_logger.info(f"Starting transcription for {total_files} files")
            debug_logger.debug(f"Transcription queue: {self.files}")
            processed_files = []
            for index, file_path in enumerate(self.files):
                if self.cancelled:
                    app_logger.warning("Transcription cancelled by user")
                    debug_logger.debug("Transcription cancelled")
                    return
                app_logger.info(f"Transcribing: {file_path}")
                debug_logger.debug(f"Processing file {index + 1}/{total_files}: {file_path}")
                self.current_file.emit(os.path.basename(file_path))
                success = transcribe_audio(
                    file_path,
                    on_progress=lambda value: self.progress.emit(value),
                    stop_flag=lambda: self.cancelled
                )
                if success == "cancelled":
                    app_logger.info(f"Transcription cancelled for: {file_path}")
                    debug_logger.debug(f"Cancelled transcription for: {file_path}")
                    return
                if not success:
                    app_logger.error(f"Transcription failed for: {file_path}")
                    debug_logger.debug(f"Transcription failed for: {file_path}")
                    self.failed.emit(file_path)
                    return
                processed_files.append(file_path)
                self.progress.emit(int(((index + 1) / total_files) * 100))
            app_logger.info("All files transcribed successfully")
            debug_logger.debug(f"Processed files: {processed_files}")
            self.finished.emit("Todas as transcrições foram concluídas.", processed_files)
        except Exception as e:
            app_logger.error(f"Unhandled error during transcription: {e}", exc_info=True)
            debug_logger.debug(f"Transcription error: {traceback.format_exc()}")
            self.failed.emit("Erro interno na transcrição")

class BackgroundAppUpdateChecker(QThread):
    """A thread for checking application updates in the background."""
    update_available = pyqtSignal(str, str)

    def run(self) -> None:
        try:
            response = requests.get(
                GITHUB_RELEASES_URL,
                headers={"Accept": "application/vnd.github.v3+json"},
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            latest_version = data.get("tag_name", "").lstrip("v")
            release_url = data.get("html_url", "")
            if latest_version and version.parse(latest_version) > version.parse(VERSION):
                app_logger.info(f"New version available: {latest_version}")
                debug_logger.debug(f"Update check found new version: {latest_version}, URL: {release_url}")
                self.update_available.emit(latest_version, release_url)
            else:
                app_logger.info("No new version available")
                debug_logger.debug("Update check: No new version found")
        except requests.RequestException as e:
            app_logger.warning(f"Failed to check for application updates: {e}")
            debug_logger.debug(f"Update check error: {str(e)}")

class ClickableStatusBar(QStatusBar):
    """A custom QStatusBar that emits a signal when clicked."""
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StatusBar")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

class MainWindow(QWidget):
    """Main application window for managing audio file transcription and sensitive word detection."""
    def __init__(self) -> None:
        """Initialize the main window with UI components and transcription controls."""
        super().__init__()
        app_logger.debug("Initializing MainWindow")
        debug_logger.debug("Starting MainWindow setup")
        try:
            self.setWindowTitle("Police Transcriber")
            self.setMinimumSize(600, 520)
            self.setObjectName("MainWindow")

            # Initialize state variables early
            self.queued_files = []
            self.current_file = None
            self.processed_files = []
            self.thread = None
            self.release_url = ""

            layout = QVBoxLayout()
            layout.setAlignment(Qt.AlignTop)
            layout.setSpacing(8)
            layout.setContentsMargins(8, 8, 8, 8)

            # Initialize menu bar
            menu_bar = QMenuBar(self)
            menu_bar.setObjectName("MenuBar")

            # Arquivo menu
            file_menu = menu_bar.addMenu("Arquivo")
            open_file_action = QAction(QIcon("assets/icons/audio_file.png"), "Selecionar Arquivo...", self)
            open_file_action.triggered.connect(self.select_file)
            file_menu.addAction(open_file_action)
            open_folder_action = QAction(QIcon("assets/icons/library_music.png"), "Selecionar Pasta...", self)
            open_folder_action.triggered.connect(self.select_folder)
            file_menu.addAction(open_folder_action)
            file_menu.addSeparator()
            exit_action = QAction(QIcon("assets/icons/exit.png"), "Sair", self)
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)

            # Editar menu
            edit_menu = menu_bar.addMenu("Editar")
            edit_words_action = QAction(QIcon("assets/icons/edit.png"), "Editar Palavras Sensíveis...", self)
            edit_words_action.triggered.connect(self.open_word_editor)
            edit_menu.addAction(edit_words_action)

            # Ferramentas menu
            tools_menu = menu_bar.addMenu("Ferramentas")
            backup_transcriptions_action = QAction(QIcon("assets/icons/backup.png"), u"Fazer Backup das Transcrições...", self)
            backup_transcriptions_action.triggered.connect(self.backup_transcriptions)
            tools_menu.addAction(backup_transcriptions_action)
            open_log_action = QAction(QIcon("assets/icons/log.png"), u"Abrir Log", self)
            open_log_action.triggered.connect(self.open_log_file)
            tools_menu.addAction(open_log_action)
            open_debug_log_action = QAction(QIcon("assets/icons/bug_report.png"), u"Abrir Debug Log", self)
            open_debug_log_action.triggered.connect(self.open_debug_log_file)
            tools_menu.addAction(open_debug_log_action)
            tools_menu.addSeparator()
            settings_action = QAction(QIcon("assets/icons/settings.png"), u"Opções...", self)
            settings_action.triggered.connect(self.open_settings_dialog)
            tools_menu.addAction(settings_action)
            app_logger.debug(f"Added Opções action to Ferramentas menu: {settings_action.text()}")

            # Ajuda menu
            help_menu = menu_bar.addMenu("Ajuda")
            help_action = QAction(QIcon("assets/icons/help.png"), "Ajuda Online...", self)
            help_action.triggered.connect(self.open_help_link)
            help_menu.addAction(help_action)
            about_action = QAction(QIcon("assets/icons/about.png"), "Sobre", self)
            about_action.triggered.connect(self.show_about)
            help_menu.addAction(about_action)

            layout.setMenuBar(menu_bar)

            # Add instruction label
            instruction_label = QLabel("Selecione um arquivo .mp3 ou uma pasta para transcrição:")
            instruction_label.setObjectName("InstructionLabel")
            layout.addWidget(instruction_label)

            # Initialize file selection buttons
            button_layout = QHBoxLayout()
            button_layout.setSpacing(8)
            self.select_file_button = QPushButton("Selecionar Arquivo")
            self.select_file_button.setIcon(QIcon("assets/icons/audio_file.png"))
            self.select_file_button.clicked.connect(self.select_file)
            self.select_file_button.setObjectName("PrimaryButton")
            button_layout.addWidget(self.select_file_button)

            self.select_folder_button = QPushButton("Selecionar Pasta")
            self.select_folder_button.setIcon(QIcon("assets/icons/library_music.png"))
            self.select_folder_button.clicked.connect(self.select_folder)
            self.select_folder_button.setObjectName("PrimaryButton")
            button_layout.addWidget(self.select_folder_button)

            layout.addLayout(button_layout)

            # Initialize file list with context menu
            self.file_list = QListWidget()
            self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
            self.file_list.customContextMenuRequested.connect(self.show_context_menu)
            self.file_list.setObjectName("FileList")
            layout.addWidget(self.file_list)

            # Initialize current file label
            self.current_file_label = QLabel("Arquivo atual: Nenhum")
            self.current_file_label.setAlignment(Qt.AlignCenter)
            self.current_file_label.setObjectName("StatusLabel")
            layout.addWidget(self.current_file_label)

            # Initialize transcription control buttons
            transcribe_layout = QHBoxLayout()
            transcribe_layout.setSpacing(8)
            self.transcribe_button = QPushButton("Iniciar Transcrição")
            self.transcribe_button.setObjectName("PrimaryButton")
            self.transcribe_button.setIcon(QIcon("assets/icons/start.png"))
            self.transcribe_button.clicked.connect(self.start_transcription)
            transcribe_layout.addWidget(self.transcribe_button)

            self.stop_button = QPushButton("Parar")
            self.stop_button.setObjectName("DangerButton")
            self.stop_button.setIcon(QIcon("assets/icons/stop.png"))
            self.stop_button.setEnabled(False)
            self.stop_button.clicked.connect(self.stop_transcription)
            transcribe_layout.addWidget(self.stop_button)
            layout.addLayout(transcribe_layout)

            # Initialize progress bar
            self.progress = QProgressBar()
            self.progress.setValue(0)
            self.progress.setObjectName("TranscriptionProgressBar")
            self.progress.setFormat("%p%")
            self.progress.setTextVisible(True)
            layout.addWidget(self.progress)

            # Initialize elapsed time label
            self.elapsed_label = QLabel("Duração: 00:00:00")
            self.elapsed_label.setAlignment(Qt.AlignCenter)
            self.elapsed_label.setObjectName("StatusLabel")
            layout.addWidget(self.elapsed_label)

            # Initialize status bar
            self.status_bar = ClickableStatusBar()
            self.status_bar.showMessage(f"Modelo carregado: {SELECTED_MODEL}")
            self.status_bar.clicked.connect(self.handle_status_bar_click)
            self.status_bar.messageChanged.connect(self.update_status_bar_cursor)
            layout.addWidget(self.status_bar)

            # Initialize background update checker
            self.update_checker = None
            if CHECK_FOR_UPDATES:
                self.update_checker = BackgroundAppUpdateChecker()
                self.update_checker.update_available.connect(self.notify_update_available)
                self.update_checker.start()
                debug_logger.debug("Started BackgroundAppUpdateChecker")

            # Initialize timer
            self.elapsed_timer = QTimer()
            self.elapsed_timer.timeout.connect(self.update_elapsed_time)
            self.elapsed_seconds = 0

            self.setLayout(layout)
            self.update_transcription_button_state()
            app_logger.debug("MainWindow initialization completed")
            debug_logger.debug("MainWindow setup finished")
        except Exception as e:
            app_logger.error(f"Failed to initialize MainWindow: {e}", exc_info=True)
            debug_logger.debug(f"MainWindow initialization error: {traceback.format_exc()}")
            raise

    def update_transcription_button_state(self) -> None:
        """Update the transcription button's enabled state and tooltip based on model availability and queued files."""
        is_model_available = is_model_downloaded(SELECTED_MODEL)
        has_queued_files = bool(self.queued_files)
        self.transcribe_button.setEnabled(is_model_available and has_queued_files)
        if not is_model_available:
            self.transcribe_button.setToolTip(
                "Modelo selecionado não está baixado. Reinicie o aplicativo após alterar as configurações."
            )
        elif not has_queued_files:
            self.transcribe_button.setToolTip("Nenhum arquivo selecionado para transcrição.")
        else:
            self.transcribe_button.setToolTip("Iniciar a transcrição dos arquivos selecionados.")
        app_logger.debug(f"Transcription button state: enabled={self.transcribe_button.isEnabled()}, "
                         f"model_downloaded={is_model_available}, has_queued_files={has_queued_files}")
        debug_logger.debug(f"Updated transcribe button: enabled={self.transcribe_button.isEnabled()}")

    def closeEvent(self, event) -> None:
        """Handle the window close event and log it."""
        app_logger.debug("MainWindow closeEvent triggered")
        debug_logger.debug("Closing MainWindow")
        event.accept()

    def notify_update_available(self, version: str, release_url: str) -> None:
        """Display a clickable notification in the status bar when a new version is available."""
        self.release_url = release_url
        self.status_bar.showMessage(f"🔔 New version v{version} available! Click to download.")
        self.status_bar.setToolTip(f"A new version (v{version}) is available. Click to visit the download page.")
        self.status_bar.setCursor(Qt.PointingHandCursor)
        app_logger.info(f"Update notification shown: v{version}")
        debug_logger.debug(f"Update notification for version {version}, URL: {release_url}")

    def update_status_bar_cursor(self, message: str) -> None:
        """Update the status bar cursor based on the current message."""
        if message.startswith("🔔 New version"):
            self.status_bar.setCursor(Qt.PointingHandCursor)
        else:
            self.status_bar.setCursor(Qt.ArrowCursor)
        debug_logger.debug(f"Status bar cursor updated for message: {message}")

    def handle_status_bar_click(self) -> None:
        """Handle clicks on the status bar to open the release URL if an update is available."""
        message = self.status_bar.currentMessage()
        if message.startswith("🔔 New version") and self.release_url:
            try:
                QDesktopServices.openUrl(QUrl(self.release_url))
                app_logger.info(f"Opened release URL: {self.release_url}")
                debug_logger.debug(f"User clicked update link: {self.release_url}")
            except Exception as e:
                app_logger.error(f"Failed to open release URL: {e}")
                debug_logger.debug(f"Error opening release URL: {str(e)}")

    def select_file(self) -> None:
        """Open a file dialog to select an MP3 file and update the transcription queue."""
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo MP3", "", "Audio Files (*.mp3)")
        if path:
            self.file_list.clear()
            self.queued_files = [path]
            self.current_file = None
            self.processed_files = []
            self.file_list.addItem(path)
            self.progress.setValue(0)
            self.current_file_label.setText("Arquivo atual: Nenhum")
            self.update_transcription_button_state()
            app_logger.info(f"Selected file for transcription: {path}")
            debug_logger.debug(f"Added file to queue: {path}")

    def select_folder(self) -> None:
        """Open a folder dialog to select a directory and add MP3 files to the transcription queue."""
        folder = QFileDialog.getExistingDirectory(self, "Selecionar Pasta")
        if folder:
            self.file_list.clear()
            self.queued_files = []
            self.current_file = None
            self.processed_files = []
            for filename in os.listdir(folder):
                if filename.endswith(".mp3"):
                    file_path = os.path.join(folder, filename)
                    self.queued_files.append(file_path)
                    self.file_list.addItem(file_path)
            self.progress.setValue(0)
            self.current_file_label.setText("Arquivo atual: Nenhum")
            self.update_transcription_button_state()
            app_logger.info(f"Selected folder for transcription: {folder}")
            debug_logger.debug(f"Added {len(self.queued_files)} files from folder: {folder}")

    def show_context_menu(self, position: QPoint) -> None:
        """Display a context menu for the file list to allow removing queued files."""
        item = self.file_list.itemAt(position)
        if not item:
            return
        selected_file = item.text()
        menu = QMenu(self)
        remove_action = QAction("Remover da Fila", self)
        remove_action.setEnabled(selected_file != self.current_file and selected_file not in self.processed_files)
        remove_action.triggered.connect(lambda: self.remove_from_queue(selected_file))
        menu.addAction(remove_action)
        menu.exec_(self.file_list.mapToGlobal(position))
        debug_logger.debug(f"Showed context menu for file: {selected_file}")

    def remove_from_queue(self, file_path: str) -> None:
        """Remove a file from the transcription queue if it is not currently being processed."""
        if file_path in self.queued_files and file_path != self.current_file:
            self.queued_files.remove(file_path)
            for index in range(self.file_list.count()):
                if self.file_list.item(index).text() == file_path:
                    self.file_list.takeItem(index)
                    break
            app_logger.info(f"Removed {file_path} from queue")
            debug_logger.debug(f"Removed file from queue: {file_path}")
            self.update_transcription_button_state()

    def open_word_editor(self) -> None:
        """Open a dialog for editing the list of sensitive words."""
        try:
            dialog = WordEditorDialog(self)
            dialog.exec_()
            app_logger.info("Opened word editor dialog")
            debug_logger.debug("WordEditorDialog shown")
        except Exception as e:
            app_logger.error(f"Failed to open word editor: {e}")
            debug_logger.debug(f"Word editor error: {str(e)}")
            QMessageBox.critical(self, "Erro", "Não foi possível abrir o editor de palavras sensíveis.")

    def open_log_file(self) -> None:
        """Open the application log file in the default text editor."""
        log_file = os.path.join(LOG_FOLDER, "app.log")
        try:
            if os.path.exists(log_file):
                QDesktopServices.openUrl(QUrl.fromLocalFile(log_file))
                app_logger.info(f"Opened log file: {log_file}")
                debug_logger.debug(f"Log file opened: {log_file}")
            else:
                app_logger.warning("Log file does not exist")
                debug_logger.debug("Attempted to open non-existent log file")
                QMessageBox.warning(self, "Aviso", "O arquivo de log não existe.")
        except Exception as e:
            app_logger.error(f"Failed to open log file: {e}")
            debug_logger.debug(f"Log file open error: {str(e)}")
            QMessageBox.critical(self, "Erro", "Não foi possível abrir o arquivo de log.")

    def backup_transcriptions(self) -> None:
        """Create a ZIP backup of all transcriptions in the output folder and delete the originals."""
        try:
            if not os.path.exists(OUTPUT_FOLDER):
                app_logger.warning("Output folder does not exist")
                debug_logger.debug("Backup attempted but output folder missing")
                QMessageBox.warning(self, "Aviso", "Nenhuma transcrição encontrada para backup.")
                return
            files_to_backup = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".txt")]
            if not files_to_backup:
                app_logger.warning("No transcription files found for backup")
                debug_logger.debug("No .txt files found in output folder for backup")
                QMessageBox.warning(self, "Aviso", "Nenhuma transcrição encontrada para backup.")
                return
            default_filename = f"transcriptions_backup_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.zip"
            zip_path, _ = QFileDialog.getSaveFileName(
                self,
                "Salvar Backup das Transcrições",
                os.path.join(os.path.expanduser("~"), default_filename),
                "ZIP Files (*.zip)"
            )
            if not zip_path:
                app_logger.info("Backup cancelled by user: No save location selected")
                debug_logger.debug("User cancelled backup file selection")
                return
            with ZipFile(zip_path, "w") as zip_file:
                for file_name in files_to_backup:
                    file_path = os.path.join(OUTPUT_FOLDER, file_name)
                    zip_file.write(file_path, file_name)
            for file_name in files_to_backup:
                os.remove(os.path.join(OUTPUT_FOLDER, file_name))
            app_logger.info(f"Created backup: {zip_path} and deleted original transcriptions")
            debug_logger.debug(f"Backup created: {zip_path}, deleted {len(files_to_backup)} files")
            QMessageBox.information(self, "Sucesso", f"Backup criado em {zip_path}. Transcrições originais foram removidas.")
        except Exception as e:
            app_logger.error(f"Failed to backup transcriptions: {e}")
            debug_logger.debug(f"Backup error: {str(e)}")
            QMessageBox.critical(self, "Erro", "Não foi possível criar o backup das transcrições.")

    def open_debug_log_file(self) -> None:
        """Open the debug log file in the default text editor."""
        log_file = os.path.join(LOG_FOLDER, "debug.log")
        try:
            if os.path.exists(log_file):
                QDesktopServices.openUrl(QUrl.fromLocalFile(log_file))
                app_logger.info(f"Opened debug log file: {log_file}")
                debug_logger.debug(f"Debug log file opened: {log_file}")
            else:
                app_logger.warning("Debug log file does not exist")
                debug_logger.debug("Attempted to open non-existent debug log file")
                QMessageBox.warning(self, "Aviso", "O arquivo de debug log não existe.")
        except Exception as e:
            app_logger.error(f"Failed to open debug log file: {e}")
            debug_logger.debug(f"Debug log file open error: {str(e)}")
            QMessageBox.critical(self, "Erro", "Não foi possível abrir o arquivo de debug log.")

    def open_settings_dialog(self) -> None:
        """Open the settings dialog to configure application options."""
        try:
            from config import load_config
            # Reload configuration before opening dialog
            config = load_config()
            global SELECTED_MODEL, OUTPUT_FOLDER, LOGGING_LEVEL, VERBOSE, CHECK_FOR_UPDATES
            SELECTED_MODEL = config["selected_model"]
            OUTPUT_FOLDER = config["output_folder"]
            LOGGING_LEVEL = config["logging_level"]
            VERBOSE = config["verbose"]
            CHECK_FOR_UPDATES = config["check_for_updates"]
            app_logger.debug(f"Loaded configuration before opening SettingsDialog: logging_level={LOGGING_LEVEL}")

            dialog = SettingsDialog(self)
            if dialog.exec_():
                # Reload configuration after saving
                config = load_config()
                SELECTED_MODEL = config["selected_model"]
                OUTPUT_FOLDER = config["output_folder"]
                LOGGING_LEVEL = config["logging_level"]
                VERBOSE = config["verbose"]
                CHECK_FOR_UPDATES = config["check_for_updates"]
                app_logger.debug(f"Loaded configuration after saving: logging_level={LOGGING_LEVEL}")
                self.status_bar.showMessage(f"Modelo carregado: {SELECTED_MODEL}")
                self.update_transcription_button_state()
                if not is_model_downloaded(SELECTED_MODEL):
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("Reinicialização Necessária")
                    msg_box.setText("O novo modelo selecionado não está baixado. O aplicativo será fechado para baixar e aplicar as alterações.")
                    msg_box.setStandardButtons(QMessageBox.Ok)
                    msg_box.accepted.connect(self.close_application)
                    msg_box.exec_()
            app_logger.info("Opened settings dialog")
            debug_logger.debug("SettingsDialog shown")
        except Exception as e:
            app_logger.error(f"Failed to open settings dialog: {e}")
            debug_logger.debug(f"Settings dialog error: {str(e)}")
            QMessageBox.critical(self, "Erro", "Não foi possível abrir as configurações.")

    def start_transcription(self) -> None:
        """Start the transcription process for queued files after verifying model availability."""
        if not is_model_downloaded(SELECTED_MODEL):
            QMessageBox.information(
                self,
                "Reinicialização Necessária",
                "O modelo selecionado não está baixado. Por favor, reinicie o aplicativo para aplicar as alterações."
            )
            app_logger.info(f"Transcription blocked: Model {SELECTED_MODEL} not downloaded. User prompted to restart.")
            debug_logger.debug(f"Transcription attempt blocked due to missing model: {SELECTED_MODEL}")
            return
        self.transcribe_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.elapsed_seconds = 0
        self.elapsed_label.setText("Duração: 00:00:00")
        self.elapsed_timer.start(1000)
        self.status_bar.showMessage("Transcrição em andamento...")
        self.progress.setValue(0)
        self.current_file_label.setText("Arquivo atual: Iniciando...")
        app_logger.info("Starting transcription process")
        debug_logger.debug(f"Transcription started with {len(self.queued_files)} files")
        self.thread = TranscriptionThread(self.queued_files)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.current_file.connect(self.update_current_file)
        self.thread.finished.connect(self.transcription_done)
        self.thread.failed.connect(self.transcription_failed)
        self.thread.start()

    def update_current_file(self, file_name: str) -> None:
        """Update the UI and queue state to reflect the currently transcribing file."""
        self.current_file = next((f for f in self.queued_files if os.path.basename(f) == file_name), None)
        self.current_file_label.setText(f"Arquivo atual: {file_name}")
        if self.current_file in self.queued_files:
            self.queued_files.remove(self.current_file)
            self.processed_files.append(self.current_file)
        app_logger.debug(f"Updated current file: {file_name}")
        debug_logger.debug(f"Current file set to: {file_name}, remaining queue: {self.queued_files}")

    def stop_transcription(self) -> None:
        """Cancel the ongoing transcription process and reset the UI."""
        if self.thread:
            self.thread.cancelled = True
        self.elapsed_timer.stop()
        self.stop_button.setEnabled(False)
        self.update_transcription_button_state()
        self.progress.setValue(0)
        self.elapsed_label.setText("Transcrição cancelada")
        self.status_bar.showMessage("Transcrição cancelada")
        self.current_file_label.setText("Arquivo atual: Nenhum")
        self.current_file = None
        app_logger.info("Transcription stopped by user")
        debug_logger.debug("Transcription process cancelled")

    def update_elapsed_time(self) -> None:
        """Update the elapsed time display during transcription."""
        self.elapsed_seconds += 1
        hours, remainder = divmod(self.elapsed_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.elapsed_label.setText(f"Duração: {hours:02d}:{minutes:02d}:{seconds:02d}")
        debug_logger.debug(f"Updated transcription elapsed time: {self.elapsed_seconds} seconds")

    def transcription_done(self, message: str, file_paths: list[str]) -> None:
        """Handle successful transcription completion and display a summary."""
        self.elapsed_timer.stop()
        self.stop_button.setEnabled(False)
        self.update_transcription_button_state()
        self.status_bar.showMessage("Transcrição concluída com sucesso")
        self.current_file_label.setText("Arquivo atual: Nenhum")
        self.current_file = None
        self.show_summary_panel(file_paths)
        app_logger.info("Transcription completed successfully")
        debug_logger.debug(f"Transcription finished, processed {len(file_paths)} files")
        QMessageBox.information(self, "Sucesso", message)

    def transcription_failed(self, file_path: str) -> None:
        """Handle transcription failure and display an error message."""
        self.elapsed_timer.stop()
        self.stop_button.setEnabled(False)
        self.update_transcription_button_state()
        self.status_bar.showMessage("Erro na transcrição")
        self.current_file_label.setText("Arquivo atual: Nenhum")
        self.current_file = None
        app_logger.error(f"Transcription failed for file: {file_path}")
        debug_logger.debug(f"Transcription failure for: {file_path}")
        QMessageBox.critical(self, "Erro", f"Erro ao transcrever o arquivo: {file_path}")

    def open_help_link(self) -> None:
        """Open the application's online help page in the default web browser."""
        url = "https://github.com/andreipa/police-transcriber/wiki"
        try:
            QDesktopServices.openUrl(QUrl(url))
            app_logger.info("Opened help link")
            debug_logger.debug(f"Opened help URL: {url}")
        except Exception as e:
            app_logger.error(f"Failed to open help link: {e}")
            debug_logger.debug(f"Help link error: {str(e)}")

    def show_about(self) -> None:
        """Display an About dialog with the application logo, name, version, and developer info."""
        class AboutDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Sobre")
                self.setMinimumSize(300, 250)
                self.setObjectName("AboutDialog")
                layout = QVBoxLayout()
                layout.setAlignment(Qt.AlignCenter)
                layout.setSpacing(8)
                logo = QLabel()
                pixmap = QPixmap("assets/images/splash.png")
                logo.setPixmap(pixmap.scaledToWidth(120, Qt.SmoothTransformation))
                logo.setAlignment(Qt.AlignCenter)
                logo.setObjectName("AboutLogo")
                name_label = QLabel(APP_NAME)
                name_label.setObjectName("AboutNameLabel")
                name_label.setAlignment(Qt.AlignCenter)
                version_label = QLabel(f"Versão: {VERSION}")
                version_label.setObjectName("AboutVersionLabel")
                version_label.setAlignment(Qt.AlignCenter)
                developer_label = QLabel("Developed by TechDev Andrade Ltda.")
                developer_label.setObjectName("AboutVersionLabel")
                developer_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(logo)
                layout.addSpacing(8)
                layout.addWidget(name_label)
                layout.addWidget(version_label)
                layout.addWidget(developer_label)
                self.setLayout(layout)

            def mousePressEvent(self, event):
                if event.button() == Qt.LeftButton:
                    self.accept()
                super().mousePressEvent(event)

        dialog = AboutDialog(self)
        dialog.exec_()
        app_logger.info("Showed About dialog")
        debug_logger.debug("About dialog displayed")

    def show_summary_panel(self, file_paths: list[str]) -> None:
        """Display a dialog summarizing the transcription results for processed files."""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Resumo da Transcrição")
            dialog.setMinimumWidth(500)
            dialog.setObjectName("SummaryDialog")
            layout = QVBoxLayout(dialog)
            layout.setSpacing(8)
            layout.addWidget(QLabel(f"<b>Resumo de {len(file_paths)} arquivo(s) transcrito(s):</b>"))
            for file_path in file_paths:
                txt_path = Path(OUTPUT_FOLDER) / (Path(file_path).stem + "-" + datetime.now().strftime("%d-%m-%Y") + ".txt")
                if not txt_path.exists():
                    app_logger.warning(f"Transcription file not found: {txt_path}")
                    debug_logger.debug(f"Missing transcription file: {txt_path}")
                    continue
                with open(txt_path, "r", encoding="utf-8") as file:
                    content = file.read()
                lines = content.splitlines()
                word_count = sum(1 for line in lines if line.strip() and not line.startswith("Nenhuma"))
                file_layout = QHBoxLayout()
                file_layout.setSpacing(8)
                file_label = QLabel(f"{os.path.basename(file_path)}: {word_count} palavras sensíveis")
                file_label.setObjectName("SummaryLabel")
                file_layout.addWidget(file_label)
                open_button = QPushButton("Abrir")
                open_button.setObjectName("PrimaryButton")
                open_button.clicked.connect(
                    lambda _, path=str(txt_path.resolve()): QDesktopServices.openUrl(QUrl.fromLocalFile(path))
                )
                file_layout.addWidget(open_button)
                layout.addLayout(file_layout)
            button_box = QDialogButtonBox(QDialogButtonBox.Ok)
            button_box.setObjectName("SummaryButtonBox")
            button_box.accepted.connect(dialog.accept)
            layout.addWidget(button_box)
            dialog.exec_()
            app_logger.info(f"Showed transcription summary for {len(file_paths)} files")
            debug_logger.debug(f"Displayed summary dialog for files: {file_paths}")
        except Exception as e:
            app_logger.error(f"Failed to display transcription summary: {e}")
            debug_logger.debug(f"Summary dialog error: {str(e)}")

    def close_application(self) -> None:
        """Close the application."""
        if self.thread and self.thread.isRunning():
            self.stop_transcription()
        app_logger.info("Closing application after settings save")
        debug_logger.debug("Application closing triggered from settings dialog")
        QApplication.quit()
