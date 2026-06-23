import pytest
from pydantic import ValidationError
from app.content.schema import Question, LoadedQuestion


def test_valid_question():
    q = Question(
        id="ds-arrays-001",
        difficulty="basic",
        question="Access time of array index?",
        options=["O(1)", "O(n)"],
        answer=0,
    )
    assert q.type == "mcq"
    assert q.answer == 0
    assert q.tags == []


def test_answer_out_of_range_rejected():
    with pytest.raises(ValidationError):
        Question(
            id="x", difficulty="basic", question="q",
            options=["a", "b"], answer=5,
        )


def test_too_few_options_rejected():
    with pytest.raises(ValidationError):
        Question(
            id="x", difficulty="basic", question="q",
            options=["only one"], answer=0,
        )


def test_bad_difficulty_rejected():
    with pytest.raises(ValidationError):
        Question(
            id="x", difficulty="expert", question="q",
            options=["a", "b"], answer=0,
        )


def test_loaded_question_has_subject_topic():
    q = LoadedQuestion(
        id="x", difficulty="basic", question="q",
        options=["a", "b"], answer=0,
        subject="data-structures", topic="arrays",
    )
    assert q.subject == "data-structures"
    assert q.topic == "arrays"
