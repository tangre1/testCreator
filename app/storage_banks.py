from pathlib import Path
import json
from typing import List

from app.repo_banks import list_banks_db, list_topics_db


BANKS_DIR = Path("banks")


def list_banks() -> List[str]:
    """
    DB-first list of banks, JSON fallback.
    """
    try:
        banks = list_banks_db()
        if banks:
            return banks
    except Exception:
        pass

    if not BANKS_DIR.exists():
        return []

    return sorted(
        f.name
        for f in BANKS_DIR.iterdir()
        if f.is_file() and f.suffix == ".json"
    )


def list_topics(bank_file: str) -> List[str]:
    """
    DB-first topics, JSON fallback.
    """
    bank_path = BANKS_DIR / bank_file
    if not bank_path.exists():
        return []

    data = json.loads(bank_path.read_text(encoding="utf-8"))
    course = data["course"]
    unit = data["unit"]

    try:
        topics = list_topics_db(course, unit)
        if topics:
            return topics
    except Exception:
        pass

    questions = data.get("questions", [])
    return sorted({q.get("topic") for q in questions if q.get("topic")})
