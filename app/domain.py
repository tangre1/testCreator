from typing import Optional, List


class Question:
    """
    Domain-level Question.
    Storage-agnostic.
    """

    def __init__(
        self,
        external_id: str,
        latex: str,
        topic: Optional[str] = None,
        difficulty: Optional[int] = None,
    ):
        self.external_id = external_id
        self.latex = latex
        self.topic = topic
        self.difficulty = difficulty


class Bank:
    """
    Domain-level Bank.
    The rest of the app depends ONLY on this.
    """

    def __init__(self, course: str, unit: str, questions: List[Question]):
        self.course = course
        self.unit = unit
        self.questions = questions
