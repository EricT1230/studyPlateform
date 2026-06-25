# Phase 2 — Content Expansion + Notes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.
>
> Read first: [AGENTS.md](../../../AGENTS.md), [ARCHITECTURE.md](../../ARCHITECTURE.md), [Phase 2 spec](../specs/2026-06-24-phase2-content-and-notes-design.md).
> **Prerequisite:** Phase 1 complete (Review.jsx exists). Part A (content) needs no code — see the spec; this plan covers **Part B: the notes feature**.

**Goal:** Add file-based per-topic notes (`content/<subject>/<topic>.notes.md`) with a backend read/write API and a frontend editor panel embedded in practice, review, and tutorial pages.

**Architecture:** A pure path-resolver + file I/O service (`notes_service`) backs `GET`/`PUT /notes/{subject}/{topic}`. The frontend `NotesPanel` loads and saves notes via `api/client`. Notes are Markdown files in `content/`, git-managed — no DB.

**Tech Stack:** FastAPI, pytest (backend); React + Vite (frontend).

## Global Constraints

- Notes are stored ONLY as files at `content/<subject>/<topic>.notes.md`. Never in the DB. Never mixed with `<topic>.yaml` (questions) or `<topic>.md` (tutorial).
- All file reads/writes use `encoding="utf-8"`.
- `subject` and `topic` path segments MUST match `^[A-Za-z0-9_-]+$` — reject anything else with HTTP 400 (prevents path traversal outside `content/`).
- `GET /notes` for a topic with no notes file returns `markdown: ""` (HTTP 200), NOT 404 — the editor opens on empty content.
- Backend tests run from `backend/` with venv active: `python -m pytest`.

---

## File Structure

```
backend/app/
  notes_service.py     CREATE  notes_path() (safe resolve) + read_notes() + write_notes()
  api/notes.py         CREATE  GET/PUT /notes/{subject}/{topic}
  main.py              MODIFY  register notes router
backend/tests/
  test_notes_service.py  CREATE
  test_notes_api.py      CREATE
frontend/src/
  components/NotesPanel.jsx   CREATE  collapsible textarea editor
  api/client.js              MODIFY  getNotes / saveNotes
  pages/Practice.jsx         MODIFY  embed NotesPanel for current question's topic
  pages/Review.jsx           MODIFY  embed NotesPanel
  pages/Tutorial.jsx         MODIFY  embed NotesPanel
```

---

## Task 1: notes_service (safe path + read/write)

**Files:**
- Create: `backend/app/notes_service.py`
- Test: `backend/tests/test_notes_service.py`

**Interfaces:**
- Produces: `notes_path(content_dir: Path, subject: str, topic: str) -> Path` — returns `content_dir/subject/{topic}.notes.md`; raises `ValueError` if `subject`/`topic` fails `^[A-Za-z0-9_-]+$`.
- Produces: `read_notes(content_dir, subject, topic) -> str` — file contents, or `""` if absent. Raises `ValueError` on bad segment.
- Produces: `write_notes(content_dir, subject, topic, markdown: str) -> None` — creates parent dir if needed, writes UTF-8. Raises `ValueError` on bad segment.

- [x] **Step 1: Write the failing test**

`backend/tests/test_notes_service.py`:
```python
import pytest
from app.notes_service import notes_path, read_notes, write_notes


def test_read_missing_returns_empty(tmp_path):
    assert read_notes(tmp_path, "data-structures", "arrays") == ""


def test_write_then_read_roundtrip(tmp_path):
    write_notes(tmp_path, "data-structures", "arrays", "# my note\n")
    assert read_notes(tmp_path, "data-structures", "arrays") == "# my note\n"


def test_write_creates_subject_dir(tmp_path):
    write_notes(tmp_path, "new-subject", "new-topic", "hello")
    assert (tmp_path / "new-subject" / "new-topic.notes.md").exists()


def test_notes_path_location(tmp_path):
    p = notes_path(tmp_path, "english", "vocabulary")
    assert p == tmp_path / "english" / "vocabulary.notes.md"


@pytest.mark.parametrize("bad", ["..", "a/b", "a.b", "x/../y", ".", ""])
def test_bad_segment_rejected(tmp_path, bad):
    with pytest.raises(ValueError):
        notes_path(tmp_path, bad, "ok")
    with pytest.raises(ValueError):
        notes_path(tmp_path, "ok", bad)
```

- [x] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_notes_service.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.notes_service'`.

- [x] **Step 3: Write the implementation**

