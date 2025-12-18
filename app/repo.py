from typing import List
from sqlmodel import select

from app.db import get_session
from app.models_db import Question, QuestionBank


def get_questions(course: str, unit: str) -> List[Question]:
    with get_session() as session:
        bank = session.exec(
            select(QuestionBank)
            .where(QuestionBank.course == course)
            .where(QuestionBank.unit == unit)
        ).first()

        if not bank:
            return []

        return session.exec(
            select(Question).where(Question.bank_id == bank.id)
        ).all()
