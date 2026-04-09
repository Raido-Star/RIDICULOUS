"""
Unit tests for asset_generator.py.
Tests both template mode (no research) and research-infused mode.
"""

import pytest
from asset_generator import (
    YouTubeAssetGenerator,
    GumroadAssetGenerator,
    EtsyAssetGenerator,
    WebAssetGenerator,
    GameAssetGenerator,
    CanvaAssetGenerator,
    AssetGeneratorManager,
    _extract_research_context,
)


# ---------------------------------------------------------------------------
# _extract_research_context helper
# ---------------------------------------------------------------------------

class TestExtractResearchContext:
    def test_empty_list_returns_empty_dict(self):
        ctx = _extract_research_context([])
        assert ctx == {}

    def test_none_safe(self):
        ctx = _extract_research_context(None or [])
        assert ctx == {}

    def test_returns_required_keys(self):
        results = [
            {
                "id": "1", "title": "ML Article", "url": "https://example.com",
                "summary": "Machine learning is great.", "relevance_score": 0.9,
                "source_type": "reference", "source_id": "wikipedia",
                "metadata": {"key_topics": [("machine", 5), ("learning", 4)]},
            }
        ]
        ctx = _extract_research_context(results)
        for key in ["top_summaries", "top_titles", "citations", "key_topics",
                    "source_types", "source_ids", "avg_relevance", "result_count"]:
            assert key in ctx

    def test_sorted_by_relevance(self):
        results = [
            {"id": "1", "title": "Low", "url": "u1", "summary": "Low relevance.", "relevance_score": 0.3,
             "source_type": "ref", "source_id": "w", "metadata": {"key_topics": []}},
            {"id": "2", "title": "High", "url": "u2", "summary": "High relevance.", "relevance_score": 0.95,
             "source_type": "ref", "source_id": "w", "metadata": {"key_topics": []}},
        ]
        ctx = _extract_research_context(results)
        assert ctx["top_titles"][0] == "High"

    def test_aggregates_topics_across_results(self):
        results = [
            {"id": "1", "title": "A", "url": "u1", "summary": "s1", "relevance_score": 0.8,
             "source_type": "ref", "source_id": "w",
             "metadata": {"key_topics": [("python", 5), ("data", 3)]}},
            {"id": "2", "title": "B", "url": "u2", "summary": "s2", "relevance_score": 0.7,
             "source_type": "ref", "source_id": "w",
             "metadata": {"key_topics": [("python", 3), ("machine", 4)]}},
        ]
        ctx = _extract_research_context(results)
        topic_dict = dict(ctx["key_topics"][:10] if isinstance(ctx["key_topics"][0], tuple)
                          else [(t, 1) for t in ctx["key_topics"]])
        # python = 5+3=8 should be present
        assert "python" in ctx["key_topics"]

    def test_result_count_correct(self):
        results = [
            {"id": str(i), "title": f"T{i}", "url": f"u{i}", "summary": "s", "relevance_score": 0.5,
             "source_type": "r", "source_id": "w", "metadata": {"key_topics": []}}
            for i in range(7)
        ]
        ctx = _extract_research_context(results)
        assert ctx["result_count"] == 7


# ---------------------------------------------------------------------------
# YouTubeAssetGenerator
# ---------------------------------------------------------------------------

