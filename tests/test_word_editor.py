#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

import os
import unittest
from unittest.mock import patch, MagicMock, mock_open

from PyQt5.QtWidgets import QApplication

from config import SENSITIVE_WORDS_FILE
from gui.word_editor import WordEditorDialog


class TestWordEditorDialog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the QApplication instance required for PyQt tests."""
        cls.app = QApplication([])

    def setUp(self):
        """Set up the test environment."""
        self.sensitive_words_file = SENSITIVE_WORDS_FILE

    @patch("PyQt5.QtWidgets.QListWidget")
    @patch("PyQt5.QtWidgets.QPushButton")
    @patch("PyQt5.QtWidgets.QLabel")
    @patch("PyQt5.QtWidgets.QVBoxLayout")
    @patch("PyQt5.QtWidgets.QHBoxLayout")
    def test_word_editor_dialog_init(self, mock_hbox_layout, mock_vbox_layout, mock_label, mock_button, mock_list_widget):
        """Test WordEditorDialog initialization."""
        dialog = WordEditorDialog()

        self.assertEqual(dialog.windowTitle(), "Editar Palavras Sensíveis")
        self.assertEqual(dialog.minimumSize().width(), 420)
        self.assertEqual(dialog.minimumSize().height(), 400)
        self.assertEqual(dialog.objectName(), "WordEditorDialog")

        mock_label.assert_called_once_with("Palavras Sensíveis Atuais")
        mock_list_widget.assert_called_once()
        self.assertEqual(dialog.word_list, mock_list_widget.return_value)

        self.assertEqual(mock_button.call_count, 5)  # add, edit, remove, save, cancel
        self.assertEqual(dialog.add_button.toolTip(), "Adicionar uma nova palavra à lista")
        self.assertEqual(dialog.edit_button.toolTip(), "Editar a palavra selecionada na lista")
        self.assertEqual(dialog.remove_button.toolTip(), "Remover a palavra selecionada da lista")
        self.assertEqual(dialog.save_button.toolTip(), "Salvar todas as alterações feitas na lista")
        self.assertEqual(dialog.cancel_button.toolTip(), "Cancelar e fechar sem salvar")

        mock_vbox_layout.assert_called_once()
        mock_hbox_layout.assert_called()

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="word1\nword2\nword3\n")
    def test_load_words_file_exists(self, mock_open_file, mock_exists):
        """Test load_words loads words from file."""
        mock_exists.return_value = True
        dialog = WordEditorDialog()
        dialog.word_list = MagicMock()

        dialog.load_words()

        dialog.word_list.clear.assert_called_once()
        mock_exists.assert_called_once_with(self.sensitive_words_file)
        mock_open_file.assert_called_once_with(self.sensitive_words_file, "r", encoding="utf-8")
        dialog.word_list.addItems.assert_called_once_with(["word1", "word2", "word3"])
        dialog.word_list.setEnabled.assert_not_called()

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_load_words_empty_file(self, mock_open_file, mock_exists):
        """Test load_words handles empty file."""
        mock_exists.return_value = True
        dialog = WordEditorDialog()
        dialog.word_list = MagicMock()

        dialog.load_words()

        dialog.word_list.clear.assert_called_once()
        mock_exists.assert_called_once_with(self.sensitive_words_file)
        mock_open_file.assert_called_once_with(self.sensitive_words_file, "r", encoding="utf-8")
        dialog.word_list.addItem.assert_called_once_with("(nenhuma palavra cadastrada)")
        dialog.word_list.setEnabled.assert_called_once_with(False)

    @patch("os.path.exists")
    def test_load_words_file_not_found(self, mock_exists):
        """Test load_words handles missing file."""
        mock_exists.return_value = False
        dialog = WordEditorDialog()
        dialog.word_list = MagicMock()

        dialog.load_words()

        dialog.word_list.clear.assert_called_once()
        mock_exists.assert_called_once_with(self.sensitive_words_file)
        dialog.word_list.addItem.assert_called_once_with("(nenhuma palavra cadastrada)")
        dialog.word_list.setEnabled.assert_called_once_with(False)

    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    @patch("PyQt5.QtWidgets.QMessageBox")
    def test_save_words_success(self, mock_msgbox, mock_open_file, mock_makedirs):
        """Test save_words saves words to file."""
        dialog = WordEditorDialog()
        dialog.word_list = MagicMock()
        dialog.word_list.count.return_value = 3
        dialog.word_list.item.side_effect = [
            MagicMock(text=lambda: "word1"),
            MagicMock(text=lambda: "word2"),
            MagicMock(text=lambda: "word3")
        ]

        dialog.save_words()

        mock_makedirs.assert_called_once_with(os.path.dirname(self.sensitive_words_file), exist_ok=True)
        mock_open_file.assert_called_once_with(self.sensitive_words_file, "w", encoding="utf-8")
        mock_open_file().write.assert_called_once_with("word1\nword2\nword3")
        mock_msgbox.information.assert_called_once_with(dialog, "Sucesso", "Lista salva com sucesso!")
        dialog.accept.assert_called_once()

    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    @patch("PyQt5.QtWidgets.QMessageBox")
    def test_save_words_empty_list(self, mock_msgbox, mock_open_file, mock_makedirs):
        """Test save_words handles empty list."""
        dialog = WordEditorDialog()
        dialog.word_list = MagicMock()
        dialog.word_list.count.return_value = 1
        dialog.word_list.isEnabled.return_value = False

        dialog.save_words()

        mock_makedirs.assert_called_once_with(os.path.dirname(self.sensitive_words_file), exist_ok=True)
        mock_open_file.assert_called_once_with(self.sensitive_words_file, "w", encoding="utf-8")
        mock_open_file().write.assert_called_once_with("")
        mock_msgbox.information.assert_called_once_with(dialog, "Sucesso", "Lista salva com sucesso!")
        dialog.accept.assert_called_once()

    @patch("os.makedirs")
    @patch("builtins.open")
    @patch("PyQt5.QtWidgets.QMessageBox")
    def test_save_words_exception(self, mock_msgbox, mock_open_file, mock_makedirs):
        """Test save_words handles file write exceptions."""
        mock_makedirs.return_value = None
        mock_open_file.side_effect = IOError("Write error")
        dialog = WordEditorDialog()
        dialog.word_list = MagicMock()
        dialog.word_list.count.return_value = 0

        dialog.save_words()

        mock_makedirs.assert_called_once_with(os.path.dirname(self.sensitive_words_file), exist_ok=True)
        mock_open_file.assert_called_once_with(self.sensitive_words_file, "w", encoding="utf-8")
        mock_msgbox.critical.assert_called_once_with(dialog, "Erro", "Falha ao salvar a lista de palavras.")
        dialog.accept.assert_not_called()

    @patch("PyQt5.QtWidgets.QInputDialog.getText")
    def test_add_word_valid_input(self, mock_get_text):
        """Test add_word adds a new word to the list."""
        mock_get_text.return_value = ("new_word", True)
        dialog = WordEditorDialog()
        dialog.word_list = MagicMock()

        dialog.add_word()

        dialog.word_list.addItem.assert_called_once_with("new_word")
        dialog.word_list.clear.assert_not_called()
        dialog.word_list.setEnabled.assert_not_called()

    @patch("PyQt5.QtWidgets.QInputDialog.getText")
    def test_add_word_empty_list(self, mock_get_text):
        """Test add_word enables and clears empty list before adding."""
        mock_get_text.return_value = ("new_word", True)
        dialog = WordEditorDialog()
        dialog.word_list = MagicMock()
        dialog.word_list.isEnabled.return_value = False

        dialog.add_word()

        dialog.word_list.clear.assert_called_once()
        dialog.word_list.setEnabled.assert_called_once_with(True)
        dialog.word_list.addItem.assert_called_once_with("new_word")

    @patch("PyQt5.QtWidgets.QInputDialog.getText")
    def test_add_word_cancelled(self, mock_get_text):
        """Test add_word handles cancelled input."""
        mock_get_text.return_value = ("", False)
        dialog = WordEditorDialog()
        dialog.word_list = MagicMock()

        dialog.add_word()

        dialog.word_list.addItem.assert_not_called()

    @patch("PyQt5.QtWidgets.QInputDialog.getText")
    @patch("PyQt5.QtWidgets.QMessageBox")
    def test_edit_word_valid_input(self, mock_msgbox, mock_get_text):
        """Test edit_word updates the selected word."""
        mock_get_text.return_value = ("updated_word", True)
        dialog = WordEditorDialog()
        dialog.word_list = MagicMock()
        selected_item = MagicMock()
        dialog.word_list.currentItem.return_value = selected_item

        dialog.edit_word()

        selected_item.setText.assert_called_once_with("updated_word")
        mock_msgbox.warning.assert_not_called()

    @patch("PyQt5.QtWidgets.QMessageBox")
    def test_edit_word_no_selection(self, mock_msgbox):
        """Test edit_word handles no selected word."""
        dialog = WordEditorDialog()
        dialog.word_list = MagicMock()
        dialog.word_list.currentItem.return_value = None

        dialog.edit_word()

        mock_msgbox.warning.assert_called_once_with(dialog, "Aviso", "Selecione uma palavra para editar.")

    @patch("PyQt5.QtWidgets.QMessageBox")
    def test_remove_word_valid_selection(self, mock_msgbox):
        """Test remove_word removes the selected word."""
        dialog = WordEditorDialog()
        dialog.word_list = MagicMock()
        selected_item = MagicMock()
        dialog.word_list.currentItem.return_value = selected_item
        dialog.word_list.row.return_value = 0

        dialog.remove_word()

        dialog.word_list.takeItem.assert_called_once_with(0)
        mock_msgbox.warning.assert_not_called()

    @patch("PyQt5.QtWidgets.QMessageBox")
    def test_remove_word_no_selection(self, mock_msgbox):
        """Test remove_word handles no selected word."""
        dialog = WordEditorDialog()
        dialog.word_list = MagicMock()
        dialog.word_list.currentItem.return_value = None

        dialog.remove_word()

        dialog.word_list.takeItem.assert_not_called()
        mock_msgbox.warning.assert_called_once_with(dialog, "Aviso", "Selecione uma palavra para remover.")

    def test_reject(self):
        """Test reject calls the parent reject method."""
        dialog = WordEditorDialog()
        dialog.reject()
        # No specific assertions needed; just ensure no exceptions are raised
        # and parent method is called implicitly via super().reject()


if __name__ == "__main__":
    unittest.main()
