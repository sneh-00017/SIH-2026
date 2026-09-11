import json
import os
import sqlite3
from datetime import datetime, timezone

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "safesight.db")


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                media_type TEXT NOT NULL CHECK(media_type IN ('image', 'video')),
                filename TEXT NOT NULL,
                risk_score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                hazards_json TEXT NOT NULL,
                explanation_json TEXT NOT NULL,
                risk_factors_json TEXT NOT NULL,
                detected_objects_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )


def now():
    return datetime.now(timezone.utc).isoformat()


def save_analysis(result, media_type, filename, metadata=None):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO analyses (
                media_type, filename, risk_score, risk_level,
                hazards_json, explanation_json, risk_factors_json,
                detected_objects_json, metadata_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                media_type,
                filename,
                int(result.get("risk_score", result.get("score", 0))),
                result.get("risk_level", "LOW"),
                json.dumps(result.get("hazards", [])),
                json.dumps(result.get("explanation", [])),
                json.dumps(result.get("risk_factors", [])),
                json.dumps(result.get("detected_objects", [])),
                json.dumps(metadata or {}),
                now(),
            ),
        )
        return cursor.lastrowid


def list_analyses(limit=50):
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM analyses ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()

    analyses = []
    for row in rows:
        item = dict(row)
        for field in ("hazards", "explanation", "risk_factors", "detected_objects", "metadata"):
            item[field] = json.loads(item.pop(f"{field}_json"))
        analyses.append(item)
    return analyses
