import sqlite3


def record_attempt(
    conn: sqlite3.Connection, question_id: str, is_correct: bool, chosen: int
) -> int:
    cur = conn.execute(
        "INSERT INTO attempts (question_id, is_correct, chosen) VALUES (?, ?, ?)",
        (question_id, 1 if is_correct else 0, chosen),
    )
    conn.commit()
    return cur.lastrowid


def wrong_question_ids(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute(
        """
        SELECT a.question_id AS qid
        FROM attempts a
        JOIN (
            SELECT question_id, MAX(id) AS last_id
            FROM attempts GROUP BY question_id
        ) m ON a.id = m.last_id
        WHERE a.is_correct = 0
        """
    ).fetchall()
    return {r["qid"] for r in rows}
