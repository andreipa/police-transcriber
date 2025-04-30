# -*- coding: utf-8 -*-
#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

"""Settings dialog for configuring the Police Transcriber application."""

import os
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
)

from config import (
    AVAILABLE_MODELS,
    SELECTED_MODEL,
    LOGGING_LEVEL,
    OUTPUT_FOLDER,
    CHECK_FOR_UPDATES,
    app_logger,
    debug_logger,
    save_config,
)


class SettingsDialog(QDialog):
    """Dialog for configuring application settings, including model, logging, output folder, and updates."""

    def __init__(self, parent=None) -> None:
        """Initialize the settings dialog with configuration options.

        Args:
            parent: The parent widget (e.g., MainWindow).
        """
        super().__init__(parent)
        self.setWindowTitle("Configurações")
        self.setFixedSize(500, 450)  # Prevent resizing/maximization
        self.setObjectName("SettingsDialog")  # For stylesheet targeting
        app_logger.debug("Initializing SettingsDialog")
        debug_logger.debug("Starting SettingsDialog setup")

        # Initialize output folder
        self.output_folder = OUTPUT_FOLDER

        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(24)  # Further increased spacing for better separation
        layout.setContentsMargins(12, 24, 12, 12)

        # Group: Configurações de Transcrição
        transcription_group = QGroupBox("Configurações de Transcrição")
        transcription_group.setObjectName("SettingsGroupBox")
        transcription_layout = QVBoxLayout()
        transcription_layout.setSpacing(8)
        transcription_layout.setContentsMargins(8, 8, 8, 8)

        # Model selection row (label, ComboBox, and description)
        model_row = QHBoxLayout()
        model_label = QLabel("Modelo:")
        model_label.setFixedWidth(80)  # Increased to prevent overlap
        model_label.setObjectName("SettingsLabel")
        self.model_combo = QComboBox()
        self.model_combo.addItems(AVAILABLE_MODELS.keys())
        self.model_combo.setCurrentText(SELECTED_MODEL)
        self.model_combo.setObjectName("SettingsComboBox")
        self.model_combo.setFixedWidth(120)  # Reduced to give more space to description
        self.model_combo.setToolTip("Selecione o modelo de transcrição a ser usado.")
        model_row.addWidget(model_label)
        model_row.addWidget(self.model_combo)

        # Model description beside ComboBox
        self.model_description = QLabel(self.get_model_description(SELECTED_MODEL))
        self.model_description.setWordWrap(True)
        self.model_description.setMaximumWidth(250)  # Limit width to ensure wrapping
        self.model_description.setObjectName("SettingsDescription")
        model_row.addWidget(self.model_description)
        self.model_combo.currentTextChanged.connect(self.update_model_description)

        transcription_layout.addLayout(model_row)
        transcription_group.setLayout(transcription_layout)
        layout.addWidget(transcription_group)

        # Group: Configurações de Log
        logging_group = QGroupBox("Configurações de Log")
        logging_group.setObjectName("SettingsGroupBox")
        logging_layout = QVBoxLayout()
        logging_layout.setSpacing(8)
        logging_layout.setContentsMargins(8, 8, 8, 8)

        # Logging level row (label, ComboBox, and description)
        logging_row = QHBoxLayout()
        logging_label = QLabel("Nível de Log:")
        logging_label.setFixedWidth(94)  # Increased to prevent overlap
        logging_label.setObjectName("SettingsLabel")
        self.logging_combo = QComboBox()
        self.logging_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.logging_combo.setCurrentText(LOGGING_LEVEL)
        self.logging_combo.setObjectName("SettingsComboBox")
        self.logging_combo.setFixedWidth(115)  # Reduced to give more space to description
        self.logging_combo.setToolTip("Selecione o nível de log para app.log")
        logging_row.addWidget(logging_label)
        logging_row.addWidget(self.logging_combo)

        # Logging level description beside ComboBox
        self.logging_description = QLabel(self.get_logging_description(LOGGING_LEVEL))
        self.logging_description.setWordWrap(True)
        self.logging_description.setMaximumWidth(250)  # Limit width to ensure wrapping
        self.logging_description.setObjectName("SettingsDescription")
        logging_row.addWidget(self.logging_description)
        self.logging_combo.currentTextChanged.connect(self.update_logging_description)

        logging_layout.addLayout(logging_row)
        logging_group.setLayout(logging_layout)
        layout.addWidget(logging_group)

        # Group: Saída
        output_group = QGroupBox("Saída")
        output_group.setObjectName("SettingsGroupBox")
        output_layout = QVBoxLayout()
        output_layout.setSpacing(8)
        output_layout.setContentsMargins(8, 8, 8, 8)

        # Output folder row (just the button)
        output_form = QFormLayout()
        output_form.setLabelAlignment(Qt.AlignRight)
        output_form.setFormAlignment(Qt.AlignLeft)
        output_form.setSpacing(8)

        output_label = QLabel("Pasta de Saída:")
        output_label.setFixedWidth(105)  # Fixed label width for consistent spacing
        output_label.setObjectName("SettingsLabel")
        self.output_button = QPushButton("Selecionar")
        self.output_button.setObjectName("OutputFolderButton")
        self.output_button.setMaximumWidth(150)
        self.output_button.setIcon(QIcon("assets/icons/folder.png"))
        self.output_button.clicked.connect(self.select_output_folder)
        output_row = QHBoxLayout()
        output_row.setSpacing(8)
        output_row.addWidget(self.output_button)
        output_form.addRow(output_label, output_row)

        output_layout.addLayout(output_form)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # Group: Atualizações
        updates_group = QGroupBox("Atualizações")
        updates_group.setObjectName("SettingsGroupBox")
        updates_layout = QVBoxLayout()
        updates_layout.setSpacing(8)
        updates_layout.setContentsMargins(8, 8, 8, 8)

        # Check for updates row
        updates_form = QFormLayout()
        updates_form.setLabelAlignment(Qt.AlignRight)
        updates_form.setFormAlignment(Qt.AlignLeft)
        updates_form.setSpacing(8)

        updates_label = QLabel("Verificar Atualizações:")
        updates_label.setFixedWidth(150)  # Match the width of other labels
        updates_label.setObjectName("SettingsLabel")
        self.updates_combo = QComboBox()
        self.updates_combo.addItems(["Sim", "Não"])
        self.updates_combo.setCurrentText("Sim" if CHECK_FOR_UPDATES else "Não")
        self.updates_combo.setObjectName("SettingsComboBox")
        self.updates_combo.setFixedWidth(115)  # Match the width of other ComboBoxes
        self.updates_combo.setToolTip("Verifica automaticamente se há novas versões do aplicativo ao iniciar.")
        updates_row = QHBoxLayout()
        updates_row.addWidget(self.updates_combo)
        updates_row.addStretch()
        updates_form.addRow(updates_label, updates_row)

        updates_layout.addLayout(updates_form)
        updates_group.setLayout(updates_layout)
        layout.addWidget(updates_group)

        # Status label for feedback
        self.status_label = QLabel("")
        self.status_label.setObjectName("SettingsStatusLabel")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumHeight(30)
        self.status_label.setMaximumWidth(300)
        layout.addWidget(self.status_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.setAlignment(Qt.AlignRight)
        save_button = QPushButton("Salvar")
        save_button.setObjectName("PrimaryButton")
        save_button.setMinimumWidth(100)
        save_button.setIcon(QIcon("assets/icons/save.png"))  # Added icon for Save
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancelar")
        cancel_button.setObjectName("SettingsButton")
        cancel_button.setMinimumWidth(100)
        cancel_button.setIcon(QIcon("assets/icons/cancel.png"))  # Added icon for Cancel
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        app_logger.debug("SettingsDialog stylesheet applied: QComboBox#SettingsComboBox width should be 450px")
        app_logger.debug("SettingsDialog initialization completed")
        debug_logger.debug("SettingsDialog setup finished")

    def get_model_description(self, model: str) -> str:
        """Get a description of the selected model.

        Args:
            model: The model name (e.g., 'base', 'small', 'medium', 'large-v2').

        Returns:
            A string describing the model's characteristics.
        """
        descriptions = {
            "base": "145 MB - Baixa precisão, rápido, ideal para testes.",
            "small": "484 MB - Precisão moderada, bom equilíbrio.",
            "medium": "1.53 GB - Alta precisão, recomendado para uso geral.",
            "large-v2": "3.09 GB - Máxima precisão, ideal para transcrições críticas, mas mais lento.",
        }
        return descriptions.get(model, "Selecione um modelo para ver a descrição.")

    def update_model_description(self, model: str) -> None:
        """Update the model description label when the selected model changes.

        Args:
            model: The newly selected model name.
        """
        self.model_description.setText(self.get_model_description(model))
        app_logger.debug(f"Updated model description: {model}")
        debug_logger.debug(f"Model description changed to: {model}")

    def get_logging_description(self, level: str) -> str:
        """Get a description of the selected logging level.

        Args:
            level: The logging level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').

        Returns:
            A string describing the logging level's characteristics.
        """
        descriptions = {
            "DEBUG": "Todos os detalhes (desenvolvimento).",
            "INFO": "Eventos principais (monitoramento).",
            "WARNING": "Avisos não críticos.",
            "ERROR": "Erros recuperáveis (padrão).",
            "CRITICAL": "Erros graves que param o aplicativo.",
        }
        return descriptions.get(level, "Selecione um nível de log para ver a descrição.")

    def update_logging_description(self, level: str) -> None:
        """Update the logging description label when the selected logging level changes.

        Args:
            level: The newly selected logging level.
        """
        self.logging_description.setText(self.get_logging_description(level))
        app_logger.debug(f"Updated logging description: {level}")
        debug_logger.debug(f"Logging description changed to: {level}")

    def select_output_folder(self) -> None:
        """Open a folder picker dialog to select the output folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Selecionar Pasta de Saída",
            self.output_folder or os.path.expanduser("~"),
            QFileDialog.ShowDirsOnly
        )
        if folder:
            self.output_folder = folder
            app_logger.info(f"Selected output folder: {folder}")
            debug_logger.debug(f"Output folder selection changed to: {folder}")

    def accept(self) -> None:
        """Save settings when the Salvar button is clicked."""
        try:
            selected_model = self.model_combo.currentText()
            logging_level = self.logging_combo.currentText()
            # Automatically enable debug.log if logging level is DEBUG
            verbose = (logging_level == "DEBUG")
            output_folder = self.output_folder
            check_for_updates = (self.updates_combo.currentText() == "Sim")

            # Validate output folder
            if not os.path.isdir(output_folder):
                app_logger.warning(f"Invalid output folder: {output_folder}. Attempting to create.")
                Path(output_folder).mkdir(parents=True, exist_ok=True)
                if not os.path.isdir(output_folder):
                    self.status_label.setText("Erro: Pasta de saída inválida.")
                    self.status_label.setProperty("error", True)
                    self.status_label.style().unpolish(self.status_label)
                    self.status_label.style().polish(self.status_label)
                    app_logger.error(f"Failed to create output folder: {output_folder}")
                    return

            save_config(
                selected_model=selected_model,
                logging_level=logging_level,
                verbose=verbose,
                output_folder=output_folder,
                check_for_updates=check_for_updates,
            )
            app_logger.info(
                f"Saved settings: model={selected_model}, logging_level={logging_level}, "
                f"verbose={verbose}, output_folder={output_folder}, check_for_updates={check_for_updates}"
            )
            self.status_label.setText("Configurações salvas com sucesso!")
            self.status_label.setProperty("error", False)
            self.status_label.style().unpolish(self.status_label)
            self.status_label.style().polish(self.status_label)
            debug_logger.debug("Settings saved successfully")
            super().accept()
        except Exception as e:
            app_logger.error(f"Failed to save settings: {e}")
            self.status_label.setText("Erro ao salvar configurações.")
            self.status_label.setProperty("error", True)
            self.status_label.style().unpolish(self.status_label)
            self.status_label.style().polish(self.status_label)
            debug_logger.debug(f"Failed to save settings: {str(e)}")
            QMessageBox.critical(self, "Erro", "Falha ao salvar configurações. Verifique os logs para detalhes.")

    def reject(self) -> None:
        """Handle the Cancelar button click."""
        self.status_label.setText("")
        app_logger.debug("SettingsDialog cancelled")
        debug_logger.debug("User cancelled SettingsDialog")
        super().reject()