# Study Drill Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a personal MCQ drilling tool (FastAPI + SQLite backend, React + Vite frontend) that loads question banks from text files, records every answer, and shows what you don't know.

**Architecture:** Three layers with content fully separated from code. `content/` holds YAML questions + Markdown tutorials (git-managed). A FastAPI backend loads the bank into memory and stores only attempt history in SQLite. A React frontend drills questions, shows instant feedback, and surfaces weak spots.

**Tech Stack:** Python 3.11+, FastAPI, Uvicorn, PyYAML, Pydantic v2, pytest, httpx (TestClient); React 18, Vite, React Router.

## Global Constraints

- Python 3.11+ (uses `str | None` syntax and `list[str]` generics).
- Backend runs on `http://localhost:8000`; frontend dev server on `http://localhost:5173`. CORS allows the frontend origin.
- SQLite stores ONLY attempt history. Question content is NEVER written to the DB — it is read from `content/` files at startup.
- MCQ is the only question type in this MVP. The `type` field exists but only `"mcq"` is valid.
- Difficulty is one of exactly: `basic`, `intermediate`, `advanced`, `master`.
- Question `id` is a stable unique string; progress is keyed on it.
- `answer` is a 0-based index into `options`.
- All file reads/writes use `encoding="utf-8"` (Windows default is cp1252 — must be explicit).
- All paths in commands assume project root `C:\Users\arad2\study-platform`. Backend lives in `backend/`, frontend in `frontend/`, content in `content/`.

---

## File Structure

```
study-platform/
  content/                      # question banks + tutorials (git-managed data)
    data-structures/
      arrays.yaml
      linked-lists.yaml
      arrays.md                 # optional tutorial
    algorithms/
      sorting.yaml
    english/
      vocabulary.yaml
      communication.yaml
  backend/
    requirements.txt
    app/
      __init__.py
      config.py                 # resolves content/ and DB paths
      main.py                   # create_app(), wires routers, loads bank
      content/
        __init__.py
        schema.py               # Pydantic Question / LoadedQuestion + validation
        loader.py               # load_questions(content_dir) -> list[LoadedQuestion]
      db/
        __init__.py
        database.py             # get_connection(), init_db()
        attempts.py             # record_attempt(), wrong_question_ids()
      stats_service.py          # compute_stats(conn, questions)
      api/
        __init__.py
        subjects.py             # GET /subjects
        questions.py            # GET /questions
        attempts.py             # POST /attempts
        stats.py                # GET /stats
        tutorials.py            # GET /tutorials/{subject}/{topic}
    tests/
      conftest.py               # fixtures: temp content dir, app, client
      test_schema.py
      test_loader.py
      test_attempts_repo.py
      test_questions_api.py
      test_attempts_api.py
      test_stats_api.py
      test_tutorials_api.py
  frontend/
    package.json
    vite.config.js
    index.html
    src/
      main.jsx
      App.jsx                   # router + nav
      api/client.js             # fetch wrappers
      pages/
        Dashboard.jsx
        Practice.jsx
        Tutorial.jsx
        Browse.jsx
      components/
        QuestionCard.jsx
        Filters.jsx
      styles.css
```

Backend files are split by responsibility (schema / loading / db / stats / one router per endpoint) so each stays small and independently testable. Frontend is split by page plus two shared components.

---

## Task 1: Backend setup + Question schema

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py` (empty)
- Create: `backend/app/content/__init__.py` (empty)
- Create: `backend/app/content/schema.py`
- Test: `backend/tests/test_schema.py`

**Interfaces:**
- Produces: `Question` (Pydantic model) with fields `id: str`, `type: Literal["mcq"]="mcq"`, `difficulty: Literal["basic","intermediate","advanced","master"]`, `tags: list[str]=[]`, `question: str`, `options: list[str]`, `answer: int`, `explanation: str=""`. Raises `ValidationError` if `answer` out of range or `< 2` options.
- Produces: `LoadedQuestion(Question)` adding `subject: str`, `topic: str`.

- [ ] **Step 1: Create requirements.txt**

```
fastapi==0.115.6
uvicorn==0.34.0
pyyaml==6.0.2
pydantic==2.10.4
pytest==8.3.4
httpx==0.28.1
```

- [ ] **Step 2: Set up virtualenv and install**

Run (PowerShell, from `backend/`):
```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Expected: installs without error. (If activation is blocked, run `Set-ExecutionPolicy -Scope Process Bypass` first.)

- [ ] **Step 3: Create empty package markers**

Create `backend/app/__init__.py` and `backend/app/content/__init__.py` as empty files.

- [ ] **Step 4: Write the failing test**

`backend/tests/test_schema.py`:
```python
import pytest
from pydantic import ValidationError
from app.content.schema import Question, LoadedQuestion


def test_valid_question():
    q = Question(
        id="ds-arrays-001",
        difficulty="basic",
        question="Access time of array index?",
        options=["O(1)", "O(n)"],
        answer=0,
    )
    assert q.type == "mcq"
    assert q.answer == 0
    assert q.tags == []


def test_answer_out_of_range_rejected():
    with pytest.raises(ValidationError):
        Question(
            id="x", difficulty="basic", question="q",
            options=["a", "b"], answer=5,
        )


def test_too_few_options_rejected():
    with pytest.raises(ValidationError):
        Question(
            id="x", difficulty="basic", question="q",
            options=["only one"], answer=0,
        )


def test_bad_difficulty_rejected():
    with pytest.raises(ValidationError):
        Question(
            id="x", difficulty="expert", question="q",
            options=["a", "b"], answer=0,
        )


def test_loaded_question_has_subject_topic():
    q = LoadedQuestion(
        id="x", difficulty="basic", question="q",
        options=["a", "b"], answer=0,
        subject="data-structures", topic="arrays",
    )
    assert q.subject == "data-structures"
    assert q.topic == "arrays"
```

- [ ] **Step 5: Run test to verify it fails**

Run (from `backend/`): `python -m pytest tests/test_schema.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.content.schema'`.

- [ ] **Step 6: Write minimal implementation**

`backend/app/content/schema.py`:
```python
from typing import Literal
from pydantic import BaseModel, model_validator


class Question(BaseModel):
    id: str
    type: Literal["mcq"] = "mcq"
    difficulty: Literal["basic", "intermediate", "advanced", "master"]
    tags: list[str] = []
    question: str
    options: list[str]
    answer: int
    explanation: str = ""

    @model_validator(mode="after")
    def _check(self) -> "Question":
        if len(self.options) < 2:
            raise ValueError("a question needs at least 2 options")
        if not 0 <= self.answer < len(self.options):
            raise ValueError(
                f"answer index {self.answer} out of range for "
                f"{len(self.options)} options"
            )
        return self


class LoadedQuestion(Question):
    subject: str
    topic: str
```

- [ ] **Step 7: Run test to verify it passes**

Run: `python -m pytest tests/test_schema.py -v`
Expected: PASS (5 passed).

- [ ] **Step 8: Commit**

```bash
git add backend/requirements.txt backend/app/__init__.py backend/app/content/__init__.py backend/app/content/schema.py backend/tests/test_schema.py
git commit -m "feat: add question schema with validation"
```

