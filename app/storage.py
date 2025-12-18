import json
from pathlib import Path


class Bank:
    def __init__(self, course, unit, questions):
        self.course = course
        self.unit = unit
        self.questions = questions


def load_bank(bank_file: str):
    bank_path = Path("banks") / bank_file

    if not bank_path.exists():
        raise FileNotFoundError(f"Bank file '{bank_file}' not found")

    data = json.loads(bank_path.read_text(encoding="utf-8"))

    return Bank(
        course=data["course"],
        unit=data["unit"],
        questions=data["questions"],
    )
