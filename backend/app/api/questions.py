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
