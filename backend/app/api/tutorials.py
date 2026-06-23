from fastapi import APIRouter, Request, HTTPException

router = APIRouter()


@router.get("/tutorials/{subject}/{topic}")
def get_tutorial(request: Request, subject: str, topic: str):
    path = request.app.state.content_dir / subject / f"{topic}.md"
    if not path.exists():
        raise HTTPException(status_code=404, detail="tutorial not found")
    return {
        "subject": subject,
        "topic": topic,
        "markdown": path.read_text(encoding="utf-8"),
    }
