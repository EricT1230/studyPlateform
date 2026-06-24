# Phase 4 — New Question Types Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans.
>
> Read first: [AGENTS.md](../../../AGENTS.md), [ARCHITECTURE.md](../../ARCHITECTURE.md) (§5.2), [Phase 4 spec](../specs/2026-06-24-phase4-question-types-design.md).
> **Prerequisite:** Phase 1 complete (`attempts.py` has reschedule logic; `Review.jsx` exists). If Phase 1 isn't done, do it first.

**Goal:** Add `flashcard` and `open_ended` question types alongside `mcq`, converging all grading to a binary `is_correct` so the scheduler and tables are untouched.

**Architecture:** One `type` field + three hooks (validation per type, grading→`is_correct`, frontend card dispatch). The scheduler, `attempts` table, and `schedule` table are unchanged — this Phase proves the binary-`is_correct` design.

**Tech Stack:** FastAPI, pytest (backend); React + Vite (frontend).

## Global Constraints

- `type ∈ {mcq, flashcard, open_ended}`; default `mcq`. Question content stays in YAML, never the DB.
- Per-type required fields: `mcq` → `question, options, answer`; `flashcard` → `front, back`; `open_ended` → `question, reference`. `difficulty ∈ {basic, intermediate, advanced, master}`.
- Grading converges to binary `is_correct`: `mcq` computed server-side (`chosen == answer`); `flashcard`/`open_ended` are user self-graded (client sends `self_correct`).
- The scheduler (`scheduler_service`), `attempts` table, and `schedule` table MUST NOT change. If a task seems to require changing them, stop — the design is being violated.
- Backend tests run from `backend/` with venv active: `python -m pytest`.

> **Design note (vs spec wording):** the spec says "discriminated union." This plan uses one `Question` model with a per-type `model_validator` — functionally identical (enforces per-type required fields) but far less invasive to the existing loader (`LoadedQuestion(**item)`) and `model_dump()`. This is a deliberate, equivalent simplification.

---

## File Structure

```
backend/app/content/schema.py   MODIFY  Question gains type-specific optional fields + per-type validator
backend/app/api/attempts.py      MODIFY  accept chosen|self_correct, converge to is_correct
backend/tests/test_schema.py     MODIFY  add flashcard / open_ended validation tests
backend/tests/test_attempts_api.py MODIFY add self-graded attempt + reschedule tests
content/english/vocabulary-cards.yaml  CREATE  flashcard seed
content/algorithms/proofs.yaml          CREATE  open_ended seed
frontend/src/components/QuestionView.jsx  CREATE  dispatch by type
frontend/src/components/FlashCard.jsx      CREATE
frontend/src/components/OpenEndedCard.jsx  CREATE
frontend/src/api/client.js                 MODIFY  postAttempt supports self_correct
frontend/src/pages/Practice.jsx            MODIFY  render QuestionView
frontend/src/pages/Review.jsx              MODIFY  render QuestionView
```

---

## Task 1: Schema supports three question types

**Files:**
- Modify: `backend/app/content/schema.py`
- Modify: `backend/tests/test_schema.py` (append)

**Interfaces:**
- Produces: `Question` with optional `question/options/answer/explanation` (mcq), `front/back` (flashcard), `reference` (open_ended), plus `type: Literal["mcq","flashcard","open_ended"]="mcq"`. A `model_validator(mode="after")` enforces per-type required fields and (for mcq) the answer-range / ≥2-options rules. `LoadedQuestion(Question)` still adds `subject`, `topic`.

- [ ] **Step 1: Write the failing tests (append to `test_schema.py`)**

```python
def test_flashcard_valid():
    q = Question(id="c1", type="flashcard", difficulty="basic", front="Q", back="A")
    assert q.type == "flashcard"


def test_flashcard_missing_back_rejected():
    with pytest.raises(ValidationError):
        Question(id="c1", type="flashcard", difficulty="basic", front="Q")


def test_open_ended_valid():
    q = Question(id="o1", type="open_ended", difficulty="advanced",
                 question="Prove X", reference="Because Y")
    assert q.type == "open_ended"


def test_open_ended_missing_reference_rejected():
    with pytest.raises(ValidationError):
        Question(id="o1", type="open_ended", difficulty="advanced", question="Prove X")


def test_mcq_still_requires_its_fields():
    with pytest.raises(ValidationError):
        Question(id="m1", type="mcq", difficulty="basic", front="oops")  # missing mcq fields
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_schema.py -v`
Expected: FAIL — current schema rejects `type="flashcard"` (Literal only allows "mcq") / requires mcq fields.

