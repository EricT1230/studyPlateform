import pytest
from fastapi.testclient import TestClient
from app.main import create_app


@pytest.fixture
def content_dir(tmp_path):
    ds = tmp_path / "data-structures"
    ds.mkdir()
    (ds / "arrays.yaml").write_text("""
- id: ds-arrays-001
  difficulty: basic
  tags: [arrays]
  question: Access time of array index?
  options: ["O(1)", "O(n)"]
  answer: 0
  explanation: Direct address computation.
""", encoding="utf-8")
    (ds / "arrays.md").write_text("# Arrays\n\nContiguous memory.", encoding="utf-8")
    en = tmp_path / "english"
    en.mkdir()
    (en / "vocabulary.yaml").write_text("""
- id: en-vocab-001
  difficulty: basic
  question: "Pick the synonym of 'deprecate' in software."
  options: ["promote", "discourage use of", "compile"]
  answer: 1
  explanation: Deprecated APIs are discouraged from use.
""", encoding="utf-8")
    return tmp_path


@pytest.fixture
def client(content_dir, tmp_path):
    app = create_app(content_dir=content_dir, db_path=tmp_path / "test.db")
    return TestClient(app)
