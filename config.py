#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

import os

# Application metadata
APP_NAME = "Police Transcriber"
"""Name of the application."""

VERSION = "v1.0.0-alpha"
"""Current version of the application."""

SLOGAN_PT = "Detecção Automática de Conversas Ilícitas com IA"
"""Portuguese slogan for the application."""

SLOGAN_EN = "Automatic Detection of Illicit Conversations with AI"
"""English slogan for the application."""

# Whisper model configuration
MODEL_NAME = "base"
"""Name of the Whisper model used for transcription."""

MODEL_FILENAME = "model.bin"
"""Filename of the Whisper model binary."""

LOCAL_MODEL_PATH = os.path.join("models", MODEL_NAME)
"""Local path where the Whisper model is stored."""

MODEL_DOWNLOAD_URL = "https://huggingface.co/TheBloke/faster-whisper-large-v3-GGUF/resolve/main/model.bin"
"""URL for downloading the Whisper model."""

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