- [ ] **Step 3: Rewrite `schema.py`**

Replace the entire contents of `backend/app/content/schema.py` with:
```python
from typing import Literal
from pydantic import BaseModel, model_validator


class Question(BaseModel):
    id: str
    type: Literal["mcq", "flashcard", "open_ended"] = "mcq"
    difficulty: Literal["basic", "intermediate", "advanced", "master"]
    tags: list[str] = []
    # mcq fields
    question: str | None = None
    options: list[str] | None = None
    answer: int | None = None
    explanation: str = ""
    # flashcard fields
    front: str | None = None
    back: str | None = None
    # open_ended fields
    reference: str | None = None

    @model_validator(mode="after")
    def _check(self) -> "Question":
        if self.type == "mcq":
            if self.question is None or self.options is None or self.answer is None:
                raise ValueError("mcq requires question, options, and answer")
            if len(self.options) < 2:
                raise ValueError("mcq needs at least 2 options")
            if not 0 <= self.answer < len(self.options):
                raise ValueError(
                    f"answer index {self.answer} out of range for "
                    f"{len(self.options)} options"
                )
        elif self.type == "flashcard":
            if self.front is None or self.back is None:
                raise ValueError("flashcard requires front and back")
        elif self.type == "open_ended":
            if self.question is None or self.reference is None:
                raise ValueError("open_ended requires question and reference")
        return self


class LoadedQuestion(Question):
    subject: str
    topic: str
```

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_schema.py -v`
Expected: PASS — including the original MVP mcq tests (mcq enforcement preserved).

- [ ] **Step 5: Run full suite (loader/routers must still work)**

Run: `python -m pytest`
Expected: PASS (model_dump now includes extra null fields — harmless).

- [ ] **Step 6: Commit**

```bash
git add backend/app/content/schema.py backend/tests/test_schema.py
git commit -m "feat: support flashcard and open_ended question types in schema"
```

---

## Task 2: POST /attempts converges grading to is_correct

**Files:**
- Modify: `backend/app/api/attempts.py`
- Modify: `backend/tests/test_attempts_api.py` (append)

**Interfaces:**
- Consumes: `record_attempt`, `get_box`/`upsert_schedule` (Phase 1), `next_schedule` (Phase 1), `app.state.questions_by_id`.
- Produces: `POST /attempts` body `{question_id, chosen?, self_correct?}`. mcq → `chosen` required, `is_correct = chosen == answer`; flashcard/open_ended → `self_correct` required, `is_correct = self_correct`. Missing the required field → 400. Reschedules (Phase 1 logic) regardless of type. Response `{is_correct, answer, explanation}` (`answer` is `None` for non-mcq).

- [ ] **Step 1: Write the failing tests (append to `test_attempts_api.py`)**

First extend the test content. In `backend/tests/conftest.py`, inside the `content_dir` fixture, add a flashcard file before `return tmp_path`:
```python
    (en / "cards.yaml").write_text("""
- id: en-card-001
  type: flashcard
  difficulty: basic
  front: "deprecated"
  back: "discouraged from use"
""", encoding="utf-8")
```
Then append to `test_attempts_api.py`:
```python
def test_flashcard_self_correct_records_and_schedules(client):
    from datetime import date
    from app.db.schedule import get_box
    resp = client.post("/attempts", json={"question_id": "en-card-001", "self_correct": True})
    assert resp.status_code == 200
    assert resp.json()["is_correct"] is True
    # first correct -> box promotes to 2 (Phase 1 scheduler)
    assert get_box(client.app.state.db, "en-card-001") == 2


def test_flashcard_missing_self_correct_400(client):
    resp = client.post("/attempts", json={"question_id": "en-card-001", "chosen": 0})
    assert resp.status_code == 400


