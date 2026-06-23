import sqlite3
from collections import defaultdict


def compute_stats(conn: sqlite3.Connection, questions) -> dict:
    by_id = {q.id: q for q in questions}
    rows = conn.execute(
        "SELECT question_id, is_correct FROM attempts"
    ).fetchall()

    subj: dict[str, list[int]] = defaultdict(lambda: [0, 0])   # [correct, total]
    diff: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    perq: dict[str, list[int]] = defaultdict(lambda: [0, 0])   # [wrong, total]

    for r in rows:
        q = by_id.get(r["question_id"])
        if q is None:
            continue
        correct = r["is_correct"]
        subj[q.subject][0] += correct
        subj[q.subject][1] += 1
        diff[q.difficulty][0] += correct
        diff[q.difficulty][1] += 1
        perq[r["question_id"]][0] += 0 if correct else 1
        perq[r["question_id"]][1] += 1

    def _acc(c: int, t: int) -> float:
        return round(c / t, 3) if t else 0.0

    by_subject = [
        {"subject": s, "correct": v[0], "attempted": v[1], "accuracy": _acc(*v)}
        for s, v in sorted(subj.items())
    ]
    by_difficulty = [
        {"difficulty": d, "correct": v[0], "attempted": v[1], "accuracy": _acc(*v)}
        for d, v in sorted(diff.items())
    ]
    weakest = sorted(
        (
            {"question_id": qid, "wrong": v[0], "total": v[1]}
            for qid, v in perq.items()
            if v[0] > 0
        ),
        key=lambda x: (-x["wrong"], x["question_id"]),
    )[:10]
    return {
        "by_subject": by_subject,
        "by_difficulty": by_difficulty,
        "weakest_questions": weakest,
    }
