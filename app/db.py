from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

from app.paths import get_user_data_dir


# Ensure user data directory exists
DATA_DIR = get_user_data_dir()
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "questions.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)
