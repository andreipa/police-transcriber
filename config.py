#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

"""Configuration settings for the Police Transcriber application."""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any

# Application metadata
APP_NAME = "Police Transcriber"
"""Name of the application."""

VERSION = "v1.0.0-beta"
"""Current version of the application."""

SLOGAN_PT = "Detecção Automática de Conversas Ilícitas com IA"
"""Portuguese slogan for the application."""

SLOGAN_EN = "Automatic Detection of Illicit Conversations with AI"
"""English slogan for the application."""

# Whisper model configuration
AVAILABLE_MODELS = {
    "base": {
        "files": ["model.bin", "vocabulary.txt", "tokenizer.json", "config.json"],
        "download_url": "https://huggingface.co/guillaumekln/faster-whisper-base/resolve/main",
        "requires_token": False,
    },
    "small": {
        "files": ["model.bin", "vocabulary.txt", "tokenizer.json", "config.json"],
        "download_url": "https://huggingface.co/guillaumekln/faster-whisper-small/resolve/main",
        "requires_token": False,
    },
    "medium": {
        "files": ["model.bin", "vocabulary.txt", "tokenizer.json", "config.json"],
        "download_url": "https://huggingface.co/guillaumekln/faster-whisper-medium/resolve/main",
        "requires_token": False,
    },
    "large-v2": {
        "files": ["model.bin", "vocabulary.txt", "tokenizer.json", "config.json"],
        "download_url": "https://huggingface.co/guillaumekln/faster-whisper-large-v2/resolve/main",
        "requires_token": False,
    },
}
"""Dictionary of available Whisper models with their required files, download URLs, and token requirements."""

# Configuration file
CONFIG_FILE = "config.json"
"""Path to the JSON configuration file for persistent settings."""

# Default configuration
DEFAULT_CONFIG = {
    "selected_model": "large-v2",
    "logging_level": "ERROR",
    "verbose": True,
    "output_folder": os.path.join(os.path.dirname(__file__), "output"),
    "check_for_updates": True,
}
"""Default configuration settings."""

# Valid options for configuration
VALID_MODELS = list(AVAILABLE_MODELS.keys())
"""List of valid model names."""

VALID_LOGGING_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
"""List of valid logging levels: DEBUG (10), INFO (20), WARNING (30), ERROR (40), CRITICAL (50)."""

# Logging configuration
LOG_FOLDER = "logs"
"""Directory where application logs are stored."""

Path(LOG_FOLDER).mkdir(exist_ok=True)  # Ensure log folder exists

# Set up app.log logger
APP_LOG_FILE = os.path.join(LOG_FOLDER, "app.log")
app_logger = logging.getLogger("app")
app_handler = logging.FileHandler(APP_LOG_FILE, encoding="utf-8")
app_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
app_logger.addHandler(app_handler)

# Set up debug.log logger (for verbose mode)
DEBUG_LOG_FILE = os.path.join(LOG_FOLDER, "debug.log")
debug_logger = logging.getLogger("debug")
debug_handler = logging.FileHandler(DEBUG_LOG_FILE, encoding="utf-8")
debug_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
debug_logger.addHandler(debug_handler)
debug_logger.setLevel(logging.DEBUG)  # Debug logger always logs at DEBUG level

def is_model_downloaded(model: str, base_path: str = "models") -> bool:
    """Check if all required model files are downloaded.

    Args:
        model: The model name to check.
        base_path: Base directory for model files (default: 'models').

    Returns:
        True if all model files exist, False otherwise.
    """
    model_path = os.path.join(base_path, model)
    required_files = AVAILABLE_MODELS[model]["files"]
    app_logger.debug(f"Checking model files in: {model_path}")
    return all(os.path.exists(os.path.join(model_path, file)) for file in required_files)

def load_config() -> Dict[str, Any]:
    """Load configuration from config.json, creating it with defaults if it doesn't exist.

    Returns:
        A dictionary with configuration settings.

    Note:
        Must be called before using app_logger or debug_logger to ensure proper configuration.
    """
    abs_config_path = os.path.abspath(CONFIG_FILE)
    app_logger.debug(f"Attempting to load config from: {abs_config_path}")
    if not os.path.exists(abs_config_path):
        app_logger.debug("Config file not found, creating with defaults")
        save_config(**DEFAULT_CONFIG)
        app_logger.info(f"Created default configuration file: {abs_config_path}")

    try:
        with open(abs_config_path, "r", encoding="utf-8") as file:
            config = json.load(file)
        app_logger.debug(f"Loaded config: {config}")
        # Validate configuration
        config = validate_config(config)
        update_logging(config["logging_level"], config["verbose"])
        return config
    except Exception as e:
        app_logger.error(f"Failed to load config: {e}")
        app_logger.debug("Returning default config due to error")
        return DEFAULT_CONFIG

