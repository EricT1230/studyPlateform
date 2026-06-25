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