---

## Task 2: Content loader

**Files:**
- Create: `backend/app/content/loader.py`
- Test: `backend/tests/test_loader.py`

**Interfaces:**
- Consumes: `LoadedQuestion` from `app.content.schema`.
- Produces: `load_questions(content_dir: Path) -> list[LoadedQuestion]`. Scans `content_dir/*/*.yaml`; `subject` = parent dir name, `topic` = file stem. Raises `ValueError` on duplicate `id` across all files.

- [ ] **Step 1: Write the failing test**

`backend/tests/test_loader.py`:
```python
import pytest
from app.content.loader import load_questions


def _write(content_dir, subject, topic, text):
    d = content_dir / subject
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{topic}.yaml").write_text(text, encoding="utf-8")


def test_loads_questions_with_subject_and_topic(tmp_path):
    _write(tmp_path, "data-structures", "arrays", """
- id: ds-arrays-001
  difficulty: basic
  question: Access time?
  options: ["O(1)", "O(n)"]
  answer: 0
""")
    questions = load_questions(tmp_path)
    assert len(questions) == 1
    assert questions[0].subject == "data-structures"
    assert questions[0].topic == "arrays"
    assert questions[0].id == "ds-arrays-001"


def test_empty_yaml_file_is_skipped(tmp_path):
    _write(tmp_path, "english", "vocabulary", "")
    assert load_questions(tmp_path) == []


def test_duplicate_id_raises(tmp_path):
    body = """
- id: dup-001
  difficulty: basic
  question: q
  options: ["a", "b"]
  answer: 0
"""
    _write(tmp_path, "english", "vocabulary", body)
    _write(tmp_path, "algorithms", "sorting", body)
    with pytest.raises(ValueError, match="duplicate"):
        load_questions(tmp_path)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_loader.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.content.loader'`.

- [ ] **Step 3: Write minimal implementation**

`backend/app/content/loader.py`:
```python
from pathlib import Path
import yaml
from .schema import LoadedQuestion


def load_questions(content_dir: Path) -> list[LoadedQuestion]:
    questions: list[LoadedQuestion] = []
    seen: set[str] = set()
    for yaml_file in sorted(content_dir.glob("*/*.yaml")):
        subject = yaml_file.parent.name
        topic = yaml_file.stem
        raw = yaml.safe_load(yaml_file.read_text(encoding="utf-8")) or []
        for item in raw:
            q = LoadedQuestion(subject=subject, topic=topic, **item)
            if q.id in seen:
                raise ValueError(f"duplicate question id: {q.id}")
            seen.add(q.id)
            questions.append(q)
    return questions
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_loader.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add backend/app/content/loader.py backend/tests/test_loader.py
git commit -m "feat: add YAML content loader"
```

---

## Task 3: SQLite database + attempts repository

**Files:**
- Create: `backend/app/db/__init__.py` (empty)
- Create: `backend/app/db/database.py`
- Create: `backend/app/db/attempts.py`
- Test: `backend/tests/test_attempts_repo.py`

**Interfaces:**
- Produces: `get_connection(db_path) -> sqlite3.Connection` (row_factory = Row, `check_same_thread=False`).
- Produces: `init_db(conn) -> None` creating the `attempts` table.
- Produces: `record_attempt(conn, question_id: str, is_correct: bool, chosen: int) -> int` (returns new row id).
- Produces: `wrong_question_ids(conn) -> set[str]` — ids whose MOST RECENT attempt was incorrect.

- [ ] **Step 1: Create empty package marker**

Create `backend/app/db/__init__.py` as an empty file.

- [ ] **Step 2: Write the failing test**

`backend/tests/test_attempts_repo.py`:
```python
import pytest
from app.db.database import get_connection, init_db
from app.db.attempts import record_attempt, wrong_question_ids


@pytest.fixture
def conn(tmp_path):
    c = get_connection(tmp_path / "test.db")
    init_db(c)
    yield c
    c.close()


def test_record_returns_row_id(conn):
    rid = record_attempt(conn, "q1", True, 0)
    assert rid == 1


def test_wrong_ids_empty_initially(conn):
    assert wrong_question_ids(conn) == set()


def test_wrong_id_listed_when_last_attempt_wrong(conn):
    record_attempt(conn, "q1", False, 1)
    assert wrong_question_ids(conn) == {"q1"}


def test_question_leaves_wrong_book_after_correct(conn):
    record_attempt(conn, "q1", False, 1)
    record_attempt(conn, "q1", True, 0)
    assert wrong_question_ids(conn) == set()
```

- [ ] **Step 3: Run test to verify it fails**

Run: `python -m pytest tests/test_attempts_repo.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.db.database'`.

- [ ] **Step 4: Write minimal implementation**

`backend/app/db/database.py`:
```python
import sqlite3
from pathlib import Path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS attempts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT    NOT NULL,
    is_correct  INTEGER NOT NULL,
    chosen      INTEGER NOT NULL,
    answered_at TEXT    NOT NULL DEFAULT (datetime('now'))
);
"""


def get_connection(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(_SCHEMA)
    conn.commit()
```

`backend/app/db/attempts.py`:
```python
import sqlite3


def record_attempt(
    conn: sqlite3.Connection, question_id: str, is_correct: bool, chosen: int
) -> int:
    cur = conn.execute(
        "INSERT INTO attempts (question_id, is_correct, chosen) VALUES (?, ?, ?)",
        (question_id, 1 if is_correct else 0, chosen),
    )
    conn.commit()
    return cur.lastrowid


def wrong_question_ids(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute(
        """
        SELECT a.question_id AS qid
        FROM attempts a
        JOIN (
            SELECT question_id, MAX(id) AS last_id
            FROM attempts GROUP BY question_id
        ) m ON a.id = m.last_id
        WHERE a.is_correct = 0
        """
    ).fetchall()
    return {r["qid"] for r in rows}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest tests/test_attempts_repo.py -v`
Expected: PASS (4 passed).

- [ ] **Step 6: Commit**

```bash
git add backend/app/db/__init__.py backend/app/db/database.py backend/app/db/attempts.py backend/tests/test_attempts_repo.py
git commit -m "feat: add sqlite attempts repository"
```

---

## Task 4: App factory + config + shared test fixtures

**Files:**
- Create: `backend/app/config.py`
- Create: `backend/app/main.py`
- Create: `backend/app/api/__init__.py` (empty)
- Create: `backend/tests/conftest.py`

**Interfaces:**
- Produces: `config.CONTENT_DIR`, `config.DB_PATH` (Path constants).
- Produces: `create_app(content_dir: Path = CONTENT_DIR, db_path: Path = DB_PATH) -> FastAPI`. Stores on `app.state`: `questions` (list[LoadedQuestion]), `content_dir` (Path), `db` (Connection). Includes all five routers (added in later tasks; for now include only what exists).
- Produces (conftest): `client` fixture — a `TestClient` over `create_app` with a temp content dir (one DS question, one English question) and temp DB.

