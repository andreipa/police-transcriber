#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

import logging
import unittest
from unittest.mock import patch, mock_open, MagicMock

# Import the module to test
from core.transcriber import load_sensitive_words, format_time, transcribe_audio


class TestTranscriber(unittest.TestCase):
    def setUp(self):
        # Suppress logging to stderr during tests
        logging.getLogger().handlers = []
        logging.getLogger().setLevel(logging.CRITICAL)

        # Mock configuration variables
        self.patcher_config = patch.multiple(
            'core.transcriber',
            LOCAL_MODEL_PATH='mock_model_path',
            SENSITIVE_WORDS_FILE='mock_sensitive_words.txt',
            OUTPUT_FOLDER='mock_output_folder'
        )
        self.patcher_config.start()

        # Ensure output folder creation is mocked
        self.patcher_os_makedirs = patch('os.makedirs')
        self.patcher_os_makedirs.start()

    def tearDown(self):
        # Stop all patchers
        self.patcher_config.stop()
        self.patcher_os_makedirs.stop()

    def test_load_sensitive_words_success(self):
        # Mock file content
        mock_file_content = "word1\nword2\n\nword3"
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            words = load_sensitive_words()
        self.assertEqual(words, {'word1', 'word2', 'word3'})

    def test_load_sensitive_words_file_not_found(self):
        # Mock file opening to raise FileNotFoundError
        with patch('builtins.open', side_effect=FileNotFoundError):
            words = load_sensitive_words()
        self.assertEqual(words, set())

    def test_format_time(self):
        # Test various time inputs
        test_cases = [
            (0, "00:00:00"),
            (59, "00:00:59"),
            (60, "00:01:00"),
            (3661, "01:01:01"),
            (86399, "23:59:59")
        ]
        for seconds, expected in test_cases:
            with self.subTest(seconds=seconds):
                result = format_time(seconds)
                self.assertEqual(result, expected)

    @patch('core.transcriber.WhisperModel')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.stat')
    def test_transcribe_audio_success_with_sensitive_words(self, mock_stat, mock_file, mock_whisper):
        # Mock sensitive words
        with patch('core.transcriber.load_sensitive_words', return_value={'badword'}):
            # Mock WhisperModel
            mock_model = MagicMock()
            mock_segment1 = MagicMock(text="This is a badword", start=0, end=2)
            mock_segment2 = MagicMock(text="Normal text", start=2, end=4)
            mock_model.transcribe.return_value = ([mock_segment1, mock_segment2], MagicMock(duration=4.0))
            mock_whisper.return_value = mock_model

            # Mock os.stat to indicate non-empty file
            mock_stat.return_value.st_size = 100

            # Mock progress and update callbacks
            progress_callback = MagicMock()
            update_callback = MagicMock()

            # Run transcription
            result = transcribe_audio(
                file_path='test.mp3',
                on_progress=progress_callback,
                on_update_message=update_callback
            )

            # Assertions
            self.assertTrue(result)
            update_callback.assert_any_call("Carregando modelo...")
            update_callback.assert_any_call("Transcrição concluída com sucesso.")
            progress_callback.assert_called_with(100)
            mock_file().write.assert_any_call("[00:00:00 - 00:00:02] This is a badword\n")

    @patch('core.transcriber.WhisperModel')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.stat')
    def test_transcribe_audio_no_sensitive_words(self, mock_stat, mock_file, mock_whisper):
        # Mock sensitive words
        with patch('core.transcriber.load_sensitive_words', return_value={'badword'}):
            # Mock WhisperModel
            mock_model = MagicMock()
            mock_segment = MagicMock(text="Normal text", start=0, end=2)
            mock_model.transcribe.return_value = ([mock_segment], MagicMock(duration=2.0))
            mock_whisper.return_value = mock_model

            # Mock os.stat to indicate empty file
            mock_stat.return_value.st_size = 0

            # Mock progress and update callbacks
            progress_callback = MagicMock()
            update_callback = MagicMock()

            # Run transcription
            result = transcribe_audio(
                file_path='test.mp3',
                on_progress=progress_callback,
                on_update_message=update_callback
            )

            # Assertions
            self.assertTrue(result)
            mock_file().write.assert_called_with("Nenhuma palavra sensível encontrada.")
            update_callback.assert_any_call("Transcrição concluída com sucesso.")
            progress_callback.assert_called_with(100)

    @patch('core.transcriber.WhisperModel')
    @patch('builtins.open', new_callable=mock_open)
    def test_transcribe_audio_cancelled(self, mock_file, mock_whisper):
        # Mock sensitive words
        with patch('core.transcriber.load_sensitive_words', return_value={'badword'}):
            # Mock WhisperModel
            mock_model = MagicMock()
            mock_segment = MagicMock(text="This is a badword", start=0, end=2)
            mock_model.transcribe.return_value = ([mock_segment], MagicMock(duration=2.0))
            mock_whisper.return_value = mock_model

            # Mock stop_flag to return True (cancel)
            stop_flag = MagicMock(return_value=True)
            update_callback = MagicMock()

            # Run transcription
            result = transcribe_audio(
                file_path='test.mp3',
                on_update_message=update_callback,
                stop_flag=stop_flag
            )

            # Assertions
            self.assertEqual(result, "cancelled")
            update_callback.assert_called_with("Transcrição cancelada pelo usuário.")

    @patch('core.transcriber.WhisperModel')
    @patch('builtins.open', new_callable=mock_open)
    def test_transcribe_audio_model_failure(self, mock_file, mock_whisper):
        # Mock sensitive words
        with patch('core.transcriber.load_sensitive_words', return_value={'badword'}):
            # Mock WhisperModel to raise an exception
            mock_whisper.side_effect = Exception("Model loading failed")

            # Mock update callback
            update_callback = MagicMock()

            # Run transcription
            result = transcribe_audio(
                file_path='test.mp3',
                on_update_message=update_callback
            )

            # Assertions
            self.assertFalse(result)
            update_callback.assert_called_with("Erro durante a transcrição.")


if __name__ == '__main__':
    unittest.main()
