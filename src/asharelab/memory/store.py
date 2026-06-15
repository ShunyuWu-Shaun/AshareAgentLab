from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from asharelab.models import AgentReport, Hypothesis, MarketEvent


class MarketMemory:
    """SQLite-backed memory with explicit JSON payloads for auditability."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self._create_schema()

    def _create_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                event_date TEXT NOT NULL,
                topic TEXT NOT NULL,
                symbol TEXT,
                payload TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                payload TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS hypotheses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                payload TEXT NOT NULL
            );
            """
        )
        self.conn.commit()

    def add_events(self, events: Iterable[MarketEvent]) -> None:
        rows = [
            (
                event.event_id,
                event.event_date.isoformat(),
                event.topic,
                event.symbol,
                event.model_dump_json(),
            )
            for event in events
        ]
        self.conn.executemany(
            """
            INSERT OR REPLACE INTO events(event_id, event_date, topic, symbol, payload)
            VALUES (?, ?, ?, ?, ?)
            """,
            rows,
        )
        self.conn.commit()

    def recent_events(self, limit: int = 200) -> list[MarketEvent]:
        cur = self.conn.execute(
            "SELECT payload FROM events ORDER BY event_date DESC, event_id DESC LIMIT ?", (limit,)
        )
        return [MarketEvent.model_validate_json(row[0]) for row in cur.fetchall()]

    def add_report(self, report: AgentReport) -> None:
        self.conn.execute(
            "INSERT INTO reports(report_date, agent_name, payload) VALUES (?, ?, ?)",
            (report.report_date.isoformat(), report.agent_name, report.model_dump_json()),
        )
        self.conn.commit()

    def add_hypotheses(self, hypotheses: Iterable[Hypothesis]) -> None:
        self.conn.executemany(
            "INSERT INTO hypotheses(title, payload) VALUES (?, ?)",
            [(hyp.title, hyp.model_dump_json()) for hyp in hypotheses],
        )
        self.conn.commit()

    def topic_counts(self) -> dict[str, int]:
        cur = self.conn.execute("SELECT topic, COUNT(*) FROM events GROUP BY topic")
        return {str(topic): int(count) for topic, count in cur.fetchall()}

    def dump_json(self) -> str:
        payload = {
            "events": [json.loads(event.model_dump_json()) for event in self.recent_events()],
            "topic_counts": self.topic_counts(),
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)

