"""
Unit tests for sources.py — all adapters, using mocked HTTP via aioresponses.
Tests verify correct parsing, error isolation, and SearchResult structure.
"""

import re
import pytest
import json

try:
    from aioresponses import aioresponses
    HAS_AIORESPONSES = True
except ImportError:
    HAS_AIORESPONSES = False

from sources import (
    WikipediaAdapter,
    ArXivAdapter,
    HNAlgoliaAdapter,
    RedditAdapter,
    GitHubAdapter,
    SearchResult,
    SOURCE_REGISTRY,
    SOURCE_TYPE_MAP,
)

pytestmark = pytest.mark.skipif(
    not HAS_AIORESPONSES, reason="aioresponses not installed"
)

ARXIV_SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>Machine Learning in Practice</title>
    <id>http://arxiv.org/abs/2401.00001v1</id>
    <summary>This paper explores practical applications of machine learning algorithms in real-world scenarios.</summary>
    <author><name>Jane Smith</name></author>
    <author><name>John Doe</name></author>
  </entry>
  <entry>
    <title>Deep Neural Networks</title>
    <id>http://arxiv.org/abs/2401.00002v1</id>
    <summary>A survey of deep neural network architectures and training techniques.</summary>
    <author><name>Alice Brown</name></author>
  </entry>
