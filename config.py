#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

"""Configuration settings for the Police Transcriber application."""
import os

# Application metadata
APP_NAME = "Police Transcriber"
"""Name of the application."""

VERSION = "v0.0.1-alpha"
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
        "requires_token": False
    },
    "small": {
        "files": ["model.bin", "vocabulary.txt", "tokenizer.json", "config.json"],
        "download_url": "https://huggingface.co/guillaumekln/faster-whisper-small/resolve/main",
        "requires_token": False
    },
    "medium": {
        "files": ["model.bin", "vocabulary.txt", "tokenizer.json", "config.json"],
        "download_url": "https://huggingface.co/guillaumekln/faster-whisper-medium/resolve/main",
        "requires_token": False
    },
    "large-v2": {
        "files": ["model.bin", "vocabulary.txt", "tokenizer.json", "config.json"],
        "download_url": "https://huggingface.co/guillaumekln/faster-whisper-medium/resolve/main",
        "requires_token": False
    }
}
"""Dictionary of available Whisper models with their required files, download URLs, and token requirements."""

SELECTED_MODEL = "large-v2"
"""Name of the currently selected Whisper model (e.g., 'base', 'small', 'medium', 'large-v2')."""

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

OUTPUT_FOLDER = "output"
"""Directory where transcription output files are saved."""

LOG_FOLDER = "logs"
"""Directory where application logs are stored."""

# Platform-specific settings
SUPPRESS_QT_WARNINGS = True
"""Flag to suppress Qt-related warnings on macOS."""