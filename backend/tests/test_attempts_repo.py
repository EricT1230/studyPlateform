import pytest
from app.db.database import get_connection, init_db
from app.db.attempts import record_attempt, wrong_question_ids


@pytest.fixture
def conn(tmp_path):
    c = get_connection(tmp_path / "test.db")
    init_db(c)
    yield c
    c.close()


def test_record_returns_row_id(conn):
    rid = record_attempt(conn, "q1", True, 0)
    assert rid == 1


def test_wrong_ids_empty_initially(conn):
    assert wrong_question_ids(conn) == set()


def test_wrong_id_listed_when_last_attempt_wrong(conn):
    record_attempt(conn, "q1", False, 1)
    assert wrong_question_ids(conn) == {"q1"}


def test_question_leaves_wrong_book_after_correct(conn):
    record_attempt(conn, "q1", False, 1)
    record_attempt(conn, "q1", True, 0)
    assert wrong_question_ids(conn) == set()
