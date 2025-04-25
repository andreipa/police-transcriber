#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

"""Main application window for the Police Transcriber, providing a GUI for audio transcription."""

import logging
import os
from datetime import datetime
from pathlib import Path

import requests
from PyQt5.QtCore import QPoint, Qt, QThread, QTimer, QUrl, pyqtSignal
from PyQt5.QtGui import QDesktopServices, QIcon, QPixmap
from PyQt5.QtWidgets import (
    QAction, QDialog, QDialogButtonBox, QFileDialog, QHBoxLayout, QLabel,
    QListWidget, QMenu, QMenuBar, QMessageBox, QProgressBar, QPushButton,
    QStatusBar, QVBoxLayout, QWidget
)
from packaging import version

from config import APP_NAME, GITHUB_RELEASES_URL, OUTPUT_FOLDER, VERSION
from core.transcriber import transcribe_audio
from gui.word_editor import WordEditorDialog


class TranscriptionThread(QThread):
    """A thread for transcribing multiple audio files sequentially."""

    progress = pyqtSignal(int)
    """Signal emitted to report transcription progress as a percentage."""

    current_file = pyqtSignal(str)
    """Signal emitted to indicate the current file being transcribed."""

    finished = pyqtSignal(str, list)
    """Signal emitted when transcription completes, with a message and list of processed files."""

    failed = pyqtSignal(str)
    """Signal emitted when transcription fails, with an error message."""

    cancelled = False
    """Flag to indicate if transcription has been cancelled."""

    def __init__(self, files: list[str]) -> None:
        """Initialize the transcription thread with a list of files to process.

        Args:
            files: List of file paths to transcribe.
        """
        super().__init__()
        self.files = files

    def run(self) -> None:
        """Execute the transcription process for all files in the queue."""
        try:
            total_files = len(self.files)
            logging.info(f"Starting transcription for {total_files} files")
            processed_files = []

            for index, file_path in enumerate(self.files):
                if self.cancelled:
                    logging.warning("Transcription cancelled by user")
                    return

                logging.info(f"Transcribing: {file_path}")
                self.current_file.emit(os.path.basename(file_path))
                success = transcribe_audio(
                    file_path,
                    on_progress=lambda value: self.progress.emit(value),
                    stop_flag=lambda: self.cancelled
                )

                if success == "cancelled":
                    logging.info(f"Transcription cancelled for: {file_path}")
                    return
                if not success:
                    logging.error(f"Transcription failed for: {file_path}")
                    self.failed.emit(file_path)
                    return

                processed_files.append(file_path)
                self.progress.emit(int(((index + 1) / total_files) * 100))

            logging.info("All files transcribed successfully")
            self.finished.emit("Todas as transcrições foram concluídas.", processed_files)
        except Exception as e:
            logging.error(f"Unhandled error during transcription: {e}")
            self.failed.emit("Erro interno na transcrição")

class BackgroundAppUpdateChecker(QThread):
    """A thread for checking application updates in the background."""

    update_available = pyqtSignal(str)
    """Signal emitted when a new application version is available, with the version string."""

    def run(self) -> None:
        """Check for the latest application release on GitHub and emit update signal if available."""
        try:
            # Temporarily disabled due to repository inaccessibility
            logging.info("Application update check disabled")
            return
        except requests.RequestException as e:
            logging.warning(f"Failed to check for application updates: {e}")

