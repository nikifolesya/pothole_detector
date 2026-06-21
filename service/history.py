from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from time import time
from typing import Any


class RunHistory:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at REAL NOT NULL,
                    input_path TEXT NOT NULL,
                    backend TEXT NOT NULL,
                    latency_ms REAL NOT NULL,
                    detections_count INTEGER NOT NULL,
                    result_json TEXT NOT NULL
                )
                """
            )

    def add(self, result: dict[str, Any]) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO runs (
                    created_at, input_path, backend, latency_ms, detections_count, result_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    time(),
                    result["image"],
                    result["backend"],
                    float(result["latency_ms"]),
                    int(result["count"]),
                    json.dumps(result, ensure_ascii=False),
                ),
            )
            return int(cur.lastrowid)

    def stats(self) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT COUNT(*), AVG(latency_ms), MAX(latency_ms), SUM(detections_count)
                FROM runs
                """
            ).fetchone()
            recent = conn.execute(
                """
                SELECT id, created_at, input_path, backend, latency_ms, detections_count
                FROM runs
                ORDER BY id DESC
                LIMIT 10
                """
            ).fetchall()
        return {
            "runs": row[0] or 0,
            "avg_latency_ms": round(row[1] or 0.0, 2),
            "max_latency_ms": round(row[2] or 0.0, 2),
            "detections_total": row[3] or 0,
            "recent": [
                {
                    "id": r[0],
                    "created_at": r[1],
                    "input_path": r[2],
                    "backend": r[3],
                    "latency_ms": r[4],
                    "detections_count": r[5],
                }
                for r in recent
            ],
        }