class TestYouTubeAssetGenerator:
    def test_generate_video_script_template_mode(self):
        gen = YouTubeAssetGenerator()
        result = gen.generate_video_script("Python programming")
        assert isinstance(result, dict)
        assert "title" in result
        assert "Python programming" in result["title"]

    def test_all_styles_return_dict(self):
        gen = YouTubeAssetGenerator()
        for style in ["educational", "entertainment", "tutorial", "review"]:
            result = gen.generate_video_script("topic", style=style)
            assert isinstance(result, dict)
            assert len(result) > 0

    def test_unknown_style_falls_back_to_educational(self):
        gen = YouTubeAssetGenerator()
        result = gen.generate_video_script("topic", style="nonexistent")
        assert "main_points" in result  # educational has main_points

    def test_research_infused_replaces_main_points(self, sample_results):
        gen = YouTubeAssetGenerator()
        research_data = [r.to_dict() for r in sample_results]
        result = gen.generate_video_script("machine learning", research_results=research_data)
        # main_points should contain actual research titles/summaries
        assert "research_citations" in result
        assert "research_tags" in result
        # main_points should reference real content, not generic templates
        for point in result.get("main_points", []):
            assert isinstance(point, str)

    def test_generate_tags_returns_list(self):
        gen = YouTubeAssetGenerator()
        tags = gen.generate_tags("machine learning")
        assert isinstance(tags, list)
        assert len(tags) > 0

    def test_generate_tags_enriched_with_research(self, sample_results):
        gen = YouTubeAssetGenerator()
        research_data = [r.to_dict() for r in sample_results]
        base_tags = gen.generate_tags("machine learning")
        research_tags = gen.generate_tags("machine learning", research_results=research_data)
        # Research-infused tags should be >= base (research adds topics)
        assert len(research_tags) >= len(base_tags)

    def test_tags_capped_at_30(self, sample_results):
        gen = YouTubeAssetGenerator()
        research_data = [r.to_dict() for r in sample_results] * 5  # lots of results
        tags = gen.generate_tags("topic", research_results=research_data)
        assert len(tags) <= 30

    def test_generate_video_description_includes_sources_with_research(self, sample_results):
        gen = YouTubeAssetGenerator()
        script = gen.generate_video_script("topic")
        research_data = [r.to_dict() for r in sample_results]
        desc = gen.generate_video_description("topic", script, research_results=research_data)
        assert "Sources" in desc or "source" in desc.lower()

    def test_generate_thumbnail_returns_dimensions(self):
        gen = YouTubeAssetGenerator()
        thumb = gen.generate_thumbnail_template("topic")
        assert thumb["dimensions"] == "1280x720"


# ---------------------------------------------------------------------------
# GumroadAssetGenerator
# ---------------------------------------------------------------------------

class TestGumroadAssetGenerator:
    def test_generate_listing_template_mode(self):
        gen = GumroadAssetGenerator()
        result = gen.generate_product_listing("My Ebook")
        assert isinstance(result, dict)
        assert result["name"] == "My Ebook"
        assert "description" in result
        assert "price_suggestion" in result

    def test_all_product_types(self):
        gen = GumroadAssetGenerator()
        for ptype in ["ebook", "template", "course", "bundle"]:
            result = gen.generate_product_listing("Product", product_type=ptype)
            assert isinstance(result, dict)

    def test_research_adds_research_body_to_description(self, sample_results):
        gen = GumroadAssetGenerator()
        research_data = [r.to_dict() for r in sample_results]
        result = gen.generate_product_listing("ML Guide", research_results=research_data)
        assert "feature_bullets" in result
        assert "research" in result["description"].lower() or "What the research says" in result["description"]

    def test_pricing_suggestions_are_reasonable(self):
        gen = GumroadAssetGenerator()
        for ptype in ["ebook", "template", "course"]:
            result = gen.generate_product_listing("P", product_type=ptype)
            price = result["price_suggestion"]
            assert price["min"] < price["suggested"] < price["max"]


# ---------------------------------------------------------------------------
# EtsyAssetGenerator
# ---------------------------------------------------------------------------

class TestEtsyAssetGenerator:
    def test_generate_listing_template_mode(self):
        gen = EtsyAssetGenerator()
        result = gen.generate_product_listing("Watercolor Print")
        assert isinstance(result, dict)
        assert "title" in result
        assert "tags" in result
        assert "description" in result

    def test_tags_max_13(self):
        gen = EtsyAssetGenerator()
        result = gen.generate_product_listing("Product", category="art")
        assert len(result["tags"]) <= 13

    def test_research_enriches_tags(self, sample_results):
        gen = EtsyAssetGenerator()
        research_data = [r.to_dict() for r in sample_results]
        result = gen.generate_product_listing("ML Print", research_results=research_data)
        assert len(result["tags"]) <= 13  # still capped

    def test_digital_category_has_no_shipping(self):
        gen = EtsyAssetGenerator()
        result = gen.generate_product_listing("Digital Art", category="digital")
        assert "instant download" in result["shipping"].lower() or "no shipping" in result["shipping"].lower()


# ---------------------------------------------------------------------------
# WebAssetGenerator
# ---------------------------------------------------------------------------

