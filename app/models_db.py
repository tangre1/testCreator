from typing import Optional
from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class QuestionBank(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # NEW: stable external key
    bank_key: str = Field(index=True, unique=True)

    course: str
    unit: str
    title: Optional[str] = None


class Question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    external_id: str = Field(index=True)
    bank_id: int = Field(foreign_key="questionbank.id")

    latex: str
    topic: Optional[str] = None
    difficulty: Optional[int] = None


class CreateQuestionRequest(BaseModel):
    external_id: str
    latex: str
    topic: Optional[str] = None
    difficulty: Optional[int] = None