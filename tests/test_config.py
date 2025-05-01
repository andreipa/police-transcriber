#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.
import json
import logging
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from config import (
    is_model_downloaded,
    load_config,
    validate_config,
    save_config,
    update_logging,
    DEFAULT_CONFIG,
    app_logger,
    debug_logger,
    debug_handler,
    CONFIG_FILE,
    AVAILABLE_MODELS,
)


@pytest.fixture
def temp_config_dir(tmp_path):
    """Fixture to create a temporary directory for config and model files."""
    config_file = tmp_path / CONFIG_FILE
    model_dir = tmp_path / "models" / "large-v2"
    model_dir.mkdir(parents=True, exist_ok=True)
    log_dir = tmp_path / "logs"
    log_dir.mkdir(exist_ok=True)
    return tmp_path, config_file, model_dir, log_dir


@pytest.fixture
def mock_logger():
    """Fixture to mock loggers."""
    with patch("config.app_logger") as mock_app, patch("config.debug_logger") as mock_debug:
        yield mock_app, mock_debug


def test_is_model_downloaded_all_files_exist(temp_config_dir):
    """Test is_model_downloaded when all model files exist."""
    _, _, model_dir, _ = temp_config_dir
    for file in AVAILABLE_MODELS["large-v2"]["files"]:
        (model_dir / file).touch()  # Create empty file
    assert is_model_downloaded("large-v2") is True


def test_is_model_downloaded_missing_files(temp_config_dir):
    """Test is_model_downloaded when some model files are missing."""
    _, _, model_dir, _ = temp_config_dir
    # Create only one file
    (model_dir / "model.bin").touch()
    assert is_model_downloaded("large-v2") is False


def test_load_config_default_creation(temp_config_dir, mock_logger):
    """Test load_config creating default config when config.json doesn't exist."""
    tmp_path, config_file, _, _ = temp_config_dir
    mock_app, _ = mock_logger
    with patch("config.save_config") as mock_save:
        config = load_config()
        mock_save.assert_called_once_with(**DEFAULT_CONFIG)
        mock_app.info.assert_called_once_with(f"Created default configuration file: {CONFIG_FILE}")
        assert config == DEFAULT_CONFIG


def test_load_config_valid_file(temp_config_dir):
    """Test load_config with a valid config.json."""
    tmp_path, config_file, _, _ = temp_config_dir
    config_data = {
        "selected_model": "small",
        "logging_level": "INFO",
        "verbose": False,
        "output_folder": str(tmp_path / "output"),
        "check_for_updates": False
    }
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config_data, f)

    with patch("config.update_logging") as mock_update:
        config = load_config()
        assert config == config_data
        mock_update.assert_called_once_with("INFO", False)


def test_load_config_invalid_json(temp_config_dir, mock_logger):
    """Test load_config with invalid JSON in config.json."""
    tmp_path, config_file, _, _ = temp_config_dir
    mock_app, _ = mock_logger
    with open(config_file, "w", encoding="utf-8") as f:
        f.write("invalid json")

    config = load_config()
    mock_app.error.assert_called_once()
    assert config == DEFAULT_CONFIG


def test_validate_config_valid():
    """Test validate_config with a valid configuration."""
    config = DEFAULT_CONFIG.copy()
    validated = validate_config(config)
    assert validated == config


def test_validate_config_invalid_model(temp_config_dir, mock_logger):
    """Test validate_config with an invalid model."""
    tmp_path, _, _, _ = temp_config_dir
    mock_app, _ = mock_logger
    config = DEFAULT_CONFIG.copy()
    config["selected_model"] = "invalid_model"
    validated = validate_config(config)
    mock_app.warning.assert_called_once()
    assert validated["selected_model"] == DEFAULT_CONFIG["selected_model"]


def test_validate_config_invalid_logging_level(temp_config_dir, mock_logger):
    """Test validate_config with an invalid logging level."""
    tmp_path, _, _, _ = temp_config_dir
    mock_app, _ = mock_logger
    config = DEFAULT_CONFIG.copy()
    config["logging_level"] = "INVALID"
    validated = validate_config(config)
    mock_app.warning.assert_called_once()
    assert validated["logging_level"] == DEFAULT_CONFIG["logging_level"]


def test_validate_config_invalid_verbose(temp_config_dir, mock_logger):
    """Test validate_config with an invalid verbose value."""
    tmp_path, _, _, _ = temp_config_dir
    mock_app, _ = mock_logger
    config = DEFAULT_CONFIG.copy()
    config["verbose"] = "not_a_boolean"
    validated = validate_config(config)
    mock_app.warning.assert_called_once()
    assert validated["verbose"] == DEFAULT_CONFIG["verbose"]


def test_validate_config_invalid_output_folder(temp_config_dir, mock_logger):
    """Test validate_config with an invalid output folder."""
    tmp_path, _, _, _ = temp_config_dir
    mock_app, _ = mock_logger
    config = DEFAULT_CONFIG.copy()
    config["output_folder"] = ""
    validated = validate_config(config)
    mock_app.warning.assert_called_once()
    assert validated["output_folder"] == DEFAULT_CONFIG["output_folder"]
    assert (Path(tmp_path) / "output").exists()  # Ensure default folder is created


def test_save_config_success(temp_config_dir, mock_logger):
    """Test save_config successfully saving to config.json."""
    tmp_path, config_file, _, _ = temp_config_dir
    mock_app, _ = mock_logger
    config_data = {
        "selected_model": "base",
        "logging_level": "DEBUG",
        "verbose": True,
        "output_folder": str(tmp_path / "output"),
        "check_for_updates": True
    }
    with patch("config.update_logging") as mock_update:
        save_config(**config_data)
        mock_update.assert_called_once_with("DEBUG", True)
        mock_app.debug.assert_any_call(f"Saving config to: {os.path.abspath(CONFIG_FILE)}")
        mock_app.debug.assert_any_call(f"Successfully saved config to: {os.path.abspath(CONFIG_FILE)}")
        assert config_file.exists()
        with open(config_file, "r", encoding="utf-8") as f:
            saved_config = json.load(f)
        assert saved_config == config_data


def test_save_config_failure(temp_config_dir, mock_logger):
    """Test save_config handling file write errors."""
    tmp_path, config_file, _, _ = temp_config_dir
    mock_app, _ = mock_logger
    with patch("builtins.open", side_effect=IOError("Permission denied")):
        save_config()
        mock_app.error.assert_called_once_with(f"Failed to save config to {CONFIG_FILE}: Permission denied")


def test_update_logging_verbose_enabled(temp_config_dir):
    """Test update_logging enabling verbose mode."""
    tmp_path, _, _, _ = temp_config_dir
    debug_logger.handlers = []  # Clear handlers
    update_logging("INFO", True)
    assert debug_handler in debug_logger.handlers
    assert app_logger.level == logging.INFO


def test_update_logging_verbose_disabled(temp_config_dir):
    """Test update_logging disabling verbose mode."""
    tmp_path, _, _, _ = temp_config_dir
    debug_logger.handlers = [debug_handler]  # Add handler
    update_logging("WARNING", False)
    assert debug_handler not in debug_logger.handlers
    assert app_logger.level == logging.WARNING


if __name__ == "__main__":
    pytest.main()