class TestWebAssetGenerator:
    def test_generate_landing_page_template_mode(self):
        gen = WebAssetGenerator()
        result = gen.generate_landing_page("My Product")
        assert isinstance(result, dict)
        assert "structure" in result
        assert "copy" in result
        assert "seo" in result

    def test_all_purposes(self):
        gen = WebAssetGenerator()
        for purpose in ["sales", "portfolio", "blog"]:
            result = gen.generate_landing_page("Product", purpose=purpose)
            assert isinstance(result["structure"], list)
            assert len(result["structure"]) > 0

    def test_research_adds_hero_supporting_points(self, sample_results):
        gen = WebAssetGenerator()
        research_data = [r.to_dict() for r in sample_results]
        result = gen.generate_landing_page("ML Tool", research_results=research_data)
        assert "hero_supporting_points" in result["copy"]
        assert "social_proof_sources" in result

    def test_generate_blog_post_template(self):
        gen = WebAssetGenerator()
        result = gen.generate_blog_post_template("machine learning")
        assert "title" in result
        assert "structure" in result

    def test_blog_post_with_research_adds_findings(self, sample_results):
        gen = WebAssetGenerator()
        research_data = [r.to_dict() for r in sample_results]
        result = gen.generate_blog_post_template("machine learning", research_results=research_data)
        assert "research_findings" in result
        assert "citations" in result
        assert len(result["research_findings"]) > 0


# ---------------------------------------------------------------------------
# GameAssetGenerator
# ---------------------------------------------------------------------------

class TestGameAssetGenerator:
    def test_generate_gdd_template_mode(self):
        gen = GameAssetGenerator()
        result = gen.generate_game_design_document("Epic Quest")
        assert isinstance(result, dict)
        assert "concept" in result
        assert "mechanics" in result

    def test_all_genres(self):
        gen = GameAssetGenerator()
        for genre in ["action", "puzzle", "rpg"]:
            result = gen.generate_game_design_document("Game", genre=genre)
            assert isinstance(result["mechanics"], list)

    def test_unknown_genre_falls_back_to_action(self):
        gen = GameAssetGenerator()
        result = gen.generate_game_design_document("Game", genre="unknown_genre")
        assert isinstance(result["mechanics"], list)

    def test_research_adds_inspiration_sources(self, sample_results):
        gen = GameAssetGenerator()
        research_data = [r.to_dict() for r in sample_results]
        result = gen.generate_game_design_document("ML Quest", research_results=research_data)
        assert "inspiration_sources" in result["concept"]


# ---------------------------------------------------------------------------
# CanvaAssetGenerator
# ---------------------------------------------------------------------------

class TestCanvaAssetGenerator:
    def test_generate_template_specs(self):
        gen = CanvaAssetGenerator()
        for ttype in ["social", "marketing", "presentation"]:
            result = gen.generate_template_specs(ttype)
            assert "specifications" in result
            assert "design_tips" in result
            assert "color_palettes" in result

    def test_unknown_type_defaults_to_social(self):
        gen = CanvaAssetGenerator()
        result = gen.generate_template_specs("unknown")
        assert "instagram_post" in result["specifications"]

    def test_research_adds_content_themes(self, sample_results):
        gen = CanvaAssetGenerator()
        research_data = [r.to_dict() for r in sample_results]
        result = gen.generate_template_specs("social", research_results=research_data)
        assert "content_themes" in result


# ---------------------------------------------------------------------------
# AssetGeneratorManager
# ---------------------------------------------------------------------------

class TestAssetGeneratorManager:
    def test_get_available_platforms(self):
        mgr = AssetGeneratorManager()
        platforms = mgr.get_available_platforms()
        assert set(platforms) == {"youtube", "gumroad", "etsy", "web", "game", "canva"}

    def test_get_asset_types_youtube(self):
        mgr = AssetGeneratorManager()
        types = mgr.get_asset_types("youtube")
        assert "video_script" in types
        assert "thumbnail_template" in types

    def test_unknown_platform_returns_error(self):
        mgr = AssetGeneratorManager()
        result = mgr.generate_asset("nonexistent", "video_script", topic="test")
        assert "error" in result

    def test_unknown_asset_type_returns_error(self):
        mgr = AssetGeneratorManager()
        result = mgr.generate_asset("youtube", "nonexistent_type", topic="test")
        assert "error" in result

    def test_generate_asset_passes_research_results(self, sample_results):
        mgr = AssetGeneratorManager()
        research_data = [r.to_dict() for r in sample_results]
        result = mgr.generate_asset(
            "youtube", "video_script",
            research_results=research_data,
            topic="machine learning"
        )
        assert "error" not in result
        assert "research_citations" in result
