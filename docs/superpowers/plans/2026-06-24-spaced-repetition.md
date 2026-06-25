# Spaced Repetition (Leitner) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> Before starting, read [AGENTS.md](../../../AGENTS.md) and [HANDOFF.md](../../HANDOFF.md). Design rationale: [spaced-repetition design spec](../specs/2026-06-24-spaced-repetition-design.md).

**Goal:** Add Leitner-box spaced repetition so the app schedules which questions are due each day, updating each question's schedule on every answer.

**Architecture:** A pure-logic `scheduler_service` computes `(new_box, new_due_date)` from `(current_box, is_correct, today)`. A new `schedule` SQLite table (one row per question) holds the derived state; a `schedule` repository reads/writes it. `POST /attempts` reschedules the answered question. `GET /review` returns today's due questions (sorted); `GET /stats` gains `due_today`. The frontend adds a Review page and a dashboard due-count.

**Tech Stack:** Python 3.11+, FastAPI, SQLite (stdlib sqlite3), pytest; React + Vite (existing frontend).

## Global Constraints

- SQLite stores ONLY derived/behavioral state. Question content is NEVER written to the DB — questions come from `app.state.questions` / `app.state.questions_by_id`, loaded from YAML at startup. The `schedule` table stores only `question_id` + scheduling numbers.
- `attempts` table is the immutable fact log and MUST NOT be changed by this feature.
- Leitner boxes are integers 1..5. `INTERVALS = {1: 1, 2: 3, 3: 7, 4: 16, 5: 35}` (days). `MAX_BOX = 5`.
- Transition (applied to the PRE-answer box; a never-scheduled question uses `current_box = 1`): correct → `min(box + 1, 5)`; wrong → `1`. Then `due_date = today + INTERVALS[new_box]` days.
- Dates are stored and compared as `YYYY-MM-DD` ISO strings (`date.isoformat()`); ISO date strings compare correctly with `<=`.
- "Today" is the server local date: `datetime.date.today()`. Pure functions and repository functions take `today` as a parameter (never call `date.today()` inside them) so tests can pass a fixed date.
- Review list ordering: `due_date ASC, box ASC, question_id ASC` (most-overdue first, then lowest box, then stable by id).
- A question id present in `schedule` but absent from the loaded bank (deleted from YAML) is skipped in `/review` — consistent with stats' stale-attempt handling.
- Run backend tests from `backend/` with the venv active: `python -m pytest`. All file reads/writes use `encoding="utf-8"`.

---

## File Structure

```
backend/app/
  scheduler_service.py     CREATE  pure Leitner logic: next_schedule(current_box, is_correct, today)
  db/schedule.py           CREATE  schedule repository: get_box / upsert_schedule / due_question_ids / due_count
  db/database.py           MODIFY  add `schedule` table to init schema
  api/attempts.py          MODIFY  after recording an attempt, reschedule the question
  api/review.py            CREATE  GET /review
  stats_service.py         MODIFY  compute_stats gains a `today` param and returns `due_today`
  api/stats.py             MODIFY  pass date.today() into compute_stats
  main.py                  MODIFY  register review router
backend/tests/
  test_scheduler_service.py  CREATE
  test_schedule_repo.py      CREATE
  test_review_api.py         CREATE
  test_attempts_api.py       MODIFY  assert reschedule side effect
  test_stats_api.py          MODIFY  assert due_today
frontend/src/
  api/client.js            MODIFY  add getReview()
  pages/Review.jsx         CREATE  review drilling page (reuses QuestionCard)
  App.jsx                  MODIFY  add /review route + nav link
  pages/Dashboard.jsx      MODIFY  add "today's reviews" block
```

Each backend file has one responsibility (pure logic / persistence / one endpoint). The pure `scheduler_service` carries the load-bearing algorithm and is unit-tested in isolation.

---

## Task 1: Scheduler service (pure Leitner logic)

**Files:**
- Create: `backend/app/scheduler_service.py`
- Test: `backend/tests/test_scheduler_service.py`

