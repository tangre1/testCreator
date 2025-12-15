from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class Question(BaseModel):
    """
    Represents a single exam question.

    Each question is assumed to already contain valid LaTeX.
    The system assembles questions; it does not generate content.
    """
    id: str = Field(..., description="Unique question identifier")
    topic: str = Field(..., description="Topic or subtopic label")
    difficulty: int = Field(
        ...,
        ge=1,
        description="Relative difficulty level (1 = easiest)"
    )
    latex: str = Field(
        ...,
        description="LaTeX code for the question (e.g., \\question ...)"
    )


class QuestionBank(BaseModel):
    """
    Represents a collection of questions for a single unit.
    """
    course: str = Field(..., description="Course identifier (e.g., CS 345)")
    unit: str = Field(..., description="Unit or chapter name")
    questions: List[Question]


class ExamRequest(BaseModel):
    """
    Input parameters for generating an exam.
    """
    total_questions: int = Field(
        ...,
        gt=0,
        description="Total number of questions on the exam"
    )

    topic_weights: Dict[str, float] = Field(
        ...,
        description="Mapping of topic → proportion of exam (must sum to ~1.0)"
    )

    seed: Optional[int] = Field(
        None,
        description="Optional random seed for reproducible exams"
    )
