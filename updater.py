
import os
import sys
import requests
from packaging import version

# The owner and repository name of your GitHub project.
OWNER = "joaomagdaleno"
REPO = "UniversalConverter"

def get_current_version():
    """Reads the version from the VERSION.txt file."""
    if getattr(sys, 'frozen', False):
        # The application is running as a bundled executable
        base_path = sys._MEIPASS
    else:
        # The application is running as a standard Python script
        base_path = os.path.dirname(os.path.abspath(__file__))

    version_file_path = os.path.join(base_path, 'VERSION.txt')

    try:
        with open(version_file_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0" # Default version if file not found

def check_for_updates():
    """
    Compares the current version with the latest version from GitHub.

    Returns:
        A tuple (is_update_available, latest_version_str, download_url).
        is_update_available (bool): True if a new version is available.
        latest_version_str (str): The latest version number, or None if an error occurred.
        download_url (str): The direct URL for the release asset, or None.
    """
    current_v_str = get_current_version()
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        release_data = response.json()

        latest_v_str = release_data["tag_name"].lstrip('v')
        current_v = version.parse(current_v_str)
        latest_v = version.parse(latest_v_str)

        if latest_v > current_v:
            for asset in release_data.get("assets", []):
                if asset["name"].endswith(".zip"):
                    return True, latest_v_str, asset["browser_download_url"]
            return True, latest_v_str, None # Update available but no asset found

    except (requests.exceptions.RequestException, KeyError):
        pass

    return False, None, None

import tempfile

def download_update(url, progress_callback):
    """Downloads the update file and reports progress."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, 'update.zip')

        with open(file_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                progress = int(100 * downloaded / total_size)
                progress_callback(progress)

        return file_path
    except requests.exceptions.RequestException:
        return None
