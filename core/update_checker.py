#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

import requests

from config import GITHUB_RELEASES_URL


# Check for updates on GitHub
def get_latest_version():
    try:
        response = requests.get(GITHUB_RELEASES_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("tag_name", "").lstrip("v"), data.get("html_url")
        return None, None
    except Exception as e:
        print(f"Failed to check latest version: {e}")
        return None, None


def is_newer_version(latest, current):
    from packaging import version
    return version.parse(latest) > version.parse(current)
