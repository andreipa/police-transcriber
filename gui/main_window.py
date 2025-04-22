#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

import logging
import os

import requests
from PyQt5.QtCore import Qt, QThread, QTimer, QUrl, pyqtSignal
from PyQt5.QtGui import QDesktopServices, QIcon, QPixmap
from PyQt5.QtWidgets import (
    QAction, QDialog, QDialogButtonBox, QFileDialog, QHBoxLayout,
    QLabel, QListWidget, QMenuBar, QMessageBox, QProgressBar,
    QPushButton, QStatusBar, QVBoxLayout, QWidget
)

from config import APP_NAME, VERSION, OUTPUT_FOLDER
from core.model_updater import check_for_model_update
from core.transcriber import transcribe_audio
from gui.word_editor import WordEditorDialog


class TranscriptionThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str, str)
    failed = pyqtSignal(str)
    cancelled = False

    def __init__(self, files):
        super().__init__()
        self.files = files

    def run(self):
        try:
            total = len(self.files)
            logging.info(f"Transcription started for {total} files.")

            for i, file_path in enumerate(self.files):
                if self.cancelled:
                    logging.warning("Transcription was cancelled by the user.")
                    return

                logging.info(f"Transcribing: {file_path}")
                success = transcribe_audio(
                    file_path,
                    on_progress=lambda val: self.progress.emit(val),
                    stop_flag=lambda: self.cancelled
                )

                if success == "cancelled":
                    logging.info(f"Transcription cancelled for: {file_path}")
                    return
                elif not success:
                    logging.error(f"Transcription failed for: {file_path}")
                    self.failed.emit(file_path)
                    return

                self.progress.emit(int(((i + 1) / total) * 100))

            logging.info("All files transcribed successfully.")
            last_file = self.files[-1] if self.files else ""
            self.finished.emit("Todas as transcrições foram concluídas.", last_file)
        except Exception as e:
            logging.exception("Unhandled error during transcription.")
            self.failed.emit("Erro interno na transcrição.")


