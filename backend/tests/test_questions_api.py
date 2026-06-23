def test_subjects_lists_subjects_and_topics(client):
    resp = client.get("/subjects")
    assert resp.status_code == 200
    data = resp.json()
    subjects = {row["subject"] for row in data}
    assert subjects == {"data-structures", "english"}
    ds = next(r for r in data if r["subject"] == "data-structures")
    assert ds["topics"] == ["arrays"]


def test_questions_returns_all(client):
    resp = client.get("/questions")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_questions_filtered_by_subject(client):
    resp = client.get("/questions", params={"subject": "english"})
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == "en-vocab-001"


def test_questions_only_wrong(client):
    # answer ds-arrays-001 incorrectly, then request only_wrong
    client.post("/attempts", json={"question_id": "ds-arrays-001", "chosen": 1})
    resp = client.get("/questions", params={"only_wrong": "true"})
    ids = [q["id"] for q in resp.json()]
    assert ids == ["ds-arrays-001"]