Note: This task wires routers incrementally. For now `create_app` includes no routers (none exist yet). Each later API task adds its `app.include_router(...)` line AND its router file. The conftest fixture is built now so later API tasks can use it.

- [ ] **Step 1: Create empty package marker**

Create `backend/app/api/__init__.py` as an empty file.

- [ ] **Step 2: Write config.py**

`backend/app/config.py`:
```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # study-platform/
CONTENT_DIR = BASE_DIR / "content"
DB_PATH = BASE_DIR / "backend" / "progress.db"
```

- [ ] **Step 3: Write main.py (app factory, no routers yet)**

`backend/app/main.py`:
```python
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

    # Routers are registered here as later tasks add them:
    # from .api import subjects, questions, attempts, stats, tutorials
    # app.include_router(subjects.router)  ... etc.
    return app


app = create_app()
```

- [ ] **Step 4: Write conftest.py**

`backend/tests/conftest.py`:
```python
import pytest
from fastapi.testclient import TestClient
from app.main import create_app


@pytest.fixture
def content_dir(tmp_path):
    ds = tmp_path / "data-structures"
    ds.mkdir()
    (ds / "arrays.yaml").write_text("""
- id: ds-arrays-001
  difficulty: basic
  tags: [arrays]
  question: Access time of array index?
  options: ["O(1)", "O(n)"]
  answer: 0
  explanation: Direct address computation.
""", encoding="utf-8")
    (ds / "arrays.md").write_text("# Arrays\n\nContiguous memory.", encoding="utf-8")
    en = tmp_path / "english"
    en.mkdir()
    (en / "vocabulary.yaml").write_text("""
- id: en-vocab-001
  difficulty: basic
  question: "Pick the synonym of 'deprecate' in software."
  options: ["promote", "discourage use of", "compile"]
  answer: 1
  explanation: Deprecated APIs are discouraged from use.
""", encoding="utf-8")
    return tmp_path


@pytest.fixture
def client(content_dir, tmp_path):
    app = create_app(content_dir=content_dir, db_path=tmp_path / "test.db")
    return TestClient(app)
```

- [ ] **Step 5: Verify the app boots (sanity)**

Run: `python -m pytest tests/ -v`
Expected: PASS — existing tests still pass; conftest imports without error (no API tests yet).

- [ ] **Step 6: Commit**

```bash
git add backend/app/config.py backend/app/main.py backend/app/api/__init__.py backend/tests/conftest.py
git commit -m "feat: add app factory, config, and test fixtures"
```

---

## Task 5: GET /subjects endpoint

**Files:**
- Create: `backend/app/api/subjects.py`
- Modify: `backend/app/main.py` (register router)
- Test: `backend/tests/test_questions_api.py` (subjects portion)

**Interfaces:**
- Consumes: `request.app.state.questions`.
- Produces: `GET /subjects` -> `[{"subject": str, "topics": [str, ...]}, ...]`, sorted by subject, topics sorted.

- [ ] **Step 1: Write the failing test**

`backend/tests/test_questions_api.py`:
```python
def test_subjects_lists_subjects_and_topics(client):
    resp = client.get("/subjects")
    assert resp.status_code == 200
    data = resp.json()
    subjects = {row["subject"] for row in data}
    assert subjects == {"data-structures", "english"}
    ds = next(r for r in data if r["subject"] == "data-structures")
    assert ds["topics"] == ["arrays"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_questions_api.py -v`
Expected: FAIL — 404 (route not registered).

- [ ] **Step 3: Write the router**

`backend/app/api/subjects.py`:
```python
from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/subjects")
def get_subjects(request: Request):
    tree: dict[str, set[str]] = {}
    for q in request.app.state.questions:
        tree.setdefault(q.subject, set()).add(q.topic)
    return [
        {"subject": s, "topics": sorted(topics)}
        for s, topics in sorted(tree.items())
    ]
```

- [ ] **Step 4: Register the router in main.py**

In `backend/app/main.py`, replace the router comment block with:
```python
    from .api import subjects
    app.include_router(subjects.router)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest tests/test_questions_api.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/subjects.py backend/app/main.py backend/tests/test_questions_api.py
git commit -m "feat: add GET /subjects endpoint"
```

---

## Task 6: GET /questions endpoint (with filters)

**Files:**
- Create: `backend/app/api/questions.py`
- Modify: `backend/app/main.py` (register router)
- Test: `backend/tests/test_questions_api.py` (append)

**Interfaces:**
- Consumes: `request.app.state.questions`, `wrong_question_ids` from `app.db.attempts`.
- Produces: `GET /questions?subject=&topic=&difficulty=&only_wrong=` -> `[question_dict, ...]` where each dict is `LoadedQuestion.model_dump()` (includes subject, topic, answer, explanation). `only_wrong=true` keeps only ids whose latest attempt was wrong.

- [ ] **Step 1: Write the failing test (append to test_questions_api.py)**

```python
def test_questions_returns_all(client):
    resp = client.get("/questions")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_questions_filtered_by_subject(client):
    resp = client.get("/questions", params={"subject": "english"})
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == "en-vocab-001"


def test_questions_only_wrong(client):
    # answer ds-arrays-001 incorrectly, then request only_wrong
    client.post("/attempts", json={"question_id": "ds-arrays-001", "chosen": 1})
    resp = client.get("/questions", params={"only_wrong": "true"})
    ids = [q["id"] for q in resp.json()]
    assert ids == ["ds-arrays-001"]
```

(Note: `test_questions_only_wrong` depends on POST /attempts from Task 7. If running Task 6 in isolation, expect that one test to fail until Task 7 lands; the first two must pass now.)

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_questions_api.py -k questions -v`
Expected: FAIL — 404 on `/questions`.

- [ ] **Step 3: Write the router**

`backend/app/api/questions.py`:
```python
from fastapi import APIRouter, Request
from ..db.attempts import wrong_question_ids

router = APIRouter()


@router.get("/questions")
def get_questions(
    request: Request,
    subject: str | None = None,
    topic: str | None = None,
    difficulty: str | None = None,
    only_wrong: bool = False,
):
    items = request.app.state.questions
    if subject:
        items = [q for q in items if q.subject == subject]
    if topic:
        items = [q for q in items if q.topic == topic]
    if difficulty:
        items = [q for q in items if q.difficulty == difficulty]
    if only_wrong:
        wrong = wrong_question_ids(request.app.state.db)
        items = [q for q in items if q.id in wrong]
    return [q.model_dump() for q in items]
```

- [ ] **Step 4: Register the router in main.py**

In `backend/app/main.py`, update the import/registration block to:
```python
    from .api import subjects, questions
    app.include_router(subjects.router)
    app.include_router(questions.router)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest tests/test_questions_api.py -k "questions and not only_wrong" -v`
Expected: PASS for the two non-`only_wrong` tests.

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/questions.py backend/app/main.py backend/tests/test_questions_api.py
git commit -m "feat: add GET /questions with filters"
```

---

## Task 7: POST /attempts endpoint

**Files:**
- Create: `backend/app/api/attempts.py`
- Modify: `backend/app/main.py` (register router)
- Test: `backend/tests/test_attempts_api.py`

