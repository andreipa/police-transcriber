import os
import time
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QListWidget, QListWidgetItem, QHBoxLayout,
    QProgressBar, QMessageBox, QSpacerItem, QSizePolicy, QStatusBar,
    QMenuBar, QAction
)
from PyQt5.QtWidgets import QMenuBar, QMenu, QAction, QDialog, QDialogButtonBox, QTextEdit
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from gui.word_editor import WordEditorDialog
from core.model_updater import check_for_model_update
from core.transcriber import transcribe_audio

class TranscriptionThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
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

            logging.info("All files transcribed successfully.")
            self.finished.emit("Todas as transcrições foram concluídas.")
        except Exception as e:
            logging.exception("Unhandled error during transcription.")
            self.failed.emit("Erro interno na transcrição.")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Police Transcriber")
        self.setFixedSize(600, 520)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        # Create the menu bar
        menu_bar = QMenuBar(self)

        # ===== FILE MENU =====
        file_menu = menu_bar.addMenu("Arquivo")
        open_file_action = QAction("Selecionar Arquivo", self)
        open_file_action.triggered.connect(self.select_file)
        file_menu.addAction(open_file_action)

        open_folder_action = QAction("Selecionar Pasta", self)
        open_folder_action.triggered.connect(self.select_folder)
        file_menu.addAction(open_folder_action)
        file_menu.addSeparator()

        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # ===== TOOLS MENU =====
        tools_menu = menu_bar.addMenu("Ferramentas")

        word_editor_action = QAction("Editar Palavras Sensíveis", self)
        word_editor_action.triggered.connect(self.open_word_editor)
        tools_menu.addAction(word_editor_action)

        update_model_action = QAction("Verificar Atualização do Modelo", self)
        update_model_action.triggered.connect(self.check_model_update)
        tools_menu.addAction(update_model_action)

        # ===== HELP MENU =====
        help_menu = menu_bar.addMenu("Ajuda")
        help_action = QAction("Ajuda Online...", self)
        help_action.triggered.connect(self.open_help_link)
        help_menu.addSeparator()
        about_action = QAction("Sobre", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # Add the menu bar to the layout
        layout.setMenuBar(menu_bar)

        instructions = QLabel("Selecione um arquivo .mp3 ou uma pasta para transcrição:")
        layout.addWidget(instructions)

        button_layout = QHBoxLayout()

        self.select_file_btn = QPushButton("Selecionar Arquivo")
        self.select_file_btn.setToolTip("Selecionar um arquivo de áudio (.mp3)")
        self.select_file_btn.setIcon(QIcon("assets/icons/file.png"))
        self.select_file_btn.clicked.connect(self.select_file)
        button_layout.addWidget(self.select_file_btn)

        self.select_folder_btn = QPushButton("Selecionar Pasta")
        self.select_folder_btn.setToolTip("Selecionar uma pasta com arquivos .mp3")
        self.select_folder_btn.setIcon(QIcon("assets/icons/folder.png"))
        self.select_folder_btn.clicked.connect(self.select_folder)
        button_layout.addWidget(self.select_folder_btn)

        layout.addLayout(button_layout)

        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        transcribe_layout = QHBoxLayout()

        self.transcribe_button = QPushButton("Iniciar Transcrição")
        self.transcribe_button.setObjectName("PrimaryButton")
        self.transcribe_button.setToolTip("Iniciar a transcrição dos arquivos selecionados")
        self.transcribe_button.setIcon(QIcon("assets/icons/start.png"))
        self.transcribe_button.setEnabled(False)
        self.transcribe_button.clicked.connect(self.start_transcription)
        transcribe_layout.addWidget(self.transcribe_button)

        self.stop_button = QPushButton("Parar")
        self.stop_button.setObjectName("DangerButton")
        self.stop_button.setToolTip("Parar o processo de transcrição")
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

        self.setLayout(layout)

        self.elapsed_timer = QTimer()
        self.elapsed_timer.timeout.connect(self.update_elapsed_time)
        self.elapsed_seconds = 0

        self.thread = None

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

    def transcription_done(self, message):
        self.elapsed_timer.stop()
        self.stop_button.setEnabled(False)
        self.transcribe_button.setEnabled(True)
        self.status_bar.showMessage("Transcrição concluída com sucesso.")
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

    def show_about(self):
        from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout
        from PyQt5.QtGui import QPixmap
        from config import APP_NAME, VERSION

        dialog = QDialog(self)
        dialog.setWindowTitle("Sobre")
        dialog.setFixedSize(300, 250)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        logo = QLabel()
        pixmap = QPixmap("assets/images/splash.png")  # Make sure this path is correct
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