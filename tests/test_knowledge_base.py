"""
Unit tests for knowledge_base.py — persistence, search, and HCI methods.
Uses a temporary SQLite DB via the tmp_db fixture (in conftest.py).
"""

import pytest
from datetime import datetime


SESSION_ID_1 = "session-aaa-111"
SESSION_ID_2 = "session-bbb-222"


def _make_session(kb, session_id, query, source_types=None, complete=True):
    source_types = source_types or ["wikipedia", "arxiv"]
    started = "2026-01-01T10:00:00"
    kb.save_session(session_id, query, source_types, started)
    if complete:
        kb.complete_session(
            session_id,
            completed_at="2026-01-01T10:05:00",
            result_count=5,
            avg_relevance=0.75,
            quality_score=0.80,
        )


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------

class TestSessionManagement:
    def test_save_and_load_session(self, tmp_db):
        _make_session(tmp_db, SESSION_ID_1, "machine learning")
        session = tmp_db.load_session(SESSION_ID_1)
        assert session is not None
        assert session["id"] == SESSION_ID_1
        assert session["query"] == "machine learning"
        assert session["result_count"] == 5

    def test_load_nonexistent_session_returns_none(self, tmp_db):
        result = tmp_db.load_session("does-not-exist")
        assert result is None

    def test_source_types_deserialized_as_list(self, tmp_db):
        _make_session(tmp_db, SESSION_ID_1, "test", source_types=["wikipedia", "reddit"])
        session = tmp_db.load_session(SESSION_ID_1)
        assert isinstance(session["source_types"], list)
        assert "wikipedia" in session["source_types"]
        assert "reddit" in session["source_types"]

    def test_duplicate_save_ignored(self, tmp_db):
        _make_session(tmp_db, SESSION_ID_1, "machine learning")
        # Save again with same ID — should not raise
        _make_session(tmp_db, SESSION_ID_1, "different query")
        session = tmp_db.load_session(SESSION_ID_1)
        # INSERT OR IGNORE means first write wins
        assert session["query"] == "machine learning"

    def test_complete_session_updates_fields(self, tmp_db):
        tmp_db.save_session(SESSION_ID_1, "test query", ["wikipedia"], "2026-01-01T00:00:00")
        tmp_db.complete_session(
            SESSION_ID_1,
            completed_at="2026-01-01T01:00:00",
            result_count=12,
            avg_relevance=0.88,
            quality_score=0.91,
        )
        session = tmp_db.load_session(SESSION_ID_1)
        assert session["result_count"] == 12
        assert abs(session["avg_relevance"] - 0.88) < 0.001
        assert session["completed_at"] == "2026-01-01T01:00:00"

    def test_get_recent_sessions_returns_completed_only(self, tmp_db):
        # One complete, one in-progress
        _make_session(tmp_db, SESSION_ID_1, "query one", complete=True)
        tmp_db.save_session(SESSION_ID_2, "query two", ["wikipedia"], "2026-01-02T00:00:00")
        # Not completed ↑
        sessions = tmp_db.get_recent_sessions(10)
        ids = [s["id"] for s in sessions]
        assert SESSION_ID_1 in ids
        assert SESSION_ID_2 not in ids

    def test_get_recent_sessions_newest_first(self, tmp_db):
        _make_session(tmp_db, SESSION_ID_1, "first query")
        _make_session(tmp_db, SESSION_ID_2, "second query")
        # Manually set completed_at to ensure ordering
        tmp_db.complete_session(SESSION_ID_1, "2026-01-01T10:00:00", 3, 0.7, 0.7)
        tmp_db.complete_session(SESSION_ID_2, "2026-01-02T10:00:00", 5, 0.8, 0.8)
        sessions = tmp_db.get_recent_sessions(10)
        if len(sessions) >= 2:
            assert sessions[0]["completed_at"] >= sessions[1]["completed_at"]

    def test_get_recent_sessions_respects_limit(self, tmp_db):
        for i in range(5):
            sid = f"session-{i:03d}"
            _make_session(tmp_db, sid, f"query {i}")
        sessions = tmp_db.get_recent_sessions(3)
        assert len(sessions) <= 3


