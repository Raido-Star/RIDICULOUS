"""
Integration tests for main.py MCP tools.
Tests tool functions directly (without starting the HTTP server).
"""

import pytest
import json
import asyncio
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse(response: str) -> dict:
    """Parse JSON tool response."""
    return json.loads(response)


def _setup_engine_with_results(sample_results):
    """Inject sample results into the global engine."""
    import main
    main.engine.results = list(sample_results)
    from research_engine import ResearchParameters
    main.engine.parameters = ResearchParameters(query="machine learning")
    main.engine.stats["avg_relevance"] = 0.8


# ---------------------------------------------------------------------------
# Research status / control tools
# ---------------------------------------------------------------------------

class TestResearchStatusTools:
    def test_get_research_status_idle(self):
        import main
        main.engine.is_running = False
        main.engine.results = []
        result = _parse(main.get_research_status())
        assert "is_running" in result
        assert result["is_running"] is False

    def test_pause_when_not_running(self):
        import main
        main.engine.is_running = False
        result = _parse(main.pause_research())
        assert result["status"] == "error"

    def test_resume_when_not_paused(self):
        import main
        main.engine.is_paused = False
        result = _parse(main.resume_research())
        assert result["status"] == "error"

    def test_stop_when_not_running(self):
        import main
        main.engine.is_running = False
        result = _parse(main.stop_research())
        assert result["status"] == "error"

    def test_update_parameters_no_running_task(self):
        import main
        from research_engine import ResearchParameters
        main.engine.parameters = ResearchParameters(query="test")
        result = _parse(main.update_parameters(depth=None, max_results=15, relevance_threshold=None, detail_level=None))
        assert result["status"] == "updated"
        assert main.engine.parameters.max_results == 15


# ---------------------------------------------------------------------------
# Results tools
# ---------------------------------------------------------------------------

class TestResultsTools:
    def test_get_results_empty(self):
        import main
        main.engine.results = []
        result = _parse(main.get_results())
        assert result["status"] == "empty"

    def test_get_results_json_format(self, sample_results):
        import main
        _setup_engine_with_results(sample_results)
        result = _parse(main.get_results(format="json", limit=None))
        assert result["status"] == "success"
        assert result["count"] == len(sample_results)
        assert isinstance(result["results"], list)

    def test_get_results_with_limit(self, sample_results):
        import main
        _setup_engine_with_results(sample_results)
        result = _parse(main.get_results(format="json", limit=1))
        assert result["count"] == 1

    def test_export_results_empty(self, tmp_path):
        import main
        main.engine.results = []
        result = _parse(main.export_results(filename=str(tmp_path / "out.md")))
        assert result["status"] == "error"

    def test_export_results_creates_file(self, sample_results, tmp_path):
        import main
        _setup_engine_with_results(sample_results)
        outfile = str(tmp_path / "results.md")
        result = _parse(main.export_results(filename=outfile, format="markdown"))
        assert result["status"] == "success"
        from pathlib import Path
        assert Path(outfile).exists()


# ---------------------------------------------------------------------------
# Analysis tools
# ---------------------------------------------------------------------------

class TestAnalysisTools:
    def test_analyze_results_empty(self):
        import main
        main.engine.results = []
        result = _parse(main.analyze_results())
        assert result["status"] == "error"

    def test_analyze_results_with_data(self, sample_results):
        import main
        _setup_engine_with_results(sample_results)
        result = _parse(main.analyze_results())
        assert "total_results" in result
        assert result["total_results"] == len(sample_results)
        assert "avg_relevance" in result
        assert "quality_score" in result

    def test_get_statistics(self, sample_results):
        import main
        _setup_engine_with_results(sample_results)
        result = _parse(main.get_statistics())
        assert "current_results" in result

    def test_search_results_finds_match(self, sample_results):
        import main
        _setup_engine_with_results(sample_results)
        result = _parse(main.search_results(query="machine learning", min_relevance=0.0))
        assert result["status"] == "success"
        assert result["matches"] >= 1

    def test_search_results_no_match(self, sample_results):
        import main
        _setup_engine_with_results(sample_results)
        result = _parse(main.search_results(query="xyzzy teleportation banana", min_relevance=0.0))
        assert result["status"] == "success"
        assert result["matches"] == 0


# ---------------------------------------------------------------------------
# Content building tools
# ---------------------------------------------------------------------------

class TestContentTools:
    def test_build_content_no_results(self):
        import main
        main.engine.results = []
        result = _parse(main.build_content(content_type="article"))
        assert result["status"] == "error"

    def test_build_content_article(self, sample_results):
        import main
        _setup_engine_with_results(sample_results)
        result = _parse(main.build_content(content_type="article", tone="professional", output_file=None))
        assert result["status"] == "success"
        assert "content" in result
        assert len(result["content"]) > 0

    def test_build_content_all_types(self, sample_results):
        import main
        _setup_engine_with_results(sample_results)
        for ctype in ["article", "report", "summary", "presentation"]:
            result = _parse(main.build_content(content_type=ctype, tone="professional", output_file=None))
            assert result["status"] == "success"

    def test_build_content_unknown_type(self, sample_results):
        import main
        _setup_engine_with_results(sample_results)
        result = _parse(main.build_content(content_type="invalid_type"))
        assert result["status"] == "error"


