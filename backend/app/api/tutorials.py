from fastapi import APIRouter, Request, HTTPException

router = APIRouter()
SUPPORTED_LANGUAGES = {"zh": "", "en": ".en"}


@router.get("/tutorials/{subject}/{topic}")
def get_tutorial(request: Request, subject: str, topic: str, lang: str = "zh"):
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail="unsupported tutorial language")

    topic_dir = request.app.state.content_dir / subject
    path = topic_dir / f"{topic}{SUPPORTED_LANGUAGES[lang]}.md"
    if not path.exists():
        raise HTTPException(status_code=404, detail="tutorial not found")

    available_languages = [
        code
        for code, suffix in SUPPORTED_LANGUAGES.items()
        if (topic_dir / f"{topic}{suffix}.md").exists()
    ]
    return {
        "subject": subject,
        "topic": topic,
        "language": lang,
        "available_languages": available_languages,
        "markdown": path.read_text(encoding="utf-8"),
    }
