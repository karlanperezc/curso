from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(_connect(db_path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_document(db_path: Path, filename: str, text: str) -> int:
    with closing(_connect(db_path)) as conn:
        cursor = conn.execute(
            "INSERT INTO documents (filename, text, created_at) VALUES (?, ?, ?)",
            (filename, text, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        return cursor.lastrowid


def list_documents(db_path: Path) -> list[sqlite3.Row]:
    with closing(_connect(db_path)) as conn:
        return conn.execute(
            "SELECT id, filename, text, created_at FROM documents ORDER BY id DESC"
        ).fetchall()


def get_document(db_path: Path, doc_id: int) -> sqlite3.Row | None:
    with closing(_connect(db_path)) as conn:
        return conn.execute(
            "SELECT id, filename, text, created_at FROM documents WHERE id = ?",
            (doc_id,),
        ).fetchone()


def delete_document(db_path: Path, doc_id: int) -> None:
    with closing(_connect(db_path)) as conn:
        conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()
