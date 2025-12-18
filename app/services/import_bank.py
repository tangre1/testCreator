import json
from pathlib import Path
from typing import IO

from app.db import get_session, init_db
from app.models_db import QuestionBank, Question


def import_bank_from_dict(data: dict, bank_key: str) -> str:
    """
    Import a question bank from a parsed JSON dict.
    Returns the bank_key.
    """

    init_db()

    with get_session() as session:
        # Guard against duplicates
        existing = session.exec(
            QuestionBank.__table__.select().where(
                QuestionBank.bank_key == bank_key
            )
        ).first()

        if existing:
            raise ValueError(f"Bank '{bank_key}' already exists")

        bank = QuestionBank(
            bank_key=bank_key,
            course=data["course"],
            unit=data["unit"],
            title=data.get("title"),
        )
        session.add(bank)
        session.commit()
        session.refresh(bank)

        for q in data["questions"]:
            question = Question(
                external_id=q["id"],
                bank_id=bank.id,
                latex=q["latex"],
                topic=q.get("topic"),
                difficulty=q.get("difficulty"),
            )
            session.add(question)

        session.commit()

    return bank_key

