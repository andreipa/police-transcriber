#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

import os
import unittest
from unittest.mock import patch, MagicMock, mock_open

import requests

from config import MODEL_FILES, LOCAL_MODEL_PATH, MODEL_DOWNLOAD_BASE_URL, SELECTED_MODEL
from core.model_downloader import (
    is_model_fully_downloaded,
    download_model_file,
    download_model,
    ensure_model_available
)


class TestModelDownloader(unittest.TestCase):
    def setUp(self):
        """Set up the test environment."""
        self.model_files = MODEL_FILES
        self.local_model_path = LOCAL_MODEL_PATH
        self.download_url = MODEL_DOWNLOAD_BASE_URL
        self.selected_model = SELECTED_MODEL
        self.test_file = "test_model.bin"
        self.test_url = f"{self.download_url}/{self.test_file}"
        self.test_dest_path = os.path.join(self.local_model_path, self.test_file)
        self.total_size = 1000
        self.file_size = 500

    @patch("os.path.exists")
    def test_is_model_fully_downloaded_all_files_present(self, mock_exists):
        """Test is_model_fully_downloaded when all model files exist."""
        mock_exists.return_value = True
        result = is_model_fully_downloaded()
        self.assertTrue(result)
        self.assertEqual(mock_exists.call_count, len(self.model_files))
        for file_name in self.model_files:
            mock_exists.assert_any_call(os.path.join(self.local_model_path, file_name))

    @patch("os.path.exists")
    def test_is_model_fully_downloaded_missing_file(self, mock_exists):
        """Test is_model_fully_downloaded when a model file is missing."""
        mock_exists.side_effect = [True, False] + [True] * (len(self.model_files) - 2)
        result = is_model_fully_downloaded()
        self.assertFalse(result)
        self.assertEqual(mock_exists.call_count, 2)  # Stops at first missing file

    @patch("os.path.exists")
    def test_is_model_fully_downloaded_exception(self, mock_exists):
        """Test is_model_fully_downloaded handles exceptions."""
        mock_exists.side_effect = OSError("Permission denied")
        result = is_model_fully_downloaded()
        self.assertFalse(result)
        mock_exists.assert_called_once()

    @patch("requests.get")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_model_file_success(self, mock_file_open, mock_get):
        """Test download_model_file downloads a file successfully."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]
        mock_get.return_value = mock_response

        progress_callback = MagicMock()
        success, downloaded_total = download_model_file(
            file_name=self.test_file,
            url=self.test_url,
            dest_path=self.test_dest_path,
            file_size=12,  # chunk1 (6 bytes) + chunk2 (6 bytes)
            downloaded_total=0,
            total_size=self.total_size,
            progress_callback=progress_callback
        )

        self.assertTrue(success)
        self.assertEqual(downloaded_total, 12)
        mock_get.assert_called_once_with(self.test_url, headers={}, stream=True, timeout=30)
        mock_file_open.assert_called_once_with(self.test_dest_path, "wb")
        mock_file_open().write.assert_any_call(b"chunk1")
        mock_file_open().write.assert_any_call(b"chunk2")
        progress_callback.assert_called_with(1)  # 12/1000 * 100 = 1.2, min(1, 100)

    @patch("requests.get")
    def test_download_model_file_http_error(self, mock_get):
        """Test download_model_file handles HTTP errors."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        success, downloaded_total = download_model_file(
            file_name=self.test_file,
            url=self.test_url,
            dest_path=self.test_dest_path,
            file_size=self.file_size,
            downloaded_total=0,
            total_size=self.total_size
        )

        self.assertFalse(success)
        self.assertEqual(downloaded_total, 0)
        mock_get.assert_called_once_with(self.test_url, headers={}, stream=True, timeout=30)

    @patch("requests.get")
    def test_download_model_file_request_exception(self, mock_get):
        """Test download_model_file handles request exceptions."""
        mock_get.side_effect = requests.RequestException("Network error")

        try:
            success, downloaded_total = download_model_file(
                file_name=self.test_file,
                url=self.test_url,
                dest_path=self.test_dest_path,
                file_size=self.file_size,
                downloaded_total=0,
                total_size=self.total_size
            )
        except requests.RequestException:
            self.fail("RequestException was not handled by download_model_file")

        self.assertFalse(success)
        self.assertEqual(downloaded_total, 0)
        mock_get.assert_called_once_with(self.test_url, headers={}, stream=True, timeout=30)
        mock_get.reset_mock()  # Clean up mock

    @patch("os.makedirs")
    @patch("os.path.exists")
    @patch("requests.head")
    def test_download_model_all_files_exist(self, mock_head, mock_exists, mock_makedirs):
        """Test download_model when all files already exist."""
        mock_exists.return_value = True
        result = download_model()
        self.assertTrue(result)
        mock_makedirs.assert_called_once_with(self.local_model_path, exist_ok=True)
        mock_exists.assert_called()
        mock_head.assert_not_called()

    @patch("os.makedirs")
    @patch("os.path.exists")
    @patch("requests.head")
    @patch("core.model_downloader.download_model_file")
    def test_download_model_download_success(self, mock_download_file, mock_head, mock_exists, mock_makedirs):
        """Test download_model downloads missing files successfully."""
        # Ensure side_effect covers all MODEL_FILES checks
        mock_exists.side_effect = [False] + [True] * (len(self.model_files) - 1)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-length": "500"}
        mock_head.return_value = mock_response
        mock_download_file.return_value = (True, 500)

        progress_callback = MagicMock()
        result = download_model(progress_callback=progress_callback)

        self.assertTrue(result)
        mock_makedirs.assert_called_once_with(self.local_model_path, exist_ok=True)
        mock_head.assert_called_once_with(
            f"{self.download_url}/{self.model_files[0]}", headers={}, allow_redirects=True, timeout=10
        )
        mock_download_file.assert_called_once_with(
            file_name=self.model_files[0],
            url=f"{self.download_url}/{self.model_files[0]}",
            dest_path=os.path.join(self.local_model_path, self.model_files[0]),
            file_size=500,
            downloaded_total=0,
            total_size=500,
            progress_callback=progress_callback
        )
        progress_callback.assert_called()
        # Reset mocks to prevent interference
        mock_head.reset_mock()
        mock_download_file.reset_mock()
        mock_exists.reset_mock()
        mock_makedirs.reset_mock()

    @patch("os.makedirs")
    @patch("os.path.exists")
    @patch("requests.head")
    def test_download_model_head_failure(self, mock_head, mock_exists, mock_makedirs):
        """Test download_model handles HEAD request failure."""
        mock_exists.return_value = False
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_head.return_value = mock_response

        result = download_model()
        self.assertFalse(result)
        mock_makedirs.assert_called_once_with(self.local_model_path, exist_ok=True)
        mock_head.assert_called_once()

    @patch("core.model_downloader.is_model_fully_downloaded")
    @patch("core.model_downloader.download_model")
    def test_ensure_model_available_already_downloaded(self, mock_download, mock_is_downloaded):
        """Test ensure_model_available when model is already downloaded."""
        mock_is_downloaded.return_value = True
        status_callback = MagicMock()
        progress_callback = MagicMock()

        result = ensure_model_available(on_status=status_callback, on_progress=progress_callback)
        self.assertTrue(result)
        mock_is_downloaded.assert_called_once()
        mock_download.assert_not_called()
        status_callback.assert_not_called()
        progress_callback.assert_not_called()

    @patch("core.model_downloader.is_model_fully_downloaded")
    @patch("core.model_downloader.download_model")
    def test_ensure_model_available_download_success(self, mock_download, mock_is_downloaded):
        """Test ensure_model_available downloads model successfully."""
        mock_is_downloaded.return_value = False
        mock_download.return_value = True
        status_callback = MagicMock()
        progress_callback = MagicMock()

        result = ensure_model_available(on_status=status_callback, on_progress=progress_callback)
        self.assertTrue(result)
        mock_is_downloaded.assert_called_once()
        mock_download.assert_called_once_with(progress_callback=progress_callback)
        status_callback.assert_called_with(f"Baixando modelo {self.selected_model}...")

    @patch("core.model_downloader.is_model_fully_downloaded")
    @patch("core.model_downloader.download_model")
    def test_ensure_model_available_download_failure(self, mock_download, mock_is_downloaded):
        """Test ensure_model_available handles download failure."""
        mock_is_downloaded.return_value = False
        mock_download.return_value = False
        status_callback = MagicMock()
        progress_callback = MagicMock()

        result = ensure_model_available(on_status=status_callback, on_progress=progress_callback)
        self.assertFalse(result)
        mock_is_downloaded.assert_called_once()
        mock_download.assert_called_once_with(progress_callback=progress_callback)
        status_callback.assert_called_with(f"Baixando modelo {self.selected_model}...")

    @patch("core.model_downloader.is_model_fully_downloaded")
    def test_ensure_model_available_exception(self, mock_is_downloaded):
        """Test ensure_model_available handles exceptions."""
        mock_is_downloaded.side_effect = Exception("Unexpected error")
        result = ensure_model_available()
        self.assertFalse(result)
        mock_is_downloaded.assert_called_once()


if __name__ == "__main__":
    unittest.main()
