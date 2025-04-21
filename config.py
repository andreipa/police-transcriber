# config.py

import os

APP_NAME = "Police Transcriber"
VERSION = "v1.0.0-alpha"
SLOGAN_PT = "Detecção Automática de Conversas Ilícitas com IA"
SLOGAN_EN = "Automatic Detection of Illicit Conversations with AI"

# Whisper model settings
MODEL_NAME = "base"
MODEL_FILENAME = "model.bin"

LOCAL_MODEL_PATH = os.path.join("models", MODEL_NAME)
MODEL_DOWNLOAD_URL = "https://huggingface.co/TheBloke/faster-whisper-large-v3-GGUF/resolve/main/model.bin"

# Transcription settings
SENSITIVE_WORDS_FILE = os.path.join("data", "sensible_words.txt")
OUTPUT_FOLDER = "output"
LOG_FOLDER = "logs"

# MacOS debug suppression
SUPPRESS_QT_WARNINGS = True