#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

"""Module for downloading and verifying Whisper model files for the Police Transcriber application."""

import os
from typing import Callable, Optional

import requests

from config import (
    LOCAL_MODEL_PATH,
    MODEL_FILES,
    MODEL_DOWNLOAD_BASE_URL,
    SELECTED_MODEL,
    app_logger,
    debug_logger,
)


def is_model_fully_downloaded() -> bool:
    """Check if all required model files are present in the model directory.

    Returns:
        True if all model files exist, False otherwise.
    """
    try:
        app_logger.debug(f"Verifying model files for {SELECTED_MODEL} in {LOCAL_MODEL_PATH}")
        debug_logger.debug(f"Checking model files: {MODEL_FILES}")

        for file_name in MODEL_FILES:
            file_path = os.path.join(LOCAL_MODEL_PATH, file_name)
            if not os.path.exists(file_path):
                app_logger.warning(f"Missing model file: {file_path}")
                debug_logger.debug(f"File not found: {file_path}")
                return False

        app_logger.info(f"All model files for {SELECTED_MODEL} verified")
        debug_logger.debug("Model verification successful")
        return True
    except Exception as e:
        app_logger.error(f"Failed to check model status: {e}")
        debug_logger.debug(f"Model verification error: {str(e)}")
        return False


def download_model_file(
        file_name: str,
        url: str,
        dest_path: str,
        file_size: int,
        downloaded_total: int,
        total_size: int,
        progress_callback: Optional[Callable[[int], None]] = None,
) -> tuple[bool, int]:
    """Download a single model file with progress reporting.

    Args:
        file_name: Name of the file to download.
        url: URL to download the file from.
        dest_path: Destination path for the downloaded file.
        file_size: Expected size of the file in bytes.
        downloaded_total: Cumulative bytes downloaded across all files.
        total_size: Total size of all files to download.
        progress_callback: Optional function to report cumulative download progress (0-100).

    Returns:
        Tuple of (success: bool, updated_downloaded_total: int).
    """
    try:
        app_logger.info(f"Downloading {file_name} from {url}")
        debug_logger.debug(f"Starting download: {file_name}, destination: {dest_path}")

        headers = {}
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        if response.status_code != 200:
            app_logger.error(f"Download failed for {url}: HTTP {response.status_code}")
            debug_logger.debug(f"HTTP error {response.status_code} for {url}")
            return False, downloaded_total

        downloaded_file = 0
        with open(dest_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded_file += len(chunk)
                    downloaded_total += len(chunk)
                    if progress_callback and total_size:
                        progress = min(int((downloaded_total / total_size) * 100), 100)
                        progress_callback(progress)
                        debug_logger.debug(f"Download progress for {file_name}: {downloaded_file}/{file_size} bytes")

        app_logger.debug(f"Successfully downloaded {file_name}")
        debug_logger.debug(f"Completed download: {file_name}, size: {downloaded_file} bytes")
        return True, downloaded_total
    except requests.RequestException as e:
        app_logger.error(f"Download failed for {file_name}: {e}")
        debug_logger.debug(f"Download error for {file_name}: {str(e)}")
        return False, downloaded_total


def download_model(progress_callback: Optional[Callable[[int], None]] = None) -> bool:
    """Download all required model files from the Hugging Face repository.

    Args:
        progress_callback: Optional function to report cumulative download progress (0-100).

    Returns:
        True if all files were downloaded successfully, False otherwise.
    """
    try:
        os.makedirs(LOCAL_MODEL_PATH, exist_ok=True)
        app_logger.info(f"Preparing to download model {SELECTED_MODEL} to {LOCAL_MODEL_PATH}")
        debug_logger.debug(f"Creating directory if needed: {LOCAL_MODEL_PATH}")

        headers = {}
        total_sizes = []
        files_to_download = []

        # Check which files need downloading
        for file_name in MODEL_FILES:
            dest_path = os.path.join(LOCAL_MODEL_PATH, file_name)
            if os.path.exists(dest_path):
                app_logger.debug(f"Skipping {file_name}: already exists")
                debug_logger.debug(f"Valid file found: {file_name}")
                continue

            url = f"{MODEL_DOWNLOAD_BASE_URL}/{file_name}"
            response = requests.head(url, headers=headers, allow_redirects=True, timeout=10)
            if response.status_code != 200:
                app_logger.error(f"Failed to access {url}: HTTP {response.status_code}")
                debug_logger.debug(f"HEAD request failed for {url}: HTTP {response.status_code}")
                return False
            size = int(response.headers.get("content-length", 0))
            total_sizes.append(size if size > 0 else 1)  # Avoid division by zero
            files_to_download.append((file_name, url, dest_path, size))

        if not files_to_download:
            app_logger.info(f"All model files for {SELECTED_MODEL} already downloaded")
            debug_logger.debug("No files need downloading")
            return True

        total_size = sum(size for _, _, _, size in files_to_download)
        downloaded_total = 0

        for file_name, url, dest_path, file_size in files_to_download:
            success, downloaded_total = download_model_file(
                file_name, url, dest_path, file_size, downloaded_total, total_size, progress_callback
            )
            if not success:
                app_logger.error(f"Failed to download model {SELECTED_MODEL} due to error with {file_name}")
                return False

        app_logger.info(f"All model files for {SELECTED_MODEL} downloaded successfully")
        debug_logger.debug(f"Completed download of {len(files_to_download)} files for {SELECTED_MODEL}")
        return True
    except Exception as e:
        app_logger.error(f"Model download failed: {e}")
        debug_logger.debug(f"Model download error: {str(e)}")
        return False


# In model_downloader.py, modify ensure_model_available
def ensure_model_available(
        on_status: Optional[Callable[[str], None]] = None,
        on_progress: Optional[Callable[[int], None]] = None,
) -> bool:
    """Ensure all required model files are available, downloading them if necessary.

    Args:
        on_status: Optional callback to update status messages (e.g., for SplashScreen).
        on_progress: Optional callback to report download progress (0-100).

    Returns:
        True if the model is available, False if download fails.
    """
    try:
        app_logger.info(f"Ensuring model {SELECTED_MODEL} is available")
        debug_logger.debug(f"Checking model availability for {SELECTED_MODEL}")

        if is_model_fully_downloaded():
            app_logger.info(f"Model {SELECTED_MODEL} already available and verified")
            debug_logger.debug("Model files verified, no download needed")
            return True

        # Optional: Uncomment for confirmation dialog
        # if SELECTED_MODEL == "large-v2":
        #     from PyQt5.QtWidgets import QMessageBox
        #     reply = QMessageBox.question(
        #         None, "Confirmar Download",
        #         "O modelo large-v2 requer 3.09 GB. Deseja baixar agora?",
        #         QMessageBox.Yes | QMessageBox.No
        #     )
        #     if reply == QMessageBox.No:
        #         app_logger.info("User cancelled large-v2 model download")
        #         debug_logger.debug("Download cancelled by user")
        #         return False

        if on_status:
            on_status(f"Baixando modelo {SELECTED_MODEL}...")
            debug_logger.debug(f"Set status message: Baixando modelo {SELECTED_MODEL}...")

        success = download_model(progress_callback=on_progress)
        if success:
            app_logger.info(f"Model {SELECTED_MODEL} successfully downloaded and verified")
            debug_logger.debug("Model download and verification completed")
        else:
            app_logger.error(f"Failed to download model {SELECTED_MODEL}")
            debug_logger.debug("Model download failed")
        return success
    except Exception as e:
        app_logger.error(f"Failed to ensure model availability: {e}")
        debug_logger.debug(f"Model availability error: {str(e)}")
        return False