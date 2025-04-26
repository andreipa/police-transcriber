#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

import logging
import os

import requests

from config import LOCAL_MODEL_PATH, MODEL_FILES, MODEL_DOWNLOAD_BASE_URL, SELECTED_MODEL

MIN_MODEL_BIN_SIZE = {
    "base": 145 * 1024 * 1024,  # 145 MB for base model.bin
    "small": 484 * 1024 * 1024,  # 484 MB for small.bin
    "medium": 1.53 * 1024 * 1024 * 1024,  # 1.53 GB for medium.bin
    "large-v2": 3.09 * 1024 * 1024 * 1024  # 3.09 GB for large-v2 model.bin
}

def is_model_fully_downloaded() -> bool:
    """Check if all required model files are present and valid.

    Returns:
        True if all model files exist and the main model file meets the minimum size, False otherwise.
    """
    try:
        for file_name in MODEL_FILES:
            file_path = os.path.join(LOCAL_MODEL_PATH, file_name)
            if not os.path.exists(file_path):
                logging.warning(f"Missing model file: {file_path}")
                return False

            # Check size for main model file (model.bin or *.bin)
            if file_name.endswith('.bin'):
                size = os.path.getsize(file_path)
                min_size = MIN_MODEL_BIN_SIZE.get(SELECTED_MODEL, 145 * 1024 * 1024)  # Default to base size
                if size < min_size:
                    logging.warning(f"Model file {file_name} is too small: {size} bytes, expected >= {min_size} bytes")
                    return False

        logging.info("All model files verified")
        return True
    except Exception as e:
        logging.error(f"Failed to check model status: {e}")
        return False


def download_model(progress_callback=None) -> bool:
    """Download all required model files from the Hugging Face repository.

    Args:
        progress_callback: Optional function to report cumulative download progress (0-100).

    Returns:
        True if all files were downloaded successfully, False otherwise.
    """
    try:
        os.makedirs(LOCAL_MODEL_PATH, exist_ok=True)
        headers = {}

        total_sizes = []
        for file_name in MODEL_FILES:
            url = f"{MODEL_DOWNLOAD_BASE_URL}/{file_name}"
            response = requests.head(url, headers=headers, allow_redirects=True, timeout=10)
            if response.status_code != 200:
                logging.error(f"Failed to access {url}: HTTP {response.status_code}")
                return False
            size = int(response.headers.get("content-length", 0))
            total_sizes.append(size if size > 0 else 1)  # Avoid division by zero

        total_size = sum(total_sizes)
        downloaded_total = 0

        for file_index, file_name in enumerate(MODEL_FILES):
            url = f"{MODEL_DOWNLOAD_BASE_URL}/{file_name}"
            dest_path = os.path.join(LOCAL_MODEL_PATH, file_name)

            logging.info(f"Downloading {file_name} from {url}")
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            if response.status_code != 200:
                logging.error(f"Download failed for {url}: HTTP {response.status_code}")
                return False

            file_size = total_sizes[file_index]
            downloaded_file = 0

            with open(dest_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded_file += len(chunk)
                        downloaded_total += len(chunk)
                        if progress_callback and total_size:
                            progress = int((downloaded_total / total_size) * 100)
                            progress_callback(min(progress, 100))

        logging.info("All model files downloaded successfully")
        return True
    except requests.RequestException as e:
        logging.error(f"Model download failed: {e}")
        return False


def ensure_model_available(on_status=None, on_progress=None) -> bool:
    """Ensure all required model files are available, downloading them if necessary.

    Args:
        on_status: Optional callback to update status messages.
        on_progress: Optional callback to report download progress (0-100).

    Returns:
        True if the model is available, False if download fails.
    """
    try:
        if is_model_fully_downloaded():
            logging.info("Model already available and verified")
            return True

        if on_status:
            on_status("Baixando modelo...")

        return download_model(progress_callback=on_progress)
    except Exception as e:
        logging.error(f"Failed to ensure model availability: {e}")
        return False