def test_mcq_missing_chosen_400(client):
    resp = client.post("/attempts", json={"question_id": "ds-arrays-001", "self_correct": True})
    assert resp.status_code == 400
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_attempts_api.py -k "flashcard or missing_chosen" -v`
Expected: FAIL — current router has no `self_correct` handling (treats body as mcq).

- [ ] **Step 3: Rewrite `attempts.py`**

Replace the entire contents of `backend/app/api/attempts.py` with (this is the Phase-1 version extended for types):
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
    chosen: int | None = None
    self_correct: bool | None = None


@router.post("/attempts")
def post_attempt(request: Request, attempt: AttemptIn):
    q = request.app.state.questions_by_id.get(attempt.question_id)
    if q is None:
        raise HTTPException(status_code=404, detail="question not found")
    conn = request.app.state.db

    if q.type == "mcq":
        if attempt.chosen is None:
            raise HTTPException(status_code=400, detail="mcq attempt requires 'chosen'")
        is_correct = attempt.chosen == q.answer
        chosen_value = attempt.chosen
    else:
        if attempt.self_correct is None:
            raise HTTPException(
                status_code=400, detail="self-graded attempt requires 'self_correct'"
            )
        is_correct = attempt.self_correct
        chosen_value = -1  # N/A for self-graded types

    record_attempt(conn, q.id, is_correct, chosen_value)

    today = date.today()
    current_box = get_box(conn, q.id)
    if current_box is None:
        current_box = 1
    new_box, new_due = next_schedule(current_box, is_correct, today)
    upsert_schedule(conn, q.id, new_box, new_due, today)

    return {"is_correct": is_correct, "answer": q.answer, "explanation": q.explanation}
```

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_attempts_api.py -v`
Expected: PASS — existing mcq attempt tests + new self-graded tests.

- [ ] **Step 5: Run full suite**

Run: `python -m pytest`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/attempts.py backend/tests/test_attempts_api.py backend/tests/conftest.py
git commit -m "feat: converge mcq/self-graded attempts to binary is_correct"
```

---

## Task 3: Seed content for new types

**Files:**
- Create: `content/english/vocabulary-cards.yaml`
- Create: `content/algorithms/proofs.yaml`

**Interfaces:** Consumes the Task-1 schema. No new code; verification is "loader accepts the bank."

- [ ] **Step 1: Write the flashcard seed**

`content/english/vocabulary-cards.yaml`:
```yaml
- id: en-card-001
  type: flashcard
  difficulty: basic
  tags: [vocabulary]
  front: |
    idempotent
  back: |
    執行一次或多次結果相同。常見於 REST API 與部署腳本的描述。
- id: en-card-002
  type: flashcard
  difficulty: basic
  tags: [vocabulary]
  front: |
    race condition
  back: |
    多個執行緒/程序的執行順序影響最終結果，導致非預期行為。
- id: en-card-003
  type: flashcard
  difficulty: intermediate
  tags: [vocabulary]
  front: |
    backpressure
  back: |
    當消費者跟不上生產者時，系統向上游施加的「減速」訊號，避免被壓垮。
```

- [ ] **Step 2: Write the open_ended seed**

`content/algorithms/proofs.yaml`:
```yaml
- id: algo-proof-001
  type: open_ended
  difficulty: advanced
  tags: [sorting, lower-bound]
  question: |
    證明任何以比較為基礎的排序，最差情況時間複雜度下界為 Ω(n log n)。
  reference: |
    比較排序可建成決策樹，每個葉節點對應一種排列，故至少有 n! 個葉。
    高度 h 的二元樹最多 2^h 個葉，需 2^h >= n!，即 h >= log2(n!)。
    由 Stirling，log2(n!) = Θ(n log n)，故最差比較次數（樹高）為 Ω(n log n)。
- id: algo-proof-002
  type: open_ended
  difficulty: master
  tags: [graph, greedy]
  question: |
    簡述為何 Dijkstra 演算法在「有負權邊」時可能失效。
  reference: |
    Dijkstra 一旦把某節點標記為最短（出堆）就不再更新，
    其正確性依賴「之後的路徑不會更短」這個非負權前提。
    有負權邊時，較晚走到的路徑可能反而更短，違反此前提，故結果可能錯誤。
```

