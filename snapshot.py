"""
SQLite snapshot storage for Sebo weekly SEO data.
Stores full comparison dumps and auto-logs quick wins / losing keywords as recommendations.
"""

import json
import sqlite3
from datetime import datetime, timezone

DB_FILE = "sebo.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                site_url    TEXT    NOT NULL,
                created_at  TEXT    NOT NULL,
                data_json   TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS recommendations (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id      INTEGER NOT NULL REFERENCES snapshots(id),
                type             TEXT    NOT NULL,
                keyword_or_page  TEXT    NOT NULL,
                value_before     REAL,
                created_at       TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS results (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                recommendation_id INTEGER NOT NULL REFERENCES recommendations(id),
                value_after       REAL,
                measured_at       TEXT    NOT NULL,
                delta_percent     REAL
            );
        """)


def save_snapshot(site_url: str, data: dict) -> int:
    """Persist a full comparison snapshot. Returns the new snapshot id."""
    init_db()
    now = datetime.now(timezone.utc).isoformat()

    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO snapshots (site_url, created_at, data_json) VALUES (?, ?, ?)",
            (site_url, now, json.dumps(data)),
        )
        snapshot_id = cur.lastrowid

    recs = []
    for row in data.get("queries", {}).get("quick_wins", []):
        recs.append(("quick_win", row["key"], row["current_position"]))
    for row in data.get("queries", {}).get("losing", []):
        recs.append(("losing", row["key"], row["current_position"]))

    if recs:
        with _connect() as conn:
            conn.executemany(
                "INSERT INTO recommendations (snapshot_id, type, keyword_or_page, value_before, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                [(snapshot_id, t, k, v, now) for t, k, v in recs],
            )

    return snapshot_id


def get_latest_snapshot(site_url: str) -> dict | None:
    """Return the most recent snapshot data for a site, or None."""
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT data_json FROM snapshots WHERE site_url = ? ORDER BY created_at DESC LIMIT 1",
            (site_url,),
        ).fetchone()
    return json.loads(row["data_json"]) if row else None


def get_snapshot_count(site_url: str) -> int:
    """Return total number of snapshots saved for a site."""
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as n FROM snapshots WHERE site_url = ?",
            (site_url,),
        ).fetchone()
    return row["n"]


if __name__ == "__main__":
    init_db()
    print(f"DB initialised: {DB_FILE}")
    print("Tables: snapshots, recommendations, results")
