from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import CONTENT_DIR, DB_PATH
from .content.loader import load_questions
from .db.database import get_connection, init_db


def create_app(content_dir: Path = CONTENT_DIR, db_path: Path = DB_PATH) -> FastAPI:
    app = FastAPI(title="Study Drill Platform")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.questions = load_questions(content_dir)
    app.state.content_dir = content_dir
    conn = get_connection(db_path)
    init_db(conn)
    app.state.db = conn

    from .api import subjects, questions, attempts
    app.include_router(subjects.router)
    app.include_router(questions.router)
    app.include_router(attempts.router)
    return app


app = create_app()
