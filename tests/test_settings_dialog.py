#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.
import json
import os
import unittest
from unittest.mock import patch

from PyQt5.QtWidgets import QApplication

from gui.settings_dialog import SettingsDialog


class TestSettingsDialog(unittest.TestCase):
    def setUp(self):
        """Set up the test environment."""
        self.app = QApplication([])  # Required for PyQt widgets
        self.test_config_path = "test_config.json"
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)

    def tearDown(self):
        """Clean up the test environment."""
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)

    def test_settings_dialog_initialization(self):
        """Test that SettingsDialog initializes with the correct configuration values."""
        test_config = {
            "selected_model": "base",
            "logging_level": "INFO",
            "verbose": False,
            "output_folder": "test_output",
            "check_for_updates": True
        }
        with open(self.test_config_path, "w", encoding="utf-8") as f:
            json.dump(test_config, f)
        with patch("config.CONFIG_FILE", self.test_config_path):
            dialog = SettingsDialog()
            self.assertEqual(dialog.model_combo.currentText(), "base")
            self.assertEqual(dialog.logging_combo.currentText(), "INFO")
            self.assertEqual(dialog.updates_combo.currentText(), "Sim")
            self.assertEqual(dialog.output_folder, "test_output")

    def test_settings_dialog_save(self):
        """Test that SettingsDialog saves the configuration correctly."""
        with patch("config.CONFIG_FILE", self.test_config_path):
            dialog = SettingsDialog()
            dialog.model_combo.setCurrentText("small")
            dialog.logging_combo.setCurrentText("DEBUG")
            dialog.updates_combo.setCurrentText("Não")
            dialog.output_folder = "new_output"
            dialog.accept()
            with open(self.test_config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            self.assertEqual(config["selected_model"], "small")
            self.assertEqual(config["logging_level"], "DEBUG")
            self.assertTrue(config["verbose"])  # verbose is True for DEBUG
            self.assertEqual(config["output_folder"], "new_output")
            self.assertFalse(config["check_for_updates"])


if __name__ == "__main__":
    unittest.main()
