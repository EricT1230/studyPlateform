from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/subjects")
def get_subjects(request: Request):
    tree: dict[str, set[str]] = {}
    for q in request.app.state.questions:
        tree.setdefault(q.subject, set()).add(q.topic)
    return [
        {"subject": s, "topics": sorted(topics)}
        for s, topics in sorted(tree.items())
    ]
