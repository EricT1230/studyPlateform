def test_correct_attempt(client):
    resp = client.post("/attempts", json={"question_id": "ds-arrays-001", "chosen": 0})
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_correct"] is True
    assert body["answer"] == 0
    assert "Direct address" in body["explanation"]


def test_wrong_attempt(client):
    resp = client.post("/attempts", json={"question_id": "ds-arrays-001", "chosen": 1})
    body = resp.json()
    assert body["is_correct"] is False
    assert body["answer"] == 0


def test_unknown_question_404(client):
    resp = client.post("/attempts", json={"question_id": "nope", "chosen": 0})
    assert resp.status_code == 404


def test_attempt_is_recorded(client):
    client.post("/attempts", json={"question_id": "ds-arrays-001", "chosen": 1})
    wrong = client.get("/questions", params={"only_wrong": "true"}).json()
    assert [q["id"] for q in wrong] == ["ds-arrays-001"]
