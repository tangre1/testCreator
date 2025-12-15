from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse

from .storage import load_bank
from .generator import generate_exam
from .latex import build_latex
from .models import ExamRequest

app = FastAPI(
    title="Exam Builder",
    description="Generate LaTeX exams from structured question banks",
    version="1.0.0"
)


@app.post("/generate-exam", response_class=PlainTextResponse)
def generate_exam_endpoint(
    bank_file: str = Query(..., description="Question bank JSON filename"),
    request: ExamRequest = ...
):
    """
    Generate a LaTeX exam from a question bank.

    Flow:
    1. Load question bank from file
    2. Select questions based on topic weights
    3. Assemble LaTeX document
    4. Return raw .tex content
    """

    # Load question bank
    try:
        bank = load_bank(bank_file)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Question bank '{bank_file}' not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid question bank format: {e}"
        )

    # Generate exam questions
    try:
        selected_questions = generate_exam(
            questions=bank.questions,
            total=request.total_questions,
            weights=request.topic_weights,
            seed=request.seed
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    # Build LaTeX document
    latex_document = build_latex(
        course=bank.course,
        unit=bank.unit,
        questions=selected_questions
    )

    return latex_document
