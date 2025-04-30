#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

import os
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock, mock_open

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from config import (
    GITHUB_RELEASES_URL, LOG_FOLDER, OUTPUT_FOLDER, VERSION
)
from gui.main_window import (
    TranscriptionThread,
    BackgroundAppUpdateChecker,
    ClickableStatusBar,
    MainWindow
)


class TestMainWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the QApplication instance required for PyQt tests."""
        cls.app = QApplication([])

    def setUp(self):
        """Set up the test environment."""
        self.files = ["file1.mp3", "file2.mp3"]
        self.log_file = os.path.join(LOG_FOLDER, "app.log")
        self.debug_log_file = os.path.join(LOG_FOLDER, "debug.log")
        self.output_folder = OUTPUT_FOLDER
        self.github_url = GITHUB_RELEASES_URL
        self.test_zip = f"transcriptions_backup_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.zip"

    @patch("gui.main_window.transcribe_audio")
    def test_transcription_thread_success(self, mock_transcribe):
        """Test TranscriptionThread successfully transcribes files."""
        mock_transcribe.return_value = True
        thread = TranscriptionThread(self.files)
        thread.progress = MagicMock()
        thread.current_file = MagicMock()
        thread.finished = MagicMock()

        thread.run()

        self.assertEqual(thread.current_file.emit.call_count, 2)
        thread.current_file.emit.assert_any_call("file1.mp3")
        thread.current_file.emit.assert_any_call("file2.mp3")
        thread.progress.emit.assert_any_call(50)  # First file: 1/2 * 100
        thread.progress.emit.assert_any_call(100)  # Second file: 2/2 * 100
        thread.finished.emit.assert_called_once_with(
            "Todas as transcrições foram concluídas.", self.files
        )

    @patch("gui.main_window.transcribe_audio")
    def test_transcription_thread_cancelled(self, mock_transcribe):
        """Test TranscriptionThread handles cancellation."""
        mock_transcribe.return_value = "cancelled"
        thread = TranscriptionThread(self.files)
        thread.current_file = MagicMock()
        thread.finished = MagicMock()

        thread.run()

        thread.current_file.emit.assert_called_once_with("file1.mp3")
        thread.finished.emit.assert_not_called()

    @patch("gui.main_window.transcribe_audio")
    def test_transcription_thread_failure(self, mock_transcribe):
        """Test TranscriptionThread handles transcription failure."""
        mock_transcribe.return_value = False
        thread = TranscriptionThread(self.files)
        thread.current_file = MagicMock()
        thread.failed = MagicMock()

        thread.run()

        thread.current_file.emit.assert_called_once_with("file1.mp3")
        thread.failed.emit.assert_called_once_with("file1.mp3")

    @patch("gui.main_window.transcribe_audio")
    def test_transcription_thread_exception(self, mock_transcribe):
        """Test TranscriptionThread handles exceptions."""
        mock_transcribe.side_effect = Exception("Transcription error")
        thread = TranscriptionThread(self.files)
        thread.current_file = MagicMock()
        thread.failed = MagicMock()

        thread.run()

        thread.current_file.emit.assert_called_once_with("file1.mp3")
        thread.failed.emit.assert_called_once_with("Erro interno na transcrição")

    @patch("requests.get")
    def test_background_app_update_checker_new_version(self, mock_get):
        """Test BackgroundAppUpdateChecker detects a new version."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tag_name": "v1.0.0",
            "html_url": "https://github.com/release"
        }
        mock_get.return_value = mock_response

        checker = BackgroundAppUpdateChecker()
        checker.update_available = MagicMock()

        checker.run()

        mock_get.assert_called_once_with(
            self.github_url,
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=5
        )
        checker.update_available.emit.assert_called_once_with("1.0.0", "https://github.com/release")

    @patch("requests.get")
    def test_background_app_update_checker_no_new_version(self, mock_get):
        """Test BackgroundAppUpdateChecker when no new version is available."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tag_name": f"v{VERSION}",
            "html_url": "https://github.com/release"
        }
        mock_get.return_value = mock_response

        checker = BackgroundAppUpdateChecker()
        checker.update_available = MagicMock()

        checker.run()

        checker.update_available.emit.assert_not_called()

    @patch("requests.get")
    def test_background_app_update_checker_request_exception(self, mock_get):
        """Test BackgroundAppUpdateChecker handles request exceptions."""
        mock_get.side_effect = requests.RequestException("Network error")
        checker = BackgroundAppUpdateChecker()
        checker.update_available = MagicMock()

        checker.run()

        checker.update_available.emit.assert_not_called()

    def test_clickable_status_bar_mouse_press(self):
        """Test ClickableStatusBar emits clicked signal on left mouse press."""
        status_bar = ClickableStatusBar()
        status_bar.clicked = MagicMock()

        event = MagicMock()
        event.button.return_value = Qt.LeftButton
        status_bar.mousePressEvent(event)

        status_bar.clicked.emit.assert_called_once()
        event.button.assert_called_once()

    @patch("gui.main_window.is_model_downloaded")
    def test_main_window_update_transcription_button_state(self, mock_is_downloaded):
        """Test MainWindow.update_transcription_button_state updates button state."""
        window = MainWindow()
        window.queued_files = ["file1.mp3"]
        mock_is_downloaded.return_value = True

        window.update_transcription_button_state()

        self.assertTrue(window.transcribe_button.isEnabled())
        self.assertEqual(
            window.transcribe_button.toolTip(),
            "Iniciar a transcrição dos arquivos selecionados."
        )

        window.queued_files = []
        window.update_transcription_button_state()
        self.assertFalse(window.transcribe_button.isEnabled())
        self.assertEqual(
            window.transcribe_button.toolTip(),
            "Nenhum arquivo selecionado para transcrição."
        )

        mock_is_downloaded.return_value = False
        window.queued_files = ["file1.mp3"]
        window.update_transcription_button_state()
        self.assertFalse(window.transcribe_button.isEnabled())
        self.assertEqual(
            window.transcribe_button.toolTip(),
            "Modelo selecionado não está baixado. Reinicie o aplicativo após alterar as configurações."
        )

    @patch("PyQt5.QtWidgets.QFileDialog.getOpenFileName")
    def test_main_window_select_file(self, mock_get_open_file_name):
        """Test MainWindow.select_file updates the file queue."""
        mock_get_open_file_name.return_value = ("/path/to/file.mp3", "")
        window = MainWindow()
        window.file_list = MagicMock()
        window.update_transcription_button_state = MagicMock()

        window.select_file()

        self.assertEqual(window.queued_files, ["/path/to/file.mp3"])
        self.assertEqual(window.current_file, None)
        self.assertEqual(window.processed_files, [])
        window.file_list.clear.assert_called_once()
        window.file_list.addItem.assert_called_once_with("/path/to/file.mp3")
        self.assertEqual(window.progress.value(), 0)
        self.assertEqual(window.current_file_label.text(), "Arquivo atual: Nenhum")
        window.update_transcription_button_state.assert_called_once()

    @patch("PyQt5.QtWidgets.QFileDialog.getExistingDirectory")
    @patch("os.listdir")
    def test_main_window_select_folder(self, mock_listdir, mock_get_directory):
        """Test MainWindow.select_folder updates the file queue with MP3 files."""
        mock_get_directory.return_value = "/path/to/folder"
        mock_listdir.return_value = ["file1.mp3", "file2.txt", "file3.mp3"]
        window = MainWindow()
        window.file_list = MagicMock()
        window.update_transcription_button_state = MagicMock()

        window.select_folder()

        self.assertEqual(window.queued_files, ["/path/to/folder/file1.mp3", "/path/to/folder/file3.mp3"])
        self.assertEqual(window.current_file, None)
        self.assertEqual(window.processed_files, [])
        window.file_list.clear.assert_called_once()
        window.file_list.addItem.assert_any_call("/path/to/folder/file1.mp3")
        window.file_list.addItem.assert_any_call("/path/to/folder/file3.mp3")
        self.assertEqual(window.progress.value(), 0)
        self.assertEqual(window.current_file_label.text(), "Arquivo atual: Nenhum")
        window.update_transcription_button_state.assert_called_once()

    def test_main_window_remove_from_queue(self):
        """Test MainWindow.remove_from_queue removes a file from the queue."""
        window = MainWindow()
        window.queued_files = ["file1.mp3", "file2.mp3"]
        window.current_file = "file3.mp3"
        window.processed_files = []
        window.file_list = MagicMock()
        window.file_list.count.return_value = 2
        window.file_list.item.side_effect = [MagicMock(text=lambda: "file1.mp3"), MagicMock(text=lambda: "file2.mp3")]
        window.update_transcription_button_state = MagicMock()

        window.remove_from_queue("file1.mp3")

        self.assertEqual(window.queued_files, ["file2.mp3"])
        window.file_list.takeItem.assert_called_once_with(0)
        window.update_transcription_button_state.assert_called_once()

    @patch("os.path.exists")
    @patch("PyQt5.QtGui.QDesktopServices.openUrl")
    def test_main_window_open_log_file_success(self, mock_open_url, mock_exists):
        """Test MainWindow.open_log_file opens the log file."""
        mock_exists.return_value = True
        window = MainWindow()

        window.open_log_file()

        mock_exists.assert_called_once_with(self.log_file)
        mock_open_url.assert_called_once_with(window.QUrl.fromLocalFile(self.log_file))

    @patch("os.path.exists")
    @patch("PyQt5.QtWidgets.QMessageBox.warning")
    def test_main_window_open_log_file_not_found(self, mock_warning, mock_exists):
        """Test MainWindow.open_log_file handles missing log file."""
        mock_exists.return_value = False
        window = MainWindow()

        window.open_log_file()

        mock_exists.assert_called_once_with(self.log_file)
        mock_warning.assert_called_once_with(
            window, "Aviso", "O arquivo de log não existe."
        )

    @patch("os.path.exists")
    @patch("PyQt5.QtGui.QDesktopServices.openUrl")
    def test_main_window_open_debug_log_file_success(self, mock_open_url, mock_exists):
        """Test MainWindow.open_debug_log_file opens the debug log file."""
        mock_exists.return_value = True
        window = MainWindow()

        window.open_debug_log_file()

        mock_exists.assert_called_once_with(self.debug_log_file)
        mock_open_url.assert_called_once_with(window.QUrl.fromLocalFile(self.debug_log_file))

    @patch("os.path.exists")
    @patch("PyQt5.QtWidgets.QMessageBox.warning")
    def test_main_window_open_debug_log_file_not_found(self, mock_warning, mock_exists):
        """Test MainWindow.open_debug_log_file handles missing debug log file."""
        mock_exists.return_value = False
        window = MainWindow()

        window.open_debug_log_file()

        mock_exists.assert_called_once_with(self.debug_log_file)
        mock_warning.assert_called_once_with(
            window, "Aviso", "O arquivo de debug log não existe."
        )

    @patch("os.path.exists")
    @patch("os.listdir")
    @patch("PyQt5.QtWidgets.QFileDialog.getSaveFileName")
    @patch("zipfile.ZipFile")
    @patch("os.remove")
    @patch("PyQt5.QtWidgets.QMessageBox.information")
    def test_main_window_backup_transcriptions_success(
            self, mock_info, mock_remove, mock_zipfile, mock_get_save_file, mock_listdir, mock_exists
    ):
        """Test MainWindow.backup_transcriptions creates a ZIP and deletes originals."""
        mock_exists.return_value = True
        mock_listdir.return_value = ["trans1.txt", "trans2.txt"]
        mock_get_save_file.return_value = (self.test_zip, "")
        window = MainWindow()

        window.backup_transcriptions()

        mock_exists.assert_called_once_with(self.output_folder)
        mock_listdir.assert_called_once_with(self.output_folder)
        mock_get_save_file.assert_called_once()
        mock_zipfile.assert_called_once_with(self.test_zip, "w")
        mock_zipfile().write.assert_any_call(os.path.join(self.output_folder, "trans1.txt"), "trans1.txt")
        mock_zipfile().write.assert_any_call(os.path.join(self.output_folder, "trans2.txt"), "trans2.txt")
        mock_remove.assert_any_call(os.path.join(self.output_folder, "trans1.txt"))
        mock_remove.assert_any_call(os.path.join(self.output_folder, "trans2.txt"))
        mock_info.assert_called_once_with(
            window, "Sucesso", f"Backup criado em {self.test_zip}. Transcrições originais foram removidas."
        )

    @patch("os.path.exists")
    @patch("PyQt5.QtWidgets.QMessageBox.warning")
    def test_main_window_backup_transcriptions_no_files(self, mock_warning, mock_exists):
        """Test MainWindow.backup_transcriptions handles no transcription files."""
        mock_exists.return_value = True
        window = MainWindow()
        with patch("os.listdir", return_value=[]):
            window.backup_transcriptions()
        mock_warning.assert_called_once_with(
            window, "Aviso", "Nenhuma transcrição encontrada para backup."
        )

    @patch("gui.main_window.load_config")
    @patch("gui.main_window.SettingsDialog")
    @patch("PyQt5.QtWidgets.QMessageBox")
    @patch("gui.main_window.is_model_downloaded")
    def test_main_window_open_settings_dialog(self, mock_is_downloaded, mock_msgbox, mock_dialog, mock_load_config):
        """Test MainWindow.open_settings_dialog reloads config and handles model download."""
        mock_load_config.return_value = {
            "selected_model": "base",
            "logging_level": "DEBUG",
            "verbose": True,
            "output_folder": "output",
            "check_for_updates": True
        }
        mock_dialog_instance = MagicMock()
        mock_dialog_instance.exec_.return_value = True
        mock_dialog.return_value = mock_dialog_instance
        mock_is_downloaded.return_value = False
        window = MainWindow()
        window.status_bar = MagicMock()
        window.update_transcription_button_state = MagicMock()

        window.open_settings_dialog()

        mock_load_config.assert_called()
        self.assertEqual(window.status_bar.showMessage.call_args[0][0], "Modelo carregado: base")
        mock_dialog.assert_called_once_with(window)
        mock_msgbox.assert_called_once()
        mock_msgbox.return_value.setWindowTitle.assert_called_once_with("Reinicialização Necessária")
        window.update_transcription_button_state.assert_called_once()

    @patch("gui.main_window.is_model_downloaded")
    @patch("gui.main_window.TranscriptionThread")
    def test_main_window_start_transcription(self, mock_thread, mock_is_downloaded):
        """Test MainWindow.start_transcription starts the transcription thread."""
        mock_is_downloaded.return_value = True
        window = MainWindow()
        window.queued_files = ["file1.mp3"]
        window.transcribe_button = MagicMock()
        window.stop_button = MagicMock()
        window.elapsed_timer = MagicMock()
        window.status_bar = MagicMock()
        window.progress = MagicMock()
        window.current_file_label = MagicMock()

        window.start_transcription()

        window.transcribe_button.setEnabled.assert_called_once_with(False)
        window.stop_button.setEnabled.assert_called_once_with(True)
        self.assertEqual(window.elapsed_seconds, 0)
        window.elapsed_timer.start.assert_called_once_with(1000)
        window.status_bar.showMessage.assert_called_once_with("Transcrição em andamento...")
        window.progress.setValue.assert_called_once_with(0)
        window.current_file_label.setText.assert_called_once_with("Arquivo atual: Iniciando...")
        mock_thread.assert_called_once_with(["file1.mp3"])
        mock_thread.return_value.start.assert_called_once()

    def test_main_window_stop_transcription(self):
        """Test MainWindow.stop_transcription cancels the transcription."""
        window = MainWindow()
        window.thread = MagicMock()
        window.elapsed_timer = MagicMock()
        window.stop_button = MagicMock()
        window.update_transcription_button_state = MagicMock()
        window.progress = MagicMock()
        window.status_bar = MagicMock()
        window.current_file_label = MagicMock()

        window.stop_transcription()

        self.assertTrue(window.thread.cancelled)
        window.elapsed_timer.stop.assert_called_once()
        window.stop_button.setEnabled.assert_called_once_with(False)
        window.update_transcription_button_state.assert_called_once()
        window.progress.setValue.assert_called_once_with(0)
        window.status_bar.showMessage.assert_called_once_with("Transcrição cancelada")
        window.current_file_label.setText.assert_called_once_with("Arquivo atual: Nenhum")
        self.assertIsNone(window.current_file)

    def test_main_window_update_current_file(self):
        """Test MainWindow.update_current_file updates the UI and queue."""
        window = MainWindow()
        window.queued_files = ["file1.mp3", "file2.mp3"]
        window.processed_files = []
        window.current_file_label = MagicMock()

        window.update_current_file("file1.mp3")

        self.assertEqual(window.current_file, "file1.mp3")
        self.assertEqual(window.queued_files, ["file2.mp3"])
        self.assertEqual(window.processed_files, ["file1.mp3"])
        window.current_file_label.setText.assert_called_once_with("Arquivo atual: file1.mp3")

    def test_main_window_transcription_done(self):
        """Test MainWindow.transcription_done handles successful transcription."""
        window = MainWindow()
        window.elapsed_timer = MagicMock()
        window.stop_button = MagicMock()
        window.update_transcription_button_state = MagicMock()
        window.status_bar = MagicMock()
        window.current_file_label = MagicMock()
        window.show_summary_panel = MagicMock()
        window.QMessageBox = MagicMock()

        window.transcription_done("Success", ["file1.mp3"])

        window.elapsed_timer.stop.assert_called_once()
        window.stop_button.setEnabled.assert_called_once_with(False)
        window.update_transcription_button_state.assert_called_once()
        window.status_bar.showMessage.assert_called_once_with("Transcrição concluída com sucesso")
        window.current_file_label.setText.assert_called_once_with("Arquivo atual: Nenhum")
        self.assertIsNone(window.current_file)
        window.show_summary_panel.assert_called_once_with(["file1.mp3"])
        window.QMessageBox.information.assert_called_once_with(window, "Sucesso", "Success")

    def test_main_window_transcription_failed(self):
        """Test MainWindow.transcription_failed handles transcription failure."""
        window = MainWindow()
        window.elapsed_timer = MagicMock()
        window.stop_button = MagicMock()
        window.update_transcription_button_state = MagicMock()
        window.status_bar = MagicMock()
        window.current_file_label = MagicMock()
        window.QMessageBox = MagicMock()

        window.transcription_failed("file1.mp3")

        window.elapsed_timer.stop.assert_called_once()
        window.stop_button.setEnabled.assert_called_once_with(False)
        window.update_transcription_button_state.assert_called_once()
        window.status_bar.showMessage.assert_called_once_with("Erro na transcrição")
        window.current_file_label.setText.assert_called_once_with("Arquivo atual: Nenhum")
        self.assertIsNone(window.current_file)
        window.QMessageBox.critical.assert_called_once_with(
            window, "Erro", "Erro ao transcrever o arquivo: file1.mp3"
        )

    @patch("PyQt5.QtGui.QDesktopServices.openUrl")
    def test_main_window_open_help_link(self, mock_open_url):
        """Test MainWindow.open_help_link opens the help URL."""
        window = MainWindow()
        window.open_help_link()
        mock_open_url.assert_called_once_with(window.QUrl("https://github.com/andreipa/police-transcriber"))

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="[00:00:00 - 00:00:05] Sensitive word\n")
    @patch("PyQt5.QtWidgets.QDialog")
    def test_main_window_show_summary_panel(self, mock_dialog, mock_open_file, mock_exists):
        """Test MainWindow.show_summary_panel displays transcription summary."""
        mock_exists.return_value = True
        window = MainWindow()
        files = ["file1.mp3"]
        window.show_summary_panel(files)
        mock_exists.assert_called_once()
        mock_open_file.assert_called_once()
        mock_dialog.assert_called_once()
        mock_dialog.return_value.exec_.assert_called_once()


if __name__ == "__main__":
    unittest.main()
