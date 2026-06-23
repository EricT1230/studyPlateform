def test_tutorial_returns_markdown(client):
    resp = client.get("/tutorials/data-structures/arrays")
    assert resp.status_code == 200
    body = resp.json()
    assert body["subject"] == "data-structures"
    assert "Contiguous memory" in body["markdown"]


def test_missing_tutorial_404(client):
    resp = client.get("/tutorials/english/vocabulary")
    assert resp.status_code == 404
