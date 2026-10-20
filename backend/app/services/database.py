
import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parents[2] / "codeguard.db"


def get_connection() -> sqlite3.Connection:
    """Create a SQLite connection with dictionary-like rows."""
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    """Create the review history table if it does not exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS review_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                language TEXT NOT NULL,
                code TEXT NOT NULL,
                status TEXT NOT NULL,
                findings_json TEXT NOT NULL,
                ai_review_json TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
