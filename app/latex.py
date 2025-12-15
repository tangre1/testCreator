from pathlib import Path
from typing import List

from .models import Question

# Path to the LaTeX template
TEMPLATE_PATH = Path("templates/exam.tex")


def build_latex(course: str, unit: str, questions: List[Question]) -> str:
    """
    Assemble a LaTeX exam document from selected questions.

    Args:
        course: Course identifier (e.g., Precalculus I)
        unit: Unit or chapter name
        questions: Ordered list of selected questions

    Returns:
        Complete LaTeX document as a string
    """

    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError("LaTeX template not found")

    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    # Number questions in CSU style (article-safe)
    question_block = "\n\n".join(
        f"\\noindent\\textbf{{{i + 1}.}} {q.latex}"
        for i, q in enumerate(questions)
    )

    # Replace template placeholders
    latex_document = (
        template
        .replace("{{ COURSE }}", course)
        .replace("{{ UNIT }}", unit)
        .replace("{{ QUESTIONS }}", question_block)
    )

    return latex_document