**Interfaces:**
- Produces: `INTERVALS: dict[int, int]` = `{1:1, 2:3, 3:7, 4:16, 5:35}`, `MAX_BOX = 5`.
- Produces: `next_schedule(current_box: int, is_correct: bool, today: datetime.date) -> tuple[int, datetime.date]`. Returns `(new_box, new_due_date)`. Correct → `min(current_box+1, 5)`; wrong → `1`; `new_due_date = today + INTERVALS[new_box]` days. No DB, no `date.today()` inside.

- [x] **Step 1: Write the failing test**

`backend/tests/test_scheduler_service.py`:
```python
from datetime import date, timedelta
from app.scheduler_service import next_schedule, INTERVALS, MAX_BOX

TODAY = date(2026, 6, 24)


def test_correct_promotes_one_box():
    box, due = next_schedule(2, True, TODAY)
    assert box == 3
    assert due == TODAY + timedelta(days=INTERVALS[3])


def test_wrong_resets_to_box_one():
    box, due = next_schedule(4, False, TODAY)
    assert box == 1
    assert due == TODAY + timedelta(days=1)


def test_correct_caps_at_max_box():
    box, due = next_schedule(MAX_BOX, True, TODAY)
    assert box == MAX_BOX
    assert due == TODAY + timedelta(days=INTERVALS[MAX_BOX])


def test_first_correct_vs_first_wrong_differ():
    # A never-scheduled question is passed current_box=1 by the caller.
    correct_box, correct_due = next_schedule(1, True, TODAY)
    wrong_box, wrong_due = next_schedule(1, False, TODAY)
    assert correct_box == 2 and correct_due == TODAY + timedelta(days=3)
    assert wrong_box == 1 and wrong_due == TODAY + timedelta(days=1)
```

- [x] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_scheduler_service.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.scheduler_service'`.

- [x] **Step 3: Write minimal implementation**

`backend/app/scheduler_service.py`:
```python
from datetime import date, timedelta

INTERVALS = {1: 1, 2: 3, 3: 7, 4: 16, 5: 35}
MAX_BOX = 5


def next_schedule(current_box: int, is_correct: bool, today: date) -> tuple[int, date]:
    """Compute the next Leitner box and due date.

    current_box is the box BEFORE this answer (a never-scheduled question
    should be passed current_box=1 by the caller).
    """
    if is_correct:
        new_box = min(current_box + 1, MAX_BOX)
    else:
        new_box = 1
    new_due = today + timedelta(days=INTERVALS[new_box])
    return new_box, new_due
```

- [x] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_scheduler_service.py -v`
Expected: PASS (4 passed).

- [x] **Step 5: Commit**

```bash
git add backend/app/scheduler_service.py backend/tests/test_scheduler_service.py
git commit -m "feat: add Leitner scheduler service (pure logic)"
```

---

## Task 2: Schedule table + repository

**Files:**
- Modify: `backend/app/db/database.py` (add `schedule` table to schema)
- Create: `backend/app/db/schedule.py`
- Test: `backend/tests/test_schedule_repo.py`

**Interfaces:**
- Consumes: `get_connection`, `init_db` from `app.db.database`.
- Produces (`db/schedule.py`):
  - `get_box(conn, question_id: str) -> int | None` — current box, or None if no row.
  - `upsert_schedule(conn, question_id: str, box: int, due_date: date, today: date) -> None` — insert or update the row; stores dates as ISO strings; sets `last_reviewed = today`.
  - `due_question_ids(conn, today: date) -> list[str]` — ids with `due_date <= today`, ordered `due_date ASC, box ASC, question_id ASC`.
  - `due_count(conn, today: date) -> int` — number of rows with `due_date <= today`.

- [x] **Step 1: Add the schedule table to the schema**

In `backend/app/db/database.py`, the `_SCHEMA` string currently creates only `attempts`. Append the `schedule` table so `_SCHEMA` becomes:
```python
_SCHEMA = """
CREATE TABLE IF NOT EXISTS attempts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT    NOT NULL,
    is_correct  INTEGER NOT NULL,
    chosen      INTEGER NOT NULL,
    answered_at TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS schedule (
    question_id   TEXT PRIMARY KEY,
    box           INTEGER NOT NULL,
    due_date      TEXT    NOT NULL,
    last_reviewed TEXT    NOT NULL
);
"""
```
(`init_db` uses `executescript`, which runs both statements.)

- [x] **Step 2: Write the failing test**

`backend/tests/test_schedule_repo.py`:
```python
from datetime import date
import pytest
from app.db.database import get_connection, init_db
from app.db.schedule import get_box, upsert_schedule, due_question_ids, due_count

