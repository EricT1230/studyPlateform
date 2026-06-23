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
