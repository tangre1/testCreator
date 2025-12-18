from app.repo import get_questions
from app.domain import Bank, Question


def load_bank_from_db(course: str, unit: str) -> Bank:
    db_questions = get_questions(course, unit)

    if not db_questions:
        raise FileNotFoundError("No questions found in database")

    questions = [
        Question(
            external_id=q.external_id,
            latex=q.latex,
            topic=q.topic,
            difficulty=q.difficulty,
        )
        for q in db_questions
    ]

    return Bank(course=course, unit=unit, questions=questions)
