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
