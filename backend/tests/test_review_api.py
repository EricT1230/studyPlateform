from datetime import date

from app.db.schedule import upsert_schedule


def test_review_empty_initially(client):
    assert client.get("/review").json() == []


def test_review_returns_due_question_after_wrong_answer(client):
    # Wrong answer -> box 1, due_date is tomorrow (interval 1), so it should
    # NOT appear in today's review.
    client.post("/attempts", json={"question_id": "ds-arrays-001", "chosen": 1})
    assert client.get("/review").json() == []


def test_review_returns_question_once_due(client):
    # Force a due-today schedule by writing directly, then verify /review surfaces it.
    upsert_schedule(client.app.state.db, "ds-arrays-001", 1, date.today(), date.today())
    data = client.get("/review").json()
    assert [q["id"] for q in data] == ["ds-arrays-001"]
    # full question shape is returned (reused by the frontend card)
    assert data[0]["options"] and "answer" in data[0]


def test_review_skips_ids_not_in_bank(client):
    upsert_schedule(
        client.app.state.db, "deleted-question", 1, date.today(), date.today()
    )
    assert client.get("/review").json() == []
