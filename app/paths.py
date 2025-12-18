import sys
from pathlib import Path


APP_NAME = "ExamBuilder"


def get_user_data_dir() -> Path:
    """
    Return OS-appropriate user data directory.
    macOS: ~/Library/Application Support/ExamBuilder
    """

    home = Path.home()

    if sys.platform == "darwin":
        return home / "Library" / "Application Support" / APP_NAME

    # Fallback (Linux / Windows later)
    return home / f".{APP_NAME.lower()}"
