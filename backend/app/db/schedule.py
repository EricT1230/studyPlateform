import sqlite3
from datetime import date


def get_box(conn: sqlite3.Connection, question_id: str) -> int | None:
    row = conn.execute(
        "SELECT box FROM schedule WHERE question_id = ?", (question_id,)
    ).fetchone()
    return row["box"] if row else None


def upsert_schedule(
    conn: sqlite3.Connection,
    question_id: str,
    box: int,
    due_date: date,
    today: date,
) -> None:
    conn.execute(
        """
        INSERT INTO schedule (question_id, box, due_date, last_reviewed)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(question_id) DO UPDATE SET
            box = excluded.box,
            due_date = excluded.due_date,
            last_reviewed = excluded.last_reviewed
        """,
        (question_id, box, due_date.isoformat(), today.isoformat()),
    )
    conn.commit()


def due_question_ids(conn: sqlite3.Connection, today: date) -> list[str]:
    rows = conn.execute(
        """
        SELECT question_id FROM schedule
        WHERE due_date <= ?
        ORDER BY due_date ASC, box ASC, question_id ASC
        """,
        (today.isoformat(),),
    ).fetchall()
    return [r["question_id"] for r in rows]


def due_count(conn: sqlite3.Connection, today: date) -> int:
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM schedule WHERE due_date <= ?",
        (today.isoformat(),),
    ).fetchone()
    return row["n"]
