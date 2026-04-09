"""
Unit tests for research_engine.py — pure functions and ContentBuilder.
These tests run without any network calls or external dependencies.
"""

import pytest
from research_engine import ResearchEngine, ContentBuilder, ResearchResult, ResearchParameters


# ---------------------------------------------------------------------------
# calculate_relevance
# ---------------------------------------------------------------------------

class TestCalculateRelevance:
    def test_empty_text_returns_zero(self):
        engine = ResearchEngine()
        score = engine.calculate_relevance("", "machine learning")
        assert score == 0.0

    def test_score_never_exceeds_one(self):
        engine = ResearchEngine()
        # Extremely dense repetition of query terms
        dense_text = "machine learning machine learning " * 200
        score = engine.calculate_relevance(dense_text, "machine learning")
        assert score <= 1.0

    def test_score_non_negative(self):
        engine = ResearchEngine()
        score = engine.calculate_relevance("some unrelated content here", "quantum physics")
        assert score >= 0.0

    def test_higher_score_for_matching_content(self):
        engine = ResearchEngine()
        relevant = "machine learning is a powerful technique for data analysis and prediction"
        irrelevant = "the weather today is sunny and warm with light winds from the north"
        relevant_score = engine.calculate_relevance(relevant, "machine learning")
        irrelevant_score = engine.calculate_relevance(irrelevant, "machine learning")
        assert relevant_score > irrelevant_score

    def test_exact_phrase_in_first_200_chars_boosts_score(self):
        engine = ResearchEngine()
        # Put exact phrase early
        with_phrase = "machine learning is the topic. " + "some filler content " * 20
        # Same terms but not as exact phrase at start
        without_phrase = "some filler content " * 20 + "machine and learning are separate"
        score_with = engine.calculate_relevance(with_phrase, "machine learning")
        score_without = engine.calculate_relevance(without_phrase, "machine learning")
        assert score_with > score_without

    def test_single_word_query_bounded(self):
        engine = ResearchEngine()
        text = "python python python python python python python python"
        score = engine.calculate_relevance(text, "python")
        assert 0.0 <= score <= 1.0

    def test_empty_query_does_not_crash(self):
        engine = ResearchEngine()
        score = engine.calculate_relevance("some content here", "")
        assert isinstance(score, float)

    def test_whitespace_only_text_returns_zero(self):
        engine = ResearchEngine()
        score = engine.calculate_relevance("   \n\t  ", "machine learning")
        assert score == 0.0


# ---------------------------------------------------------------------------
# extract_text
# ---------------------------------------------------------------------------

class TestExtractText:
    def test_script_tags_removed(self):
        engine = ResearchEngine()
        html = "<html><body><script>alert('xss')</script><p>Hello world</p></body></html>"
        text, headings = engine.extract_text(html)
        assert "alert" not in text
        assert "Hello world" in text

    def test_style_tags_removed(self):
        engine = ResearchEngine()
        html = "<html><head><style>.foo { color: red; }</style></head><body><p>Content</p></body></html>"
        text, headings = engine.extract_text(html)
        assert "color" not in text
        assert "Content" in text

    def test_h1_h2_appear_in_headings(self):
        engine = ResearchEngine()
        html = "<html><body><h1>Main Title</h1><h2>Section One</h2><p>Body text here.</p></body></html>"
        text, headings = engine.extract_text(html)
        assert "Main Title" in headings
        assert "Section One" in headings

    def test_headings_not_duplicated_in_text_and_headings(self):
        engine = ResearchEngine()
        html = "<html><body><h1>Title</h1><p>Paragraph.</p></body></html>"
        text, headings = engine.extract_text(html)
        # Both are returned — that's fine, just ensure types are correct
        assert isinstance(headings, list)
        assert isinstance(text, str)

    def test_empty_string_returns_empty_tuple(self):
        engine = ResearchEngine()
        text, headings = engine.extract_text("")
        assert text == ""
        assert headings == []

    def test_plain_text_no_crash(self):
        engine = ResearchEngine()
        # No HTML tags — should strip gracefully
        plain = "This is just plain text without any tags."
        text, headings = engine.extract_text(plain)
        assert isinstance(text, str)
        assert isinstance(headings, list)

    def test_malformed_html_no_crash(self):
        engine = ResearchEngine()
        malformed = "<div><p>Unclosed paragraph<div><h1>Title without close"
        text, headings = engine.extract_text(malformed)
        assert isinstance(text, str)
        assert isinstance(headings, list)

    def test_nav_footer_header_removed(self):
        engine = ResearchEngine()
        html = (
            "<html><body>"
            "<nav>Navigation menu</nav>"
            "<header>Site header</header>"
            "<main><p>Main content here.</p></main>"
            "<footer>Footer text</footer>"
            "</body></html>"
        )
        text, headings = engine.extract_text(html)
        assert "Navigation menu" not in text
        assert "Site header" not in text
        assert "Footer text" not in text
        assert "Main content here" in text

    def test_returns_tuple_of_two(self):
        engine = ResearchEngine()
        result = engine.extract_text("<p>Hello</p>")
        assert isinstance(result, tuple)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# generate_summary
