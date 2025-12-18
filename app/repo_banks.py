from sqlmodel import select

from app.db import get_session
from app.models_db import QuestionBank, Question


def list_banks_db():
    """
    Return all bank_keys from the database.
    """
    with get_session() as session:
        banks = session.exec(select(QuestionBank.bank_key)).all()
        return sorted(banks)


def list_topics_db(bank_key: str):
    """
    Return distinct topics for a bank from the database.
    """
    with get_session() as session:
        bank = session.exec(
            select(QuestionBank).where(QuestionBank.bank_key == bank_key)
        ).first()

        if not bank:
            return []

        topics = session.exec(
            select(Question.topic)
            .where(Question.bank_id == bank.id)
        ).all()

        return sorted({t for t in topics if t})


def create_bank(
    *,
    bank_key: str,
    course: str,
    unit: str,
    title: str | None = None,
):
    """
    Create an empty QuestionBank (breakdown).
    """
    with get_session() as session:
        existing = session.exec(
            select(QuestionBank).where(QuestionBank.bank_key == bank_key)
        ).first()

        if existing:
            raise ValueError(f"Bank '{bank_key}' already exists")

        bank = QuestionBank(
            bank_key=bank_key,
            course=course,
            unit=unit,
            title=title,
        )

        session.add(bank)
        session.commit()
        session.refresh(bank)

        return bank
