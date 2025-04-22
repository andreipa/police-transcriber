#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.
import os

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout


class FileSummaryDialog(QDialog):
    def __init__(self, file_path: str, duration: float, word_count: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Resumo da Transcrição")
        self.setFixedSize(400, 200)

        layout = QVBoxLayout()

        # Labels
        layout.addWidget(QLabel(f"<b>Arquivo:</b> {os.path.basename(file_path)}"))

        mins, secs = divmod(int(duration), 60)
        hrs, mins = divmod(mins, 60)
        duration_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"
        layout.addWidget(QLabel(f"<b>Duração:</b> {duration_str}"))

        layout.addWidget(QLabel(f"<b>Palavras Sensíveis Detectadas:</b> {word_count}"))

        # Button to open file
        button_layout = QHBoxLayout()
        open_button = QPushButton("Abrir Arquivo de Saída")
        open_button.setToolTip("Clique para abrir o arquivo transcrito")
        open_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(file_path)))
        open_button.setObjectName("PrimaryButton")
        button_layout.addStretch()
        button_layout.addWidget(open_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        self.setLayout(layout)
