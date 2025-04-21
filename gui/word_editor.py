from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton,
    QHBoxLayout, QInputDialog, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import os

SENSITIVE_WORDS_FILE = os.path.join("data", "sensible_words.txt")

class WordEditorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Palavras Sensíveis")
        self.setFixedSize(420, 400)

        layout = QVBoxLayout()

        # Title
        title = QLabel("Palavras Sensíveis Atuais")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        # Word list
        self.word_list = QListWidget()
        layout.addWidget(self.word_list)

        self.load_words()

        # Buttons layout
        button_layout = QHBoxLayout()

        self.add_button = QPushButton(" Adicionar")
        self.add_button.setToolTip("Adicionar uma nova palavra à lista")
        self.add_button.setIcon(QIcon("assets/icons/add.png"))
        self.add_button.setObjectName("PrimaryButton")
        self.add_button.clicked.connect(self.add_word)

        self.edit_button = QPushButton(" Editar")
        self.edit_button.setToolTip("Editar a palavra selecionada na lista")
        self.edit_button.setIcon(QIcon("assets/icons/edit.png"))
        self.edit_button.setObjectName("PrimaryButton")
        self.edit_button.clicked.connect(self.edit_word)

        self.remove_button = QPushButton(" Remover")
        self.remove_button.setToolTip("Remover a palavra selecionada da lista")
        self.remove_button.setIcon(QIcon("assets/icons/delete.png"))
        self.remove_button.setObjectName("DangerButton")
        self.remove_button.clicked.connect(self.remove_word)

        for btn in [self.add_button, self.edit_button, self.remove_button]:
            btn.setCursor(Qt.PointingHandCursor)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.remove_button)
        layout.addLayout(button_layout)

        # Spacer
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Bottom buttons layout
        bottom_buttons = QHBoxLayout()

        self.save_btn = QPushButton("  Salvar Alterações")
        self.save_btn.setToolTip("Salvar todas as alterações feitas na lista")
        self.save_btn.setIcon(QIcon("assets/icons/save.png"))
        self.save_btn.setObjectName("PrimaryButton")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_words)

        self.cancel_btn = QPushButton("  Cancelar")
        self.cancel_btn.setToolTip("Cancelar e fechar sem salvar")
        self.cancel_btn.setIcon(QIcon("assets/icons/cancel.png"))
        self.cancel_btn.setObjectName("DangerButton")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)

        bottom_buttons.addWidget(self.save_btn)
        bottom_buttons.addWidget(self.cancel_btn)

        layout.addLayout(bottom_buttons)

        self.setLayout(layout)

    def load_words(self):
        self.word_list.clear()
        if os.path.exists(SENSITIVE_WORDS_FILE):
            with open(SENSITIVE_WORDS_FILE, "r", encoding="utf-8") as f:
                words = [line.strip() for line in f if line.strip()]
                if words:
                    self.word_list.addItems(words)
                else:
                    self.word_list.addItem("(nenhuma palavra cadastrada)")
                    self.word_list.setEnabled(False)

    def save_words(self):
        if self.word_list.count() == 1 and not self.word_list.isEnabled():
            words = []
        else:
            words = [self.word_list.item(i).text() for i in range(self.word_list.count())]

        with open(SENSITIVE_WORDS_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(words))

        QMessageBox.information(self, "Sucesso", "Lista salva com sucesso!")
        self.accept()

    def add_word(self):
        text, ok = QInputDialog.getText(self, "Adicionar Palavra", "Nova palavra:")
        if ok and text:
            if not self.word_list.isEnabled():
                self.word_list.clear()
                self.word_list.setEnabled(True)
            self.word_list.addItem(text.strip())

    def edit_word(self):
        selected = self.word_list.currentItem()
        if selected:
            current_text = selected.text()
            new_text, ok = QInputDialog.getText(self, "Editar Palavra", "Nova palavra:", text=current_text)
            if ok and new_text:
                selected.setText(new_text.strip())
        else:
            QMessageBox.warning(self, "Aviso", "⚠️ Selecione uma palavra para editar.")

    def remove_word(self):
        selected = self.word_list.currentItem()
        if selected:
            self.word_list.takeItem(self.word_list.row(selected))
        else:
            QMessageBox.warning(self, "Aviso", "⚠️ Selecione uma palavra para remover.")