TODAY = date(2026, 6, 24)


@pytest.fixture
def conn(tmp_path):
    c = get_connection(tmp_path / "test.db")
    init_db(c)
    yield c
    c.close()


def test_get_box_none_when_absent(conn):
    assert get_box(conn, "q1") is None


def test_upsert_then_get_box(conn):
    upsert_schedule(conn, "q1", 2, date(2026, 6, 27), TODAY)
    assert get_box(conn, "q1") == 2


def test_upsert_updates_existing_row(conn):
    upsert_schedule(conn, "q1", 2, date(2026, 6, 27), TODAY)
    upsert_schedule(conn, "q1", 1, date(2026, 6, 25), TODAY)
    assert get_box(conn, "q1") == 1
    # still exactly one row
    assert conn.execute("SELECT COUNT(*) AS n FROM schedule").fetchone()["n"] == 1


def test_due_question_ids_only_due_and_sorted(conn):
    # due today (overdue), box 3
    upsert_schedule(conn, "overdue", 3, date(2026, 6, 20), TODAY)
    # due today exactly, box 1 (lower box should come before higher box same date)
    upsert_schedule(conn, "today-b1", 1, date(2026, 6, 24), TODAY)
    upsert_schedule(conn, "today-b4", 4, date(2026, 6, 24), TODAY)
    # not due yet
    upsert_schedule(conn, "future", 2, date(2026, 6, 30), TODAY)

    ids = due_question_ids(conn, TODAY)
    assert ids == ["overdue", "today-b1", "today-b4"]
    assert "future" not in ids


def test_due_count(conn):
    upsert_schedule(conn, "a", 1, date(2026, 6, 20), TODAY)
    upsert_schedule(conn, "b", 1, date(2026, 6, 30), TODAY)
    assert due_count(conn, TODAY) == 1
```

- [x] **Step 3: Run test to verify it fails**

Run: `python -m pytest tests/test_schedule_repo.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.db.schedule'`.

- [x] **Step 4: Write the repository**

`backend/app/db/schedule.py`:
```python
import sqlite3
from datetime import date


def get_box(conn: sqlite3.Connection, question_id: str) -> int | None:
    row = conn.execute(
        "SELECT box FROM schedule WHERE question_id = ?", (question_id,)
    ).fetchone()
    return row["box"] if row else None


def upsert_schedule(
    conn: sqlite3.Connection,
    question_id: str,
    box: int,
    due_date: date,
    today: date,
) -> None:
    conn.execute(
        """
        INSERT INTO schedule (question_id, box, due_date, last_reviewed)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(question_id) DO UPDATE SET
            box = excluded.box,
            due_date = excluded.due_date,
            last_reviewed = excluded.last_reviewed
        """,
        (question_id, box, due_date.isoformat(), today.isoformat()),
    )
    conn.commit()


def due_question_ids(conn: sqlite3.Connection, today: date) -> list[str]:
    rows = conn.execute(
        """
        SELECT question_id FROM schedule
        WHERE due_date <= ?
        ORDER BY due_date ASC, box ASC, question_id ASC
        """,
        (today.isoformat(),),
    ).fetchall()
    return [r["question_id"] for r in rows]


def due_count(conn: sqlite3.Connection, today: date) -> int:
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM schedule WHERE due_date <= ?",
        (today.isoformat(),),
    ).fetchone()
    return row["n"]
```

