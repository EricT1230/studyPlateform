from app.db.attempts import record_attempt


def test_stats_empty(client):
    data = client.get("/stats").json()
    assert data["by_subject"] == []
    assert data["weakest_questions"] == []


def test_stats_after_attempts(client):
    client.post("/attempts", json={"question_id": "ds-arrays-001", "chosen": 1})  # wrong
    client.post("/attempts", json={"question_id": "ds-arrays-001", "chosen": 0})  # right
    client.post("/attempts", json={"question_id": "en-vocab-001", "chosen": 1})   # right
    data = client.get("/stats").json()

    ds = next(r for r in data["by_subject"] if r["subject"] == "data-structures")
    assert ds["attempted"] == 2
    assert ds["correct"] == 1
    assert ds["accuracy"] == 0.5

    weak = data["weakest_questions"]
    assert weak[0]["question_id"] == "ds-arrays-001"
    assert weak[0]["wrong"] == 1
    assert weak[0]["total"] == 2


def test_stats_skips_attempts_for_unknown_questions(client):
    # Simulate a question that was deleted from YAML after an attempt was logged.
    record_attempt(client.app.state.db, "deleted-question", False, 0)
    client.post("/attempts", json={"question_id": "ds-arrays-001", "chosen": 0})
    data = client.get("/stats").json()
    # The stale attempt contributes to no subject/difficulty/weakest bucket.
    assert all(q["question_id"] != "deleted-question" for q in data["weakest_questions"])
    total_attempted = sum(r["attempted"] for r in data["by_subject"])
    assert total_attempted == 1
