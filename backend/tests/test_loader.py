import pytest
from app.content.loader import load_questions


def _write(content_dir, subject, topic, text):
    d = content_dir / subject
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{topic}.yaml").write_text(text, encoding="utf-8")


def test_loads_questions_with_subject_and_topic(tmp_path):
    _write(tmp_path, "data-structures", "arrays", """
- id: ds-arrays-001
  difficulty: basic
  question: Access time?
  options: ["O(1)", "O(n)"]
  answer: 0
""")
    questions = load_questions(tmp_path)
    assert len(questions) == 1
    assert questions[0].subject == "data-structures"
    assert questions[0].topic == "arrays"
    assert questions[0].id == "ds-arrays-001"


def test_empty_yaml_file_is_skipped(tmp_path):
    _write(tmp_path, "english", "vocabulary", "")
    assert load_questions(tmp_path) == []


def test_duplicate_id_raises(tmp_path):
    body = """
- id: dup-001
  difficulty: basic
  question: q
  options: ["a", "b"]
  answer: 0
"""
    _write(tmp_path, "english", "vocabulary", body)
    _write(tmp_path, "algorithms", "sorting", body)
    with pytest.raises(ValueError, match="duplicate"):
        load_questions(tmp_path)
