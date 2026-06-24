# Phase 3 — CAG Tutor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans.
>
> Read first: [AGENTS.md](../../../AGENTS.md), [ARCHITECTURE.md](../../ARCHITECTURE.md) (§5.3), [Phase 3 spec](../specs/2026-06-24-phase3-cag-tutor-design.md).
> **Prerequisite:** Phase 2 complete (notes files exist — the tutor reads them). Phase 1 helps (attempt history enriches context) but isn't strictly required.
> **Before writing `ClaudeProvider`:** re-read the `claude-api` skill for the current SDK/model details — do not write the API call from memory.

**Goal:** A text tutor that answers questions about the user's own question bank, tutorials, and notes (Cache-Augmented: relevant content stuffed into the model's context), with a swappable provider and a text English-conversation coach mode.

**Architecture:** A pure `build_context` assembles question + tutorial + notes + attempt history into a system prompt. A `TutorProvider` abstraction (Claude implementation + a fake for tests) is called by `POST /tutor/ask`. No new DB table; chat history lives in the frontend. Secrets via env var.

**Tech Stack:** FastAPI, `anthropic` SDK, pytest (backend); React + Vite (frontend).

## Global Constraints

- No new DB table. The tutor only READS existing content (`app.state.questions`, `content/*.md`, `content/*.notes.md`) and `attempts`. Chat history is held in the frontend, not persisted.
- The model API key comes from an environment variable (`ANTHROPIC_API_KEY`). Never hardcode it; never commit it. If unset, `POST /tutor/ask` returns 503 and the rest of the app is unaffected.
- `build_context`, `TutorProvider.complete`, and the prompt builders are pure of network I/O except the provider's own model call. Tests use a fake provider — **never call the real API in tests.**
- The provider is swappable: the router depends on the `TutorProvider` interface, not a concrete class. Model choice is deferred — the default implementation targets Claude (`claude-opus-4-8`) and is selected only when a key is present.
- Backend tests run from `backend/` with venv active: `python -m pytest`.

---

## File Structure

```
backend/app/tutor/__init__.py    CREATE  (empty)
backend/app/tutor/context.py     CREATE  build_context() — pure assembly
backend/app/tutor/prompts.py     CREATE  solve_system(), english_system()
backend/app/tutor/provider.py    CREATE  TutorProvider, FakeProvider, ClaudeProvider, make_provider()
backend/app/api/tutor.py         CREATE  POST /tutor/ask
backend/app/main.py              MODIFY  set app.state.tutor_provider; register router
backend/requirements.txt         MODIFY  add anthropic
backend/tests/test_tutor_context.py  CREATE
backend/tests/test_tutor_api.py      CREATE  (fake provider)
frontend/src/api/client.js       MODIFY  askTutor()
frontend/src/components/TutorPanel.jsx  CREATE
frontend/src/pages/Tutor.jsx     CREATE  English-coach page
frontend/src/App.jsx             MODIFY  /tutor route + nav link
frontend/src/components/QuestionCard.jsx  MODIFY  「問小老師」link/panel toggle
```

---

## Task 1: build_context (pure context assembly)

**Files:**
- Create: `backend/app/tutor/__init__.py` (empty)
- Create: `backend/app/tutor/context.py`
- Test: `backend/tests/test_tutor_context.py`

**Interfaces:**
- Produces: `build_context(scope: dict, questions_by_id: dict, content_dir: Path, conn) -> str`. `scope` is `{"question_id": str}` or `{"subject": str, "topic": str}`. Assembles: the question (if scoped to one) + its recent attempt history, the topic tutorial (`<topic>.md`) and notes (`<topic>.notes.md`) if present. Missing files are skipped gracefully. Unknown `question_id` → returns whatever it can (no question section).

- [ ] **Step 1: Create package marker + write the failing test**

Create empty `backend/app/tutor/__init__.py`.