**Interfaces:**
- Consumes: `request.app.state.questions`, `request.app.state.db`, `record_attempt` from `app.db.attempts`.
- Produces: `POST /attempts` body `{"question_id": str, "chosen": int}` -> `{"is_correct": bool, "answer": int, "explanation": str}`. 404 if question id unknown. Side effect: records the attempt.

- [ ] **Step 1: Write the failing test**

`backend/tests/test_attempts_api.py`:
```python
def test_correct_attempt(client):
    resp = client.post("/attempts", json={"question_id": "ds-arrays-001", "chosen": 0})
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_correct"] is True
    assert body["answer"] == 0
    assert "Direct address" in body["explanation"]


def test_wrong_attempt(client):
    resp = client.post("/attempts", json={"question_id": "ds-arrays-001", "chosen": 1})
    body = resp.json()
    assert body["is_correct"] is False
    assert body["answer"] == 0


def test_unknown_question_404(client):
    resp = client.post("/attempts", json={"question_id": "nope", "chosen": 0})
    assert resp.status_code == 404


def test_attempt_is_recorded(client):
    client.post("/attempts", json={"question_id": "ds-arrays-001", "chosen": 1})
    wrong = client.get("/questions", params={"only_wrong": "true"}).json()
    assert [q["id"] for q in wrong] == ["ds-arrays-001"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_attempts_api.py -v`
Expected: FAIL — 404 on `/attempts` (route missing).

- [ ] **Step 3: Write the router**

`backend/app/api/attempts.py`:
```python
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from ..db.attempts import record_attempt

router = APIRouter()


class AttemptIn(BaseModel):
    question_id: str
    chosen: int


@router.post("/attempts")
def post_attempt(request: Request, attempt: AttemptIn):
    by_id = {q.id: q for q in request.app.state.questions}
    q = by_id.get(attempt.question_id)
    if q is None:
        raise HTTPException(status_code=404, detail="question not found")
    is_correct = attempt.chosen == q.answer
    record_attempt(request.app.state.db, q.id, is_correct, attempt.chosen)
    return {"is_correct": is_correct, "answer": q.answer, "explanation": q.explanation}
```

- [ ] **Step 4: Register the router in main.py**

Update the block to:
```python
    from .api import subjects, questions, attempts
    app.include_router(subjects.router)
    app.include_router(questions.router)
    app.include_router(attempts.router)
```

- [ ] **Step 5: Run all API tests to verify they pass**

Run: `python -m pytest tests/test_attempts_api.py tests/test_questions_api.py -v`
Expected: PASS — including the previously-deferred `test_questions_only_wrong`.

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/attempts.py backend/app/main.py backend/tests/test_attempts_api.py
git commit -m "feat: add POST /attempts endpoint"
```

---

## Task 8: Stats service + GET /stats endpoint

**Files:**
- Create: `backend/app/stats_service.py`
- Create: `backend/app/api/stats.py`
- Modify: `backend/app/main.py` (register router)
- Test: `backend/tests/test_stats_api.py`

**Interfaces:**
- Produces: `compute_stats(conn, questions) -> dict` with keys `by_subject`, `by_difficulty` (each a list of `{name, correct, attempted, accuracy}`-shaped rows using `subject`/`difficulty` key respectively) and `weakest_questions` (list of `{question_id, wrong, total}`, top 10 by wrong count desc).
- Produces: `GET /stats` -> that dict.

- [ ] **Step 1: Write the failing test**

`backend/tests/test_stats_api.py`:
```python
def test_stats_empty(client):
    data = client.get("/stats").json()
    assert data["by_subject"] == []
    assert data["weakest_questions"] == []


def test_stats_after_attempts(client):
    client.post("/attempts", json={"question_id": "ds-arrays-001", "chosen": 1})  # wrong
    client.post("/attempts", json={"question_id": "ds-arrays-001", "chosen": 0})  # right
    client.post("/attempts", json={"question_id": "en-vocab-001", "chosen": 1})   # right
    data = client.get("/stats").json()

    ds = next(r for r in data["by_subject"] if r["subject"] == "data-structures")
    assert ds["attempted"] == 2
    assert ds["correct"] == 1
    assert ds["accuracy"] == 0.5

    weak = data["weakest_questions"]
    assert weak[0]["question_id"] == "ds-arrays-001"
    assert weak[0]["wrong"] == 1
    assert weak[0]["total"] == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_stats_api.py -v`
Expected: FAIL — 404 on `/stats`.

- [ ] **Step 3: Write the stats service**

`backend/app/stats_service.py`:
```python
import sqlite3
from collections import defaultdict


def compute_stats(conn: sqlite3.Connection, questions) -> dict:
    by_id = {q.id: q for q in questions}
    rows = conn.execute(
        "SELECT question_id, is_correct FROM attempts"
    ).fetchall()

    subj: dict[str, list[int]] = defaultdict(lambda: [0, 0])   # [correct, total]
    diff: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    perq: dict[str, list[int]] = defaultdict(lambda: [0, 0])   # [wrong, total]

    for r in rows:
        q = by_id.get(r["question_id"])
        if q is None:
            continue
        correct = r["is_correct"]
        subj[q.subject][0] += correct
        subj[q.subject][1] += 1
        diff[q.difficulty][0] += correct
        diff[q.difficulty][1] += 1
        perq[r["question_id"]][0] += 0 if correct else 1
        perq[r["question_id"]][1] += 1

    def _acc(c: int, t: int) -> float:
        return round(c / t, 3) if t else 0.0

    by_subject = [
        {"subject": s, "correct": v[0], "attempted": v[1], "accuracy": _acc(*v)}
        for s, v in sorted(subj.items())
    ]
    by_difficulty = [
        {"difficulty": d, "correct": v[0], "attempted": v[1], "accuracy": _acc(*v)}
        for d, v in sorted(diff.items())
    ]
    weakest = sorted(
        (
            {"question_id": qid, "wrong": v[0], "total": v[1]}
            for qid, v in perq.items()
            if v[0] > 0
        ),
        key=lambda x: (-x["wrong"], x["question_id"]),
    )[:10]
    return {
        "by_subject": by_subject,
        "by_difficulty": by_difficulty,
        "weakest_questions": weakest,
    }
```

- [ ] **Step 4: Write the router**

`backend/app/api/stats.py`:
```python
from fastapi import APIRouter, Request
from ..stats_service import compute_stats

router = APIRouter()


@router.get("/stats")
def get_stats(request: Request):
    return compute_stats(request.app.state.db, request.app.state.questions)
```

- [ ] **Step 5: Register the router in main.py**

Update the block to:
```python
    from .api import subjects, questions, attempts, stats
    app.include_router(subjects.router)
    app.include_router(questions.router)
    app.include_router(attempts.router)
    app.include_router(stats.router)