`backend/app/notes_service.py`:
```python
import re
from pathlib import Path

_SEGMENT = re.compile(r"^[A-Za-z0-9_-]+$")


def _check(segment: str) -> None:
    if not _SEGMENT.match(segment):
        raise ValueError(f"invalid path segment: {segment!r}")


def notes_path(content_dir: Path, subject: str, topic: str) -> Path:
    _check(subject)
    _check(topic)
    return content_dir / subject / f"{topic}.notes.md"


def read_notes(content_dir: Path, subject: str, topic: str) -> str:
    p = notes_path(content_dir, subject, topic)
    return p.read_text(encoding="utf-8") if p.exists() else ""


def write_notes(content_dir: Path, subject: str, topic: str, markdown: str) -> None:
    p = notes_path(content_dir, subject, topic)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(markdown, encoding="utf-8")
```

- [x] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_notes_service.py -v`
Expected: PASS (all parametrized cases + roundtrip).

- [x] **Step 5: Commit**

```bash
git add backend/app/notes_service.py backend/tests/test_notes_service.py
git commit -m "feat: add file-based notes service with path-safety"
```

---

## Task 2: GET/PUT /notes endpoints

**Files:**
- Create: `backend/app/api/notes.py`
- Modify: `backend/app/main.py` (register router)
- Test: `backend/tests/test_notes_api.py`

**Interfaces:**
- Consumes: `read_notes`/`write_notes` from `app.notes_service`, `app.state.content_dir`.
- Produces: `GET /notes/{subject}/{topic}` -> `{"subject", "topic", "markdown"}` (empty string if no file); 400 on bad segment.
- Produces: `PUT /notes/{subject}/{topic}` body `{"markdown": str}` -> `{"ok": true}`; writes the file; 400 on bad segment.

- [ ] **Step 1: Write the failing test**

`backend/tests/test_notes_api.py`:
```python
def test_get_notes_empty_when_absent(client):
    resp = client.get("/notes/data-structures/arrays")
    assert resp.status_code == 200
    assert resp.json()["markdown"] == ""


def test_put_then_get_notes(client):
    put = client.put("/notes/data-structures/arrays", json={"markdown": "# note\n"})
    assert put.status_code == 200
    assert put.json() == {"ok": True}
    got = client.get("/notes/data-structures/arrays").json()
    assert got["markdown"] == "# note\n"
    assert got["subject"] == "data-structures"


def test_bad_segment_get_400(client):
    assert client.get("/notes/ok/..").status_code in (400, 404)
    # a dotted segment routes but must be rejected by validation
    assert client.get("/notes/ok/a.b").status_code == 400


def test_bad_segment_put_400(client):
    assert client.put("/notes/ok/a.b", json={"markdown": "x"}).status_code == 400
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_notes_api.py -v`
Expected: FAIL — 404 (routes not registered).

- [ ] **Step 3: Write the router**

`backend/app/api/notes.py`:
```python
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from ..notes_service import read_notes, write_notes

router = APIRouter()


class NotesIn(BaseModel):
    markdown: str


@router.get("/notes/{subject}/{topic}")
def get_notes(request: Request, subject: str, topic: str):
    try:
        md = read_notes(request.app.state.content_dir, subject, topic)
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid path")
    return {"subject": subject, "topic": topic, "markdown": md}


@router.put("/notes/{subject}/{topic}")
def put_notes(request: Request, subject: str, topic: str, body: NotesIn):
    try:
        write_notes(request.app.state.content_dir, subject, topic, body.markdown)
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid path")
    return {"ok": True}
```

- [ ] **Step 4: Register the router in main.py**

In `backend/app/main.py`, add `notes` to the API import block and register it (place after the existing routers):
```python
    from .api import subjects, questions, attempts, stats, tutorials, notes
    # ... existing include_router calls ...
    app.include_router(notes.router)
```
(If Phase 1's `review` router is present, keep it; just add the `notes` import and `app.include_router(notes.router)` line.)

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_notes_api.py -v`
Expected: PASS.

- [ ] **Step 6: Run the full backend suite**

Run: `python -m pytest`
Expected: PASS (all existing tests + notes).

- [ ] **Step 7: Commit**

```bash
git add backend/app/api/notes.py backend/app/main.py backend/tests/test_notes_api.py
git commit -m "feat: add GET/PUT /notes endpoints"
```

---

## Task 3: Frontend notes panel

**Files:**
- Modify: `frontend/src/api/client.js` (add `getNotes`, `saveNotes`)
- Create: `frontend/src/components/NotesPanel.jsx`
- Modify: `frontend/src/pages/Practice.jsx`, `frontend/src/pages/Review.jsx`, `frontend/src/pages/Tutorial.jsx`

**Interfaces:**
- Consumes: `getNotes(subject, topic)`, `saveNotes(subject, topic, markdown)`.
- `NotesPanel` props: `{ subject, topic }`. Loads notes on mount/prop-change; textarea + 儲存 button calling `saveNotes`.

Frontend uses **manual verification** + `npm run build`.

- [ ] **Step 1: Add client functions**

