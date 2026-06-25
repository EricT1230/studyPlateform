from datetime import date

import pytest

from app.db.database import get_connection, init_db
from app.db.schedule import due_count, due_question_ids, get_box, upsert_schedule


TODAY = date(2026, 6, 24)


@pytest.fixture
def conn(tmp_path):
    c = get_connection(tmp_path / "test.db")
    init_db(c)
    yield c
    c.close()


def test_get_box_none_when_absent(conn):
    assert get_box(conn, "q1") is None


def test_upsert_then_get_box(conn):
    upsert_schedule(conn, "q1", 2, date(2026, 6, 27), TODAY)
    assert get_box(conn, "q1") == 2


def test_upsert_updates_existing_row(conn):
    upsert_schedule(conn, "q1", 2, date(2026, 6, 27), TODAY)
    upsert_schedule(conn, "q1", 1, date(2026, 6, 25), TODAY)
    assert get_box(conn, "q1") == 1
    assert conn.execute("SELECT COUNT(*) AS n FROM schedule").fetchone()["n"] == 1


def test_due_question_ids_only_due_and_sorted(conn):
    upsert_schedule(conn, "overdue", 3, date(2026, 6, 20), TODAY)
    upsert_schedule(conn, "today-b1", 1, date(2026, 6, 24), TODAY)
    upsert_schedule(conn, "today-b4", 4, date(2026, 6, 24), TODAY)
    upsert_schedule(conn, "future", 2, date(2026, 6, 30), TODAY)

    ids = due_question_ids(conn, TODAY)
    assert ids == ["overdue", "today-b1", "today-b4"]
    assert "future" not in ids


def test_due_count(conn):
    upsert_schedule(conn, "a", 1, date(2026, 6, 20), TODAY)
    upsert_schedule(conn, "b", 1, date(2026, 6, 30), TODAY)
    assert due_count(conn, TODAY) == 1