```

- [ ] **Step 6: Run test to verify it passes**

Run: `python -m pytest tests/test_stats_api.py -v`
Expected: PASS (2 passed).

- [ ] **Step 7: Commit**

```bash
git add backend/app/stats_service.py backend/app/api/stats.py backend/app/main.py backend/tests/test_stats_api.py
git commit -m "feat: add stats service and GET /stats endpoint"
```

---

## Task 9: GET /tutorials/{subject}/{topic} endpoint

**Files:**
- Create: `backend/app/api/tutorials.py`
- Modify: `backend/app/main.py` (register router)
- Test: `backend/tests/test_tutorials_api.py`

**Interfaces:**
- Consumes: `request.app.state.content_dir`.
- Produces: `GET /tutorials/{subject}/{topic}` -> `{"subject", "topic", "markdown"}`. 404 if `content_dir/subject/topic.md` does not exist.

- [ ] **Step 1: Write the failing test**

`backend/tests/test_tutorials_api.py`:
```python
def test_tutorial_returns_markdown(client):
    resp = client.get("/tutorials/data-structures/arrays")
    assert resp.status_code == 200
    body = resp.json()
    assert body["subject"] == "data-structures"
    assert "Contiguous memory" in body["markdown"]


def test_missing_tutorial_404(client):
    resp = client.get("/tutorials/english/vocabulary")
    assert resp.status_code == 404
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_tutorials_api.py -v`
Expected: FAIL — 404 on both (route missing; second would coincidentally 404 but first must pass after impl).

- [ ] **Step 3: Write the router**

`backend/app/api/tutorials.py`:
```python
from fastapi import APIRouter, Request, HTTPException

router = APIRouter()


@router.get("/tutorials/{subject}/{topic}")
def get_tutorial(request: Request, subject: str, topic: str):
    path = request.app.state.content_dir / subject / f"{topic}.md"
    if not path.exists():
        raise HTTPException(status_code=404, detail="tutorial not found")
    return {
        "subject": subject,
        "topic": topic,
        "markdown": path.read_text(encoding="utf-8"),
    }
```

- [ ] **Step 4: Register the router in main.py**

Update the block to:
```python
    from .api import subjects, questions, attempts, stats, tutorials
    app.include_router(subjects.router)
    app.include_router(questions.router)
    app.include_router(attempts.router)
    app.include_router(stats.router)
    app.include_router(tutorials.router)
```

- [ ] **Step 5: Run the full backend suite**

Run: `python -m pytest tests/ -v`
Expected: PASS (all tests across all files).

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/tutorials.py backend/app/main.py backend/tests/test_tutorials_api.py
git commit -m "feat: add GET /tutorials endpoint"
```

---

## Task 10: Seed content (real question banks)

**Files:**
- Create: `content/data-structures/arrays.yaml`
- Create: `content/data-structures/arrays.md`
- Create: `content/data-structures/linked-lists.yaml`
- Create: `content/algorithms/sorting.yaml`
- Create: `content/english/vocabulary.yaml`
- Create: `content/english/communication.yaml`

**Interfaces:**
- Consumes: schema from Task 1 (every question must validate).
- Produces: a real bank the running app serves. No new code.

This task has no unit test; verification is "the loader accepts every file."

- [ ] **Step 1: Write data-structures/arrays.yaml**

```yaml
- id: ds-arrays-001
  difficulty: basic
  tags: [arrays, complexity]
  question: |
    存取陣列中第 i 個元素 (random access) 的時間複雜度是？
  options: ["O(1)", "O(n)", "O(log n)", "O(n log n)"]
  answer: 0
  explanation: |
    陣列是連續記憶體，元素位址 = 起始位址 + i * 元素大小，可直接計算，故 O(1)。
- id: ds-arrays-002
  difficulty: basic
  tags: [arrays]
  question: |
    在動態陣列 (dynamic array) 尾端 append 一個元素的「攤平 (amortized)」時間複雜度是？
  options: ["O(1)", "O(n)", "O(log n)", "O(n^2)"]
  answer: 0
  explanation: |
    多數 append 是 O(1)；偶爾需要擴容並複製整個陣列為 O(n)，但攤平後仍是 O(1)。
- id: ds-arrays-003
  difficulty: intermediate
  tags: [arrays, insertion]
  question: |
    在長度為 n 的陣列「開頭」插入一個元素，最差情況時間複雜度是？
  options: ["O(1)", "O(log n)", "O(n)", "O(n log n)"]
  answer: 2
  explanation: |
    開頭插入需把後面 n 個元素全部往後搬一格，故 O(n)。
```

- [ ] **Step 2: Write data-structures/arrays.md**

```markdown
# 陣列 (Arrays)

## 核心概念
陣列是一段**連續的記憶體**，每個元素大小相同。第 i 個元素的位址可由
`base + i * size` 直接算出，因此**隨機存取是 O(1)**。

## 複雜度速查
| 操作 | 複雜度 | 原因 |
|------|--------|------|
| 隨機存取 `a[i]` | O(1) | 位址直接計算 |
| 尾端 append (動態陣列) | 攤平 O(1) | 偶爾擴容 O(n) |
| 開頭/中間插入 | O(n) | 需搬移後續元素 |
| 搜尋 (未排序) | O(n) | 逐一比對 |

## 什麼時候用
需要大量隨機存取、且元素數量變動不大時。若頻繁在開頭插入/刪除，考慮 linked list 或 deque。
```

- [ ] **Step 3: Write data-structures/linked-lists.yaml**

```yaml
- id: ds-linked-001
  difficulty: basic
  tags: [linked-list]
  question: |
    已知某節點的指標，在 singly linked list 中於其「後面」插入一個新節點，時間複雜度是？
  options: ["O(1)", "O(n)", "O(log n)", "O(n^2)"]
  answer: 0
  explanation: |
    只需改兩個指標即可，與串列長度無關，故 O(1)。
- id: ds-linked-002
  difficulty: basic
  tags: [linked-list, access]
  question: |
    在 singly linked list 中存取第 i 個元素的時間複雜度是？
  options: ["O(1)", "O(n)", "O(log n)", "O(1) 攤平"]
  answer: 1
  explanation: |
    linked list 不支援隨機存取，必須從頭沿指標走 i 步，故 O(n)。
- id: ds-linked-003
  difficulty: intermediate
  tags: [linked-list, comparison]
  question: |
    相較於陣列，linked list 的主要「缺點」是下列何者？
  options:
    - 無法在中間插入元素
    - 不支援 O(1) 隨機存取，且每個節點有額外指標記憶體開銷
    - 無法儲存任意型別
    - 一定比陣列慢
  answer: 1
  explanation: |
    linked list 失去 O(1) 隨機存取，且每節點要存指標 (額外記憶體)；但在已知位置插入/刪除是 O(1)。
```

- [ ] **Step 4: Write algorithms/sorting.yaml**