In `frontend/src/api/client.js`, add:
```javascript
export function getNotes(subject, topic) {
  return get(`/notes/${subject}/${topic}`);
}

export async function saveNotes(subject, topic, markdown) {
  const res = await fetch(`${BASE}/notes/${subject}/${topic}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ markdown }),
  });
  if (!res.ok) throw new Error(`PUT /notes -> ${res.status}`);
  return res.json();
}
```

- [ ] **Step 2: Create NotesPanel**

`frontend/src/components/NotesPanel.jsx`:
```jsx
import { useEffect, useState } from "react";
import { getNotes, saveNotes } from "../api/client";

export default function NotesPanel({ subject, topic }) {
  const [open, setOpen] = useState(false);
  const [text, setText] = useState("");
  const [status, setStatus] = useState("");

  useEffect(() => {
    if (!subject || !topic) return;
    getNotes(subject, topic).then((n) => setText(n.markdown));
  }, [subject, topic]);

  async function save() {
    setStatus("儲存中…");
    await saveNotes(subject, topic, text);
    setStatus("已儲存 ✓");
    setTimeout(() => setStatus(""), 1500);
  }

  if (!subject || !topic) return null;

  return (
    <div className="card">
      <button className="option" onClick={() => setOpen((o) => !o)}>
        ✍️ 筆記（{subject} · {topic}）{open ? "▲" : "▼"}
      </button>
      {open && (
        <div style={{ marginTop: 10 }}>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="寫下這個主題的筆記（Markdown）…"
            style={{ width: "100%", minHeight: 140, padding: 10 }}
          />
          <div style={{ marginTop: 8 }}>
            <button className="primary" onClick={save}>儲存筆記</button>
            <span style={{ marginLeft: 10, color: "#2e9e5b" }}>{status}</span>
          </div>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 3: Embed in Practice.jsx**

In `frontend/src/pages/Practice.jsx`, add the import:
```jsx
import NotesPanel from "../components/NotesPanel";
```
Then render the panel for the current question, immediately after the `<QuestionCard ... />` element (inside the `{current && ( ... )}` block):
```jsx
          <NotesPanel subject={current.subject} topic={current.topic} />
```

- [ ] **Step 4: Embed in Review.jsx**

In `frontend/src/pages/Review.jsx`, add the same import and render `<NotesPanel subject={current.subject} topic={current.topic} />` immediately after the `<QuestionCard ... />` element in the `{current && ( ... )}` block.

- [ ] **Step 5: Embed in Tutorial.jsx**

In `frontend/src/pages/Tutorial.jsx`, add the import and render the panel below the tutorial HTML. Replace the success `return` with:
```jsx
  if (error) return <p>這個主題還沒有教學文章。</p>;
  return (
    <div>
      <div dangerouslySetInnerHTML={{ __html: html }} />
      <NotesPanel subject={subject} topic={topic} />
    </div>
  );
```
(Add `import NotesPanel from "../components/NotesPanel";` at the top. `subject`/`topic` come from the existing `useParams()`.)

- [ ] **Step 6: Build to verify**

Run (from `frontend/`): `npm run build`
Expected: build succeeds; then `rm -rf dist`.

- [ ] **Step 7: Manual verification**

With backend + frontend running:
1. In `/practice`, answer a question; the ✍️ 筆記 panel shows the question's subject/topic. Expand, type, 儲存筆記 → "已儲存 ✓".
2. Reload / revisit the same topic → the saved text reloads.
3. Check `content/<subject>/<topic>.notes.md` was created on disk.
4. `/tutorial/data-structures/arrays` shows the notes panel under the article.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/api/client.js frontend/src/components/NotesPanel.jsx frontend/src/pages/Practice.jsx frontend/src/pages/Review.jsx frontend/src/pages/Tutorial.jsx
git commit -m "feat: add notes panel to practice, review, and tutorial pages"
```

---

## Self-Review Notes

- **Spec coverage:** file-based per-topic notes at `content/<subject>/<topic>.notes.md` (Task 1); GET/PUT API with empty-on-absent + path-traversal rejection (Task 2); NotesPanel embedded in practice/review/tutorial + client functions (Task 3). Content-expansion (Part A) is non-code, per spec.
- **Design-invariant check:** notes are files under `content/`, never DB; `notes_service` separates pure path-resolution from I/O; path-segment regex blocks traversal. No questions in the DB.
- **Type consistency:** `notes_path/read_notes/write_notes(content_dir, subject, topic[, markdown])`, `getNotes(subject, topic)`, `saveNotes(subject, topic, markdown)` used identically across tasks.
- **Prereq note:** Task 3 edits `Review.jsx`, which exists only after Phase 1. If Phase 1 is not yet done, skip the Review.jsx embed and add it when Phase 1 lands.
```
