import sqlite3
import uuid
from datetime import datetime

from forge.config import DB_PATH, ensure_app_dirs


def connect() -> sqlite3.Connection:
    ensure_app_dirs()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    init_db(conn)
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        );
        """
    )
    conn.commit()


def create_session(conn: sqlite3.Connection, title: str = "Untitled") -> str:
    session_id = str(uuid.uuid4())

    conn.execute(
        """
        INSERT INTO sessions(id, title, created_at)
        VALUES (?, ?, ?)
        """,
        (session_id, title, datetime.now().isoformat()),
    )
    conn.commit()

    return session_id


def add_message(
    conn: sqlite3.Connection,
    session_id: str,
    role: str,
    content: str,
) -> None:
    conn.execute(
        """
        INSERT INTO messages(session_id, role, content, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (session_id, role, content, datetime.now().isoformat()),
    )
    conn.commit()


def get_messages(conn: sqlite3.Connection, session_id: str) -> list[dict[str, str]]:
    rows = conn.execute(
        """
        SELECT role, content
        FROM messages
        WHERE session_id = ?
        ORDER BY id ASC
        """,
        (session_id,),
    ).fetchall()

    return [
        {
            "role": row["role"],
            "content": row["content"],
        }
        for row in rows
    ]


def list_sessions(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT id, title, created_at
        FROM sessions
        ORDER BY created_at DESC
        """
    ).fetchall()
