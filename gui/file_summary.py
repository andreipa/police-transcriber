#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

import os

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout


class FileSummaryDialog(QDialog):
    """A dialog window displaying a summary of a transcribed file's sensitive word count."""

    def __init__(self, file_path: str, word_count: int, parent=None) -> None:
        """Initialize the file summary dialog with file details and an open button.

        Args:
            file_path: Path to the transcribed output file.
            word_count: Number of sensitive words detected in the transcription.
            parent: Optional parent widget for the dialog.
        """
        super().__init__(parent)
        self.setWindowTitle("Resumo da Transcrição")
        self.setFixedSize(400, 150)

        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"<b>Arquivo:</b> {os.path.basename(file_path)}"))
        layout.addWidget(QLabel(f"<b>Palavras Sensíveis Detectadas:</b> {word_count}"))

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