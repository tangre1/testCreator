from typing import List, Dict, Optional
from sqlmodel import select

from app.db import get_session
from app.models_db import QuestionBank


def list_courses() -> List[str]:
    """
    Returns distinct course names from the DB.
    """
    with get_session() as session:
        rows = session.exec(select(QuestionBank.course)).all()
        return sorted({c for c in rows if c})


def list_breakdowns_by_course(course: str) -> List[Dict[str, Optional[str]]]:
    """
    Returns breakdowns (banks) for a given course.
    Each breakdown is represented by bank_key + unit + title.
    """
    with get_session() as session:
        banks = session.exec(
            select(QuestionBank)
            .where(QuestionBank.course == course)
            .order_by(QuestionBank.unit, QuestionBank.title, QuestionBank.bank_key)
        ).all()

        return [
            {
                "bank_key": b.bank_key,
                "unit": b.unit,
                "title": b.title,
            }
            for b in banks
        ]