def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the configuration and return a corrected version if necessary.

    Args:
        config: The configuration dictionary to validate.

    Returns:
        A validated configuration dictionary.
    """
    validated_config = config.copy()

    # Validate selected_model
    if validated_config.get("selected_model") not in VALID_MODELS:
        app_logger.warning(
            f"Invalid selected_model: {validated_config.get('selected_model')}. Using default: {DEFAULT_CONFIG['selected_model']}"
        )
        validated_config["selected_model"] = DEFAULT_CONFIG["selected_model"]

    # Validate logging_level
    if validated_config.get("logging_level") not in VALID_LOGGING_LEVELS:
        app_logger.warning(
            f"Invalid logging_level: {validated_config.get('logging_level')}. Using default: {DEFAULT_CONFIG['logging_level']}"
        )
        validated_config["logging_level"] = DEFAULT_CONFIG["logging_level"]

    # Validate verbose
    if not isinstance(validated_config.get("verbose"), bool):
        app_logger.warning(f"Invalid verbose value: {validated_config.get('verbose')}. Using default: {DEFAULT_CONFIG['verbose']}")
        validated_config["verbose"] = DEFAULT_CONFIG["verbose"]

    # Validate output_folder
    output_folder = validated_config.get("output_folder")
    if not output_folder or not isinstance(output_folder, str):
        app_logger.warning(f"Invalid output_folder: {output_folder}. Using default: {DEFAULT_CONFIG['output_folder']}")
        validated_config["output_folder"] = DEFAULT_CONFIG["output_folder"]
    else:
        # Ensure the output folder exists
        Path(output_folder).mkdir(parents=True, exist_ok=True)

    # Validate check_for_updates
    if not isinstance(validated_config.get("check_for_updates"), bool):
        app_logger.warning(
            f"Invalid check_for_updates value: {validated_config.get('check_for_updates')}. Using default: {DEFAULT_CONFIG['check_for_updates']}"
        )
        validated_config["check_for_updates"] = DEFAULT_CONFIG["check_for_updates"]

    return validated_config

def save_config(
        selected_model: str = DEFAULT_CONFIG["selected_model"],
        logging_level: str = DEFAULT_CONFIG["logging_level"],
        verbose: bool = DEFAULT_CONFIG["verbose"],
        output_folder: str = DEFAULT_CONFIG["output_folder"],
        check_for_updates: bool = DEFAULT_CONFIG["check_for_updates"],
) -> None:
    """Save configuration to config.json.

    Args:
        selected_model: The selected Whisper model.
        logging_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        verbose: Whether to enable verbose logging to debug.log.
        output_folder: The output folder for transcriptions.
        check_for_updates: Whether to check for application updates on startup.
    """
    config = {
        "selected_model": selected_model,
        "logging_level": logging_level,
        "verbose": verbose,
        "output_folder": output_folder,
        "check_for_updates": check_for_updates,
    }
    try:
        abs_path = os.path.abspath(CONFIG_FILE)
        app_logger.debug(f"Saving config to: {abs_path}")
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            json.dump(config, file, indent=4)
        update_logging(logging_level, verbose)
        app_logger.debug(f"Successfully saved config to: {abs_path}")
    except Exception as e:
        app_logger.error(f"Failed to save config to {CONFIG_FILE}: {e}")

def update_logging(logging_level: str, verbose: bool) -> None:
    """Update logging configuration based on logging_level and verbose settings.

    Args:
        logging_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        verbose: Whether verbose logging is enabled (writes to debug.log).
    """
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    app_logger.setLevel(level_map[logging_level])

    # Enable/disable debug logger based on verbose
    if verbose and debug_handler not in debug_logger.handlers:
        debug_logger.addHandler(debug_handler)
    elif not verbose and debug_handler in debug_logger.handlers:
        debug_logger.removeHandler(debug_handler)

# Load configuration
try:
    config = load_config()
    app_logger.debug(f"Configuration loaded successfully: {config}")
except Exception as e:
    app_logger.error(f"Critical error loading config: {e}")
    config = DEFAULT_CONFIG

SELECTED_MODEL = config["selected_model"]
"""Name of the currently selected Whisper model."""

LOGGING_LEVEL = config["logging_level"]
"""Logging level for the application."""

VERBOSE = config["verbose"]
"""Whether verbose logging is enabled."""

OUTPUT_FOLDER = config["output_folder"]
"""Directory where transcription output files are saved."""

CHECK_FOR_UPDATES = config["check_for_updates"]
"""Whether to check for application updates on startup."""

# Model-related settings
LOCAL_MODEL_PATH = os.path.join("models", SELECTED_MODEL)
"""Local directory containing the selected Whisper model's files."""

MODEL_FILES = AVAILABLE_MODELS[SELECTED_MODEL]["files"]
"""List of required model files for the selected model."""

MODEL_DOWNLOAD_BASE_URL = AVAILABLE_MODELS[SELECTED_MODEL]["download_url"]
"""Base URL for downloading the selected model's files from Hugging Face."""

# GitHub repository configuration
GITHUB_REPO = "andreipa/police-transcriber"
"""GitHub repository for checking application updates."""

GITHUB_RELEASES_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
"""URL for fetching the latest release information from GitHub."""

# Transcription configuration
SENSITIVE_WORDS_FILE = os.path.join("data", "sensible_words.txt")
"""Path to the file containing sensitive words for detection."""

# Platform-specific settings
SUPPRESS_QT_WARNINGS = False
"""Flag to suppress Qt-related warnings on macOS (disabled for debugging)."""