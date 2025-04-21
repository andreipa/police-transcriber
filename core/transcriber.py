import os
from datetime import datetime
from faster_whisper import WhisperModel
from config import LOCAL_MODEL_PATH, SENSITIVE_WORDS_FILE, OUTPUT_FOLDER
import logging

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def load_sensitive_words():
    """Load words from the slang list into a set."""
    try:
        with open(SENSITIVE_WORDS_FILE, "r", encoding="utf-8") as f:
            return set(word.strip().lower() for word in f if word.strip())
    except Exception as e:
        logging.error(f"Failed to load sensitive words: {e}")
        return set()

def format_time(seconds):
    """Convert float seconds to HH:MM:SS format."""
    hrs, rem = divmod(int(seconds), 3600)
    mins, secs = divmod(rem, 60)
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"

def transcribe_audio(file_path, on_progress=None, on_update_message=None, stop_flag=None):
    """
    Transcribe a single MP3 file and save the result if any sensitive words are found.
    Includes progress callback, status messages, and cancellation support.
    Now writes segments to file incrementally so data isn't lost if stopped early.
    """
    sensitive_words = load_sensitive_words()
    filename = os.path.basename(file_path)
    name_no_ext = os.path.splitext(filename)[0]
    timestamp = datetime.now().strftime("%d-%m-%Y")
    output_file = os.path.join(OUTPUT_FOLDER, f"{name_no_ext}-{timestamp}.txt")

    try:
        if on_update_message:
            on_update_message("Carregando modelo...")

        model = WhisperModel(
            LOCAL_MODEL_PATH,
            device="cpu",
            compute_type="int8",
            local_files_only=True
        )
        segments, info = model.transcribe(file_path, beam_size=5, word_timestamps=False)
        total_duration = info.duration if info else 1.0

        processed_seconds = 0

        with open(output_file, "w", encoding="utf-8") as out:
            for segment in segments:
                if stop_flag and stop_flag():
                    logging.warning("Transcription stopped by user.")
                    if on_update_message:
                        on_update_message("Transcrição cancelada pelo usuário.")
                    return "cancelled"

                text = segment.text.strip()
                start = segment.start
                end = segment.end

                normalized = text.lower()
                if any(word in normalized for word in sensitive_words):
                    line = f"[{format_time(start)} - {format_time(end)}] {text}"
                    out.write(line + "\n")
                    out.flush()

                processed_seconds = end
                if on_progress and total_duration:
                    percentage = int((processed_seconds / total_duration) * 100)
                    on_progress(min(percentage, 100))

            if os.stat(output_file).st_size == 0:
                out.write("Nenhuma palavra sensível encontrada.")

        if on_update_message:
            on_update_message("Transcrição concluída com sucesso.")

        return True

    except Exception as e:
        logging.error(f"Erro ao transcrever {file_path}: {e}")
        if on_update_message:
            on_update_message("Erro durante a transcrição.")
        return False