# ---------------------------------------------------------------------------
# Result management
# ---------------------------------------------------------------------------

class TestResultManagement:
    def test_save_and_load_result(self, tmp_db, sample_result):
        _make_session(tmp_db, SESSION_ID_1, "machine learning")
        tmp_db.save_result(SESSION_ID_1, sample_result)
        results = tmp_db.load_session_results(SESSION_ID_1)
        assert len(results) == 1
        assert results[0]["id"] == sample_result.id
        assert results[0]["title"] == sample_result.title

    def test_save_result_upserts(self, tmp_db, sample_result):
        _make_session(tmp_db, SESSION_ID_1, "machine learning")
        tmp_db.save_result(SESSION_ID_1, sample_result)
        tmp_db.save_result(SESSION_ID_1, sample_result)  # duplicate
        results = tmp_db.load_session_results(SESSION_ID_1)
        assert len(results) == 1  # not doubled

    def test_results_ordered_by_relevance_desc(self, tmp_db, sample_result, sample_result_2):
        _make_session(tmp_db, SESSION_ID_1, "machine learning")
        tmp_db.save_result(SESSION_ID_1, sample_result)    # relevance 0.85
        tmp_db.save_result(SESSION_ID_1, sample_result_2)  # relevance 0.78
        results = tmp_db.load_session_results(SESSION_ID_1)
        assert results[0]["relevance_score"] >= results[1]["relevance_score"]

    def test_metadata_deserialized(self, tmp_db, sample_result):
        _make_session(tmp_db, SESSION_ID_1, "machine learning")
        tmp_db.save_result(SESSION_ID_1, sample_result)
        results = tmp_db.load_session_results(SESSION_ID_1)
        assert isinstance(results[0]["metadata"], dict)
        assert "word_count" in results[0]["metadata"]

    def test_load_empty_session_returns_empty_list(self, tmp_db):
        _make_session(tmp_db, SESSION_ID_1, "test")
        results = tmp_db.load_session_results(SESSION_ID_1)
        assert results == []


# ---------------------------------------------------------------------------
# Topic management
# ---------------------------------------------------------------------------

class TestTopicManagement:
    def test_save_and_get_topics(self, tmp_db):
        _make_session(tmp_db, SESSION_ID_1, "machine learning")
        tmp_db.save_topics(SESSION_ID_1, [("machine", 8), ("learning", 7), ("data", 5)])
        topics = tmp_db.get_top_topics(n=10, across_sessions=True)
        topic_words = [t for t, _ in topics]
        assert "machine" in topic_words
        assert "learning" in topic_words

    def test_topics_sorted_by_frequency(self, tmp_db):
        _make_session(tmp_db, SESSION_ID_1, "test")
        tmp_db.save_topics(SESSION_ID_1, [("rare", 1), ("common", 50), ("medium", 10)])
        topics = tmp_db.get_top_topics(n=10)
        freqs = [freq for _, freq in topics]
        assert freqs == sorted(freqs, reverse=True)

    def test_topics_aggregated_across_sessions(self, tmp_db):
        _make_session(tmp_db, SESSION_ID_1, "query one")
        _make_session(tmp_db, SESSION_ID_2, "query two")
        tmp_db.save_topics(SESSION_ID_1, [("python", 5)])
        tmp_db.save_topics(SESSION_ID_2, [("python", 3)])
        topics = dict(tmp_db.get_top_topics(n=20, across_sessions=True))
        assert topics.get("python", 0) == 8  # 5 + 3

    def test_get_source_stats(self, tmp_db, sample_result, sample_result_2):
        _make_session(tmp_db, SESSION_ID_1, "test")
        tmp_db.save_result(SESSION_ID_1, sample_result)    # source_id="wikipedia"
        tmp_db.save_result(SESSION_ID_1, sample_result_2)  # source_id="arxiv"
        stats = tmp_db.get_source_stats()
        assert "wikipedia" in stats
        assert "arxiv" in stats
        assert stats["wikipedia"] == 1
        assert stats["arxiv"] == 1


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