```yaml
- id: algo-sort-001
  difficulty: basic
  tags: [sorting, complexity]
  question: |
    Quicksort 的「平均」時間複雜度是？
  options: ["O(n)", "O(n log n)", "O(n^2)", "O(log n)"]
  answer: 1
  explanation: |
    平均 O(n log n)；最差情況 (已排序 + 差的 pivot) 才退化為 O(n^2)。
- id: algo-sort-002
  difficulty: intermediate
  tags: [sorting, stability]
  question: |
    下列哪個排序演算法是「穩定 (stable)」的？
  options: ["Quicksort", "Heapsort", "Merge sort", "Selection sort"]
  answer: 2
  explanation: |
    Merge sort 在合併時保留相等元素的相對順序，故穩定。Quicksort/Heapsort/Selection sort 一般不穩定。
- id: algo-sort-003
  difficulty: advanced
  tags: [sorting, lower-bound]
  question: |
    任何「以比較為基礎 (comparison-based)」的排序，最差情況下的時間複雜度下界是？
  options: ["O(n)", "O(n log n)", "O(log n)", "O(n^2)"]
  answer: 1
  explanation: |
    比較排序的決策樹有 n! 個葉節點，高度至少 log(n!) = Θ(n log n)，故下界為 Ω(n log n)。
```

- [ ] **Step 5: Write english/vocabulary.yaml**

```yaml
- id: en-vocab-001
  difficulty: basic
  tags: [vocabulary]
  question: |
    In software, an API marked as "deprecated" means it is:
  options:
    - recommended as the new standard
    - still supported but discouraged and may be removed later
    - permanently deleted already
    - faster than alternatives
  answer: 1
  explanation: |
    Deprecated = 仍可用但「不建議使用」，通常未來版本會移除。
- id: en-vocab-002
  difficulty: basic
  tags: [vocabulary]
  question: |
    Your teammate says a fix is "idempotent". This means running it multiple times:
  options:
    - produces the same result as running it once
    - doubles the effect each time
    - is not allowed
    - requires a restart
  answer: 0
  explanation: |
    Idempotent = 執行一次或多次結果相同，常見於 REST / 部署腳本的描述。
- id: en-vocab-003
  difficulty: intermediate
  tags: [vocabulary]
  question: |
    "Let's not bikeshed this" in a design discussion suggests you should:
  options:
    - paint the bike shed first
    - avoid spending too much time on trivial details
    - assign more reviewers
    - revert the change
  answer: 1
  explanation: |
    Bikeshedding = 在瑣碎小事上過度爭論。這句是提醒大家別糾結細節。
```

- [ ] **Step 6: Write english/communication.yaml**

```yaml
- id: en-comm-001
  difficulty: intermediate
  tags: [communication, code-review]
  question: |
    In a code review you spot a likely bug. Which comment is most professional and constructive?
  options:
    - "This is wrong."
    - "Did you even test this?"
    - "I think this might break when the list is empty — could we add a guard or a test for that case?"
    - "Please fix."
  answer: 2
  explanation: |
    具體指出情境、用提問語氣、提供可行建議——這是外商 code review 的標準溝通方式。
- id: en-comm-002
  difficulty: intermediate
  tags: [communication, standup]
  question: |
    You are blocked in standup. Which update is clearest and most accountable?
  options:
    - "I'm stuck on stuff."
    - "Nothing works, not my fault."
    - "I'm blocked on the payment API returning 500s; I've opened a ticket and will pair with Sara after standup."
    - "Still working on it."
  answer: 2
  explanation: |
    說明「卡在哪、已採取什麼行動、下一步」——清楚、不甩鍋、可被協助。
- id: en-comm-003
  difficulty: advanced
  tags: [communication, disagreement]
  question: |
    You disagree with a reviewer's suggestion. Which reply best balances respect and pushback?
  options:
    - "No."
    - "You don't understand the code."
    - "I see your point on readability. I kept it this way for performance — here's a benchmark. Open to alternatives if you know a cleaner approach."
    - "Whatever you say."
  answer: 2
  explanation: |
    先認同對方觀點、給出有數據的理由、保持開放——這是 senior 工程師有效表達不同意見的方式。
```

- [ ] **Step 7: Verify the loader accepts the whole bank**

Run (from `backend/`, venv active):
```
python -c "from app.config import CONTENT_DIR; from app.content.loader import load_questions; qs = load_questions(CONTENT_DIR); print(len(qs), 'questions loaded')"
```
Expected: prints `18 questions loaded` (3+3+3+3+3+3) with no exception.

- [ ] **Step 8: Commit**

```bash
git add content/
git commit -m "content: add seed banks for data structures, algorithms, english"
```

---

## Task 11: Frontend scaffold + API client + nav shell

**Files:**
- Create: `frontend/` (via Vite), then `frontend/src/api/client.js`, `frontend/src/App.jsx`, `frontend/src/main.jsx`, `frontend/src/styles.css`
- Create: `frontend/.env` (API base URL)

**Interfaces:**
- Produces: `client.js` exporting `getSubjects()`, `getQuestions(params)`, `postAttempt(questionId, chosen)`, `getStats()`, `getTutorial(subject, topic)` — all returning parsed JSON.
- Produces: `App.jsx` with React Router routes for `/` (Dashboard), `/practice`, `/tutorial/:subject/:topic`, `/browse` and a top nav.

Frontend tasks use **manual verification** (run the app, observe), per the spec's testing strategy.

- [ ] **Step 1: Scaffold the Vite app**

Run (PowerShell, from project root):
```
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install react-router-dom
```

- [ ] **Step 2: Create the API client**

`frontend/src/api/client.js`:
```javascript
const BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function get(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`GET ${path} -> ${res.status}`);
  return res.json();
}

export function getSubjects() {
  return get("/subjects");
}

export function getQuestions({ subject, topic, difficulty, onlyWrong } = {}) {
  const p = new URLSearchParams();
  if (subject) p.set("subject", subject);
  if (topic) p.set("topic", topic);
  if (difficulty) p.set("difficulty", difficulty);
  if (onlyWrong) p.set("only_wrong", "true");
  const qs = p.toString();
  return get(`/questions${qs ? `?${qs}` : ""}`);
}

export async function postAttempt(questionId, chosen) {
  const res = await fetch(`${BASE}/attempts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question_id: questionId, chosen }),
  });
  if (!res.ok) throw new Error(`POST /attempts -> ${res.status}`);
  return res.json();
}

export function getStats() {
  return get("/stats");
}

export function getTutorial(subject, topic) {
  return get(`/tutorials/${subject}/${topic}`);
}
```

- [ ] **Step 3: Create the env file**

`frontend/.env`:
```
VITE_API_BASE=http://localhost:8000
```

- [ ] **Step 4: Write App.jsx (router + nav)**

`frontend/src/App.jsx`:
```jsx
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Practice from "./pages/Practice";
import Tutorial from "./pages/Tutorial";
import Browse from "./pages/Browse";