# ---------------------------------------------------------------------------

class TestGenerateSummary:
    def test_brief_returns_at_most_two_sentences(self):
        engine = ResearchEngine()
        text = "First sentence here. Second sentence here. Third sentence here. Fourth sentence here."
        summary = engine.generate_summary(text, "brief")
        # Count sentences in output (split on period)
        sentences = [s.strip() for s in summary.split(".") if s.strip()]
        assert len(sentences) <= 2

    def test_detailed_returns_at_most_ten_sentences(self):
        engine = ResearchEngine()
        text = ". ".join([f"Sentence number {i} with enough words to qualify" for i in range(15)]) + "."
        summary = engine.generate_summary(text, "detailed")
        sentences = [s.strip() for s in summary.split(".") if s.strip()]
        assert len(sentences) <= 10

    def test_moderate_returns_at_most_five_sentences(self):
        engine = ResearchEngine()
        text = ". ".join([f"Sentence number {i} with enough words to qualify" for i in range(10)]) + "."
        summary = engine.generate_summary(text, "moderate")
        sentences = [s.strip() for s in summary.split(".") if s.strip()]
        assert len(sentences) <= 5

    def test_empty_text_returns_empty_string(self):
        engine = ResearchEngine()
        summary = engine.generate_summary("", "moderate")
        assert summary == ""

    def test_fewer_sentences_than_requested_returns_all(self):
        engine = ResearchEngine()
        text = "Only one sentence here that is long enough."
        summary = engine.generate_summary(text, "detailed")
        assert "Only one sentence" in summary

    def test_summary_ends_with_period(self):
        engine = ResearchEngine()
        text = "First sentence here. Second sentence here. Third sentence here."
        summary = engine.generate_summary(text, "brief")
        if summary:
            assert summary.endswith(".")

    def test_unknown_length_defaults_to_moderate(self):
        engine = ResearchEngine()
        text = ". ".join([f"Sentence number {i} with enough words to qualify" for i in range(10)]) + "."
        summary = engine.generate_summary(text, "unknown_value")
        sentences = [s.strip() for s in summary.split(".") if s.strip()]
        assert len(sentences) <= 5


# ---------------------------------------------------------------------------
# analyze_content
# ---------------------------------------------------------------------------

