#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

"""Settings dialog for configuring the Police Transcriber application."""

import logging

from PyQt5.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QLabel, QVBoxLayout
)

from config import AVAILABLE_MODELS, SELECTED_MODEL, LOGGING_LEVEL, save_config


class SettingsDialog(QDialog):
    """Dialog for configuring application settings, including model selection and logging level."""

    def __init__(self, parent=None) -> None:
        """Initialize the settings dialog with model selection and logging options.

        Args:
            parent: The parent widget (e.g., MainWindow).
        """
        super().__init__(parent)
        self.setWindowTitle("Configurações")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        # Model selection
        layout.addWidget(QLabel("Modelo de Transcrição:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(AVAILABLE_MODELS.keys())
        self.model_combo.setCurrentText(SELECTED_MODEL)
        self.model_combo.setToolTip(
            "Selecione o modelo de transcrição:\n"
            "- Base: 145 MB, baixa precisão, rápido, ideal para testes.\n"
            "- Small: 484 MB, precisão moderada, bom equilíbrio.\n"
            "- Medium: 1.53 GB, alta precisão, recomendado para uso geral.\n"
            "- Large-v2: 3.09 GB, máxima precisão, ideal para transcrições críticas, mas mais lento."
        )
        layout.addWidget(self.model_combo)

        # Debug logging toggle
        self.debug_checkbox = QCheckBox("Habilitar Log Detalhado (Debug)")
        self.debug_checkbox.setChecked(LOGGING_LEVEL == "DEBUG")
        self.debug_checkbox.setToolTip("Habilita logs detalhados para depuração. Desative para registrar apenas erros.")
        layout.addWidget(self.debug_checkbox)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def accept(self) -> None:
        """Save settings when the OK button is clicked."""
        try:
            selected_model = self.model_combo.currentText()
            logging_level = "DEBUG" if self.debug_checkbox.isChecked() else "ERROR"
            save_config(selected_model, logging_level)
            logging.info(f"Saved settings: model={selected_model}, logging_level={logging_level}")
            super().accept()
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")
            super().reject()
