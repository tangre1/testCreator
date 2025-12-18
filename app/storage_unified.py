from pathlib import Path
import json

from app.domain import Bank, Question
from app.storage_db import load_bank_from_db


def load_bank(bank_file: str) -> Bank:
    """
    Unified loader:
    1. Try DB
    2. Fall back to JSON
    """

    bank_path = Path("banks") / bank_file

    if not bank_path.exists():
        raise FileNotFoundError(f"Bank file '{bank_file}' not found")

    data = json.loads(bank_path.read_text(encoding="utf-8"))
    course = data["course"]
    unit = data["unit"]

    # ---- Try DB first ----
    try:
        return load_bank_from_db(course, unit)
    except Exception:
        pass

    # ---- Fall back to JSON ----
    questions = [
        Question(
            external_id=q["id"],
            latex=q["latex"],
            topic=q.get("topic"),
            difficulty=q.get("difficulty"),
        )
        for q in data["questions"]
    ]

    return Bank(course=course, unit=unit, questions=questions)
