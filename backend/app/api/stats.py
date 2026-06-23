from fastapi import APIRouter, Request
from ..stats_service import compute_stats

router = APIRouter()


@router.get("/stats")
def get_stats(request: Request):
    return compute_stats(request.app.state.db, request.app.state.questions)
