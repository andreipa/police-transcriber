# core/model_updater.py

import os
import requests
from config import MODEL_DOWNLOAD_URL, LOCAL_MODEL_PATH

# Minimum expected size for the large-v3 Whisper model in bytes (~3GB)
MIN_EXPECTED_SIZE = 3 * 1024 * 1024 * 1024  # 3 GB

def check_for_model_update(progress_callback=None):
    """
    Checks if a new model version is available and downloads it if needed.
    Returns True if updated, False if up-to-date.
    """
    try:
        response = requests.head(MODEL_DOWNLOAD_URL, allow_redirects=True)
        remote_size = int(response.headers.get("content-length", 0))

        # If file exists and sizes match, skip
        if os.path.exists(LOCAL_MODEL_PATH):
            local_size = os.path.getsize(LOCAL_MODEL_PATH)
            if local_size == remote_size and local_size >= MIN_EXPECTED_SIZE:
                return False  # Already up-to-date

        # Proceed with download
        response = requests.get(MODEL_DOWNLOAD_URL, stream=True)
        response.raise_for_status()

        os.makedirs(os.path.dirname(LOCAL_MODEL_PATH), exist_ok=True)

        total_downloaded = 0
        with open(LOCAL_MODEL_PATH, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    total_downloaded += len(chunk)
                    if progress_callback and remote_size > 0:
                        progress = int((total_downloaded / remote_size) * 100)
                        progress_callback(progress)
        # Verify the downloaded file size
        final_size = os.path.getsize(LOCAL_MODEL_PATH)
        if final_size < MIN_EXPECTED_SIZE:
            os.remove(LOCAL_MODEL_PATH)
            raise ValueError("Downloaded model file is too small and likely corrupted.")

        return True  # Model was updated

    except Exception as e:
        print(f"Error checking/downloading model: {e}")
        return False