- [x] **Step 5: Run test to verify it passes**

Run: `python -m pytest tests/test_schedule_repo.py -v`
Expected: PASS (5 passed).

- [x] **Step 6: Run the full suite (the new table must not break existing tests)**

Run: `python -m pytest`
Expected: PASS (all existing tests + new ones).

- [x] **Step 7: Commit**

```bash
git add backend/app/db/database.py backend/app/db/schedule.py backend/tests/test_schedule_repo.py
git commit -m "feat: add schedule table and repository"
```

---

## Task 3: Reschedule on every attempt

**Files:**
- Modify: `backend/app/api/attempts.py`
- Test: `backend/tests/test_attempts_api.py` (append)

**Interfaces:**
- Consumes: `record_attempt` (existing), `get_box`/`upsert_schedule` from `app.db.schedule`, `next_schedule` from `app.scheduler_service`, `app.state.questions_by_id`, `app.state.db`.
- Produces: unchanged HTTP contract for `POST /attempts` (`{is_correct, answer, explanation}`); NEW side effect: the answered question's `schedule` row is created/updated.

- [ ] **Step 1: Write the failing test (append to `test_attempts_api.py`)**

Add this import at the top of `backend/tests/test_attempts_api.py`:
```python
from datetime import date
from app.db.schedule import get_box, due_question_ids
```

Append these tests:
```python
def test_correct_attempt_schedules_question_forward(client):
    # First answer is correct: new question starts box 1 -> promotes to box 2.
    client.post("/attempts", json={"question_id": "ds-arrays-001", "chosen": 0})
    box = get_box(client.app.state.db, "ds-arrays-001")
    assert box == 2
    # box 2 interval is 3 days, so it is NOT due today.
    assert "ds-arrays-001" not in due_question_ids(client.app.state.db, date.today())


def test_wrong_attempt_schedules_question_for_tomorrow(client):
    client.post("/attempts", json={"question_id": "ds-arrays-001", "chosen": 1})
    assert get_box(client.app.state.db, "ds-arrays-001") == 1


def test_unanswered_question_has_no_schedule_row(client):
    client.post("/attempts", json={"question_id": "ds-arrays-001", "chosen": 0})
    assert get_box(client.app.state.db, "en-vocab-001") is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_attempts_api.py -k "schedule" -v`
Expected: FAIL — `get_box` returns None / AssertionError (reschedule not wired yet).

- [ ] **Step 3: Modify the attempts router**

Replace the entire contents of `backend/app/api/attempts.py` with:
```python
from datetime import date
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from ..db.attempts import record_attempt
from ..db.schedule import get_box, upsert_schedule
from ..scheduler_service import next_schedule

router = APIRouter()


class AttemptIn(BaseModel):
    question_id: str
    chosen: int


@router.post("/attempts")
def post_attempt(request: Request, attempt: AttemptIn):
    q = request.app.state.questions_by_id.get(attempt.question_id)
    if q is None:
        raise HTTPException(status_code=404, detail="question not found")
    conn = request.app.state.db
    is_correct = attempt.chosen == q.answer
    record_attempt(conn, q.id, is_correct, attempt.chosen)

    today = date.today()
    current_box = get_box(conn, q.id)
    if current_box is None:
        current_box = 1
    new_box, new_due = next_schedule(current_box, is_correct, today)
    upsert_schedule(conn, q.id, new_box, new_due, today)

    return {"is_correct": is_correct, "answer": q.answer, "explanation": q.explanation}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_attempts_api.py -v`
Expected: PASS (existing attempt tests + 3 new schedule tests).

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/attempts.py backend/tests/test_attempts_api.py
git commit -m "feat: reschedule question on every attempt"
```

---

## Task 4: GET /review endpoint

**Files:**
- Create: `backend/app/api/review.py`
- Modify: `backend/app/main.py` (register router)
- Test: `backend/tests/test_review_api.py`

**Interfaces:**
- Consumes: `due_question_ids` from `app.db.schedule`, `app.state.questions_by_id`, `app.state.db`.
- Produces: `GET /review` -> `[question_dict, ...]` (same shape as `GET /questions`), only questions due today, ordered by `due_question_ids`. Ids missing from the bank are skipped.

- [ ] **Step 1: Write the failing test**

`backend/tests/test_review_api.py`:
```python
def test_review_empty_initially(client):
    assert client.get("/review").json() == []


