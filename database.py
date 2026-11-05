"""SQLite persistence layer. Uses fictional/demo transaction data only."""
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).with_name("fraudshield.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS transactions (
    id TEXT PRIMARY KEY,
    customer TEXT NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    country TEXT NOT NULL,
    hour INTEGER NOT NULL CHECK(hour BETWEEN 0 AND 23),
    channel TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize(seed_data: list[dict[str, Any]] | None = None):
    with connect() as conn:
        conn.execute(SCHEMA)
        count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        if count == 0 and seed_data:
            conn.executemany(
                "INSERT INTO transactions(id, customer, amount, country, hour, channel) VALUES (?, ?, ?, ?, ?, ?)",
                [(t["id"], t["customer"], float(t["amount"]), t["country"], int(t["hour"]), t["channel"]) for t in seed_data]
            )


def get_transactions() -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute("SELECT id, customer, amount, country, hour, channel, created_at FROM transactions ORDER BY created_at DESC, id").fetchall()
        return [dict(row) for row in rows]


def add_transaction(tx: dict[str, Any]):
    with connect() as conn:
        conn.execute(
            "INSERT INTO transactions(id, customer, amount, country, hour, channel) VALUES (?, ?, ?, ?, ?, ?)",
            (tx["id"], tx["customer"], float(tx["amount"]), tx["country"].upper(), int(tx["hour"]), tx["channel"].upper())
        )


def delete_all_transactions():
    with connect() as conn:
        conn.execute("DELETE FROM transactions")