class BackgroundAppUpdateChecker(QThread):
    update_available = pyqtSignal(str)  # emits the version tag

    def run(self):
        try:
            response = requests.get(
                "https://api.github.com/repos/andreipa/police-transcriber/releases/latest",
                headers={"Accept": "application/vnd.github.v3+json"},
                timeout=5
            )
            if response.status_code != 200:
                return

            data = response.json()
            latest_version = data.get("tag_name", "").lstrip("v")
            if latest_version and latest_version != VERSION:
                self.update_available.emit(latest_version)
        except Exception as e:
            logging.warning(f"Falha ao verificar atualização silenciosamente: {e}")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Police Transcriber")
        self.setFixedSize(600, 520)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

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

        check_model_action = QAction(QIcon("assets/icons/update.png"), "Verificar Atualização do Modelo", self)
        check_model_action.triggered.connect(self.check_model_update)
        tools_menu.addAction(check_model_action)

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

        layout.addWidget(QLabel("Selecione um arquivo .mp3 ou uma pasta para transcrição:"))

        button_layout = QHBoxLayout()
        self.select_file_btn = QPushButton("Selecionar Arquivo")
        self.select_file_btn.setIcon(QIcon("assets/icons/file.png"))
        self.select_file_btn.clicked.connect(self.select_file)
        button_layout.addWidget(self.select_file_btn)

        self.select_folder_btn = QPushButton("Selecionar Pasta")
        self.select_folder_btn.setIcon(QIcon("assets/icons/folder.png"))
        self.select_folder_btn.clicked.connect(self.select_folder)
        button_layout.addWidget(self.select_folder_btn)

        layout.addLayout(button_layout)

        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

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

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.elapsed_label = QLabel("Duração: 00:00:00")
        self.elapsed_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.elapsed_label)

        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Modelo carregado: base | Última atualização: --")

        layout.addWidget(self.status_bar)

        # Background silent check for app updates
        self.update_checker = BackgroundAppUpdateChecker()
        self.update_checker.update_available.connect(self.notify_update_available)
        self.update_checker.start()

        self.setLayout(layout)
        self.elapsed_timer = QTimer()
        self.elapsed_timer.timeout.connect(self.update_elapsed_time)
        self.elapsed_seconds = 0
        self.thread = None

    def notify_update_available(self, version):
        self.status_bar.showMessage(f"🔔 Atualização disponível: v{version}")

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo MP3", "", "Audio Files (*.mp3)")
        if path:
            self.file_list.clear()
            self.file_list.addItem(path)
            self.transcribe_button.setEnabled(True)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecionar Pasta")
        if folder:
            self.file_list.clear()
            for filename in os.listdir(folder):
                if filename.endswith(".mp3"):
                    self.file_list.addItem(os.path.join(folder, filename))
            self.transcribe_button.setEnabled(self.file_list.count() > 0)

    def open_word_editor(self):
        dialog = WordEditorDialog(self)
        dialog.exec_()

    def start_transcription(self):
        self.transcribe_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.elapsed_seconds = 0
        self.elapsed_label.setText("Duração: 00:00:00")
        self.elapsed_timer.start(1000)
        self.status_bar.showMessage("Transcrição em andamento...")

        files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        logging.info(f"Arquivos selecionados para transcrição: {files}")

        self.thread = TranscriptionThread(files)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.finished.connect(self.transcription_done)
        self.thread.failed.connect(self.transcription_failed)
        self.thread.start()

    def stop_transcription(self):
        if self.thread:
            self.thread.cancelled = True
        self.elapsed_timer.stop()
        self.stop_button.setEnabled(False)
        self.transcribe_button.setEnabled(True)
        self.progress.setValue(0)
        self.elapsed_label.setText("Transcrição cancelada.")
        self.status_bar.showMessage("Transcrição cancelada.")

    def update_elapsed_time(self):
        self.elapsed_seconds += 1
        hrs, rem = divmod(self.elapsed_seconds, 3600)
        mins, secs = divmod(rem, 60)
        self.elapsed_label.setText(f"Duração: {hrs:02d}:{mins:02d}:{secs:02d}")

    def transcription_done(self, message, file_path):
        self.elapsed_timer.stop()
        self.stop_button.setEnabled(False)
        self.transcribe_button.setEnabled(True)
        self.status_bar.showMessage("Transcrição concluída com sucesso.")
        self.show_summary_panel(file_path)
        QMessageBox.information(self, "Sucesso", message)

    def transcription_failed(self, file_path):
        self.elapsed_timer.stop()
        self.stop_button.setEnabled(False)
        self.transcribe_button.setEnabled(True)
        self.status_bar.showMessage("Erro na transcrição.")
        QMessageBox.critical(self, "Erro", f"Erro ao transcrever o arquivo: {file_path}")

    def check_model_update(self):
        self.check_update_btn.setEnabled(False)
        self.check_update_btn.setText("Verificando...")

        class ModelUpdateThread(QThread):
            update_progress = pyqtSignal(int)
            update_finished = pyqtSignal(bool)

            def run(self):
                try:
                    updated = check_for_model_update(self.update_progress.emit)
                    self.update_finished.emit(updated)
                except Exception as e:
                    logging.error(f"Erro ao verificar atualização do modelo: {e}")
                    self.update_finished.emit(False)

        def on_progress(value):
            self.progress.setValue(value)

        def on_finished(updated):
            self.check_update_btn.setEnabled(True)
            self.check_update_btn.setText("Verificar Atualização do Modelo")
            self.progress.setValue(0)

            if updated:
                self.status_bar.showMessage("Modelo atualizado com sucesso.")
                QMessageBox.information(self, "Modelo Atualizado", "Um novo modelo foi baixado com sucesso.")
            else:
                self.status_bar.showMessage("Nenhuma atualização encontrada.")
                QMessageBox.information(self, "Sem Atualizações", "Nenhuma atualização disponível no momento.")

        self.thread = ModelUpdateThread()
        self.thread.update_progress.connect(on_progress)
        self.thread.update_finished.connect(on_finished)
        self.thread.start()

    def check_app_update(self):
        try:
            response = requests.get(
                "https://api.github.com/repos/andreipa/police-transcriber/releases/latest",
                headers={"Accept": "application/vnd.github.v3+json"},
                timeout=5
            )
            if response.status_code != 200:
                raise ValueError(f"Unexpected status code: {response.status_code}")

            latest_release = response.json()
            latest_version = latest_release.get("tag_name", "").lstrip("v")

            if not latest_version:
                # No release found
                QMessageBox.information(
                    self,
                    "Atualização",
                    "Ainda não há versões publicadas."
                )
                return

            if latest_version != VERSION:
                reply = QMessageBox.question(
                    self,
                    "Atualização Disponível",
                    f"Uma nova versão ({latest_version}) está disponível.\n"
                    "Deseja abrir a página de download?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    QDesktopServices.openUrl(QUrl(latest_release["html_url"]))
            else:
                QMessageBox.information(
                    self,
                    "Atualização",
                    "Você já está usando a versão mais recente."
                )

        except Exception as e:
            # Gracefully fallback instead of crashing or raising warnings
            logging.warning(f"Não foi possível verificar atualização: {e}")
            QMessageBox.information(
                self,
                "Atualização",
                "Não foi possível verificar atualizações no momento. Tente novamente mais tarde."
            )

    def show_about(self):
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

    def open_help_link(self):
        QDesktopServices.openUrl(QUrl("https://github.com/andreipa/police-transcriber"))

    def show_summary_panel(self, file_path):
        try:
            from datetime import datetime
            from pathlib import Path

            txt_path = Path(OUTPUT_FOLDER) / (Path(file_path).stem + "-" + datetime.now().strftime("%d-%m-%Y") + ".txt")
            if not txt_path.exists():
                return

            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.splitlines()
            word_count = sum(1 for line in lines if line.strip() and not line.startswith("Nenhuma"))

            dialog = QDialog(self)
            dialog.setWindowTitle("Resumo da Transcrição")
            dialog.setMinimumWidth(450)

            layout = QVBoxLayout(dialog)

            layout.addWidget(QLabel(f"Arquivo: {os.path.basename(file_path)}"))
            layout.addWidget(QLabel(f"Palavras sensíveis detectadas: {word_count}"))
            layout.addWidget(QLabel(f"Abrir resultado:"))

            open_button = QPushButton("Abrir Arquivo")
            open_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(txt_path.resolve()))))
            layout.addWidget(open_button)

            button_box = QDialogButtonBox(QDialogButtonBox.Ok)
            button_box.accepted.connect(dialog.accept)
            layout.addWidget(button_box)

            dialog.exec_()

        except Exception as e:
            logging.error(f"Erro ao exibir resumo da transcrição: {e}")
