import sqlite3
import uuid
from datetime import datetime
import json

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

        CREATE TABLE IF NOT EXISTS model_calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            total_tokens INTEGER,
            duration_ms INTEGER,
            created_at TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        );

        CREATE TABLE IF NOT EXISTS tool_calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            tool_name TEXT NOT NULL,
            arguments TEXT NOT NULL,
            result TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        );

        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            workspace_path TEXT NOT NULL UNIQUE,
            git_remote TEXT,
            project_md_path TEXT,
            project_md_sha256 TEXT,
            project_md_content TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
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


def get_recent_messages(
    conn: sqlite3.Connection,
    session_id: str,
    limit: int = 12,
) -> list[dict[str, str]]:
    rows = conn.execute(
        """
        SELECT role, content
        FROM messages
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (
            session_id,
            limit,
        ),
    ).fetchall()

    rows.reverse()

    return [
        {
            "role": row["role"],
            "content": row["content"],
        }
        for row in rows
    ]


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


def add_model_call(
    conn: sqlite3.Connection,
    session_id: str,
    provider: str,
    model: str,
    prompt_tokens: int | None,
    completion_tokens: int | None,
    total_tokens: int | None,
    duration_ms: int | None,
) -> None:
    conn.execute(
        """
        INSERT INTO model_calls(
            session_id,
            provider,
            model,
            prompt_tokens,
            completion_tokens,
            total_tokens,
            duration_ms,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session_id,
            provider,
            model,
            prompt_tokens,
            completion_tokens,
            total_tokens,
            duration_ms,
            datetime.now().isoformat(),
        ),
    )
    conn.commit()


def list_model_calls(
    conn: sqlite3.Connection,
    session_id: str,
) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT
            provider,
            model,
            prompt_tokens,
            completion_tokens,
            total_tokens,
            duration_ms,
            created_at
        FROM model_calls
        WHERE session_id = ?
        ORDER BY id ASC
        """,
        (session_id,),
    ).fetchall()


def add_tool_call(
    conn: sqlite3.Connection,
    session_id: str,
    tool_name: str,
    arguments: dict,
    result: str,
) -> None:
    conn.execute(
        """
        INSERT INTO tool_calls(
            session_id,
            tool_name,
            arguments,
            result,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            session_id,
            tool_name,
            json.dumps(arguments, ensure_ascii=False),
            result,
            datetime.now().isoformat(),
        ),
    )
    conn.commit()


def list_tool_calls(
    conn: sqlite3.Connection,
    session_id: str,
) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT
            id,
            tool_name,
            arguments,
            result,
            created_at
        FROM tool_calls
        WHERE session_id = ?
        ORDER BY id ASC
        """,
        (session_id,),
    ).fetchall()


def upsert_project(
    conn: sqlite3.Connection,
    name: str,
    workspace_path: str,
    git_remote: str | None,
    project_md_path: str,
    project_md_sha256: str,
    project_md_content: str,
) -> None:
    now = datetime.now().isoformat()

    conn.execute(
        """
        INSERT INTO projects(
            name,
            workspace_path,
            git_remote,
            project_md_path,
            project_md_sha256,
            project_md_content,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(workspace_path) DO UPDATE SET
            name = excluded.name,
            git_remote = excluded.git_remote,
            project_md_path = excluded.project_md_path,
            project_md_sha256 = excluded.project_md_sha256,
            project_md_content = excluded.project_md_content,
            updated_at = excluded.updated_at
        """,
        (
            name,
            workspace_path,
            git_remote,
            project_md_path,
            project_md_sha256,
            project_md_content,
            now,
            now,
        ),
    )

    conn.commit()


def get_project_by_workspace(
    conn: sqlite3.Connection,
    workspace_path: str,
) -> sqlite3.Row | None:
    return conn.execute(
        """
        SELECT *
        FROM projects
        WHERE workspace_path = ?
        """,
        (workspace_path,),
    ).fetchone()