`backend/tests/test_tutor_context.py`:
```python
from pathlib import Path
import pytest
from app.db.database import get_connection, init_db
from app.content.schema import LoadedQuestion
from app.tutor.context import build_context


@pytest.fixture
def conn(tmp_path):
    c = get_connection(tmp_path / "t.db")
    init_db(c)
    yield c
    c.close()


def _q():
    return LoadedQuestion(
        id="ds-arrays-001", type="mcq", difficulty="basic",
        question="Access time?", options=["O(1)", "O(n)"], answer=0,
        explanation="Direct address.", subject="data-structures", topic="arrays",
    )


def test_context_includes_question_and_files(tmp_path, conn):
    ds = tmp_path / "data-structures"
    ds.mkdir()
    (ds / "arrays.md").write_text("# Arrays tutorial", encoding="utf-8")
    (ds / "arrays.notes.md").write_text("my note: contiguous", encoding="utf-8")
    qbi = {"ds-arrays-001": _q()}

    ctx = build_context({"question_id": "ds-arrays-001"}, qbi, tmp_path, conn)
    assert "Access time?" in ctx
    assert "Arrays tutorial" in ctx
    assert "my note: contiguous" in ctx


def test_context_missing_files_are_skipped(tmp_path, conn):
    qbi = {"ds-arrays-001": _q()}
    ctx = build_context({"question_id": "ds-arrays-001"}, qbi, tmp_path, conn)
    assert "Access time?" in ctx  # question still present; no tutorial/notes, no error


def test_context_by_subject_topic(tmp_path, conn):
    ds = tmp_path / "data-structures"
    ds.mkdir()
    (ds / "arrays.md").write_text("# Arrays tutorial", encoding="utf-8")
    ctx = build_context({"subject": "data-structures", "topic": "arrays"}, {}, tmp_path, conn)
    assert "Arrays tutorial" in ctx
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_tutor_context.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.tutor.context'`.

- [ ] **Step 3: Write context.py**

`backend/app/tutor/context.py`:
```python
from pathlib import Path


def _attempt_summary(conn, question_id: str) -> str:
    rows = conn.execute(
        "SELECT is_correct FROM attempts WHERE question_id = ? ORDER BY id DESC LIMIT 10",
        (question_id,),
    ).fetchall()
    if not rows:
        return ""
    correct = sum(r["is_correct"] for r in rows)
    return f"\n（這題最近 {len(rows)} 次作答：對 {correct} 次、錯 {len(rows) - correct} 次）"


def build_context(scope: dict, questions_by_id: dict, content_dir: Path, conn) -> str:
    parts: list[str] = []
    subject = scope.get("subject")
    topic = scope.get("topic")

    qid = scope.get("question_id")
    if qid:
        q = questions_by_id.get(qid)
        if q is not None:
            subject, topic = q.subject, q.topic
            opts = ""
            if q.options:
                opts = "\n選項：" + " / ".join(q.options)
            parts.append(
                f"【題目】{q.question or q.front or ''}{opts}"
                + (f"\n解析：{q.explanation}" if q.explanation else "")
                + (f"\n參考解答：{q.reference}" if q.reference else "")
                + _attempt_summary(conn, qid)
            )

    if subject and topic:
        tut = content_dir / subject / f"{topic}.md"
        if tut.exists():
            parts.append("【教學文章】\n" + tut.read_text(encoding="utf-8"))
        notes = content_dir / subject / f"{topic}.notes.md"
        if notes.exists():
            parts.append("【我的筆記】\n" + notes.read_text(encoding="utf-8"))

    return "\n\n".join(parts)
```

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_tutor_context.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add backend/app/tutor/__init__.py backend/app/tutor/context.py backend/tests/test_tutor_context.py
git commit -m "feat: add tutor context assembly (pure)"
```

---

## Task 2: Provider abstraction + prompts

**Files:**
- Modify: `backend/requirements.txt` (add `anthropic`)
- Create: `backend/app/tutor/prompts.py`
- Create: `backend/app/tutor/provider.py`

**Interfaces:**
- Produces (`prompts.py`): `solve_system(context: str) -> str`, `english_system() -> str`.
- Produces (`provider.py`): `TutorProvider` (Protocol with `complete(system: str, messages: list[dict]) -> str`); `FakeProvider(reply="...")` recording `last_system`/`last_messages`; `ClaudeProvider(model="claude-opus-4-8")`; `make_provider() -> TutorProvider | None` returning a `ClaudeProvider` if `ANTHROPIC_API_KEY` is set, else `None`.

No unit test runs the real model; `FakeProvider` is exercised in Task 3. `ClaudeProvider` correctness is verified by manual smoke test in Task 4.

- [ ] **Step 1: Add the dependency**

In `backend/requirements.txt`, add a line:
```
anthropic
```
Then install (from `backend/`, venv active): `pip install anthropic` and re-freeze if your workflow pins versions (`pip show anthropic` → pin the installed version).

- [ ] **Step 2: Write prompts.py**

`backend/app/tutor/prompts.py`:
```python
def solve_system(context: str) -> str:
    return (
        "你是一位有耐心、講解清楚的家教，協助一位準備轉外商、想打實基礎的工程師。\n"
        "請主要根據下面提供的「學生自己的題庫 / 教學 / 筆記」來解說，"
        "用中文、循序漸進、必要時舉例。若內容不足以回答，誠實說明並給出方向。\n\n"
        f"=== 學生的學習材料 ===\n{context}\n=== 材料結束 ==="
    )


