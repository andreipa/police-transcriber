#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QInputDialog, QLabel, QListWidget, QMessageBox,
    QPushButton, QSpacerItem, QSizePolicy, QVBoxLayout
)

SENSITIVE_WORDS_FILE = os.path.join("data", "sensible_words.txt")

class WordEditorDialog(QDialog):
    """A dialog for editing a list of sensitive words stored in a file."""

    def __init__(self, parent=None) -> None:
        """Initialize the word editor dialog with a list of sensitive words and controls.

        Args:
            parent: Optional parent widget for the dialog.
        """
        super().__init__(parent)
        self.setWindowTitle("Editar Palavras Sensíveis")
        self.setFixedSize(420, 400)

        layout = QVBoxLayout()

        title = QLabel("Palavras Sensíveis Atuais")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        self.word_list = QListWidget()
        layout.addWidget(self.word_list)
        self.load_words()

        button_layout = QHBoxLayout()
        self.add_button = QPushButton(" Adicionar")
        self.add_button.setToolTip("Adicionar uma nova palavra à lista")
        self.add_button.setIcon(QIcon("assets/icons/add.png"))
        self.add_button.clicked.connect(self.add_word)

        self.edit_button = QPushButton(" Editar")
        self.edit_button.setToolTip("Editar a palavra selecionada na lista")
        self.edit_button.setIcon(QIcon("assets/icons/edit.png"))
        self.edit_button.clicked.connect(self.edit_word)

        self.remove_button = QPushButton(" Remover")
        self.remove_button.setToolTip("Remover a palavra selecionada da lista")
        self.remove_button.setIcon(QIcon("assets/icons/delete.png"))
        self.remove_button.setObjectName("DangerButton")
        self.remove_button.clicked.connect(self.remove_word)

        for button in [self.add_button, self.edit_button, self.remove_button]:
            button.setCursor(Qt.PointingHandCursor)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.remove_button)
        layout.addLayout(button_layout)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        bottom_buttons = QHBoxLayout()
        self.save_button = QPushButton("  Salvar Alterações")
        self.save_button.setToolTip("Salvar todas as alterações feitas na lista")
        self.save_button.setIcon(QIcon("assets/icons/save.png"))
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.clicked.connect(self.save_words)

        self.cancel_button = QPushButton("  Cancelar")
        self.cancel_button.setToolTip("Cancelar e fechar sem salvar")
        self.cancel_button.setIcon(QIcon("assets/icons/cancel.png"))
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.clicked.connect(self.reject)

        bottom_buttons.addWidget(self.save_button)
        bottom_buttons.addWidget(self.cancel_button)
        layout.addLayout(bottom_buttons)

        self.setLayout(layout)

    def load_words(self) -> None:
        """Load sensitive words from the file into the list widget.

        If the file is empty or does not exist, display a placeholder message and disable the list.
        """
        self.word_list.clear()
        if os.path.exists(SENSITIVE_WORDS_FILE):
            with open(SENSITIVE_WORDS_FILE, "r", encoding="utf-8") as file:
                words = [line.strip() for line in file if line.strip()]
                if words:
                    self.word_list.addItems(words)
                else:
                    self.word_list.addItem("(nenhuma palavra cadastrada)")
                    self.word_list.setEnabled(False)
        else:
            self.word_list.addItem("(nenhuma palavra cadastrada)")
            self.word_list.setEnabled(False)

    def save_words(self) -> None:
        """Save the current list of words to the file and close the dialog.

        If the list is empty or disabled, an empty file is written.
        """
        if self.word_list.count() == 1 and not self.word_list.isEnabled():
            words = []
        else:
            words = [self.word_list.item(i).text() for i in range(self.word_list.count())]

        os.makedirs(os.path.dirname(SENSITIVE_WORDS_FILE), exist_ok=True)
        with open(SENSITIVE_WORDS_FILE, "w", encoding="utf-8") as file:
            file.write("\n".join(words))

        QMessageBox.information(self, "Sucesso", "Lista salva com sucesso!")
        self.accept()

    def add_word(self) -> None:
        """Prompt the user to add a new word to the list.

        Enables the list if it was previously disabled due to being empty.
        """
        text, ok = QInputDialog.getText(self, "Adicionar Palavra", "Nova palavra:")
        if ok and text.strip():
            if not self.word_list.isEnabled():
                self.word_list.clear()
                self.word_list.setEnabled(True)
            self.word_list.addItem(text.strip())

    def edit_word(self) -> None:
        """Prompt the user to edit the selected word in the list.

        Displays a warning if no word is selected.
        """
        selected = self.word_list.currentItem()
        if selected:
            current_text = selected.text()
            new_text, ok = QInputDialog.getText(self, "Editar Palavra", "Nova palavra:", text=current_text)
            if ok and new_text.strip():
                selected.setText(new_text.strip())
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma palavra para editar.")

    def remove_word(self) -> None:
        """Remove the selected word from the list.

        Displays a warning if no word is selected.
        """
        selected = self.word_list.currentItem()
        if selected:
            self.word_list.takeItem(self.word_list.row(selected))
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma palavra para remover.")
