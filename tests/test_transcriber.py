#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

# tests/test_transcriber.py

import os
import unittest
from datetime import datetime
from unittest.mock import patch, mock_open, MagicMock

from config import OUTPUT_FOLDER, SENSITIVE_WORDS_FILE, LOCAL_MODEL_PATH, MODEL_FILES
from core.transcriber import (
    ensure_output_directory,
    load_sensitive_words,
    format_time,
    transcribe_audio
)


class TestTranscriber(unittest.TestCase):
    def setUp(self):
        """Set up the test environment."""
        self.output_folder = OUTPUT_FOLDER
        self.sensitive_words_file = SENSITIVE_WORDS_FILE
        self.local_model_path = LOCAL_MODEL_PATH
        self.model_files = MODEL_FILES
        self.test_file_path = "test_audio.mp3"
        self.test_output_file = os.path.join(
            self.output_folder,
            f"test_audio-{datetime.now().strftime('%d-%m-%Y')}.txt"
        )

    @patch("os.makedirs")
    def test_ensure_output_directory_success(self, mock_makedirs):
        """Test ensure_output_directory creates the output directory."""
        ensure_output_directory()
        mock_makedirs.assert_called_once_with(self.output_folder, exist_ok=True)

    @patch("os.makedirs")
    def test_ensure_output_directory_exception(self, mock_makedirs):
        """Test ensure_output_directory handles exceptions."""
        mock_makedirs.side_effect = OSError("Permission denied")
        with self.assertRaises(OSError):
            ensure_output_directory()
        mock_makedirs.assert_called_once_with(self.output_folder, exist_ok=True)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="word1\nword2\n\nword3")
    def test_load_sensitive_words_success(self, mock_open_file, mock_exists):
        """Test load_sensitive_words loads words correctly."""
        mock_exists.return_value = True
        words = load_sensitive_words()
        self.assertEqual(words, {"word1", "word2", "word3"})
        mock_exists.assert_called_once_with(self.sensitive_words_file)
        mock_open_file.assert_called_once_with(self.sensitive_words_file, "r", encoding="utf-8")

    @patch("os.path.exists")
    def test_load_sensitive_words_file_not_found(self, mock_exists):
        """Test load_sensitive_words returns empty set when file is missing."""
        mock_exists.return_value = False
        words = load_sensitive_words()
        self.assertEqual(words, set())
        mock_exists.assert_called_once_with(self.sensitive_words_file)

    @patch("os.path.exists")
    @patch("builtins.open")
    def test_load_sensitive_words_exception(self, mock_open_file, mock_exists):
        """Test load_sensitive_words handles exceptions."""
        mock_exists.return_value = True
        mock_open_file.side_effect = IOError("File read error")
        words = load_sensitive_words()
        self.assertEqual(words, set())
        mock_exists.assert_called_once_with(self.sensitive_words_file)
        mock_open_file.assert_called_once_with(self.sensitive_words_file, "r", encoding="utf-8")

    def test_format_time(self):
        """Test format_time converts seconds to HH:MM:SS format."""
        self.assertEqual(format_time(3661), "01:01:01")  # 1 hour, 1 minute, 1 second
        self.assertEqual(format_time(45), "00:00:45")  # 45 seconds
        self.assertEqual(format_time(7200), "02:00:00")  # 2 hours

    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    @patch("core.transcriber.load_sensitive_words")
    @patch("faster_whisper.WhisperModel")
    def test_transcribe_audio_success_sensitive_words(
            self, mock_whisper, mock_load_words, mock_open_file, mock_makedirs, mock_exists
    ):
        """Test transcribe_audio with sensitive words detected."""
        # Mock file system
        mock_exists.side_effect = [True] + [True] * len(self.model_files)  # Input file and model files exist
        mock_makedirs.return_value = None

        # Mock sensitive words
        mock_load_words.return_value = {"sensitive"}

        # Mock Whisper model
        mock_segment = MagicMock()
        mock_segment.text = "This is a sensitive text"
        mock_segment.start = 0.0
        mock_segment.end = 5.0
        mock_info = MagicMock()
        mock_info.duration = 10.0
        mock_whisper.return_value.transcribe.return_value = ([mock_segment], mock_info)

        # Callbacks
        progress_callback = MagicMock()
        update_message_callback = MagicMock()
        stop_flag = MagicMock(return_value=False)

        result = transcribe_audio(
            self.test_file_path,
            on_progress=progress_callback,
            on_update_message=update_message_callback,
            stop_flag=stop_flag
        )

        self.assertTrue(result)
        mock_makedirs.assert_called_once_with(self.output_folder, exist_ok=True)
        mock_load_words.assert_called_once()
        mock_exists.assert_any_call(self.test_file_path)
        for file_name in self.model_files:
            mock_exists.assert_any_call(os.path.join(self.local_model_path, file_name))
        update_message_callback.assert_any_call("Carregando modelo...")
        update_message_callback.assert_any_call("Transcrição concluída com sucesso")
        progress_callback.assert_called_with(50)  # 5.0/10.0 * 100
        mock_open_file.assert_called_with(self.test_output_file, "w", encoding="utf-8")
        mock_open_file().write.assert_called_with("[00:00:00 - 00:00:05] This is a sensitive text\n")

    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    @patch("core.transcriber.load_sensitive_words")
    @patch("faster_whisper.WhisperModel")
    def test_transcribe_audio_no_sensitive_words(
            self, mock_whisper, mock_load_words, mock_open_file, mock_makedirs, mock_exists
    ):
        """Test transcribe_audio with no sensitive words detected."""
        mock_exists.side_effect = [True] + [True] * len(self.model_files)
        mock_makedirs.return_value = None
        mock_load_words.return_value = {"sensitive"}
        mock_segment = MagicMock()
        mock_segment.text = "This is a safe text"
        mock_segment.start = 0.0
        mock_segment.end = 5.0
        mock_info = MagicMock()
        mock_info.duration = 10.0
        mock_whisper.return_value.transcribe.return_value = ([mock_segment], mock_info)

        result = transcribe_audio(self.test_file_path)
        self.assertTrue(result)
        mock_open_file.assert_called_with(self.test_output_file, "w", encoding="utf-8")
        mock_open_file().write.assert_called_with("Nenhuma palavra sensível encontrada.")

    @patch("os.path.exists")
    def test_transcribe_audio_file_not_found(self, mock_exists):
        """Test transcribe_audio handles missing input file."""
        mock_exists.return_value = False
        update_message_callback = MagicMock()
        result = transcribe_audio(self.test_file_path, on_update_message=update_message_callback)
        self.assertFalse(result)
        mock_exists.assert_called_once_with(self.test_file_path)
        update_message_callback.assert_called_once_with(f"Arquivo não encontrado: {self.test_file_path}")

    @patch("os.path.exists")
    def test_transcribe_audio_invalid_format(self, mock_exists):
        """Test transcribe_audio handles invalid file format."""
        mock_exists.return_value = True
        update_message_callback = MagicMock()
        result = transcribe_audio("test_audio.wav", on_update_message=update_message_callback)
        self.assertFalse(result)
        mock_exists.assert_called_once_with("test_audio.wav")
        update_message_callback.assert_called_once_with("Formato de arquivo inválido. Use MP3.")

    @patch("os.path.exists")
    def test_transcribe_audio_missing_model_file(self, mock_exists):
        """Test transcribe_audio handles missing model file."""
        mock_exists.side_effect = [True, False] + [True] * (len(self.model_files) - 1)
        update_message_callback = MagicMock()
        result = transcribe_audio(self.test_file_path, on_update_message=update_message_callback)
        self.assertFalse(result)
        mock_exists.assert_any_call(self.test_file_path)
        mock_exists.assert_any_call(os.path.join(self.local_model_path, self.model_files[0]))
        update_message_callback.assert_called_once_with(f"Arquivo de modelo ausente: {os.path.join(self.local_model_path, self.model_files[0])}")

    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    @patch("core.transcriber.load_sensitive_words")
    @patch("faster_whisper.WhisperModel")
    def test_transcribe_audio_cancelled(
            self, mock_whisper, mock_load_words, mock_open_file, mock_makedirs, mock_exists
    ):
        """Test transcribe_audio handles cancellation."""
        mock_exists.side_effect = [True] + [True] * len(self.model_files)
        mock_makedirs.return_value = None
        mock_load_words.return_value = {"sensitive"}
        mock_segment = MagicMock()
        mock_segment.text = "This is a sensitive text"
        mock_segment.start = 0.0
        mock_segment.end = 5.0
        mock_info = MagicMock()
        mock_info.duration = 10.0
        mock_whisper.return_value.transcribe.return_value = ([mock_segment], mock_info)
        stop_flag = MagicMock(return_value=True)
        update_message_callback = MagicMock()

        result = transcribe_audio(
            self.test_file_path,
            stop_flag=stop_flag,
            on_update_message=update_message_callback
        )

        self.assertEqual(result, "cancelled")
        update_message_callback.assert_any_call("Transcrição cancelada pelo usuário")

    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("faster_whisper.WhisperModel")
    def test_transcribe_audio_exception(
            self, mock_whisper, mock_makedirs, mock_exists
    ):
        """Test transcribe_audio handles exceptions."""
        mock_exists.side_effect = [True] + [True] * len(self.model_files)
        mock_makedirs.return_value = None
        mock_whisper.side_effect = Exception("Model error")
        update_message_callback = MagicMock()

        result = transcribe_audio(self.test_file_path, on_update_message=update_message_callback)
        self.assertFalse(result)
        update_message_callback.assert_any_call("Erro durante a transcrição: Model error")


if __name__ == "__main__":
    unittest.main()