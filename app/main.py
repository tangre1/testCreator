import json
from pathlib import Path

from fastapi import (
    FastAPI,
    HTTPException,
    Query,
    UploadFile,
    File,
)
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.storage_unified import load_bank
from app.storage_banks import (
    list_banks as list_banks_unified,
    list_topics as list_topics_unified,
)
from app.repo_courses import (
    list_courses,
    list_breakdowns_by_course,
)
from app.repo_questions import (
    list_questions_by_bank,
    create_question,
    update_question,
    delete_question,
)
from app.repo_banks import create_bank
from app.generator import generate_exam
from app.latex import build_latex
from app.models import (
    ExamRequest,
    CreateBankRequest,
    CreateQuestionRequest,
)
from app.services.import_bank import import_bank_from_dict


app = FastAPI(
    title="Exam Builder",
    description="Generate LaTeX exams from structured question banks",
    version="1.0.0",
)

# --------------------
# Startup
# --------------------
@app.on_event("startup")
def on_startup():
    init_db()


# --------------------
# CORS (REQUIRED FOR REACT)
# --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# Navigation Endpoints
# --------------------

@app.get("/courses")
def get_courses():
    """
    List all courses that have question banks.
    """
    courses = list_courses()
    if not courses:
        raise HTTPException(status_code=404, detail="No courses found")
    return courses


@app.get("/courses/{course}/breakdowns")
def get_breakdowns(course: str):
    """
    List breakdowns (banks) within a course.
    """
    breakdowns = list_breakdowns_by_course(course)
    if not breakdowns:
        raise HTTPException(
            status_code=404,
            detail=f"No breakdowns found for course '{course}'",
        )
    return breakdowns


@app.get("/banks")
def list_banks():
    """
    DB-first list of banks with JSON fallback.
    Returns stable bank_key values.
    """
    return list_banks_unified()


@app.get("/banks/{bank_key}/topics")
def list_topics(bank_key: str):
    """
    DB-first list of topics with JSON fallback.
    """
    topics = list_topics_unified(bank_key)
    if not topics:
        raise HTTPException(status_code=404, detail="Bank or topics not found")
    return topics


@app.get("/banks/{bank_key}/questions")
def get_questions(bank_key: str):
    """
    List all questions in a breakdown (bank).
    """
    questions = list_questions_by_bank(bank_key)
    if not questions:
        raise HTTPException(
            status_code=404,
            detail=f"No questions found for bank '{bank_key}'",
        )
    return questions


# --------------------
# Exam Generation
# --------------------

@app.post("/generate-preview")
def generate_preview(
    bank_key: str = Query(..., description="Stable bank key"),
    request: ExamRequest = ...,
):
    """
    Generate a preview of the selected question set (no LaTeX).
    """
    try:
        bank = load_bank(bank_key)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Question bank not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    selected_questions = generate_exam(
        questions=bank.questions,
        total=request.total_questions,
        weights=request.topic_weights,
        seed=request.seed,
    )

    return {
        "course": bank.course,
        "unit": bank.unit,
        "questions": [
            {
                "id": q.external_id,
                "topic": q.topic,
                "latex": q.latex,
            }
            for q in selected_questions
        ],
    }


@app.post("/generate-exam", response_class=PlainTextResponse)
def generate_exam_endpoint(
    bank_key: str = Query(..., description="Stable bank key"),
    request: ExamRequest = ...,
):
    """
    Generate a LaTeX exam from a question bank.
    """
    try:
        bank = load_bank(bank_key)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Question bank '{bank_key}' not found",
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid question bank format: {e}",
        )

    try:
        selected_questions = generate_exam(
            questions=bank.questions,
            total=request.total_questions,
            weights=request.topic_weights,
            seed=request.seed,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    latex_document = build_latex(
        course=bank.course,
        unit=bank.unit,
        questions=selected_questions,
    )

    return latex_document


# --------------------
# Admin Endpoints
# --------------------

@app.post("/admin/import-bank")
async def import_bank_endpoint(file: UploadFile = File(...)):
    """
    Admin endpoint to import a question bank JSON file into the database.
    """
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only JSON files are allowed")

    try:
        contents = await file.read()
        data = json.loads(contents.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON file")

    bank_key = Path(file.filename).stem

    try:
        imported_key = import_bank_from_dict(data, bank_key)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "status": "success",
        "bank_key": imported_key,
    }


@app.post("/admin/banks")
def create_bank_endpoint(request: CreateBankRequest):
    """
    Admin endpoint to create an empty breakdown (bank).
    """
    try:
        bank = create_bank(
            bank_key=request.bank_key,
            course=request.course,
            unit=request.unit,
            title=request.title,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "status": "success",
        "bank_key": bank.bank_key,
        "course": bank.course,
        "unit": bank.unit,
        "title": bank.title,
    }


@app.post("/admin/banks/{bank_key}/questions")
def create_question_endpoint(
    bank_key: str,
    request: CreateQuestionRequest,
):
    """
    Admin endpoint to add a question to a breakdown (bank).
    """
    try:
        question = create_question(
            bank_key=bank_key,
            external_id=request.external_id,
            latex=request.latex,
            topic=request.topic,
            difficulty=request.difficulty,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "status": "success",
        "id": question.id,
        "external_id": question.external_id,
        "topic": question.topic,
        "difficulty": question.difficulty,
    }

@app.delete("/admin/banks/{bank_key}/questions/{external_id}")
def delete_question_endpoint(
    bank_key: str,
    external_id: str,
):
    """
    Admin endpoint to delete a question.
    """
    try:
        delete_question(
            bank_key=bank_key,
            external_id=external_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "status": "success",
        "external_id": external_id,
    }
