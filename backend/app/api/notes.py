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