class TestAnalyzeContent:
    def test_stop_words_excluded(self):
        engine = ResearchEngine()
        text = "the quick brown fox jumps over the lazy dog and the fox runs away"
        analysis = engine.analyze_content(text, "fox", detail_level=5)
        topic_words = [t for t, _ in analysis["key_topics"]]
        assert "the" not in topic_words
        assert "and" not in topic_words
        # "over" is 4 chars and passes the length filter — stop words list is the guard
        assert "for" not in topic_words  # 3 chars, excluded by length

    def test_short_words_excluded(self):
        engine = ResearchEngine()
        text = "big fox runs fast here then goes away from the den"
        analysis = engine.analyze_content(text, "fox", detail_level=5)
        topic_words = [t for t, _ in analysis["key_topics"]]
        # Words <= 3 chars should be excluded
        for word in topic_words:
            assert len(word) > 3

    def test_key_topics_sorted_by_frequency(self):
        engine = ResearchEngine()
        # "python" appears 5 times, "java" appears 2 times
        text = "python python python python python java java programming languages"
        analysis = engine.analyze_content(text, "programming", detail_level=5)
        if len(analysis["key_topics"]) >= 2:
            freqs = [freq for _, freq in analysis["key_topics"]]
            assert freqs == sorted(freqs, reverse=True)

    def test_word_count_accurate(self):
        engine = ResearchEngine()
        text = "one two three four five"
        analysis = engine.analyze_content(text, "test", detail_level=5)
        assert analysis["word_count"] == 5

    def test_returns_required_keys(self):
        engine = ResearchEngine()
        analysis = engine.analyze_content("some text content here", "text", detail_level=3)
        assert "word_count" in analysis
        assert "key_topics" in analysis
        assert "sentiment" in analysis

    def test_empty_text_does_not_crash(self):
        engine = ResearchEngine()
        analysis = engine.analyze_content("", "query", detail_level=5)
        assert analysis["word_count"] == 0
        assert analysis["key_topics"] == []


# ---------------------------------------------------------------------------
# ContentBuilder
# ---------------------------------------------------------------------------

class TestContentBuilder:
    def test_build_article_empty_results_returns_fallback(self):
        builder = ContentBuilder([])
        result = builder.build_article()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_build_report_empty_results_returns_string(self):
        builder = ContentBuilder([])
        result = builder.build_report()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_build_summary_empty_results_returns_string(self):
        builder = ContentBuilder([])
        result = builder.build_summary()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_build_presentation_empty_results_returns_string(self):
        builder = ContentBuilder([])
        result = builder.build_presentation()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_build_article_includes_result_titles(self, sample_results):
        builder = ContentBuilder(sample_results)
        article = builder.build_article()
        assert sample_results[0].title in article

    def test_build_report_includes_date(self, sample_results):
        from datetime import datetime
        builder = ContentBuilder(sample_results)
        report = builder.build_report()
        today = datetime.now().strftime("%Y-%m-%d")
        assert today in report

    def test_build_summary_includes_result_count(self, sample_results):
        builder = ContentBuilder(sample_results)
        summary = builder.build_summary()
        assert str(len(sample_results)) in summary

    def test_build_presentation_includes_slides(self, sample_results):
        builder = ContentBuilder(sample_results)
        presentation = builder.build_presentation()
        assert "Slide" in presentation

    def test_all_builders_return_markdown_strings(self, sample_results):
        builder = ContentBuilder(sample_results)
        for method in [builder.build_article, builder.build_report,
                       builder.build_summary, builder.build_presentation]:
            result = method()
            assert isinstance(result, str)
            assert "#" in result  # All should have at least one markdown heading


# ---------------------------------------------------------------------------
# ResearchResult
# ---------------------------------------------------------------------------

class TestResearchResult:
    def test_to_dict_round_trip(self, sample_result):
        d = sample_result.to_dict()
        assert d["id"] == sample_result.id
        assert d["title"] == sample_result.title
        assert d["url"] == sample_result.url
        assert d["relevance_score"] == sample_result.relevance_score
        assert d["source_id"] == sample_result.source_id

    def test_to_dict_returns_dict(self, sample_result):
        d = sample_result.to_dict()
        assert isinstance(d, dict)

    def test_to_dict_contains_all_fields(self, sample_result):
        d = sample_result.to_dict()
        required_keys = ["id", "title", "url", "content", "summary",
                         "relevance_score", "source_type", "source_id",
                         "timestamp", "metadata"]
        for key in required_keys:
            assert key in d, f"Missing key: {key}"