def test_review_returns_due_question_after_wrong_answer(client):
    # Wrong answer -> box 1, due tomorrow... but interval 1 means due_date is
    # tomorrow, NOT today, so it should NOT appear today.
    client.post("/attempts", json={"question_id": "ds-arrays-001", "chosen": 1})
    assert client.get("/review").json() == []


def test_review_returns_question_once_due(client):
    # Force a due-today schedule by writing directly, then verify /review surfaces it.
    from datetime import date
    from app.db.schedule import upsert_schedule
    upsert_schedule(client.app.state.db, "ds-arrays-001", 1, date.today(), date.today())
    data = client.get("/review").json()
    assert [q["id"] for q in data] == ["ds-arrays-001"]
    # full question shape is returned (reused by the frontend card)
    assert data[0]["options"] and "answer" in data[0]


def test_review_skips_ids_not_in_bank(client):
    from datetime import date
    from app.db.schedule import upsert_schedule
    upsert_schedule(client.app.state.db, "deleted-question", 1, date.today(), date.today())
    assert client.get("/review").json() == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_review_api.py -v`
Expected: FAIL — 404 on `/review` (route not registered).

- [ ] **Step 3: Write the router**

`backend/app/api/review.py`:
```python
from datetime import date
from fastapi import APIRouter, Request
from ..db.schedule import due_question_ids

router = APIRouter()


@router.get("/review")
def get_review(request: Request):
    today = date.today()
    ids = due_question_ids(request.app.state.db, today)
    by_id = request.app.state.questions_by_id
    return [by_id[i].model_dump() for i in ids if i in by_id]
```

- [ ] **Step 4: Register the router in `main.py`**

In `backend/app/main.py`, update the router import/registration block to include `review`:
```python
    from .api import subjects, questions, attempts, stats, tutorials, review
    app.include_router(subjects.router)
    app.include_router(questions.router)
    app.include_router(attempts.router)
    app.include_router(stats.router)
    app.include_router(tutorials.router)
    app.include_router(review.router)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest tests/test_review_api.py -v`
Expected: PASS (4 passed).

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/review.py backend/app/main.py backend/tests/test_review_api.py
git commit -m "feat: add GET /review endpoint"
```

---

## Task 5: due_today in stats

**Files:**
- Modify: `backend/app/stats_service.py` (add `today` param, return `due_today`)
- Modify: `backend/app/api/stats.py` (pass `date.today()`)
- Test: `backend/tests/test_stats_api.py` (append)

**Interfaces:**
- Consumes: `due_count` from `app.db.schedule`.
- Produces: `compute_stats(conn, questions, today: date) -> dict` — same keys as before PLUS `due_today: int`. `GET /stats` passes `date.today()`.

- [ ] **Step 1: Write the failing test (append to `test_stats_api.py`)**

```python
def test_stats_reports_due_today(client):
    from datetime import date
    from app.db.schedule import upsert_schedule
    # one due today, one due in the future
    upsert_schedule(client.app.state.db, "ds-arrays-001", 1, date.today(), date.today())
    upsert_schedule(client.app.state.db, "en-vocab-001", 3, date(2099, 1, 1), date.today())
    data = client.get("/stats").json()
    assert data["due_today"] == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_stats_api.py::test_stats_reports_due_today -v`
