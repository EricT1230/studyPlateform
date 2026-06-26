def test_tutorial_returns_markdown(client):
    resp = client.get("/tutorials/data-structures/arrays")
    assert resp.status_code == 200
    body = resp.json()
    assert body["subject"] == "data-structures"
    assert body["language"] == "zh"
    assert body["available_languages"] == ["zh", "en"]
    assert "Contiguous memory" in body["markdown"]


def test_tutorial_returns_requested_english_markdown(client):
    resp = client.get("/tutorials/data-structures/arrays?lang=en")
    assert resp.status_code == 200
    body = resp.json()
    assert body["subject"] == "data-structures"
    assert body["topic"] == "arrays"
    assert body["language"] == "en"
    assert body["available_languages"] == ["zh", "en"]
    assert "English contiguous memory tutorial" in body["markdown"]


def test_tutorial_rejects_unsupported_language(client):
    resp = client.get("/tutorials/data-structures/arrays?lang=ja")
    assert resp.status_code == 400


def test_missing_tutorial_404(client):
    resp = client.get("/tutorials/english/vocabulary")
    assert resp.status_code == 404