- [ ] **Step 3: Verify the loader accepts the whole bank**

Run (from `backend/`, venv active):
```
python -c "from app.config import CONTENT_DIR; from app.content.loader import load_questions; qs = load_questions(CONTENT_DIR); print(len(qs), 'questions'); print(sorted({q.type for q in qs}))"
```
Expected: prints the total count and `['flashcard', 'mcq', 'open_ended']` with no exception.

- [ ] **Step 4: Commit**

```bash
git add content/english/vocabulary-cards.yaml content/algorithms/proofs.yaml
git commit -m "content: add flashcard and open_ended seed questions"
```

---

## Task 4: Frontend type-dispatched cards

**Files:**
- Modify: `frontend/src/api/client.js`
- Create: `frontend/src/components/FlashCard.jsx`, `frontend/src/components/OpenEndedCard.jsx`, `frontend/src/components/QuestionView.jsx`
- Modify: `frontend/src/pages/Practice.jsx`, `frontend/src/pages/Review.jsx`

**Interfaces:**
- `postAttempt(questionId, { chosen, selfCorrect })` — sends whichever is provided.
- `QuestionView` props `{ question, onAnswered }` — renders `QuestionCard` (mcq), `FlashCard`, or `OpenEndedCard` by `question.type`.
- `FlashCard`/`OpenEndedCard` props `{ question, onAnswered }`.

Frontend uses **manual verification** + `npm run build`.

- [ ] **Step 1: Update postAttempt in client.js**

Replace the existing `postAttempt` in `frontend/src/api/client.js` with:
```javascript
export async function postAttempt(questionId, { chosen, selfCorrect } = {}) {
  const body = { question_id: questionId };
  if (chosen !== undefined && chosen !== null) body.chosen = chosen;
  if (selfCorrect !== undefined && selfCorrect !== null) body.self_correct = selfCorrect;
  const res = await fetch(`${BASE}/attempts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST /attempts -> ${res.status}`);
  return res.json();
}
```

- [ ] **Step 2: Update QuestionCard to pass chosen as an object**

In `frontend/src/components/QuestionCard.jsx`, the `choose` function calls `postAttempt(question.id, idx)`. Change it to:
```javascript
    const r = await postAttempt(question.id, { chosen: idx });
```
(Only that one call changes; the rest of QuestionCard is unchanged.)

- [ ] **Step 3: Create FlashCard.jsx**

`frontend/src/components/FlashCard.jsx`:
```jsx
import { useState } from "react";
import { postAttempt } from "../api/client";

export default function FlashCard({ question, onAnswered }) {
  const [flipped, setFlipped] = useState(false);
  const [graded, setGraded] = useState(false);

  async function grade(correct) {
    await postAttempt(question.id, { selfCorrect: correct });
    setGraded(true);
  }

  return (
    <div className="card">
      <div style={{ color: "#888", fontSize: 13 }}>
        {question.subject} · {question.topic} · 翻牌卡
      </div>
      <p style={{ whiteSpace: "pre-wrap", fontWeight: 600 }}>{question.front}</p>
      {!flipped && (
        <button className="primary" onClick={() => setFlipped(true)}>翻面看答案</button>
      )}
      {flipped && (
        <div className="explanation">
          <p style={{ whiteSpace: "pre-wrap" }}>{question.back}</p>
          {!graded ? (
            <>
              <button className="option correct" onClick={() => grade(true)}>我會</button>
              <button className="option wrong" onClick={() => grade(false)}>不會</button>
            </>
          ) : (
            <button className="primary" onClick={onAnswered}>下一題</button>
          )}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 4: Create OpenEndedCard.jsx**

`frontend/src/components/OpenEndedCard.jsx`:
```jsx
import { useState } from "react";
import { postAttempt } from "../api/client";

