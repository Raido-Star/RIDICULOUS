"""
Shared fixtures for all test modules.
"""

import pytest
from research_engine import ResearchResult, ResearchParameters, ResearchEngine, ContentBuilder


@pytest.fixture
def sample_result():
    return ResearchResult(
        id="abc123",
        title="Introduction to Machine Learning",
        url="https://en.wikipedia.org/wiki/Machine_learning",
        content=(
            "Machine learning is a subset of artificial intelligence. "
            "It enables computers to learn from data without being explicitly programmed. "
            "Supervised learning uses labeled training data. "
            "Unsupervised learning finds patterns in unlabeled data. "
            "Neural networks are inspired by the human brain. "
        ) * 8,
        summary="Machine learning enables computers to learn from data.",
        relevance_score=0.85,
        source_type="reference",
        source_id="wikipedia",
        timestamp="2026-01-01T00:00:00",
        metadata={
            "word_count": 120,
            "sentiment": "neutral",
            "key_topics": [("machine", 8), ("learning", 8), ("data", 6), ("neural", 4)],
            "entities": [],
            "readability_score": 0.0,
        },
    )


@pytest.fixture
def sample_result_2():
    return ResearchResult(
        id="def456",
        title="Deep Learning Fundamentals",
        url="https://arxiv.org/abs/1234.5678",
        content=(
            "Deep learning uses multiple layers to progressively extract features. "
            "Convolutional neural networks excel at image recognition tasks. "
            "Backpropagation is the key algorithm for training deep networks. "
            "Gradient descent optimizes the network weights iteratively. "
        ) * 8,
        summary="Deep learning uses layered neural networks for feature extraction.",
        relevance_score=0.78,
        source_type="academic",
        source_id="arxiv",
        timestamp="2026-01-02T00:00:00",
        metadata={
            "word_count": 96,
            "sentiment": "neutral",
            "key_topics": [("learning", 6), ("deep", 5), ("neural", 5), ("networks", 4)],
            "entities": [],
            "readability_score": 0.0,
        },
    )


@pytest.fixture
def sample_results(sample_result, sample_result_2):
    return [sample_result, sample_result_2]


@pytest.fixture
def engine():
    return ResearchEngine()


@pytest.fixture
def params():
    return ResearchParameters(
        query="machine learning",
        source_type="all",
        depth=3,
        max_results=5,
        relevance_threshold=0.3,
        detail_level=3,
        output_format="markdown",
        summary_length="moderate",
    )


@pytest.fixture
def tmp_db(tmp_path):
    from knowledge_base import KnowledgeBase
    return KnowledgeBase(db_path=tmp_path / "test.db")