</feed>"""

WIKIPEDIA_SEARCH_SAMPLE = {
    "query": {
        "search": [
            {"title": "Machine learning", "snippet": "Machine learning is a method of data analysis.", "pageid": 233488},
            {"title": "Deep learning", "snippet": "Deep learning is part of machine learning methods.", "pageid": 4505},
        ]
    }
}

WIKIPEDIA_SUMMARY_SAMPLE = {
    "title": "Machine learning",
    "description": "Field of artificial intelligence",
    "extract": "Machine learning (ML) is a field of inquiry devoted to understanding and building methods that 'learn'.",
}

HN_SAMPLE = {
    "hits": [
        {
            "title": "Ask HN: Best resources for ML",
            "url": "https://example.com/ml-resources",
            "objectID": "12345",
            "points": 250,
            "num_comments": 87,
            "story_text": "I'm looking for the best resources to learn machine learning.",
        },
        {
            "title": "Show HN: ML tool",
            "url": None,  # No external URL
            "objectID": "67890",
            "points": 50,
            "num_comments": 20,
            "story_text": "",
        },
    ]
}

REDDIT_SAMPLE = {
    "data": {
        "children": [
            {
                "data": {
                    "title": "Best machine learning books in 2024",
                    "selftext": "I've been learning ML for 6 months. Here are the best books I've found.",
                    "permalink": "/r/MachineLearning/comments/abc123/best_ml_books/",
                    "score": 1200,
                    "subreddit": "MachineLearning",
                    "num_comments": 145,
                    "url": "https://www.reddit.com/r/MachineLearning/comments/abc123/best_ml_books/",
                }
            },
            {
                "data": {
                    "title": "Removed post",
                    "selftext": "[removed]",
                    "permalink": "/r/ML/comments/xyz/removed/",
                    "score": 0,
                    "subreddit": "ML",
                    "num_comments": 0,
                    "url": "https://www.reddit.com/r/ML/comments/xyz/removed/",
                }
            },
        ]
    }
}

GITHUB_SAMPLE = {
    "items": [
        {
            "full_name": "tensorflow/tensorflow",
            "description": "An Open Source Machine Learning Framework for Everyone",
            "html_url": "https://github.com/tensorflow/tensorflow",
            "stargazers_count": 180000,
            "language": "Python",
            "topics": ["machine-learning", "deep-learning", "neural-network"],
        },
        {
            "full_name": "scikit-learn/scikit-learn",
            "description": "scikit-learn: machine learning in Python",
            "html_url": "https://github.com/scikit-learn/scikit-learn",
            "stargazers_count": 55000,
            "language": "Python",
            "topics": ["machine-learning", "python"],
        },
    ]
}


# ---------------------------------------------------------------------------
# SearchResult structure
# ---------------------------------------------------------------------------

class TestSearchResultStructure:
    def test_has_required_fields(self):
        sr = SearchResult(
            title="Test", url="https://example.com", snippet="A snippet",
            source_id="wikipedia", source_type="reference", authority_score=0.85,
        )
        assert sr.title == "Test"
        assert sr.source_id == "wikipedia"
        assert sr.source_type == "reference"
        assert sr.authority_score == 0.85

    def test_raw_metadata_defaults_to_empty_dict(self):
        sr = SearchResult(
            title="T", url="u", snippet="s",
            source_id="test", source_type="reference", authority_score=0.5,
        )
        assert sr.raw_metadata == {}


# ---------------------------------------------------------------------------
# Source Registry
# ---------------------------------------------------------------------------

class TestSourceRegistry:
    def test_all_adapters_present(self):
        expected = {"wikipedia", "arxiv", "hackernews", "reddit", "github"}
        assert set(SOURCE_REGISTRY.keys()) == expected

    def test_source_type_map_keys(self):
        expected_types = {"all", "academic", "technical", "community", "reference", "news", "social"}
        assert set(SOURCE_TYPE_MAP.keys()) == expected_types

    def test_all_includes_all_sources(self):
        all_sources = set(SOURCE_TYPE_MAP["all"])
        assert all_sources == {"wikipedia", "arxiv", "hackernews", "reddit", "github"}

    def test_academic_includes_arxiv(self):
        assert "arxiv" in SOURCE_TYPE_MAP["academic"]
        assert "wikipedia" in SOURCE_TYPE_MAP["academic"]


# ---------------------------------------------------------------------------
# WikipediaAdapter
# ---------------------------------------------------------------------------

class TestWikipediaAdapter:
    async def test_search_returns_results(self):
        adapter = WikipediaAdapter()
        with aioresponses() as m:
            m.get(re.compile(r".*wikipedia\.org/w/api\.php.*"), payload=WIKIPEDIA_SEARCH_SAMPLE)
            results = await adapter.search("machine learning", 5)
        assert len(results) == 2
        assert results[0].title == "Machine learning"
        assert results[0].source_id == "wikipedia"
        assert results[0].source_type == "reference"
        assert results[0].authority_score == pytest.approx(0.85)

    async def test_search_constructs_wikipedia_url(self):
        adapter = WikipediaAdapter()
        with aioresponses() as m:
            m.get(re.compile(r".*wikipedia\.org/w/api\.php.*"), payload=WIKIPEDIA_SEARCH_SAMPLE)
            results = await adapter.search("machine learning", 5)
        assert "en.wikipedia.org/wiki/" in results[0].url

    async def test_fetch_full_content_returns_extract(self):
        adapter = WikipediaAdapter()
        url = "https://en.wikipedia.org/wiki/Machine_learning"
        with aioresponses() as m:
            m.get(re.compile(r".*wikipedia\.org/api/rest_v1/page/summary.*"), payload=WIKIPEDIA_SUMMARY_SAMPLE)
            content = await adapter.fetch_full_content(url)
        assert content is not None
        assert "Machine learning" in content

    async def test_search_network_error_returns_empty(self):
        adapter = WikipediaAdapter()
        with aioresponses() as m:
            m.get(re.compile(r".*wikipedia\.org.*"), exception=Exception("network error"))
            results = await adapter.search("machine learning", 5)
        assert results == []

    async def test_search_strips_html_from_snippets(self):
        adapter = WikipediaAdapter()
        data = {
            "query": {
                "search": [
                    {"title": "ML", "snippet": "Machine <span class=\"searchmatch\">learning</span> is great.", "pageid": 1}
                ]
            }
        }
        with aioresponses() as m:
            m.get(re.compile(r".*wikipedia\.org/w/api\.php.*"), payload=data)
            results = await adapter.search("learning", 5)
        assert "<span" not in results[0].snippet


# ---------------------------------------------------------------------------
# ArXivAdapter
# ---------------------------------------------------------------------------

class TestArXivAdapter:
    async def test_search_parses_atom_xml(self):
        adapter = ArXivAdapter()
        with aioresponses() as m:
            m.get(re.compile(r".*arxiv\.org/api/query.*"), body=ARXIV_SAMPLE.encode())
            results = await adapter.search("machine learning", 5)
        assert len(results) == 2
        assert results[0].title == "Machine Learning in Practice"
        assert results[0].source_id == "arxiv"
        assert results[0].source_type == "academic"
        assert results[0].authority_score == pytest.approx(0.90)

    async def test_search_stores_abstract_in_metadata(self):
        adapter = ArXivAdapter()
        with aioresponses() as m:
            m.get(re.compile(r".*arxiv\.org/api/query.*"), body=ARXIV_SAMPLE.encode())
            results = await adapter.search("machine learning", 5)
        assert "abstract" in results[0].raw_metadata
        assert len(results[0].raw_metadata["abstract"]) > 10

    async def test_search_stores_authors_in_metadata(self):
        adapter = ArXivAdapter()
        with aioresponses() as m:
            m.get(re.compile(r".*arxiv\.org/api/query.*"), body=ARXIV_SAMPLE.encode())
            results = await adapter.search("machine learning", 5)
        assert "authors" in results[0].raw_metadata
        assert "Jane Smith" in results[0].raw_metadata["authors"]

    async def test_fetch_full_content_returns_none(self):
        # ArXiv abstract is already in raw_metadata — no second fetch needed
        adapter = ArXivAdapter()
        content = await adapter.fetch_full_content("http://arxiv.org/abs/2401.00001v1")
        assert content is None

    async def test_search_network_error_returns_empty(self):
        adapter = ArXivAdapter()
        with aioresponses() as m:
            m.get(re.compile(r".*arxiv\.org.*"), exception=Exception("timeout"))
            results = await adapter.search("quantum", 3)
        assert results == []

    async def test_search_invalid_xml_returns_empty(self):
        adapter = ArXivAdapter()
        with aioresponses() as m:
            m.get(re.compile(r".*arxiv\.org.*"), body=b"<not valid xml {{{}}")
            results = await adapter.search("test", 3)
        assert results == []


# ---------------------------------------------------------------------------
# HNAlgoliaAdapter
# ---------------------------------------------------------------------------

class TestHNAlgoliaAdapter:
    async def test_search_returns_results(self):
        adapter = HNAlgoliaAdapter()
        with aioresponses() as m:
            m.get(re.compile(r".*hn\.algolia\.com.*"), payload=HN_SAMPLE)
            results = await adapter.search("machine learning", 5)
        assert len(results) == 2
        assert results[0].source_id == "hackernews"
        assert results[0].source_type == "community"

    async def test_search_uses_hn_url_for_null_external_url(self):
        adapter = HNAlgoliaAdapter()
        with aioresponses() as m:
            m.get(re.compile(r".*hn\.algolia\.com.*"), payload=HN_SAMPLE)
            results = await adapter.search("machine learning", 5)
        # Second result has no external URL — should use HN item URL
        no_url_result = next(r for r in results if "news.ycombinator.com" in r.url)
        assert "67890" in no_url_result.url

    async def test_popular_stories_get_authority_boost(self):
        adapter = HNAlgoliaAdapter()
        with aioresponses() as m:
            m.get(re.compile(r".*hn\.algolia\.com.*"), payload=HN_SAMPLE)
            results = await adapter.search("machine learning", 5)
        # Story with 250 points should have higher authority than base
        popular = next(r for r in results if r.raw_metadata.get("points", 0) > 100)
        assert popular.authority_score > adapter.authority_score

    async def test_search_network_error_returns_empty(self):
        adapter = HNAlgoliaAdapter()
        with aioresponses() as m:
            m.get(re.compile(r".*hn\.algolia\.com.*"), exception=Exception("connection refused"))
            results = await adapter.search("test", 5)
        assert results == []


# ---------------------------------------------------------------------------
# RedditAdapter
# ---------------------------------------------------------------------------

class TestRedditAdapter:
    async def test_search_returns_results(self):
        adapter = RedditAdapter()
        with aioresponses() as m:
            m.get(re.compile(r".*reddit\.com/search\.json.*"), payload=REDDIT_SAMPLE)
            results = await adapter.search("machine learning", 5)
        assert len(results) == 1  # Removed post should be filtered out
        assert results[0].source_id == "reddit"
        assert results[0].source_type == "community"

    async def test_search_filters_removed_posts(self):
        adapter = RedditAdapter()
        with aioresponses() as m:
            m.get(re.compile(r".*reddit\.com/search\.json.*"), payload=REDDIT_SAMPLE)
            results = await adapter.search("machine learning", 5)
        for r in results:
            assert r.snippet != "[removed]"
            assert r.snippet != "[deleted]"

    async def test_search_constructs_reddit_url(self):
        adapter = RedditAdapter()
        with aioresponses() as m:
            m.get(re.compile(r".*reddit\.com/search\.json.*"), payload=REDDIT_SAMPLE)
            results = await adapter.search("machine learning", 5)
        assert "reddit.com" in results[0].url

    async def test_search_network_error_returns_empty(self):
        adapter = RedditAdapter()
        with aioresponses() as m:
            m.get(re.compile(r".*reddit\.com.*"), exception=Exception("blocked"))
            results = await adapter.search("test", 5)
        assert results == []


# ---------------------------------------------------------------------------
# GitHubAdapter
# ---------------------------------------------------------------------------

class TestGitHubAdapter:
    async def test_search_returns_results(self):
        adapter = GitHubAdapter()
        with aioresponses() as m:
            m.get(re.compile(r".*api\.github\.com/search/repositories.*"), payload=GITHUB_SAMPLE)
            results = await adapter.search("machine learning", 5)
        assert len(results) == 2
        assert results[0].source_id == "github"
        assert results[0].source_type == "technical"

    async def test_popular_repos_get_higher_authority(self):
        adapter = GitHubAdapter()
        with aioresponses() as m:
            m.get(re.compile(r".*api\.github\.com/search/repositories.*"), payload=GITHUB_SAMPLE)
            results = await adapter.search("machine learning", 5)
        # tensorflow (180k stars) should score higher than scikit-learn (55k stars)
        tf = next((r for r in results if "tensorflow" in r.title), None)
        sk = next((r for r in results if "scikit-learn" in r.title), None)
        if tf and sk:
            assert tf.authority_score >= sk.authority_score

    async def test_search_stores_stars_in_metadata(self):
        adapter = GitHubAdapter()
        with aioresponses() as m:
            m.get(re.compile(r".*api\.github\.com/search/repositories.*"), payload=GITHUB_SAMPLE)
            results = await adapter.search("machine learning", 5)
        assert results[0].raw_metadata.get("stars", 0) > 0

    async def test_search_network_error_returns_empty(self):
        adapter = GitHubAdapter()
        with aioresponses() as m:
            m.get(re.compile(r".*api\.github\.com.*"), exception=Exception("rate limited"))
            results = await adapter.search("test", 5)
        assert results == []

    async def test_star_authority_scales_with_popularity(self):
        adapter = GitHubAdapter()
        low = adapter._star_authority(10)
        mid = adapter._star_authority(1000)
        high = adapter._star_authority(100000)
        assert low <= mid <= high
        assert high <= 1.0
        assert low >= 0.5