def english_system() -> str:
    return (
        "You are a patient English conversation coach for a software engineer "
        "preparing for roles at international companies. Role-play realistic "
        "workplace scenarios (interviews, standups, code reviews, design "
        "discussions). Keep replies natural and concise. After the user speaks, "
        "gently point out one or two improvements (phrasing, clarity, tone) and "
        "model a better version, then continue the conversation."
    )
```

- [ ] **Step 3: Write provider.py**

`backend/app/tutor/provider.py`:
```python
import os
from typing import Protocol


class TutorProvider(Protocol):
    def complete(self, system: str, messages: list[dict]) -> str: ...


class FakeProvider:
    """Test double — returns a fixed reply and records its inputs."""

    def __init__(self, reply: str = "(fake tutor answer)") -> None:
        self.reply = reply
        self.last_system: str | None = None
        self.last_messages: list[dict] | None = None

    def complete(self, system: str, messages: list[dict]) -> str:
        self.last_system = system
        self.last_messages = messages
        return self.reply


class ClaudeProvider:
    """Default provider — Claude via the anthropic SDK (reads ANTHROPIC_API_KEY)."""

    def __init__(self, model: str = "claude-opus-4-8") -> None:
        import anthropic

        self._client = anthropic.Anthropic()
        self._model = model

    def complete(self, system: str, messages: list[dict]) -> str:
        resp = self._client.messages.create(
            model=self._model,
            max_tokens=2000,
            system=system,
            messages=messages,
        )
        return next((b.text for b in resp.content if b.type == "text"), "")


def make_provider() -> "TutorProvider | None":
    if os.environ.get("ANTHROPIC_API_KEY"):
        return ClaudeProvider()
    return None
```

- [ ] **Step 4: Sanity import**

Run (from `backend/`): `python -c "from app.tutor.provider import FakeProvider, make_provider; print('ok')"`
Expected: prints `ok` (no key needed — `make_provider` just returns None without one).

- [ ] **Step 5: Commit**

```bash
git add backend/requirements.txt backend/app/tutor/prompts.py backend/app/tutor/provider.py
git commit -m "feat: add tutor provider abstraction and prompts"
```

---

## Task 3: POST /tutor/ask endpoint

**Files:**
- Create: `backend/app/api/tutor.py`
- Modify: `backend/app/main.py` (set `app.state.tutor_provider`, register router)
- Test: `backend/tests/test_tutor_api.py`

**Interfaces:**
- Consumes: `build_context`, `solve_system`/`english_system`, `app.state.tutor_provider`, `app.state.questions_by_id`, `app.state.content_dir`, `app.state.db`.
- Produces: `POST /tutor/ask` body `{mode: "solve"|"english", scope?: dict, messages: [{role, content}]}` -> `{"answer": str}`. 503 if no provider configured.

- [ ] **Step 1: Write the failing test**

`backend/tests/test_tutor_api.py`:
```python
from app.tutor.provider import FakeProvider


def test_ask_503_when_no_provider(client):
    client.app.state.tutor_provider = None
    resp = client.post("/tutor/ask", json={"mode": "english", "messages": []})
    assert resp.status_code == 503


