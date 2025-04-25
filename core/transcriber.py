#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

import logging
import os
from datetime import datetime

from faster_whisper import WhisperModel

from config import LOCAL_MODEL_PATH, MODEL_FILES, SENSITIVE_WORDS_FILE, OUTPUT_FOLDER


def ensure_output_directory() -> None:
    """Create the output directory if it does not exist."""
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def load_sensitive_words() -> set[str]:
    """Load sensitive words from a file into a set for efficient lookup.

    Returns:
        A set of lowercase sensitive words, or an empty set if loading fails.
    """
    try:
        with open(SENSITIVE_WORDS_FILE, "r", encoding="utf-8") as file:
            return {word.strip().lower() for word in file if word.strip()}
    except Exception as e:
        logging.error(f"Failed to load sensitive words: {e}")
        return set()

def format_time(seconds: float) -> str:
    """Convert seconds to a formatted HH:MM:SS string.

    Args:
        seconds: The time in seconds as a float.

    Returns:
        A string in the format HH:MM:SS.
    """
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def transcribe_audio(
        file_path: str,
        on_progress=None,
        on_update_message=None,
        stop_flag=None
) -> str | bool:
    """Transcribe an MP3 file and save segments containing sensitive words.

    Writes transcription segments incrementally to a text file, supporting progress updates,
    status messages, and cancellation. If no sensitive words are found, a message is written
    to the output file.

    Args:
        file_path: Path to the MP3 file to transcribe.
        on_progress: Optional callback to report transcription progress (percentage).
        on_update_message: Optional callback to update UI with status messages.
        stop_flag: Optional function to check for transcription cancellation.

    Returns:
        True if transcription completes successfully, "cancelled" if stopped by the user,
        or False if an error occurs.
    """
    ensure_output_directory()
    sensitive_words = load_sensitive_words()
    filename = os.path.basename(file_path)
    name_no_ext = os.path.splitext(filename)[0]
    timestamp = datetime.now().strftime("%d-%m-%Y")
    output_file = os.path.join(OUTPUT_FOLDER, f"{name_no_ext}-{timestamp}.txt")

    try:
        # Validate input file
        if not os.path.exists(file_path):
            logging.error(f"Input file does not exist: {file_path}")
            if on_update_message:
                on_update_message(f"Arquivo não encontrado: {file_path}")
            return False
        if not file_path.lower().endswith('.mp3'):
            logging.error(f"Invalid file format, expected MP3: {file_path}")
            if on_update_message:
                on_update_message("Formato de arquivo inválido. Use MP3.")
            return False

        # Validate model files
        for file_name in MODEL_FILES:
            model_file_path = os.path.join(LOCAL_MODEL_PATH, file_name)
            if not os.path.exists(model_file_path):
                logging.error(f"Model file missing: {model_file_path}")
                if on_update_message:
                    on_update_message(f"Arquivo de modelo ausente: {model_file_path}")
                return False

        if on_update_message:
            on_update_message("Carregando modelo...")

        logging.debug(f"Loading WhisperModel from {LOCAL_MODEL_PATH}")
        model = WhisperModel(
            model_size_or_path=LOCAL_MODEL_PATH,
            device="cpu",
            compute_type="int8",
            local_files_only=True
        )
        logging.debug(f"Transcribing file: {file_path}")
        segments, info = model.transcribe(file_path, beam_size=5, word_timestamps=False)
        total_duration = info.duration if info else 1.0

        processed_seconds = 0

        with open(output_file, "w", encoding="utf-8") as file:
            for segment in segments:
                if stop_flag and stop_flag():
                    logging.warning("Transcription stopped by user")
                    if on_update_message:
                        on_update_message("Transcrição cancelada pelo usuário")
                    return "cancelled"

                text = segment.text.strip()
                start = segment.start
                end = segment.end

                normalized_text = text.lower()
                if any(word in normalized_text for word in sensitive_words):
                    line = f"[{format_time(start)} - {format_time(end)}] {text}"
                    file.write(line + "\n")
                    file.flush()

                processed_seconds = end
                if on_progress and total_duration:
                    percentage = int((processed_seconds / total_duration) * 100)
                    on_progress(min(percentage, 100))

            if os.stat(output_file).st_size == 0:
                file.write("Nenhuma palavra sensível encontrada.")

        if on_update_message:
            on_update_message("Transcrição concluída com sucesso")

        logging.info(f"Transcription completed successfully for {file_path}")
        return True
    except Exception as e:
        logging.error(f"Error transcribing {file_path}: {e}", exc_info=True)
        if on_update_message:
            on_update_message(f"Erro durante a transcrição: {str(e)}")
        return False