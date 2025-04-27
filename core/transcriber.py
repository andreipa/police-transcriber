#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

"""Module for transcribing MP3 files and detecting sensitive words in the Police Transcriber application."""

import os
from datetime import datetime
from typing import Callable, Optional, Set

from faster_whisper import WhisperModel

from config import (
    LOCAL_MODEL_PATH,
    MODEL_FILES,
    SENSITIVE_WORDS_FILE,
    OUTPUT_FOLDER,
    app_logger,
    debug_logger,
)


def ensure_output_directory() -> None:
    """Create the output directory if it does not exist."""
    try:
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        app_logger.debug(f"Ensured output directory exists: {OUTPUT_FOLDER}")
        debug_logger.debug(f"Created or verified output directory: {OUTPUT_FOLDER}")
    except Exception as e:
        app_logger.error(f"Failed to create output directory {OUTPUT_FOLDER}: {e}")
        debug_logger.debug(f"Output directory creation error: {str(e)}")
        raise


def load_sensitive_words() -> Set[str]:
    """Load sensitive words from a file into a set for efficient lookup.

    Returns:
        A set of lowercase sensitive words, or an empty set if loading fails.
    """
    try:
        if not os.path.exists(SENSITIVE_WORDS_FILE):
            app_logger.warning(f"Sensitive words file not found: {SENSITIVE_WORDS_FILE}")
            debug_logger.debug(f"Missing sensitive words file: {SENSITIVE_WORDS_FILE}")
            return set()

        with open(SENSITIVE_WORDS_FILE, "r", encoding="utf-8") as file:
            words = {word.strip().lower() for word in file if word.strip()}
        app_logger.debug(f"Loaded {len(words)} sensitive words from {SENSITIVE_WORDS_FILE}")
        debug_logger.debug(f"Sensitive words loaded: {words}")
        return words
    except Exception as e:
        app_logger.error(f"Failed to load sensitive words from {SENSITIVE_WORDS_FILE}: {e}")
        debug_logger.debug(f"Sensitive words load error: {str(e)}")
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
    formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    debug_logger.debug(f"Formatted time: {seconds} seconds -> {formatted}")
    return formatted


def transcribe_audio(
        file_path: str,
        on_progress: Optional[Callable[[int], None]] = None,
        on_update_message: Optional[Callable[[str], None]] = None,
        stop_flag: Optional[Callable[[], bool]] = None,
) -> str | bool:
    """Transcribe an MP3 file and save segments containing sensitive words.

    Writes transcription segments incrementally to a text file, supporting progress updates,
    status messages, and cancellation. If no sensitive words are found, a message is written
    to the output file.

    Args:
        file_path: Path to the MP3 file to transcribe.
        on_progress: Optional callback to report transcription progress (0-100).
        on_update_message: Optional callback to update UI with status messages.
        stop_flag: Optional function to check for transcription cancellation.

    Returns:
        True if transcription completes successfully, "cancelled" if stopped by the user,
        or False if an error occurs.
    """
    try:
        app_logger.info(f"Starting transcription for {file_path}")
        debug_logger.debug(f"Transcription initiated: file={file_path}")

        ensure_output_directory()
        sensitive_words = load_sensitive_words()
        debug_logger.debug(f"Sensitive words count: {len(sensitive_words)}")

        filename = os.path.basename(file_path)
        name_no_ext = os.path.splitext(filename)[0]
        timestamp = datetime.now().strftime("%d-%m-%Y")
        output_file = os.path.join(OUTPUT_FOLDER, f"{name_no_ext}-{timestamp}.txt")
        app_logger.debug(f"Output file: {output_file}")
        debug_logger.debug(f"Set output file path: {output_file}")

        # Validate input file
        if not os.path.exists(file_path):
            app_logger.error(f"Input file does not exist: {file_path}")
            debug_logger.debug(f"File not found: {file_path}")
            if on_update_message:
                on_update_message(f"Arquivo não encontrado: {file_path}")
            return False
        if not file_path.lower().endswith(".mp3"):
            app_logger.error(f"Invalid file format, expected MP3: {file_path}")
            debug_logger.debug(f"Invalid file extension: {file_path}")
            if on_update_message:
                on_update_message("Formato de arquivo inválido. Use MP3.")
            return False

        # Validate model files
        for file_name in MODEL_FILES:
            model_file_path = os.path.join(LOCAL_MODEL_PATH, file_name)
            if not os.path.exists(model_file_path):
                app_logger.error(f"Model file missing: {model_file_path}")
                debug_logger.debug(f"Missing model file: {model_file_path}")
                if on_update_message:
                    on_update_message(f"Arquivo de modelo ausente: {model_file_path}")
                return False

        if on_update_message:
            on_update_message("Carregando modelo...")
            debug_logger.debug("Set status message: Carregando modelo...")

        app_logger.debug(f"Loading WhisperModel from {LOCAL_MODEL_PATH}")
        debug_logger.debug(f"Initializing WhisperModel with device=cpu, compute_type=int8")
        model = WhisperModel(
            model_size_or_path=LOCAL_MODEL_PATH,
            device="cpu",
            compute_type="int8",
            local_files_only=True,
        )
        app_logger.debug(f"Transcribing file: {file_path}")
        debug_logger.debug(f"Starting transcription with beam_size=5, word_timestamps=False")

        segments, info = model.transcribe(file_path, beam_size=5, word_timestamps=False)
        total_duration = info.duration if info else 1.0
        debug_logger.debug(f"Transcription info: duration={total_duration} seconds")

        processed_seconds = 0
        sensitive_segments = 0

        with open(output_file, "w", encoding="utf-8") as file:
            for segment in segments:
                if stop_flag and stop_flag():
                    app_logger.warning(f"Transcription cancelled by user for {file_path}")
                    debug_logger.debug("Transcription stopped by stop_flag")
                    if on_update_message:
                        on_update_message("Transcrição cancelada pelo usuário")
                    return "cancelled"

                text = segment.text.strip()
                start = segment.start
                end = segment.end
                debug_logger.debug(f"Processed segment: start={start}, end={end}, text={text}")

                normalized_text = text.lower()
                if any(word in normalized_text for word in sensitive_words):
                    line = f"[{format_time(start)} - {format_time(end)}] {text}"
                    file.write(line + "\n")
                    file.flush()
                    sensitive_segments += 1
                    debug_logger.debug(f"Wrote sensitive segment: {line}")

                processed_seconds = end
                if on_progress and total_duration:
                    percentage = min(int((processed_seconds / total_duration) * 100), 100)
                    on_progress(percentage)
                    debug_logger.debug(f"Transcription progress: {percentage}%")

            if sensitive_segments == 0:
                file.write("Nenhuma palavra sensível encontrada.")
                debug_logger.debug("No sensitive words found, wrote default message")

        if on_update_message:
            on_update_message("Transcrição concluída com sucesso")
            debug_logger.debug("Set status message: Transcrição concluída com sucesso")

        app_logger.info(f"Transcription completed successfully for {file_path}, {sensitive_segments} sensitive segments")
        debug_logger.debug(f"Transcription finished: {sensitive_segments} segments written to {output_file}")
        return True
    except Exception as e:
        app_logger.error(f"Error transcribing {file_path}: {e}", exc_info=True)
        debug_logger.debug(f"Transcription error: {str(e)}")
        if on_update_message:
            on_update_message(f"Erro durante a transcrição: {str(e)}")
        return False