def test_english_mode_uses_coach_prompt(client):
    fake = FakeProvider("Let's practice.")
    client.app.state.tutor_provider = fake
    resp = client.post("/tutor/ask", json={
        "mode": "english",
        "messages": [{"role": "user", "content": "Help me with standup English."}],
    })
    assert resp.status_code == 200
    assert resp.json()["answer"] == "Let's practice."
    assert "conversation coach" in fake.last_system


def test_solve_mode_builds_context_from_scope(client):
    fake = FakeProvider("Here's why.")
    client.app.state.tutor_provider = fake
    resp = client.post("/tutor/ask", json={
        "mode": "solve",
        "scope": {"question_id": "ds-arrays-001"},
        "messages": [{"role": "user", "content": "Why O(1)?"}],
    })
    assert resp.status_code == 200
    # the question text from the seed fixture is stuffed into the system prompt
    assert "Access time of array index?" in fake.last_system
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_tutor_api.py -v`
Expected: FAIL — 404 on `/tutor/ask`.

- [ ] **Step 3: Write the router**

`backend/app/api/tutor.py`:
```python
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from ..tutor.context import build_context
from ..tutor.prompts import solve_system, english_system

router = APIRouter()


class TutorIn(BaseModel):
    mode: str
    scope: dict | None = None
    messages: list[dict]


@router.post("/tutor/ask")
def ask(request: Request, body: TutorIn):
    provider = getattr(request.app.state, "tutor_provider", None)
    if provider is None:
        raise HTTPException(status_code=503, detail="tutor provider not configured")

    if body.mode == "solve":
        ctx = build_context(
            body.scope or {},
            request.app.state.questions_by_id,
            request.app.state.content_dir,
            request.app.state.db,
        )
        system = solve_system(ctx)
    else:
        system = english_system()

    answer = provider.complete(system, body.messages)
    return {"answer": answer}
```

- [ ] **Step 4: Wire provider + router in main.py**

In `backend/app/main.py`:
1. Add import near the top: `from .tutor.provider import make_provider`.
2. After `app.state.db = conn` (or wherever state is set), add: `app.state.tutor_provider = make_provider()`.
3. In the router block, add `tutor` to the import and register it: `app.include_router(tutor.router)` (add `tutor` to the `from .api import ...` line).

- [ ] **Step 5: Run to verify pass**

Run: `python -m pytest tests/test_tutor_api.py -v`
Expected: PASS (3 passed — fake provider, no real API call).

- [ ] **Step 6: Run full backend suite**

Run: `python -m pytest`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add backend/app/api/tutor.py backend/app/main.py backend/tests/test_tutor_api.py
git commit -m "feat: add POST /tutor/ask endpoint with provider injection"
```

---

## Task 4: Frontend tutor UI

**Files:**
- Modify: `frontend/src/api/client.js` (add `askTutor`)
- Create: `frontend/src/components/TutorPanel.jsx`, `frontend/src/pages/Tutor.jsx`
- Modify: `frontend/src/App.jsx` (route + nav), `frontend/src/components/QuestionCard.jsx` (toggle a solve-mode panel)

**Interfaces:**
- `askTutor({ mode, scope, messages })` -> `{ answer }`.
- `TutorPanel` props `{ mode, scope }` — a small chat (message list + input) calling `askTutor`, holding history in local state.
- `/tutor` route renders an English-coach `TutorPanel mode="english"`.

Frontend uses **manual verification** + `npm run build`.

- [ ] **Step 1: Add askTutor to client.js**

In `frontend/src/api/client.js`, add:
```javascript
export async function askTutor({ mode, scope, messages }) {
  const res = await fetch(`${BASE}/tutor/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode, scope, messages }),
  });
  if (!res.ok) throw new Error(`POST /tutor/ask -> ${res.status}`);
  return res.json();
}
```

- [ ] **Step 2: Create TutorPanel.jsx**

`frontend/src/components/TutorPanel.jsx`:
```jsx
import { useState } from "react";
import { askTutor } from "../api/client";