class MainWindow(QWidget):
    """Main application window for managing audio file transcription and sensitive word detection."""

    def __init__(self) -> None:
        """Initialize the main window with UI components and transcription controls."""
        super().__init__()
        logging.debug("Initializing MainWindow")
        try:
            self.setWindowTitle("Police Transcriber")
            self.setFixedSize(600, 520)

            layout = QVBoxLayout()
            layout.setAlignment(Qt.AlignTop)

            # Initialize menu bar
            menu_bar = QMenuBar(self)
            file_menu = menu_bar.addMenu("Arquivo")
            open_file_action = QAction(QIcon("assets/icons/file.png"), "Selecionar Arquivo", self)
            open_file_action.triggered.connect(self.select_file)
            file_menu.addAction(open_file_action)
            open_folder_action = QAction(QIcon("assets/icons/folder.png"), "Selecionar Pasta", self)
            open_folder_action.triggered.connect(self.select_folder)
            file_menu.addAction(open_folder_action)
            file_menu.addSeparator()
            exit_action = QAction(QIcon("assets/icons/exit.png"), "Sair", self)
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)

            tools_menu = menu_bar.addMenu("Ferramentas")
            edit_words_action = QAction(QIcon("assets/icons/edit.png"), "Editar Palavras Sensíveis", self)
            edit_words_action.triggered.connect(self.open_word_editor)
            tools_menu.addAction(edit_words_action)
            check_app_action = QAction(QIcon("assets/icons/refresh.png"), "Verificar Atualização do Programa", self)
            check_app_action.triggered.connect(self.check_app_update)
            tools_menu.addAction(check_app_action)

            help_menu = menu_bar.addMenu("Ajuda")
            help_action = QAction(QIcon("assets/icons/help.png"), "Ajuda Online...", self)
            help_action.triggered.connect(self.open_help_link)
            help_menu.addAction(help_action)
            help_menu.addSeparator()
            about_action = QAction(QIcon("assets/icons/about.png"), "Sobre", self)
            about_action.triggered.connect(self.show_about)
            help_menu.addAction(about_action)

            layout.setMenuBar(menu_bar)

            # Add instruction label
            layout.addWidget(QLabel("Selecione um arquivo .mp3 ou uma pasta para transcrição:"))

            # Initialize file selection buttons
            button_layout = QHBoxLayout()
            self.select_file_button = QPushButton("Selecionar Arquivo")
            self.select_file_button.setIcon(QIcon("assets/icons/file.png"))
            self.select_file_button.clicked.connect(self.select_file)
            button_layout.addWidget(self.select_file_button)

            self.select_folder_button = QPushButton("Selecionar Pasta")
            self.select_folder_button.setIcon(QIcon("assets/icons/folder.png"))
            self.select_folder_button.clicked.connect(self.select_folder)
            button_layout.addWidget(self.select_folder_button)
            layout.addLayout(button_layout)

            # Initialize file list with context menu
            self.file_list = QListWidget()
            self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
            self.file_list.customContextMenuRequested.connect(self.show_context_menu)
            layout.addWidget(self.file_list)

            # Initialize current file label
            self.current_file_label = QLabel("Arquivo atual: Nenhum")
            self.current_file_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.current_file_label)

            # Initialize transcription control buttons
            transcribe_layout = QHBoxLayout()
            self.transcribe_button = QPushButton("Iniciar Transcrição")
            self.transcribe_button.setObjectName("PrimaryButton")
            self.transcribe_button.setIcon(QIcon("assets/icons/start.png"))
            self.transcribe_button.setEnabled(False)
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
            layout.addWidget(self.progress)

            # Initialize elapsed time label
            self.elapsed_label = QLabel("Duração: 00:00:00")
            self.elapsed_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.elapsed_label)

            # Initialize status bar
            self.status_bar = QStatusBar()
            self.status_bar.showMessage("Modelo carregado: large-v3 | Última atualização: --")
            layout.addWidget(self.status_bar)

            # Initialize background update checker
            self.update_checker = BackgroundAppUpdateChecker()
            self.update_checker.update_available.connect(self.notify_update_available)
            self.update_checker.start()

            # Initialize timer and state variables
            self.elapsed_timer = QTimer()
            self.elapsed_timer.timeout.connect(self.update_elapsed_time)
            self.elapsed_seconds = 0
            self.thread = None
            self.queued_files = []
            self.current_file = None
            self.processed_files = []

            self.setLayout(layout)
            logging.debug("MainWindow initialization completed")
        except Exception as e:
            logging.error(f"Failed to initialize MainWindow: {e}", exc_info=True)
            raise

    def closeEvent(self, event) -> None:
        """Handle the window close event and log it."""
        logging.debug("MainWindow closeEvent triggered")
        event.accept()

    def notify_update_available(self, version: str) -> None:
        """Display a notification in the status bar when a new application version is available.

        Args:
            version: The version string of the available update.
        """
        self.status_bar.showMessage(f"🔔 Atualização disponível: v{version}")

    def select_file(self) -> None:
        """Open a file dialog to select an MP3 file and update the transcription queue."""
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo MP3", "", "Audio Files (*.mp3)")
        if path:
            self.file_list.clear()
            self.queued_files = [path]
            self.current_file = None
            self.processed_files = []
            self.file_list.addItem(path)
            self.transcribe_button.setEnabled(True)
            self.progress.setValue(0)
            self.current_file_label.setText("Arquivo atual: Nenhum")

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
            self.transcribe_button.setEnabled(self.file_list.count() > 0)
            self.progress.setValue(0)
            self.current_file_label.setText("Arquivo atual: Nenhum")

    def show_context_menu(self, position: QPoint) -> None:
        """Display a context menu for the file list to allow removing queued files.

        Args:
            position: The position of the right-click event in the file list.
        """
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

    def remove_from_queue(self, file_path: str) -> None:
        """Remove a file from the transcription queue if it is not currently being processed.

        Args:
            file_path: The path of the file to remove from the queue.
        """
        if file_path in self.queued_files and file_path != self.current_file:
            self.queued_files.remove(file_path)
            for index in range(self.file_list.count()):
                if self.file_list.item(index).text() == file_path:
                    self.file_list.takeItem(index)
                    break
            logging.info(f"Removed {file_path} from queue")
            if not self.queued_files:
                self.transcribe_button.setEnabled(False)

    def open_word_editor(self) -> None:
        """Open a dialog for editing the list of sensitive words."""
        dialog = WordEditorDialog(self)
        dialog.exec_()

    def start_transcription(self) -> None:
        """Start the transcription process for queued files."""
        self.transcribe_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.elapsed_seconds = 0
        self.elapsed_label.setText("Duração: 00:00:00")
        self.elapsed_timer.start(1000)
        self.status_bar.showMessage("Transcrição em andamento...")
        self.progress.setValue(0)
        self.current_file_label.setText("Arquivo atual: Iniciando...")

        self.thread = TranscriptionThread(self.queued_files)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.current_file.connect(self.update_current_file)
        self.thread.finished.connect(self.transcription_done)
        self.thread.failed.connect(self.transcription_failed)
        self.thread.start()

    def update_current_file(self, file_name: str) -> None:
        """Update the UI and queue state to reflect the currently transcribing file.

        Args:
            file_name: The name of the file currently being transcribed.
        """
        self.current_file = next((f for f in self.queued_files if os.path.basename(f) == file_name), None)
        self.current_file_label.setText(f"Arquivo atual: {file_name}")
        if self.current_file in self.queued_files:
            self.queued_files.remove(self.current_file)
            self.processed_files.append(self.current_file)

    def stop_transcription(self) -> None:
        """Cancel the ongoing transcription process and reset the UI."""
        if self.thread:
            self.thread.cancelled = True
        self.elapsed_timer.stop()
        self.stop_button.setEnabled(False)
        self.transcribe_button.setEnabled(bool(self.queued_files))
        self.progress.setValue(0)
        self.elapsed_label.setText("Transcrição cancelada")
        self.status_bar.showMessage("Transcrição cancelada")
        self.current_file_label.setText("Arquivo atual: Nenhum")
        self.current_file = None

    def update_elapsed_time(self) -> None:
        """Update the elapsed time display during transcription."""
        self.elapsed_seconds += 1
        hours, remainder = divmod(self.elapsed_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.elapsed_label.setText(f"Duração: {hours:02d}:{minutes:02d}:{seconds:02d}")

    def transcription_done(self, message: str, file_paths: list[str]) -> None:
        """Handle successful transcription completion and display a summary.

        Args:
            message: The success message to display.
            file_paths: List of paths to the transcribed files.
        """
        self.elapsed_timer.stop()
        self.stop_button.setEnabled(False)
        self.transcribe_button.setEnabled(bool(self.queued_files))
        self.status_bar.showMessage("Transcrição concluída com sucesso")
        self.current_file_label.setText("Arquivo atual: Nenhum")
        self.current_file = None
        self.show_summary_panel(file_paths)
        QMessageBox.information(self, "Sucesso", message)

    def transcription_failed(self, file_path: str) -> None:
        """Handle transcription failure and display an error message.

        Args:
            file_path: The path of the file that failed to transcribe.
        """
        self.elapsed_timer.stop()
        self.stop_button.setEnabled(False)
        self.transcribe_button.setEnabled(bool(self.queued_files))
        self.status_bar.showMessage("Erro na transcrição")
        self.current_file_label.setText("Arquivo atual: Nenhum")
        self.current_file = None
        QMessageBox.critical(self, "Erro", f"Erro ao transcrever o arquivo: {file_path}")

    def check_app_update(self) -> None:
        """Check for application updates on GitHub and prompt the user if available."""
        try:
            response = requests.get(
                GITHUB_RELEASES_URL,
                headers={"Accept": "application/vnd.github.v3+json"},
                timeout=5
            )
            response.raise_for_status()
            latest_release = response.json()
            latest_version = latest_release.get("tag_name", "").lstrip("v")

            if not latest_version:
                QMessageBox.information(
                    self,
                    "Atualização",
                    "Ainda não há versões publicadas"
                )
                return

            if version.parse(latest_version) > version.parse(VERSION):
                reply = QMessageBox.question(
                    self,
                    "Atualização Disponível",
                    f"Uma nova versão ({latest_version}) está disponível.\nDeseja abrir a página de download?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    QDesktopServices.openUrl(QUrl(latest_release["html_url"]))
            else:
                QMessageBox.information(
                    self,
                    "Atualização",
                    "Você já está usando a versão mais recente"
                )
        except (requests.RequestException, ValueError) as e:
            logging.warning(f"Failed to check for application update: {e}")
            QMessageBox.information(
                self,
                "Atualização",
                "Não foi possível verificar atualizações no momento. Tente novamente mais tarde"
            )

    def open_help_link(self) -> None:
        """Open the application's online help page in the default web browser."""
        QDesktopServices.openUrl(QUrl("https://github.com/{GITHUB_REPO}"))

    def show_about(self) -> None:
        """Display an About dialog with the application logo, name, and version."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Sobre")
        dialog.setFixedSize(300, 250)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        logo = QLabel()
        pixmap = QPixmap("assets/images/splash.png")
        logo.setPixmap(pixmap.scaledToWidth(120, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)

        name_label = QLabel(APP_NAME)
        name_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        name_label.setAlignment(Qt.AlignCenter)

        version_label = QLabel(f"Versão: {VERSION}")
        version_label.setStyleSheet("color: gray; font-size: 13px;")
        version_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(logo)
        layout.addSpacing(10)
        layout.addWidget(name_label)
        layout.addWidget(version_label)

        dialog.setLayout(layout)
        dialog.exec_()

    def show_summary_panel(self, file_paths: list[str]) -> None:
        """Display a dialog summarizing the transcription results for processed files.

        Args:
            file_paths: List of paths to the transcribed files.
        """
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Resumo da Transcrição")
            dialog.setMinimumWidth(500)

            layout = QVBoxLayout(dialog)
            layout.addWidget(QLabel(f"<b>Resumo de {len(file_paths)} arquivo(s) transcrito(s):</b>"))

            for file_path in file_paths:
                txt_path = Path(OUTPUT_FOLDER) / (Path(file_path).stem + "-" + datetime.now().strftime("%d-%m-%Y") + ".txt")
                if not txt_path.exists():
                    continue

                with open(txt_path, "r", encoding="utf-8") as file:
                    content = file.read()

                lines = content.splitlines()
                word_count = sum(1 for line in lines if line.strip() and not line.startswith("Nenhuma"))

                file_layout = QHBoxLayout()
                file_layout.addWidget(QLabel(f"{os.path.basename(file_path)}: {word_count} palavras sensíveis"))
                open_button = QPushButton("Abrir")
                open_button.clicked.connect(lambda _, path=str(txt_path.resolve()): QDesktopServices.openUrl(QUrl.fromLocalFile(path)))
                file_layout.addWidget(open_button)
                layout.addLayout(file_layout)

            button_box = QDialogButtonBox(QDialogButtonBox.Ok)
            button_box.accepted.connect(dialog.accept)
            layout.addWidget(button_box)

            dialog.exec_()
        except Exception as e:
            logging.error(f"Failed to display transcription summary: {e}")