Expected: FAIL — `KeyError: 'due_today'` (stats doesn't return it yet).

- [ ] **Step 3: Modify `stats_service.py`**

Add the import at the top of `backend/app/stats_service.py`:
```python
from datetime import date
from .db.schedule import due_count
```
Change the signature and the returned dict. The function header becomes:
```python
def compute_stats(conn: sqlite3.Connection, questions, today: date) -> dict:
```
and the final `return` becomes:
```python
    return {
        "by_subject": by_subject,
        "by_difficulty": by_difficulty,
        "weakest_questions": weakest,
        "due_today": due_count(conn, today),
    }
```
(Leave all the aggregation logic between header and return unchanged.)

- [ ] **Step 4: Modify the stats router**

Replace the contents of `backend/app/api/stats.py` with:
```python
from datetime import date
from fastapi import APIRouter, Request
from ..stats_service import compute_stats

router = APIRouter()


@router.get("/stats")
def get_stats(request: Request):
    return compute_stats(
        request.app.state.db, request.app.state.questions, date.today()
    )
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_stats_api.py -v`
Expected: PASS — existing stats tests (which call through `/stats`) plus the new `due_today` test.

- [ ] **Step 6: Run the full backend suite**

Run: `python -m pytest`
Expected: PASS (all tests across all files).

- [ ] **Step 7: Commit**

```bash
git add backend/app/stats_service.py backend/app/api/stats.py backend/tests/test_stats_api.py
git commit -m "feat: add due_today count to stats"
```

---

## Task 6: Frontend review page

**Files:**
- Modify: `frontend/src/api/client.js` (add `getReview`)
- Create: `frontend/src/pages/Review.jsx`
- Modify: `frontend/src/App.jsx` (route + nav link)

**Interfaces:**
- Consumes: `getReview()` -> question array; existing `QuestionCard` component.
- Produces: `/review` route rendering the Review page; a "複習" nav link.

Frontend tasks use **manual verification** (run the app, observe), per the existing project pattern. Verify each builds with `npm run build`.

- [ ] **Step 1: Add `getReview` to the API client**

In `frontend/src/api/client.js`, add this export (next to `getStats`):
```javascript
export function getReview() {
  return get("/review");
}
```

- [ ] **Step 2: Create the Review page**

`frontend/src/pages/Review.jsx`:
```jsx
import { useEffect, useState } from "react";
import { getReview } from "../api/client";
import QuestionCard from "../components/QuestionCard";

export default function Review() {
  const [queue, setQueue] = useState(null); // null = loading
  const [idx, setIdx] = useState(0);

  useEffect(() => {
    getReview().then(setQueue);
  }, []);

  if (queue === null) return <p>載入中…</p>;

  const current = queue[idx];

  return (
    <div>
      <h2>複習</h2>
      {queue.length === 0 && (
        <p style={{ color: "#888" }}>今天沒有要複習的，去「練習」刷新題吧。</p>
      )}
      {queue.length > 0 && !current && <p>今天複習完成 🎉 共 {queue.length} 題。</p>}
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

- [ ] **Step 3: Add the route and nav link in `App.jsx`**

Replace the contents of `frontend/src/App.jsx` with:
```jsx
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Practice from "./pages/Practice";
import Review from "./pages/Review";
import Tutorial from "./pages/Tutorial";
import Browse from "./pages/Browse";

export default function App() {
  return (
    <BrowserRouter>
      <nav className="nav">
        <Link to="/">儀表板</Link>
        <Link to="/practice">練習</Link>
        <Link to="/review">複習</Link>
        <Link to="/browse">瀏覽</Link>
      </nav>
      <main className="main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/practice" element={<Practice />} />
          <Route path="/review" element={<Review />} />
          <Route path="/tutorial/:subject/:topic" element={<Tutorial />} />
          <Route path="/browse" element={<Browse />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
```

- [ ] **Step 4: Build to verify it compiles**

Run (from `frontend/`): `npm run build`
Expected: build succeeds; then `rm -rf dist`.

- [ ] **Step 5: Manual verification**

Start backend (`uvicorn app.main:app --reload` from `backend/` with venv active) and frontend (`npm run dev`). Then:
1. Go to `/review` with no due cards → shows "今天沒有要複習的…".
2. In `/practice`, answer a question wrong, wait is not practical — instead verify scheduling via the dashboard count in Task 7, or temporarily confirm `/review` is reachable and renders a card when due. (A due card appears only when `due_date <= today`; a freshly-wrong card is due tomorrow by design.)
3. Confirm the "複習" nav link works and the page loads without console errors.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/api/client.js frontend/src/pages/Review.jsx frontend/src/App.jsx
git commit -m "feat: add review page and nav link"
```

---

## Task 7: Dashboard due-today block

**Files:**
- Modify: `frontend/src/pages/Dashboard.jsx`

**Interfaces:**
- Consumes: `getStats()` (already used by Dashboard), which now returns `due_today`; `react-router-dom` `Link`.
- Produces: a "今天待複習" block linking to `/review`.

- [ ] **Step 1: Add the due-today block to the dashboard**

In `frontend/src/pages/Dashboard.jsx`, add `Link` to the imports:
```jsx
import { Link } from "react-router-dom";
```
Then, inside the returned JSX, immediately after the `<h2>儀表板</h2>` line, insert:
```jsx
      <div className="card">
        <h3>今天待複習</h3>
        <div className="stat-row">
          <span>到期題數</span>
          <span>{stats.due_today} 題</span>
        </div>
        {stats.due_today > 0 && (
          <p style={{ marginTop: 12 }}>
            <Link className="primary" to="/review"
              style={{ display: "inline-block", textDecoration: "none", padding: "10px 18px" }}>
              開始複習
            </Link>
          </p>
        )}
      </div>
```
(`stats.due_today` is always present now that `/stats` returns it.)

- [ ] **Step 2: Build to verify it compiles**

Run (from `frontend/`): `npm run build`
Expected: build succeeds; then `rm -rf dist`.

- [ ] **Step 3: Manual verification (end-to-end)**

With backend + frontend running:
1. Directly insert a due card to see the full flow. In a Python shell from `backend/` (venv active):
   ```python
   from datetime import date
   from app.main import app
   from app.db.schedule import upsert_schedule
   upsert_schedule(app.state.db, "ds-arrays-001", 1, date.today(), date.today())
   ```
   (This writes to the dev `progress.db` the running server uses; if the server holds a separate connection, instead just answer questions over several runs. For a quick check, the inserted row makes `/stats` `due_today` = 1 and `/review` return that card.)
2. Reload the dashboard → "今天待複習：1 題" with an 開始複習 button.
3. Click it → Review page shows the card → answer it → it advances; answering correct reschedules it forward (it leaves today's due list).
4. Reload dashboard → due count drops to 0.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/Dashboard.jsx
git commit -m "feat: show today's review count on dashboard"
```

---

## Self-Review Notes

- **Spec coverage:** Leitner boxes/intervals/transition (Task 1, constraints copied verbatim); `schedule` table + repository with the exact ordering rule (Task 2); unified reschedule-on-every-attempt (Task 3); `GET /review` with due-only + sorting + stale-id skip (Task 4); `due_today` in stats (Task 5); review page + nav (Task 6); dashboard due block (Task 7). All spec sections 4–7 map to a task; section 8 testing is embedded per task.
- **Deferred (per spec, intentionally absent):** daily caps/postpone, new-card queue, confidence/timing signals, SM-2 formula, streaks/notifications — none appear in any task.
- **Type consistency:** `next_schedule(current_box, is_correct, today) -> (int, date)`, `get_box(conn, qid) -> int | None`, `upsert_schedule(conn, qid, box, due_date, today)`, `due_question_ids(conn, today) -> list[str]`, `due_count(conn, today) -> int`, and `compute_stats(conn, questions, today)` are used identically across Tasks 1–7. `app.state.questions_by_id` (added in the MVP review-fix commit) is relied on by Tasks 3 and 4 and exists in `main.py`.
- **Design-invariant check:** `schedule` stores only `question_id` + numbers/dates; `attempts` untouched; questions still loaded from YAML. No violation of "questions never in the DB."
```
