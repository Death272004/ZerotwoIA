from pathlib import Path
import sqlite3
import threading
from config import MAX_DB_ROWS

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "memory.db"

# Conexión persistente por thread — evita abrir/cerrar en cada operación
_local = threading.local()


def get_conn() -> sqlite3.Connection:
    if not hasattr(_local, "conn"):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _local.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return _local.conn


def init_db() -> None:
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            role    TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)
    # Índice para acelerar ORDER BY id DESC
    conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_id ON memory(id DESC)")
    conn.commit()


def save_message(role: str, content: str) -> None:
    conn = get_conn()
    conn.execute(
        "INSERT INTO memory (role, content) VALUES (?, ?)",
        (role, content)
    )
    # Mantiene la DB acotada — borra registros viejos si supera MAX_DB_ROWS
    conn.execute("""
        DELETE FROM memory
        WHERE id NOT IN (
            SELECT id FROM memory ORDER BY id DESC LIMIT ?
        )
    """, (MAX_DB_ROWS,))
    conn.commit()


def load_history(limit: int = 20) -> list[dict]:
    conn = get_conn()
    cursor = conn.execute(
        "SELECT role, content FROM memory ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    return list(reversed([{"role": r, "content": c} for r, c in rows]))


def clear_memory() -> None:
    conn = get_conn()
    conn.execute("DELETE FROM memory")
    conn.commit()