export default function App() {
  return (
    <BrowserRouter>
      <nav className="nav">
        <Link to="/">儀表板</Link>
        <Link to="/practice">練習</Link>
        <Link to="/browse">瀏覽</Link>
      </nav>
      <main className="main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/practice" element={<Practice />} />
          <Route path="/tutorial/:subject/:topic" element={<Tutorial />} />
          <Route path="/browse" element={<Browse />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
```

- [ ] **Step 5: Replace main.jsx and add styles**

`frontend/src/main.jsx`:
```jsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

`frontend/src/styles.css`:
```css
* { box-sizing: border-box; }
body { margin: 0; font-family: system-ui, "Segoe UI", sans-serif; color: #1a1a1a; }
.nav { display: flex; gap: 16px; padding: 12px 20px; background: #11283b; }
.nav a { color: #cfe3f5; text-decoration: none; font-weight: 600; }
.nav a:hover { color: #fff; }
.main { max-width: 760px; margin: 0 auto; padding: 24px 20px; }
.card { border: 1px solid #e0e0e0; border-radius: 10px; padding: 20px; margin-bottom: 16px; }
.option { display: block; width: 100%; text-align: left; padding: 12px 14px; margin: 8px 0;
  border: 1px solid #ccc; border-radius: 8px; background: #fff; cursor: pointer; font-size: 15px; }
.option:hover { background: #f3f7fb; }
.option.correct { background: #e6f7ec; border-color: #2e9e5b; }
.option.wrong { background: #fdecec; border-color: #d24a4a; }
.explanation { margin-top: 12px; padding: 12px; background: #f7f9fb; border-radius: 8px; }
button.primary { padding: 10px 18px; border: 0; border-radius: 8px; background: #1e6fd0;
  color: #fff; font-weight: 600; cursor: pointer; }
.filters { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 16px; }
.filters select, .filters label { font-size: 14px; }
.stat-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #eee; }
```

- [ ] **Step 6: Add placeholder pages so the app boots**

Create minimal placeholders (replaced in later tasks). For each of `Dashboard.jsx`, `Practice.jsx`, `Tutorial.jsx`, `Browse.jsx` in `frontend/src/pages/`:

`frontend/src/pages/Dashboard.jsx`:
```jsx
export default function Dashboard() {
  return <div>Dashboard</div>;
}
```
`frontend/src/pages/Practice.jsx`:
```jsx
export default function Practice() {
  return <div>Practice</div>;
}
```
`frontend/src/pages/Tutorial.jsx`:
```jsx
export default function Tutorial() {
  return <div>Tutorial</div>;
}
```
`frontend/src/pages/Browse.jsx`:
```jsx
export default function Browse() {
  return <div>Browse</div>;
}
```

- [ ] **Step 7: Manual verification**

Terminal 1 (backend, from `backend/` with venv active): `uvicorn app.main:app --reload`
Terminal 2 (frontend, from `frontend/`): `npm run dev`
Open `http://localhost:5173`. Expected: nav bar with 儀表板 / 練習 / 瀏覽; clicking each shows its placeholder text; no console errors.

- [ ] **Step 8: Commit**

```bash
git add frontend/ -- ":!frontend/node_modules"
git commit -m "feat: scaffold frontend with router, nav, and api client"
```

---

## Task 12: Practice page (core drilling UI)

**Files:**
- Create: `frontend/src/components/Filters.jsx`
- Create: `frontend/src/components/QuestionCard.jsx`
- Modify: `frontend/src/pages/Practice.jsx`

**Interfaces:**
- Consumes: `getSubjects`, `getQuestions`, `postAttempt` from `api/client`.
- `Filters` props: `{ subjects, value, onChange }` where `value = { subject, topic, difficulty, onlyWrong }`.
- `QuestionCard` props: `{ question, onAnswered }`. On option click: calls `postAttempt(question.id, idx)`, shows correct/wrong styling + explanation from the response, then a "下一題" button calling `onAnswered`.

- [ ] **Step 1: Write Filters.jsx**

`frontend/src/components/Filters.jsx`:
```jsx
const DIFFICULTIES = ["basic", "intermediate", "advanced", "master"];

export default function Filters({ subjects, value, onChange }) {
  const topics = subjects.find((s) => s.subject === value.subject)?.topics || [];
  return (
    <div className="filters">
      <select
        value={value.subject}
        onChange={(e) => onChange({ ...value, subject: e.target.value, topic: "" })}
      >
        <option value="">全部科目</option>
        {subjects.map((s) => (
          <option key={s.subject} value={s.subject}>{s.subject}</option>
        ))}
      </select>

      <select
        value={value.topic}
        onChange={(e) => onChange({ ...value, topic: e.target.value })}
        disabled={!value.subject}
      >
        <option value="">全部主題</option>
        {topics.map((t) => (
          <option key={t} value={t}>{t}</option>
        ))}
      </select>

      <select
        value={value.difficulty}
        onChange={(e) => onChange({ ...value, difficulty: e.target.value })}
      >
        <option value="">全部難度</option>
        {DIFFICULTIES.map((d) => (
          <option key={d} value={d}>{d}</option>
        ))}
      </select>

      <label>
        <input
          type="checkbox"
          checked={value.onlyWrong}
          onChange={(e) => onChange({ ...value, onlyWrong: e.target.checked })}
        />
        只練我錯過的
      </label>
    </div>
  );
}
```

- [ ] **Step 2: Write QuestionCard.jsx**

`frontend/src/components/QuestionCard.jsx`:
```jsx
import { useState } from "react";
import { postAttempt } from "../api/client";

export default function QuestionCard({ question, onAnswered }) {
  const [result, setResult] = useState(null); // { is_correct, answer, explanation }
  const [chosen, setChosen] = useState(null);

  async function choose(idx) {
    if (result) return; // already answered
    setChosen(idx);
    const r = await postAttempt(question.id, idx);
    setResult(r);
  }

  function optionClass(idx) {
    if (!result) return "option";
    if (idx === result.answer) return "option correct";
    if (idx === chosen) return "option wrong";
    return "option";
  }

  return (
    <div className="card">
      <div style={{ color: "#888", fontSize: 13 }}>
        {question.subject} · {question.topic} · {question.difficulty}
      </div>
      <p style={{ whiteSpace: "pre-wrap", fontWeight: 600 }}>{question.question}</p>
      {question.options.map((opt, idx) => (
        <button key={idx} className={optionClass(idx)} onClick={() => choose(idx)}>
          {opt}
        </button>
      ))}
      {result && (
        <div className="explanation">
          <strong>{result.is_correct ? "✅ 答對了" : "❌ 答錯了"}</strong>
          <p style={{ whiteSpace: "pre-wrap" }}>{result.explanation}</p>
          <button className="primary" onClick={onAnswered}>下一題</button>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 3: Write Practice.jsx**

`frontend/src/pages/Practice.jsx`:
```jsx
import { useEffect, useState } from "react";
import { getSubjects, getQuestions } from "../api/client";
import Filters from "../components/Filters";
import QuestionCard from "../components/QuestionCard";

const EMPTY = { subject: "", topic: "", difficulty: "", onlyWrong: false };

export default function Practice() {
  const [subjects, setSubjects] = useState([]);
  const [filters, setFilters] = useState(EMPTY);
  const [queue, setQueue] = useState([]);
  const [idx, setIdx] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getSubjects().then(setSubjects);
  }, []);

  async function start() {
    setLoading(true);
    const qs = await getQuestions({
      subject: filters.subject,
      topic: filters.topic,
      difficulty: filters.difficulty,
      onlyWrong: filters.onlyWrong,
    });
    // shuffle for variety
    setQueue([...qs].sort(() => Math.random() - 0.5));
    setIdx(0);
    setLoading(false);
  }

  const current = queue[idx];

  return (
    <div>
      <h2>練習</h2>
      <Filters subjects={subjects} value={filters} onChange={setFilters} />
      <button className="primary" onClick={start}>開始練習</button>

      {loading && <p>載入中…</p>}
      {!loading && queue.length > 0 && !current && <p>本輪結束 🎉 共 {queue.length} 題。</p>}
      {!loading && queue.length === 0 && <p style={{ color: "#888" }}>選好條件後按「開始練習」。</p>}

      {current && (
        <>
          <p style={{ color: "#888" }}>第 {idx + 1} / {queue.length} 題</p>
          <QuestionCard
            key={current.id}
            question={current}
            onAnswered={() => setIdx((i) => i + 1)}
          />
        </>
      )}
    </div>
  );
}
```

- [ ] **Step 4: Manual verification**

With backend + frontend running, go to `/practice`. Expected:
1. Filters populate from `/subjects`.
2. "開始練習" loads questions; one card shows at a time.
3. Clicking an option locks the card, highlights the correct answer green (and your wrong pick red), shows the explanation.
4. "下一題" advances; after the last question you see "本輪結束".
5. Check the wrong-book: deliberately answer one wrong, then tick "只練我錯過的" and 開始練習 — only wrongly-answered questions appear.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/Filters.jsx frontend/src/components/QuestionCard.jsx frontend/src/pages/Practice.jsx
git commit -m "feat: add practice page with filters and instant feedback"
```

---

## Task 13: Dashboard + Tutorial + Browse pages

**Files:**
- Modify: `frontend/src/pages/Dashboard.jsx`
- Modify: `frontend/src/pages/Tutorial.jsx`
- Modify: `frontend/src/pages/Browse.jsx`
- Modify: `frontend/package.json` (add `marked` for Markdown rendering)

**Interfaces:**
- Consumes: `getStats`, `getTutorial`, `getQuestions` from `api/client`.
- Tutorial route is `/tutorial/:subject/:topic`; renders Markdown via `marked`.

- [ ] **Step 1: Install markdown renderer**

Run (from `frontend/`): `npm install marked`

- [ ] **Step 2: Write Dashboard.jsx**

`frontend/src/pages/Dashboard.jsx`:
```jsx
import { useEffect, useState } from "react";
import { getStats } from "../api/client";

export default function Dashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    getStats().then(setStats);
  }, []);

  if (!stats) return <p>載入中…</p>;

  const attempted = stats.by_subject.reduce((n, r) => n + r.attempted, 0);

  return (
    <div>
      <h2>儀表板</h2>
      {attempted === 0 && <p style={{ color: "#888" }}>還沒有作答紀錄。去「練習」開始第一題吧！</p>}

      <div className="card">
        <h3>各科正確率</h3>
        {stats.by_subject.length === 0 && <p style={{ color: "#888" }}>—</p>}
        {stats.by_subject.map((r) => (
          <div className="stat-row" key={r.subject}>
            <span>{r.subject}</span>
            <span>{r.correct}/{r.attempted} ({Math.round(r.accuracy * 100)}%)</span>
          </div>
        ))}
      </div>

      <div className="card">
        <h3>最常錯的題目</h3>
        {stats.weakest_questions.length === 0 && <p style={{ color: "#888" }}>—</p>}
        {stats.weakest_questions.map((q) => (
          <div className="stat-row" key={q.question_id}>
            <span>{q.question_id}</span>
            <span>錯 {q.wrong} / 共 {q.total} 次</span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Write Tutorial.jsx**

`frontend/src/pages/Tutorial.jsx`:
```jsx
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { marked } from "marked";
import { getTutorial } from "../api/client";

export default function Tutorial() {
  const { subject, topic } = useParams();
  const [html, setHtml] = useState("");
  const [error, setError] = useState(false);

  useEffect(() => {
    setError(false);
    getTutorial(subject, topic)
      .then((t) => setHtml(marked.parse(t.markdown)))
      .catch(() => setError(true));
  }, [subject, topic]);

  if (error) return <p>這個主題還沒有教學文章。</p>;
  return <div dangerouslySetInnerHTML={{ __html: html }} />;
}
```

- [ ] **Step 4: Write Browse.jsx**

`frontend/src/pages/Browse.jsx`:
```jsx
import { useEffect, useState } from "react";
import { getQuestions } from "../api/client";

export default function Browse() {
  const [questions, setQuestions] = useState([]);
  const [q, setQ] = useState("");

  useEffect(() => {
    getQuestions().then(setQuestions);
  }, []);

  const filtered = questions.filter((item) =>
    item.question.toLowerCase().includes(q.toLowerCase()) ||
    item.id.toLowerCase().includes(q.toLowerCase())
  );

  return (
    <div>
      <h2>瀏覽題庫 ({questions.length})</h2>
      <input
        placeholder="搜尋題目或 id…"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        style={{ width: "100%", padding: 10, marginBottom: 16 }}
      />
      {filtered.map((item) => (
        <div className="card" key={item.id}>
          <div style={{ color: "#888", fontSize: 13 }}>
            {item.id} · {item.subject} · {item.difficulty}
          </div>
          <p style={{ whiteSpace: "pre-wrap" }}>{item.question}</p>
          <ul>
            {item.options.map((opt, idx) => (
              <li key={idx} style={{ fontWeight: idx === item.answer ? 700 : 400 }}>
                {opt}{idx === item.answer ? "  ✅" : ""}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
```

- [ ] **Step 5: Manual verification**

With backend + frontend running:
1. `/` (Dashboard): after answering a few questions in Practice, shows per-subject accuracy and most-wrong questions. With zero attempts shows the empty hint.
2. `/tutorial/data-structures/arrays`: renders the arrays Markdown as formatted HTML (heading, table).
3. `/tutorial/english/vocabulary`: shows "還沒有教學文章" (no .md file).
4. `/browse`: lists all 18 questions; typing in the search box filters; correct option is bold with ✅.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/pages/Dashboard.jsx frontend/src/pages/Tutorial.jsx frontend/src/pages/Browse.jsx frontend/package.json frontend/package-lock.json
git commit -m "feat: add dashboard, tutorial, and browse pages"
```

---

## Self-Review Notes

- **Spec coverage:** content format (Task 1, 10), loader (Task 2), SQLite attempts-only (Task 3), all 5 API endpoints (Tasks 5–9), wrong-book tracking via latest-attempt (Task 3, exercised in 6/7), stats/weak-spots (Task 8), four frontend screens — dashboard, practice, tutorial, browse (Tasks 11–13), seed banks for data-structures + algorithms + english (Task 10), pytest backend + schema validation + manual frontend verification (throughout). All spec sections map to a task.
- **Deferred (per spec, intentionally absent):** spaced repetition, CAG tutor, flashcards/open-ended/code-runner, English speaking — none appear here.
- **Type consistency:** `record_attempt(conn, question_id, is_correct, chosen)`, `wrong_question_ids(conn) -> set[str]`, `compute_stats(conn, questions)`, `LoadedQuestion` with `subject`/`topic`, and POST /attempts returning `{is_correct, answer, explanation}` are used identically wherever referenced across tasks.
