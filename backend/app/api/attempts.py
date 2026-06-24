from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from ..db.attempts import record_attempt

router = APIRouter()


class AttemptIn(BaseModel):
    question_id: str
    chosen: int


@router.post("/attempts")
def post_attempt(request: Request, attempt: AttemptIn):
    q = request.app.state.questions_by_id.get(attempt.question_id)
    if q is None:
        raise HTTPException(status_code=404, detail="question not found")
    is_correct = attempt.chosen == q.answer
    record_attempt(request.app.state.db, q.id, is_correct, attempt.chosen)
    return {"is_correct": is_correct, "answer": q.answer, "explanation": q.explanation}