# ---------------------------------------------------------------------------
# Configuration tools
# ---------------------------------------------------------------------------

class TestConfigTools:
    def test_save_configuration_no_params(self):
        import main
        main.engine.parameters = None
        result = _parse(main.save_configuration(name="test-config"))
        assert result["status"] == "error"

    def test_save_and_load_configuration(self, tmp_path):
        import main
        import os
        from research_engine import ResearchParameters
        main.engine.parameters = ResearchParameters(query="test save load")

        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            save_result = _parse(main.save_configuration(name="my-config", description=""))
            assert save_result["status"] == "success"
            load_result = _parse(main.load_configuration(name="my-config"))
            assert load_result["status"] == "success"
            assert load_result["config"]["parameters"]["query"] == "test save load"
        finally:
            os.chdir(old_cwd)

    def test_load_nonexistent_config(self):
        import main
        result = _parse(main.load_configuration(name="does-not-exist-xyz"))
        assert result["status"] == "error"


# ---------------------------------------------------------------------------
# Knowledge Base tools
# ---------------------------------------------------------------------------

class TestKnowledgeBaseTools:
    def test_list_past_sessions_empty(self, tmp_path):
        import main
        from knowledge_base import KnowledgeBase
        # Use fresh KB for this test
        original_kb = main.kb
        main.kb = KnowledgeBase(db_path=tmp_path / "test.db")
        main.engine.kb = main.kb
        try:
            result = _parse(main.list_past_sessions(n=10))
            assert result["status"] == "success"
            assert result["session_count"] == 0
        finally:
            main.kb = original_kb
            main.engine.kb = original_kb

    def test_load_past_session_not_found(self):
        import main
        result = _parse(main.load_past_session(session_id="nonexistent-session-id"))
        assert result["status"] == "error"

    def test_search_knowledge_base_empty(self, tmp_path):
        import main
        from knowledge_base import KnowledgeBase
        original_kb = main.kb
        main.kb = KnowledgeBase(db_path=tmp_path / "test.db")
        try:
            result = _parse(main.search_knowledge_base(query="machine learning"))
            assert result["status"] == "success"
            assert result["matches"] == []
        finally:
            main.kb = original_kb


# ---------------------------------------------------------------------------
# Research-infused asset generation
# ---------------------------------------------------------------------------

class TestResearchedAssetTool:
    def test_generate_researched_asset_no_research(self):
        import main
        main.engine.results = []
        result = _parse(main.generate_researched_asset(
            platform="youtube", asset_type="video_script", topic="machine learning"
        ))
        assert result["status"] == "success"
        assert result["research_infused"] is False

    def test_generate_researched_asset_with_research(self, sample_results):
        import main
        _setup_engine_with_results(sample_results)
        result = _parse(main.generate_researched_asset(
            platform="youtube", asset_type="video_script", topic="machine learning"
        ))
        assert result["status"] == "success"
        assert result["research_infused"] is True
        assert result["research_result_count"] == len(sample_results)

    def test_generate_researched_asset_unknown_platform(self):
        import main
        result = _parse(main.generate_researched_asset(
            platform="nonexistent", asset_type="video_script"
        ))
        assert result["status"] == "error"

    def test_generate_researched_asset_uses_query_as_topic(self, sample_results):
        import main
        _setup_engine_with_results(sample_results)
        result = _parse(main.generate_researched_asset(
            platform="gumroad", asset_type="product_listing", topic="", use_current_research=True
        ))
        assert result["status"] == "success"
        # Should use engine.parameters.query as the topic
        assert result["topic"] == "machine learning"


# ---------------------------------------------------------------------------
# Asset generation tools (existing)
# ---------------------------------------------------------------------------

class TestExistingAssetTools:
    def test_list_platforms(self):
        import main
        result = _parse(main.list_platforms())
        assert result["status"] == "success"
        assert "youtube" in result["platforms"]

    def test_generate_youtube_assets_video_script(self):
        import main
        result = _parse(main.generate_youtube_assets(
            topic="Python", asset_type="video_script"
        ))
        assert result["status"] == "success"
        assert result["platform"] == "youtube"

    def test_generate_youtube_assets_unknown_type(self):
        import main
        result = _parse(main.generate_youtube_assets(
            topic="Python", asset_type="unknown_asset_xyz"
        ))
        assert "error" in result

    def test_generate_gumroad_listing(self):
        import main
        result = _parse(main.generate_gumroad_listing(product_name="My Guide", product_type="ebook"))
        assert result["status"] == "success"

    def test_generate_multi_platform_package(self):
        import main
        result = _parse(main.generate_multi_platform_package(
            project_name="Test Project",
            platforms="youtube,gumroad",
        ))
        assert result["status"] == "success"
        assert "youtube" in result["results"]
        assert "gumroad" in result["results"]
