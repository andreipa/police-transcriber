#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

import unittest
import tempfile
import os
import json
from unittest import mock
from pathlib import Path

import config as config_module


class TestConfigModule(unittest.TestCase):

    def setUp(self):
        # Create a temporary config file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_config_path = os.path.join(self.temp_dir.name, "config.json")
        self.original_config_file = config_module.CONFIG_FILE
        config_module.CONFIG_FILE = self.temp_config_path

    def tearDown(self):
        # Restore original config file path
        config_module.CONFIG_FILE = self.original_config_file
        self.temp_dir.cleanup()

    def test_save_and_load_config(self):
        # Save custom configuration
        test_config = {
            "selected_model": "small",
            "logging_level": "DEBUG",
            "verbose": True,
            "output_folder": os.path.join(self.temp_dir.name, "output"),
            "check_for_updates": False,
        }
        config_module.save_config(**test_config)

        # Load configuration
        loaded_config = config_module.load_config()

        self.assertEqual(loaded_config["selected_model"], "small")
        self.assertEqual(loaded_config["logging_level"], "DEBUG")
        self.assertTrue(loaded_config["verbose"])
        self.assertFalse(loaded_config["check_for_updates"])
        self.assertTrue(os.path.exists(loaded_config["output_folder"]))

    def test_load_config_creates_default_if_missing(self):
        # Ensure no config exists
        self.assertFalse(os.path.exists(self.temp_config_path))

        # Load config should auto-create default config
        loaded_config = config_module.load_config()
        self.assertTrue(os.path.exists(self.temp_config_path))
        self.assertEqual(loaded_config["selected_model"], config_module.DEFAULT_CONFIG["selected_model"])

    def test_validate_config_invalid_values(self):
        invalid_config = {
            "selected_model": "invalid-model",
            "logging_level": "INVALID",
            "verbose": "yes",  # should be bool
            "output_folder": None,
            "check_for_updates": "maybe"
        }

        validated = config_module.validate_config(invalid_config)

        self.assertEqual(validated["selected_model"], config_module.DEFAULT_CONFIG["selected_model"])
        self.assertEqual(validated["logging_level"], config_module.DEFAULT_CONFIG["logging_level"])
        self.assertEqual(validated["verbose"], config_module.DEFAULT_CONFIG["verbose"])
        self.assertEqual(validated["output_folder"], config_module.DEFAULT_CONFIG["output_folder"])
        self.assertEqual(validated["check_for_updates"], config_module.DEFAULT_CONFIG["check_for_updates"])

    def test_is_model_downloaded_false(self):
        # Check for model files in a non-existent directory
        result = config_module.is_model_downloaded("base", base_path=self.temp_dir.name)
        self.assertFalse(result)

    def test_is_model_downloaded_true(self):
        model_name = "base"
        base_path = Path(self.temp_dir.name) / "models" / model_name
        base_path.mkdir(parents=True)

        for file_name in config_module.AVAILABLE_MODELS[model_name]["files"]:
            with open(base_path / file_name, "w") as f:
                f.write("dummy")

        result = config_module.is_model_downloaded(model_name, base_path=self.temp_dir.name + "/models")
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
