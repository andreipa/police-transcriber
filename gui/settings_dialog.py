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
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
)

from config import (
    AVAILABLE_MODELS,
    SELECTED_MODEL,
    LOGGING_LEVEL,
    VERBOSE,
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
        self.setMinimumSize(500, 450)  # Compact size for better focus
        self.setObjectName("SettingsDialog")  # For stylesheet targeting
        app_logger.debug("Initializing SettingsDialog")
        debug_logger.debug("Starting SettingsDialog setup")

        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(8)  # Windows 11 8px grid
        layout.setContentsMargins(12, 12, 12, 12)

        # Header: Configurações de Transcrição
        transcription_header = QLabel("Configurações de Transcrição")
        transcription_header.setObjectName("SettingsLabel")
        layout.addWidget(transcription_header)

        # Form layout for transcription settings
        transcription_form = QFormLayout()
        transcription_form.setLabelAlignment(Qt.AlignRight)
        transcription_form.setFormAlignment(Qt.AlignLeft)
        transcription_form.setSpacing(8)
        transcription_form.setContentsMargins(0, 0, 0, 8)

        # Model selection
        model_label = QLabel("Modelo:")
        model_label.setObjectName("SettingsLabel")
        self.model_combo = QComboBox()
        self.model_combo.addItems(AVAILABLE_MODELS.keys())
        self.model_combo.setCurrentText(SELECTED_MODEL)
        self.model_combo.setObjectName("SettingsComboBox")
        self.model_combo.setMaximumWidth(300)
        self.model_combo.setToolTip("Selecione o modelo de transcrição a ser usado.")
        transcription_form.addRow(model_label, self.model_combo)

        # Model description
        self.model_description = QLabel(self.get_model_description(SELECTED_MODEL))
        self.model_description.setWordWrap(True)
        self.model_description.setObjectName("SettingsDescription")
        self.model_description.setMaximumWidth(300)
        transcription_form.addRow("", self.model_description)
        self.model_combo.currentTextChanged.connect(self.update_model_description)

        layout.addLayout(transcription_form)

        # Header: Logging
        logging_header = QLabel("Logging")
        logging_header.setObjectName("SettingsLabel")
        layout.addWidget(logging_header)

        # Form layout for logging settings
        logging_form = QFormLayout()
        logging_form.setLabelAlignment(Qt.AlignRight)
        logging_form.setFormAlignment(Qt.AlignLeft)
        logging_form.setSpacing(8)
        logging_form.setContentsMargins(0, 0, 0, 8)

        # Logging level
        logging_label = QLabel("Nível de Log:")
        logging_label.setObjectName("SettingsLabel")
        self.logging_combo = QComboBox()
        self.logging_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.logging_combo.setCurrentText(LOGGING_LEVEL)
        self.logging_combo.setObjectName("SettingsComboBox")
        self.logging_combo.setMaximumWidth(300)
        self.logging_combo.setToolTip(
            "Nível de log para app.log:\n"
            "- DEBUG: Todos os detalhes (desenvolvimento).\n"
            "- INFO: Eventos principais (monitoramento).\n"
            "- WARNING: Avisos não críticos.\n"
            "- ERROR: Erros recuperáveis (padrão).\n"
            "- CRITICAL: Erros graves que param o aplicativo."
        )
        logging_form.addRow(logging_label, self.logging_combo)

        # Verbose logging
        self.verbose_checkbox = QCheckBox("Habilitar Log Detalhado (debug.log)")
        self.verbose_checkbox.setChecked(VERBOSE)
        self.verbose_checkbox.setObjectName("SettingsCheckBox")
        self.verbose_checkbox.setToolTip(
            "Habilita logs detalhados em logs/debug.log para depuração. "
            "Útil para diagnosticar problemas, mas pode gerar arquivos grandes."
        )
        logging_form.addRow("", self.verbose_checkbox)

        layout.addLayout(logging_form)

        # Header: Saída e Atualizações
        output_header = QLabel("Saída e Atualizações")
        output_header.setObjectName("SettingsLabel")
        layout.addWidget(output_header)

        # Form layout for output and updates
        output_form = QFormLayout()
        output_form.setLabelAlignment(Qt.AlignRight)
        output_form.setFormAlignment(Qt.AlignLeft)
        output_form.setSpacing(8)
        output_form.setContentsMargins(0, 0, 0, 8)

        # Output folder
        output_label = QLabel("Pasta de Saída:")
        output_label.setObjectName("SettingsLabel")
        self.output_line_edit = QLineEdit(OUTPUT_FOLDER)
        self.output_line_edit.setReadOnly(True)
        self.output_line_edit.setObjectName("SettingsLineEdit")
        self.output_line_edit.setMaximumWidth(300)
        self.output_line_edit.setToolTip("Pasta onde as transcrições serão salvas.")
        output_button = QPushButton("Selecionar")
        output_button.setObjectName("PrimaryButton")
        output_button.setMaximumWidth(150)
        output_button.setIcon(QIcon("assets/icons/folder.png"))  # Added icon for clarity
        output_button.clicked.connect(self.select_output_folder)
        output_layout = QHBoxLayout()
        output_layout.setSpacing(8)
        output_layout.addWidget(self.output_line_edit)
        output_layout.addWidget(output_button)
        output_form.addRow(output_label, output_layout)

        # Check for updates
        self.updates_checkbox = QCheckBox("Verificar Atualizações ao Iniciar")
        self.updates_checkbox.setChecked(CHECK_FOR_UPDATES)
        self.updates_checkbox.setObjectName("SettingsCheckBox")
        self.updates_checkbox.setToolTip(
            "Verifica automaticamente se há novas versões do aplicativo ao iniciar."
        )
        output_form.addRow("", self.updates_checkbox)

        layout.addLayout(output_form)

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
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancelar")
        cancel_button.setObjectName("SettingsButton")
        cancel_button.setMinimumWidth(100)
        cancel_button.clicked.connect(self.reject)
        restore_button = QPushButton("Restaurar Padrões")
        restore_button.setObjectName("SettingsButton")
        restore_button.setMinimumWidth(100)
        restore_button.setToolTip("Restaura as configurações para os valores padrão.")
        restore_button.clicked.connect(self.restore_defaults)
        button_layout.addWidget(restore_button)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
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
            "base": "Base: 145 MB, baixa precisão, rápido, ideal para testes.",
            "small": "Small: 484 MB, precisão moderada, bom equilíbrio.",
            "medium": "Medium: 1.53 GB, alta precisão, recomendado para uso geral.",
            "large-v2": "Large-v2: 3.09 GB, máxima precisão, ideal para transcrições críticas, mas mais lento.",
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

    def select_output_folder(self) -> None:
        """Open a folder picker dialog to select the output folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Selecionar Pasta de Saída",
            self.output_line_edit.text() or os.path.expanduser("~"),
            QFileDialog.ShowDirsOnly
        )
        if folder:
            self.output_line_edit.setText(folder)
            app_logger.info(f"Selected output folder: {folder}")
            debug_logger.debug(f"Output folder selection changed to: {folder}")

    def restore_defaults(self) -> None:
        """Restore settings to their default values."""
        try:
            self.model_combo.setCurrentText("medium")  # Balanced default
            self.logging_combo.setCurrentText("ERROR")  # Standard for production
            self.verbose_checkbox.setChecked(False)  # Minimize logging
            self.output_line_edit.setText(os.path.expanduser("~/PoliceTranscriber/output"))  # User-specific default
            self.updates_checkbox.setChecked(True)  # Encourage updates
            self.update_model_description("medium")
            self.status_label.setText("Configurações restauradas!")
            self.status_label.setProperty("error", False)
            self.status_label.style().unpolish(self.status_label)
            self.status_label.style().polish(self.status_label)
            app_logger.info("Restored default settings")
            debug_logger.debug("Default settings restored: model=medium, logging_level=ERROR, verbose=False, "
                               "output_folder=~/PoliceTranscriber/output, check_for_updates=True")
        except Exception as e:
            app_logger.error(f"Failed to restore default settings: {e}")
            self.status_label.setText("Erro ao restaurar configurações.")
            self.status_label.setProperty("error", True)
            self.status_label.style().unpolish(self.status_label)
            self.status_label.style().polish(self.status_label)
            debug_logger.debug(f"Failed to restore defaults: {str(e)}")
            QMessageBox.critical(self, "Erro", "Falha ao restaurar configurações padrão.")

    def accept(self) -> None:
        """Save settings when the Salvar button is clicked."""
        try:
            selected_model = self.model_combo.currentText()
            logging_level = self.logging_combo.currentText()
            verbose = self.verbose_checkbox.isChecked()
            output_folder = self.output_line_edit.text()
            check_for_updates = self.updates_checkbox.isChecked()

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