class TestSearch:
    def test_search_finds_matching_title(self, tmp_db, sample_result):
        _make_session(tmp_db, SESSION_ID_1, "machine learning")
        tmp_db.save_result(SESSION_ID_1, sample_result)
        matches = tmp_db.search_all_sessions("Machine Learning")
        assert len(matches) >= 1
        titles = [m["title"] for m in matches]
        assert sample_result.title in titles

    def test_search_finds_matching_summary(self, tmp_db, sample_result):
        _make_session(tmp_db, SESSION_ID_1, "machine learning")
        tmp_db.save_result(SESSION_ID_1, sample_result)
        matches = tmp_db.search_all_sessions("computers to learn")
        assert len(matches) >= 1

    def test_search_case_insensitive(self, tmp_db, sample_result):
        _make_session(tmp_db, SESSION_ID_1, "machine learning")
        tmp_db.save_result(SESSION_ID_1, sample_result)
        lower = tmp_db.search_all_sessions("machine learning")
        upper = tmp_db.search_all_sessions("MACHINE LEARNING")
        assert len(lower) == len(upper)

    def test_search_no_matches_returns_empty(self, tmp_db, sample_result):
        _make_session(tmp_db, SESSION_ID_1, "machine learning")
        tmp_db.save_result(SESSION_ID_1, sample_result)
        matches = tmp_db.search_all_sessions("xyzzy quantum teleportation banana")
        assert matches == []


# ---------------------------------------------------------------------------
# HCI methods
# ---------------------------------------------------------------------------

class TestHCI:
    def test_get_related_sessions_returns_overlapping(self, tmp_db):
        _make_session(tmp_db, SESSION_ID_1, "machine learning basics")
        _make_session(tmp_db, SESSION_ID_2, "python programming")
        tmp_db.save_topics(SESSION_ID_1, [("machine", 5), ("learning", 5), ("data", 3)])
        tmp_db.save_topics(SESSION_ID_2, [("python", 5), ("programming", 4)])
        related = tmp_db.get_related_sessions("machine learning data", n=3)
        session_ids = [r["session_id"] for r in related]
        assert SESSION_ID_1 in session_ids

    def test_get_insight_gaps_returns_dict_keys(self, tmp_db):
        _make_session(tmp_db, SESSION_ID_1, "test query")
        tmp_db.save_topics(SESSION_ID_1, [("popular", 20), ("niche", 2)])
        gaps = tmp_db.get_insight_gaps(n=10)
        assert isinstance(gaps, list)
        for gap in gaps:
            assert "topic" in gap
            assert "gap_score" in gap

    def test_get_insight_gaps_empty_db_returns_empty(self, tmp_db):
        gaps = tmp_db.get_insight_gaps()
        assert gaps == []

    def test_get_cross_source_topics_requires_two_sources(
        self, tmp_db, sample_result, sample_result_2
    ):
        _make_session(tmp_db, SESSION_ID_1, "machine learning")
        tmp_db.save_result(SESSION_ID_1, sample_result)    # source_id="wikipedia"
        tmp_db.save_result(SESSION_ID_1, sample_result_2)  # source_id="arxiv"
        tmp_db.save_topics(SESSION_ID_1, [("learning", 8), ("data", 4)])
        cross = tmp_db.get_cross_source_topics(session_id=SESSION_ID_1)
        # All returned topics must have >= 2 sources
        for topic, sources in cross.items():
            assert len(sources) >= 2

    def test_get_cross_source_topics_no_session_filter(self, tmp_db, sample_result, sample_result_2):
        _make_session(tmp_db, SESSION_ID_1, "test")
        tmp_db.save_result(SESSION_ID_1, sample_result)
        tmp_db.save_result(SESSION_ID_1, sample_result_2)
        tmp_db.save_topics(SESSION_ID_1, [("python", 5)])
        cross = tmp_db.get_cross_source_topics()
        assert isinstance(cross, dict)
