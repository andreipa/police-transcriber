#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

import os

# Application metadata
APP_NAME = "Police Transcriber"
VERSION = "v1.0.0-alpha"

SLOGAN_PT = "Detecção Automática de Conversas Ilícitas com IA"
SLOGAN_EN = "Automatic Detection of Illicit Conversations with AI"

# Whisper model configuration
MODEL_NAME = "large-v3"
"""Display name or identifier of the local Whisper model."""

LOCAL_MODEL_PATH = os.path.join("models", MODEL_NAME)
"""Absolute or relative path to the directory containing the CTranslate2-converted Whisper model."""

# Transcription configuration
SENSITIVE_WORDS_FILE = os.path.join("data", "sensible_words.txt")
OUTPUT_FOLDER = "output"
LOG_FOLDER = "logs"

# Platform-specific settings
SUPPRESS_QT_WARNINGS = True