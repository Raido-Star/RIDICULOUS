"""
Knowledge Base Module
SQLite-backed persistence for research sessions and results.
Includes Hybrid Creative Intelligence (HCI) methods for cross-session insight.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from research_engine import ResearchResult

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    query TEXT NOT NULL,
    source_types TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    result_count INTEGER DEFAULT 0,
    avg_relevance REAL DEFAULT 0.0,
    quality_score REAL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS results (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    content TEXT NOT NULL,
    summary TEXT NOT NULL,
    relevance_score REAL NOT NULL,
    source_type TEXT NOT NULL,
    source_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS topics (
    session_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    frequency INTEGER NOT NULL,
    PRIMARY KEY (session_id, topic),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE INDEX IF NOT EXISTS idx_results_session ON results(session_id);
CREATE INDEX IF NOT EXISTS idx_results_url ON results(url);
CREATE INDEX IF NOT EXISTS idx_topics_topic ON topics(topic);
CREATE INDEX IF NOT EXISTS idx_sessions_query ON sessions(query);
"""


class KnowledgeBase:
    """
    Persistent SQLite knowledge base for research sessions.

    DB is stored at ~/.ridiculous/knowledge.db by default.
    Auto-created on first use. Uses WAL mode for safe concurrent reads
    during async background writes.
    """

    DEFAULT_PATH = Path.home() / ".ridiculous" / "knowledge.db"

    def __init__(self, db_path: Path | None = None):
        self.db_path = Path(db_path) if db_path else self.DEFAULT_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def save_session(
        self,
        session_id: str,
        query: str,
        source_types: list[str],
        started_at: str,
    ) -> None:
        """Insert a new session row when research begins."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO sessions (id, query, source_types, started_at)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, query, json.dumps(source_types), started_at),
            )

    def complete_session(
        self,
        session_id: str,
        completed_at: str,
        result_count: int,
        avg_relevance: float,
        quality_score: float,
    ) -> None:
        """Update session row when research finishes."""
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE sessions
                SET completed_at=?, result_count=?, avg_relevance=?, quality_score=?
                WHERE id=?
                """,
                (completed_at, result_count, avg_relevance, quality_score, session_id),
            )

    def load_session(self, session_id: str) -> dict[str, Any] | None:
        """Return session metadata dict or None if not found."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM sessions WHERE id=?", (session_id,)
            ).fetchone()
        if not row:
            return None
        d = dict(row)
        d["source_types"] = json.loads(d["source_types"])
        return d

    def get_recent_sessions(self, n: int = 10) -> list[dict[str, Any]]:
        """Return n most recent completed sessions, newest first."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM sessions
                WHERE completed_at IS NOT NULL
                ORDER BY completed_at DESC
                LIMIT ?
                """,
                (n,),
            ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["source_types"] = json.loads(d["source_types"])
            result.append(d)
        return result

    # ------------------------------------------------------------------
    # Result management
    # ------------------------------------------------------------------

    def save_result(self, session_id: str, result: "ResearchResult") -> None:
        """Upsert a result. Uses INSERT OR REPLACE so re-runs don't duplicate."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO results
                (id, session_id, title, url, content, summary, relevance_score,
                 source_type, source_id, timestamp, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.id,
                    session_id,
                    result.title,
                    result.url,
                    result.content,
                    result.summary,
                    result.relevance_score,
                    result.source_type,
                    result.source_id,
                    result.timestamp,
                    json.dumps(result.metadata),
                ),
            )

    def load_session_results(self, session_id: str) -> list[dict[str, Any]]:
        """Return all results for a session as list of dicts."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM results WHERE session_id=? ORDER BY relevance_score DESC",
                (session_id,),
            ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["metadata"] = json.loads(d["metadata_json"])
            del d["metadata_json"]
            result.append(d)
        return result

    # ------------------------------------------------------------------
    # Topic management
    # ------------------------------------------------------------------

    def save_topics(self, session_id: str, topics: list[tuple[str, int]]) -> None:
        """Bulk insert topic frequencies for a session."""
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO topics (session_id, topic, frequency)
                VALUES (?, ?, ?)
                """,
                [(session_id, topic, freq) for topic, freq in topics],
            )

    def get_top_topics(
        self, n: int = 20, across_sessions: bool = True
    ) -> list[tuple[str, int]]:
        """
        Return most frequent topics.
        If across_sessions=True, aggregates globally.
        If False, returns topics from the most recent session only.
        """
        with self._connect() as conn:
            if across_sessions:
                rows = conn.execute(
                    """
                    SELECT topic, SUM(frequency) as total
                    FROM topics
                    GROUP BY topic
                    ORDER BY total DESC
                    LIMIT ?
                    """,
                    (n,),
                ).fetchall()
            else:
                # Most recent completed session
                session_row = conn.execute(
                    """
                    SELECT id FROM sessions
                    WHERE completed_at IS NOT NULL
                    ORDER BY completed_at DESC LIMIT 1
                    """
                ).fetchone()
                if not session_row:
                    return []
                rows = conn.execute(
                    """
                    SELECT topic, frequency as total
                    FROM topics
                    WHERE session_id=?
                    ORDER BY total DESC
                    LIMIT ?
                    """,
                    (session_row["id"], n),
                ).fetchall()
        return [(row["topic"], row["total"]) for row in rows]

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search_all_sessions(self, query: str) -> list[dict[str, Any]]:
        """
        Search across result titles and summaries.
        Returns top 20 matches ordered by relevance_score DESC.
        """
        pattern = f"%{query.lower()}%"
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT r.*, s.query as session_query, s.completed_at
                FROM results r
                JOIN sessions s ON r.session_id = s.id
                WHERE LOWER(r.title) LIKE ?
                   OR LOWER(r.summary) LIKE ?
                ORDER BY r.relevance_score DESC
                LIMIT 20
                """,
                (pattern, pattern),
            ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["metadata"] = json.loads(d["metadata_json"])
            del d["metadata_json"]
            result.append(d)
        return result

    def get_source_stats(self) -> dict[str, int]:
        """Return count of results per source_id across all sessions."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT source_id, COUNT(*) as count
                FROM results
                GROUP BY source_id
                ORDER BY count DESC
                """
            ).fetchall()
        return {row["source_id"]: row["count"] for row in rows}

    # ------------------------------------------------------------------
    # HCI — Hybrid Creative Intelligence methods
    # ------------------------------------------------------------------

    def get_related_sessions(
        self, query: str, n: int = 3
    ) -> list[dict[str, Any]]:
        """
        Find past sessions that share topic overlap with the given query.

        Splits the query into terms and finds sessions whose topics contain
        at least one matching term. Returns up to n sessions sorted by
        topic overlap score (most overlapping first).

        This powers "session memory compounding" — surfacing prior research
        that's relevant to a new query without requiring exact query matching.
        """
        query_terms = set(
            w.lower() for w in query.split() if len(w) > 3
        )
        if not query_terms:
            return self.get_recent_sessions(n)

        with self._connect() as conn:
            # Find sessions whose topics overlap with query terms
            placeholders = ",".join("?" * len(query_terms))
            rows = conn.execute(
                f"""
                SELECT t.session_id,
                       SUM(t.frequency) as overlap_score,
                       COUNT(DISTINCT t.topic) as matched_topics,
                       s.query as session_query,
                       s.completed_at,
                       s.result_count,
                       s.avg_relevance
                FROM topics t
                JOIN sessions s ON t.session_id = s.id
                WHERE t.topic IN ({placeholders})
                  AND s.completed_at IS NOT NULL
                GROUP BY t.session_id
                ORDER BY overlap_score DESC
                LIMIT ?
                """,
                (*query_terms, n),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_insight_gaps(self, n: int = 10) -> list[dict[str, Any]]:
        """
        Identify underserved topics — high search frequency but low average relevance.

        Topics that appear often across sessions (people keep searching for them)
        but yield low-relevance results represent content opportunities:
        something the web covers poorly that you could fill.

        Returns topics sorted by "gap score" = frequency / (avg_relevance + 0.1)
        Higher gap score = more searched, less well-covered.
        """
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    t.topic,
                    SUM(t.frequency) as total_frequency,
                    AVG(s.avg_relevance) as avg_session_relevance,
                    COUNT(DISTINCT t.session_id) as session_count,
                    CAST(SUM(t.frequency) AS REAL) / (AVG(s.avg_relevance) + 0.1) as gap_score
                FROM topics t
                JOIN sessions s ON t.session_id = s.id
                WHERE s.completed_at IS NOT NULL
                  AND s.result_count > 0
                GROUP BY t.topic
                HAVING session_count >= 1
                ORDER BY gap_score DESC
                LIMIT ?
                """,
                (n,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_cross_source_topics(
        self, session_id: str | None = None
    ) -> dict[str, list[str]]:
        """
        Find topics that appear across multiple source types.

        Returns a dict mapping topic → list of source_ids that mentioned it.
        Topics with entries from both academic AND community sources are
        prime candidates for "tension detection" — the gap between expert
        framing and practitioner framing is where creative content lives.
        """
        clause = "WHERE r.session_id=?" if session_id else ""
        params = (session_id,) if session_id else ()

        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT DISTINCT r.source_id, t.topic
                FROM topics t
                JOIN results r ON t.session_id = r.session_id
                {clause}
                ORDER BY t.topic
                """,
                params,
            ).fetchall()

        topic_sources: dict[str, list[str]] = {}
        for row in rows:
            topic = row["topic"]
            source = row["source_id"]
            if topic not in topic_sources:
                topic_sources[topic] = []
            if source not in topic_sources[topic]:
                topic_sources[topic].append(source)

        # Only return topics seen from 2+ sources (those have creative tension potential)
        return {t: sources for t, sources in topic_sources.items() if len(sources) >= 2}
