import json
from pathlib import Path

from .models import QuestionBank

# Directory where question banks are stored
BANKS_DIR = Path("banks")


def load_bank(filename: str) -> QuestionBank:
    """
    Load a question bank from a JSON file.

    Args:
        filename: Name of the JSON file in the banks/ directory

    Returns:
        QuestionBank: Parsed and validated question bank

    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file contents are invalid
    """
    path = BANKS_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Question bank '{filename}' not found")

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in '{filename}': {e}")

    try:
        return QuestionBank(**data)
    except Exception as e:
        raise ValueError(f"Invalid question bank schema: {e}")
