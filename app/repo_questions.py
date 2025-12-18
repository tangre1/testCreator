from typing import List, Dict, Optional
from sqlmodel import select

from app.db import get_session
from app.models_db import Question, QuestionBank


def list_questions_by_bank(bank_key: str) -> List[Dict[str, Optional[str]]]:
    """
    Returns all questions for a given bank_key.
    """
    with get_session() as session:
        bank = session.exec(
            select(QuestionBank).where(QuestionBank.bank_key == bank_key)
        ).first()

        if not bank:
            return []

        questions = session.exec(
            select(Question)
            .where(Question.bank_id == bank.id)
            .order_by(Question.external_id)
        ).all()

        return [
            {
                "id": q.id,
                "external_id": q.external_id,
                "topic": q.topic,
                "difficulty": q.difficulty,
                "latex": q.latex,
            }
            for q in questions
        ]


def create_question(
    *,
    bank_key: str,
    external_id: str,
    latex: str,
    topic: str | None = None,
    difficulty: int | None = None,
):
    """
    Create a new question inside a bank.
    """
    with get_session() as session:
        bank = session.exec(
            select(QuestionBank).where(QuestionBank.bank_key == bank_key)
        ).first()

        if not bank:
            raise ValueError(f"Bank '{bank_key}' does not exist")

        # Prevent duplicate external_id within the same bank
        existing = session.exec(
            select(Question)
            .where(Question.bank_id == bank.id)
            .where(Question.external_id == external_id)
        ).first()

        if existing:
            raise ValueError(
                f"Question '{external_id}' already exists in bank '{bank_key}'"
            )

        question = Question(
            bank_id=bank.id,
            external_id=external_id,
            latex=latex,
            topic=topic,
            difficulty=difficulty,
        )

        session.add(question)
        session.commit()
        session.refresh(question)

        return question


def update_question(
    *,
    bank_key: str,
    external_id: str,
    latex: str | None = None,
    topic: str | None = None,
    difficulty: int | None = None,
):
    """
    Update an existing question.
    """
    with get_session() as session:
        question = session.exec(
            select(Question)
            .join(QuestionBank)
            .where(QuestionBank.bank_key == bank_key)
            .where(Question.external_id == external_id)
        ).first()

        if not question:
            raise ValueError(
                f"Question '{external_id}' not found in bank '{bank_key}'"
            )

        if latex is not None:
            question.latex = latex
        if topic is not None:
            question.topic = topic
        if difficulty is not None:
            question.difficulty = difficulty

        session.add(question)
        session.commit()
        session.refresh(question)

        return question


def delete_question(
    *,
    bank_key: str,
    external_id: str,
):
    """
    Delete a question from a bank.
    """
    with get_session() as session:
        question = session.exec(
            select(Question)
            .join(QuestionBank)
            .where(QuestionBank.bank_key == bank_key)
            .where(Question.external_id == external_id)
        ).first()

        if not question:
            raise ValueError(
                f"Question '{external_id}' not found in bank '{bank_key}'"
            )

        session.delete(question)
        session.commit()

        # Safety check: confirm deletion
        still_exists = session.exec(
            select(Question)
            .join(QuestionBank)
            .where(QuestionBank.bank_key == bank_key)
            .where(Question.external_id == external_id)
        ).first()

        if still_exists:
            raise RuntimeError("Delete failed unexpectedly")

        return True