export default function TutorPanel({ mode, scope }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  async function send() {
    if (!input.trim()) return;
    const next = [...messages, { role: "user", content: input }];
    setMessages(next);
    setInput("");
    setBusy(true);
    setErr("");
    try {
      const { answer } = await askTutor({ mode, scope, messages: next });
      setMessages([...next, { role: "assistant", content: answer }]);
    } catch (e) {
      setErr("小老師暫時無法回應（後端可能未設定 ANTHROPIC_API_KEY）。");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="card">
      <div>
        {messages.map((m, i) => (
          <p key={i} style={{ whiteSpace: "pre-wrap" }}>
            <strong>{m.role === "user" ? "你" : "🧑‍🏫 小老師"}：</strong> {m.content}
          </p>
        ))}
      </div>
      {err && <p style={{ color: "#d24a4a" }}>{err}</p>}
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="問小老師…"
        style={{ width: "100%", minHeight: 70, padding: 8 }}
      />
      <button className="primary" onClick={send} disabled={busy}>
        {busy ? "思考中…" : "送出"}
      </button>
    </div>
  );
}
```

- [ ] **Step 3: Create the English-coach page**

`frontend/src/pages/Tutor.jsx`:
```jsx
import TutorPanel from "../components/TutorPanel";

export default function Tutor() {
  return (
    <div>
      <h2>英文對話教練</h2>
      <p style={{ color: "#888" }}>用英文跟小老師練習面試、standup、code review 等情境。</p>
      <TutorPanel mode="english" />
    </div>
  );
}
```

- [ ] **Step 4: Add route + nav in App.jsx**

In `frontend/src/App.jsx`: import `Tutor` (`import Tutor from "./pages/Tutor";`), add a nav link `<Link to="/tutor">小老師</Link>`, and add the route `<Route path="/tutor" element={<Tutor />} />`.

- [ ] **Step 5: Add a solve-mode panel to QuestionCard**

In `frontend/src/components/QuestionCard.jsx`, import the panel and a toggle. Add at the top: `import TutorPanel from "./TutorPanel";` and a state `const [askOpen, setAskOpen] = useState(false);`. Inside the `{result && ( ... )}` explanation block, after the 下一題 button, add:
```jsx
          <button className="option" onClick={() => setAskOpen((o) => !o)}>
            🧑‍🏫 問小老師
          </button>
          {askOpen && (
            <TutorPanel mode="solve" scope={{ question_id: question.id }} />
          )}
```

- [ ] **Step 6: Build to verify**

Run (from `frontend/`): `npm run build`
Expected: build succeeds; then `rm -rf dist`.

- [ ] **Step 7: Manual verification**

Set `ANTHROPIC_API_KEY` in the backend environment, restart `uvicorn`, then with the frontend running:
1. `/tutor` (English coach): type an English message → small delay → coach replies; without a key, the panel shows the friendly error and the rest of the app keeps working.
2. In `/practice`, answer a question → 🧑‍🏫 問小老師 → ask "為什麼是 O(1)?" → the answer references the question/notes context.
3. Confirm no key is committed and `ANTHROPIC_API_KEY` is only in the environment.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/api/client.js frontend/src/components/TutorPanel.jsx frontend/src/pages/Tutor.jsx frontend/src/App.jsx frontend/src/components/QuestionCard.jsx
git commit -m "feat: add tutor chat UI (solve panel + english coach page)"
```

---

## Self-Review Notes

- **Spec coverage:** pure `build_context` from question+tutorial+notes+history (Task 1); swappable `TutorProvider` with Claude default + fake + env-gated `make_provider` and both prompt modes (Task 2); `POST /tutor/ask` with 503-when-unconfigured (Task 3); chat UI — solve panel on cards + English-coach page, history in frontend (Task 4).
- **Deferred (per spec, absent):** vector retrieval, STT/TTS voice, chat persistence, multi-provider UI.
- **Design-invariant check:** no new DB table; tutor only reads existing content + attempts; key via env, never committed; router depends on the `TutorProvider` interface; frontend calls go through `api/client`.
- **Type consistency:** `build_context(scope, questions_by_id, content_dir, conn)`, `TutorProvider.complete(system, messages) -> str`, `make_provider() -> TutorProvider | None`, `askTutor({mode, scope, messages})` used identically across tasks.
- **API correctness:** `ClaudeProvider` uses `anthropic.Anthropic()` (reads `ANTHROPIC_API_KEY`) + `messages.create(model="claude-opus-4-8", max_tokens=2000, system=..., messages=...)`, per the claude-api skill. Re-verify the SDK call against that skill before implementing.
```