export default function OpenEndedCard({ question, onAnswered }) {
  const [revealed, setRevealed] = useState(false);
  const [graded, setGraded] = useState(false);

  async function grade(correct) {
    await postAttempt(question.id, { selfCorrect: correct });
    setGraded(true);
  }

  return (
    <div className="card">
      <div style={{ color: "#888", fontSize: 13 }}>
        {question.subject} · {question.topic} · {question.difficulty} · 開放式
      </div>
      <p style={{ whiteSpace: "pre-wrap", fontWeight: 600 }}>{question.question}</p>
      {!revealed && (
        <button className="primary" onClick={() => setRevealed(true)}>看參考解答</button>
      )}
      {revealed && (
        <div className="explanation">
          <strong>參考解答</strong>
          <p style={{ whiteSpace: "pre-wrap" }}>{question.reference}</p>
          {!graded ? (
            <>
              <button className="option correct" onClick={() => grade(true)}>我對了</button>
              <button className="option wrong" onClick={() => grade(false)}>我錯了</button>
            </>
          ) : (
            <button className="primary" onClick={onAnswered}>下一題</button>
          )}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 5: Create QuestionView.jsx (dispatcher)**

`frontend/src/components/QuestionView.jsx`:
```jsx
import QuestionCard from "./QuestionCard";
import FlashCard from "./FlashCard";
import OpenEndedCard from "./OpenEndedCard";

export default function QuestionView({ question, onAnswered }) {
  if (question.type === "flashcard") {
    return <FlashCard question={question} onAnswered={onAnswered} />;
  }
  if (question.type === "open_ended") {
    return <OpenEndedCard question={question} onAnswered={onAnswered} />;
  }
  return <QuestionCard question={question} onAnswered={onAnswered} />;
}
```

- [ ] **Step 6: Use QuestionView in Practice.jsx and Review.jsx**

In `frontend/src/pages/Practice.jsx`: replace the import `import QuestionCard from "../components/QuestionCard";` with `import QuestionView from "../components/QuestionView";`, and replace the `<QuestionCard ... />` element with:
```jsx
          <QuestionView
            key={current.id}
            question={current}
            onAnswered={() => setIdx((i) => i + 1)}
          />
```
Do the identical swap in `frontend/src/pages/Review.jsx`.

- [ ] **Step 7: Build to verify**

Run (from `frontend/`): `npm run build`
Expected: build succeeds; then `rm -rf dist`.

- [ ] **Step 8: Manual verification**

With backend + frontend running, in `/practice` filter to a flashcard topic (english · vocabulary-cards) and an open_ended topic (algorithms · proofs):
1. mcq still works exactly as before (select → instant correct/wrong + explanation).
2. Flashcard: shows front → 翻面看答案 → back + 我會/不會 → choosing records the attempt → 下一題.
3. Open_ended: shows question → 看參考解答 → reference + 我對了/我錯了 → 下一題.
4. After answering each, that question enters the Phase-1 schedule (verify via dashboard due-count over time, or that a wrong self-grade keeps box 1).

- [ ] **Step 9: Commit**

```bash
git add frontend/src/api/client.js frontend/src/components/QuestionCard.jsx frontend/src/components/FlashCard.jsx frontend/src/components/OpenEndedCard.jsx frontend/src/components/QuestionView.jsx frontend/src/pages/Practice.jsx frontend/src/pages/Review.jsx
git commit -m "feat: add flashcard and open-ended cards via type dispatch"
```

---

## Self-Review Notes

- **Spec coverage:** `type` + per-type validation (Task 1); grading hook converging to `is_correct` with 400 on missing field (Task 2); seed content (Task 3); frontend dispatch + two new cards + client change (Task 4). The scheduler, `attempts`, and `schedule` tables are untouched — the architectural claim is verified.
- **Deviation from spec wording:** single-model validator instead of a discriminated union — equivalent enforcement, less churn; noted in Global Constraints.
- **Type consistency:** `Question.type ∈ {mcq,flashcard,open_ended}`; `postAttempt(id, {chosen, selfCorrect})`; `QuestionView`/`FlashCard`/`OpenEndedCard` props `{question, onAnswered}` used identically. Builds on Phase 1's `attempts.py` (reschedule) and `Review.jsx`.
- **Prereq:** requires Phase 1. `chosen_value = -1` sentinel keeps the `attempts.chosen NOT NULL` column satisfied for self-graded types without changing the table.
```
