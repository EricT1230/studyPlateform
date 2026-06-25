def test_get_notes_empty_when_absent(client):
    resp = client.get("/notes/data-structures/arrays")
    assert resp.status_code == 200
    assert resp.json()["markdown"] == ""


def test_put_then_get_notes(client):
    put = client.put("/notes/data-structures/arrays", json={"markdown": "# note\n"})
    assert put.status_code == 200
    assert put.json() == {"ok": True}
    got = client.get("/notes/data-structures/arrays").json()
    assert got["markdown"] == "# note\n"
    assert got["subject"] == "data-structures"


def test_bad_segment_get_400(client):
    assert client.get("/notes/ok/..").status_code in (400, 404)
    # a dotted segment routes but must be rejected by validation
    assert client.get("/notes/ok/a.b").status_code == 400


def test_bad_segment_put_400(client):
    assert client.put("/notes/ok/a.b", json={"markdown": "x"}).status_code == 400
