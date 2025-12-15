from pathlib import Path
from typing import List

from .models import Question

# Path to the LaTeX template
TEMPLATE_PATH = Path("templates/exam.tex")


def build_latex(course: str, unit: str, questions: List[Question]) -> str:
    """
    Assemble a LaTeX exam document from selected questions.

    Args:
        course: Course identifier (e.g., CS 345)
        unit: Unit or chapter name
        questions: Ordered list of selected questions

    Returns:
        Complete LaTeX document as a string
    """

    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError("LaTeX template not found")

    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    # Concatenate question LaTeX blocks
    question_block = "\n".join(q.latex for q in questions)

    # Replace template placeholders
    latex_document = (
        template
        .replace("{{ COURSE }}", course)
        .replace("{{ UNIT }}", unit)
        .replace("{{ QUESTIONS }}", question_block)
    )

    return latex_document
