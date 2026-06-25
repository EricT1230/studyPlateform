import sqlite3
from pathlib import Path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS attempts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT    NOT NULL,
    is_correct  INTEGER NOT NULL,
    chosen      INTEGER NOT NULL,
    answered_at TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS schedule (
    question_id   TEXT PRIMARY KEY,
    box           INTEGER NOT NULL,
    due_date      TEXT    NOT NULL,
    last_reviewed TEXT    NOT NULL
);
"""


def get_connection(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(_SCHEMA)
    conn.commit()
