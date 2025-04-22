#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

import logging
import os

import requests

from config import MODEL_DOWNLOAD_URL, LOCAL_MODEL_PATH

# Minimum expected size for the Whisper model in bytes (approximately 3GB)
MIN_MODEL_SIZE = 3 * 1024 * 1024 * 1024


def check_for_model_update(progress_callback=None) -> bool:
    """Check for a new Whisper model version and download it if needed.

    Compares the remote model's size with the local file (if it exists) to determine if an update
    is required. Downloads the model incrementally, reporting progress via a callback. Verifies
    the downloaded file's size to ensure it is not corrupted.

    Args:
        progress_callback: Optional function to report download progress as a percentage.

    Returns:
        True if the model was updated or downloaded, False if the local model is up-to-date or
        an error occurs.

    Raises:
        ValueError: If the downloaded model file is too small and likely corrupted.
        requests.RequestException: If the network request fails.
    """
    try:
        # Check remote model size
        response = requests.head(MODEL_DOWNLOAD_URL, allow_redirects=True)
        response.raise_for_status()
        remote_size = int(response.headers.get("content-length", 0))

        # Skip download if local file exists and matches remote size
        if os.path.exists(LOCAL_MODEL_PATH):
            local_size = os.path.getsize(LOCAL_MODEL_PATH)
            if local_size == remote_size and local_size >= MIN_MODEL_SIZE:
                logging.info("Local model is up-to-date")
                return False

        # Download the model
        response = requests.get(MODEL_DOWNLOAD_URL, stream=True)
        response.raise_for_status()

        # Ensure the local directory exists
        os.makedirs(os.path.dirname(LOCAL_MODEL_PATH), exist_ok=True)

        # Write the model file incrementally
        total_downloaded = 0
        with open(LOCAL_MODEL_PATH, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    total_downloaded += len(chunk)
                    if progress_callback and remote_size > 0:
                        progress = int((total_downloaded / remote_size) * 100)
                        progress_callback(progress)

        # Verify the downloaded file size
        final_size = os.path.getsize(LOCAL_MODEL_PATH)
        if final_size < MIN_MODEL_SIZE:
            os.remove(LOCAL_MODEL_PATH)
            raise ValueError("Downloaded model file is too small and likely corrupted")

        logging.info("Model updated successfully")
        return True

    except (requests.RequestException, ValueError, OSError) as e:
        logging.error(f"Error checking or downloading model: {e}")
        return False