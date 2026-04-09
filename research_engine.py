"""
Research Engine Module
Handles multi-source content gathering, TF-IDF relevance scoring, and analysis.
"""

import asyncio
import json
import math
import uuid
from typing import Any
from datetime import datetime
import re
from urllib.parse import urlparse
from dataclasses import dataclass, asdict
import hashlib

try:
    import aiohttp
    from bs4 import BeautifulSoup
    import markdown
except ImportError:
    aiohttp = None
    BeautifulSoup = None
    markdown = None


@dataclass
class ResearchResult:
    """Represents a single research finding."""
    id: str
    title: str
    url: str
    content: str
    summary: str
    relevance_score: float
    source_type: str
    source_id: str          # "wikipedia", "arxiv", "hackernews", "reddit", "github"
    timestamp: str
    metadata: dict[str, Any]

    def to_dict(self):
        return asdict(self)


@dataclass
class ResearchParameters:
    """Parameters for a research task."""
    query: str
    source_type: str = "all"
    depth: int = 5
    max_results: int = 20
    relevance_threshold: float = 0.3
    detail_level: int = 5
    output_format: str = "markdown"
    summary_length: str = "moderate"


class ResearchEngine:
    """
    Multi-source research engine with TF-IDF relevance scoring and
    optional SQLite persistence via KnowledgeBase.
    """

    def __init__(self, knowledge_base=None):
        self.results: list[ResearchResult] = []
        self.parameters: ResearchParameters | None = None
        self.is_running = False
        self.is_paused = False
        self.progress = 0
        self.kb = knowledge_base
        self.current_session_id: str | None = None
        self.stats: dict[str, Any] = {
            "total_queries": 0,
            "total_results": 0,
            "avg_relevance": 0.0,
            "processing_time": 0.0,
            "sources_analyzed": 0,
            "errors": 0,
            "sources": {},
        }

    # ------------------------------------------------------------------
    # Text extraction
    # ------------------------------------------------------------------

    def extract_text(self, html: str) -> tuple[str, list[str]]:
        """
        Extract clean text and headings from HTML.

        Returns:
            (clean_text, headings_list) where headings_list contains
            the text content of h1/h2/h3 tags.
        """
        if not html:
            return ("", [])

        headings: list[str] = []

        if not BeautifulSoup:
            # Fallback: extract h1/h2/h3 text with regex, then strip all tags
            heading_matches = re.findall(r"<h[123][^>]*>(.*?)</h[123]>", html, re.IGNORECASE | re.DOTALL)
            for match in heading_matches:
                clean = re.sub(r"<[^>]+>", "", match).strip()
                if clean:
                    headings.append(clean)
            text = re.sub(r"<[^>]+>", "", html)
            return (text.strip(), headings)

        soup = BeautifulSoup(html, "html.parser")

        # Collect headings before removing anything
        for tag in soup.find_all(["h1", "h2", "h3"]):
            heading_text = tag.get_text(strip=True)
            if heading_text:
                headings.append(heading_text)

        # Remove noise elements
        for el in soup(["script", "style", "nav", "footer", "header"]):
            el.decompose()

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)

        return (text, headings)

    # ------------------------------------------------------------------
    # TF-IDF relevance scoring
    # ------------------------------------------------------------------

    def calculate_relevance(
        self,
        text: str,
        query: str,
        headings: list[str] | None = None,
        source_authority: float = 1.0,
    ) -> float:
        """
        Calculate relevance score using TF-IDF with heading boost,
        phrase proximity bonus, and source authority multiplier.

        Uses self.results as the rolling corpus for IDF calculation —
        scores become more precise as the session grows.
        """
        if not text or not text.strip():
            return 0.0

        query_terms = [t for t in query.lower().split() if t]
        if not query_terms:
            return 0.0

        text_lower = text.lower()
        text_words = re.findall(r"\b\w+\b", text_lower)
        total_words = len(text_words)
        if total_words == 0:
            return 0.0

        # Build corpus from current results for IDF
        # Each result's content is one "document" in the corpus
        corpus_docs = [
            re.findall(r"\b\w+\b", r.content.lower())
            for r in self.results
        ]
        N = len(corpus_docs) + 1  # +1 for current document

        # TF-IDF score
        tfidf_total = 0.0
        for term in query_terms:
            # TF: frequency of term in this document
            tf = text_words.count(term) / total_words

            # IDF: how rare is this term across the corpus
            docs_with_term = sum(1 for doc in corpus_docs if term in doc) + 1  # +1 for this doc
            idf = math.log((1 + N) / (1 + docs_with_term)) + 1

            tfidf_total += tf * idf

        # Normalize by number of query terms
        base_score = min(1.0, tfidf_total / len(query_terms))

        # Heading boost: query terms appearing in h1/h2/h3 get a bonus
        if headings:
            headings_text = " ".join(headings).lower()
            heading_matches = sum(
                1 for term in query_terms if term in headings_text
            )
            if heading_matches > 0:
                base_score += 0.15 * (heading_matches / len(query_terms))

        # Phrase proximity: exact full query in first 200 chars
        if query.lower() in text_lower[:200]:
            base_score += 0.20

        # Source authority multiplier — boosts high-authority sources
        final_score = min(1.0, base_score * source_authority)

        return max(0.0, final_score)

    # ------------------------------------------------------------------
    # Summary generation
    # ------------------------------------------------------------------

    def generate_summary(self, text: str, length: str = "moderate") -> str:
        """Generate a summary by extractive sentence selection."""
        if not text or not text.strip():
            return ""

        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        length_map = {
            "brief": 2,
            "moderate": 5,
            "detailed": 10,
        }
        num_sentences = min(len(sentences), length_map.get(length, 5))

        summary = ". ".join(sentences[:num_sentences])
        if summary and not summary.endswith("."):
            summary += "."

        return summary

    # ------------------------------------------------------------------
    # Content analysis
    # ------------------------------------------------------------------

    def analyze_content(
        self, text: str, query: str, detail_level: int
    ) -> dict[str, Any]:
        """Analyze content: word count, key topics, metadata."""
        analysis: dict[str, Any] = {
            "word_count": len(text.split()),
            "sentiment": "neutral",
            "key_topics": [],
            "entities": [],
            "readability_score": 0.0,
        }

        if not text:
            return analysis

        words = re.findall(r"\b\w+\b", text.lower())
        word_freq: dict[str, int] = {}
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "from", "this", "that", "these",
            "those", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "may", "might", "its", "it", "as", "if",
            "into", "than", "so", "not", "can", "also", "such",
        }

        for word in words:
            if len(word) > 3 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1

        analysis["key_topics"] = sorted(
            word_freq.items(), key=lambda x: x[1], reverse=True
        )[:10]

        return analysis

    # ------------------------------------------------------------------
    # Single result processing
    # ------------------------------------------------------------------

    async def process_result(
        self,
        search_result: Any,  # sources.SearchResult
        params: "ResearchParameters",
        adapter: Any | None = None,  # sources.SourceAdapter
    ) -> ResearchResult | None:
        """
        Fetch, extract, score, and build a ResearchResult from a search hit.

        For ArXiv, uses the pre-fetched abstract from raw_metadata to avoid
        a redundant network request. For all others, fetches via the adapter.
        """
        try:
            source_id = getattr(search_result, "source_id", "unknown")
            authority = getattr(search_result, "authority_score", 1.0)

            # Fetch content — ArXiv has it in raw_metadata already
            if source_id == "arxiv" and search_result.raw_metadata.get("abstract"):
                html = search_result.raw_metadata["abstract"]
            elif adapter is not None:
                html = await adapter.fetch_full_content(search_result.url)
            else:
                html = await self._fetch_content_generic(search_result.url)

            # Fallback to snippet if no full content
            if not html:
                html = getattr(search_result, "snippet", "") or ""

            if not html:
                return None

            text, headings = self.extract_text(html)
            if len(text) < 80:
                return None

            relevance = self.calculate_relevance(
                text, params.query, headings, authority
            )
            if relevance < params.relevance_threshold:
                return None

            summary = self.generate_summary(text, params.summary_length)
            metadata = self.analyze_content(text, params.query, params.detail_level)

            result_id = hashlib.md5(search_result.url.encode()).hexdigest()[:12]

            return ResearchResult(
                id=result_id,
                title=search_result.title,
                url=search_result.url,
                content=text[: 1000 * params.detail_level],
                summary=summary,
                relevance_score=relevance,
                source_type=getattr(search_result, "source_type", params.source_type),
                source_id=source_id,
                timestamp=datetime.now().isoformat(),
                metadata=metadata,
            )

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Error processing result {getattr(search_result, 'url', '?')}: {e}")
            return None

    async def _fetch_content_generic(self, url: str) -> str | None:
        """Generic aiohttp fetch for sources without a dedicated adapter."""
        if not aiohttp:
            return f"Sample content from {url}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        return await response.text()
                    return None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    # ------------------------------------------------------------------
    # Main research loop
    # ------------------------------------------------------------------

    async def run_research(
        self, params: "ResearchParameters"
    ) -> list[ResearchResult]:
        """
        Run multi-source research concurrently, process results sequentially,
        and persist everything to the knowledge base if configured.
        """
        from sources import SOURCE_TYPE_MAP, SOURCE_REGISTRY

        self.parameters = params
        self.is_running = True
        self.results = []
        self.progress = 0
        self.stats["total_queries"] += 1
        self.stats["sources"] = {}

        session_id = str(uuid.uuid4())
        self.current_session_id = session_id
        start_time = datetime.now()

        # Resolve adapters for requested source_type
        adapter_ids = SOURCE_TYPE_MAP.get(
            params.source_type, SOURCE_TYPE_MAP["all"]
        )
        active_adapters = [
            SOURCE_REGISTRY[aid]
            for aid in adapter_ids
            if aid in SOURCE_REGISTRY
        ]

        # Save session to KB at start
        if self.kb:
            self.kb.save_session(
                session_id,
                params.query,
                adapter_ids,
                start_time.isoformat(),
            )

        try:
            # Concurrent search across all active adapters
            per_adapter_max = max(3, params.max_results // max(len(active_adapters), 1))
            search_coros = [
                adapter.search(params.query, per_adapter_max)
                for adapter in active_adapters
            ]
            search_results_nested = await asyncio.gather(
                *search_coros, return_exceptions=True
            )

            # Flatten + deduplicate by URL, attach adapter reference
            all_pairs: list[tuple[Any, Any]] = []
            seen_urls: set[str] = set()
            for adapter, results_or_exc in zip(active_adapters, search_results_nested):
                if isinstance(results_or_exc, Exception):
                    self.stats["errors"] += 1
                    continue
                for sr in results_or_exc:
                    if sr.url not in seen_urls:
                        seen_urls.add(sr.url)
                        all_pairs.append((adapter, sr))

            self.stats["sources_analyzed"] = len(all_pairs)
            total_tasks = len(all_pairs)

            # Sequential processing (respects rate limits, avoids concurrency issues)
            for i, (adapter, search_result) in enumerate(all_pairs):
                if not self.is_running:
                    break

                while self.is_paused:
                    await asyncio.sleep(0.1)

                result = await self.process_result(search_result, params, adapter)

                if result:
                    self.results.append(result)
                    self.stats["total_results"] += 1
                    # Track per-source counts
                    sid = adapter.source_id
                    self.stats["sources"][sid] = self.stats["sources"].get(sid, 0) + 1
                    # Persist to KB
                    if self.kb:
                        self.kb.save_result(session_id, result)

                self.progress = int((i + 1) / max(total_tasks, 1) * 100)

                if len(self.results) >= params.max_results:
                    break

                # Respect adapter rate limit
                await asyncio.sleep(adapter.rate_limit_delay)

            # Finalize stats
            if self.results:
                self.stats["avg_relevance"] = (
                    sum(r.relevance_score for r in self.results) / len(self.results)
                )

            processing_time = (datetime.now() - start_time).total_seconds()
            self.stats["processing_time"] = processing_time

            # Complete session in KB
            if self.kb:
                quality = self._compute_quality_score()
                self.kb.complete_session(
                    session_id,
                    datetime.now().isoformat(),
                    len(self.results),
                    self.stats["avg_relevance"],
                    quality,
                )
                # Aggregate and save topics
                topic_freq: dict[str, int] = {}
                for r in self.results:
                    for topic, freq in r.metadata.get("key_topics", []):
                        topic_freq[topic] = topic_freq.get(topic, 0) + freq
                if topic_freq:
                    self.kb.save_topics(session_id, list(topic_freq.items()))

        finally:
            self.is_running = False
            self.is_paused = False

        return self.results

    def _compute_quality_score(self) -> float:
        """Compute a composite quality score for the current session."""
        if not self.results:
            return 0.0
        relevance_score = self.stats.get("avg_relevance", 0.0)
        source_diversity = len(self.stats.get("sources", {})) / 5.0
        quantity_score = min(1.0, len(self.results) / 20.0)
        return relevance_score * 0.5 + source_diversity * 0.3 + quantity_score * 0.2

    # ------------------------------------------------------------------
    # Control methods
    # ------------------------------------------------------------------

    def stop(self):
        """Stop the research process."""
        self.is_running = False
        self.is_paused = False

    def pause(self):
        """Pause the research process."""
        self.is_paused = True

    def resume(self):
        """Resume the research process."""
        self.is_paused = False

    def update_parameters(self, **kwargs):
        """Update parameters while running."""
        if self.parameters:
            for key, value in kwargs.items():
                if hasattr(self.parameters, key):
                    setattr(self.parameters, key, value)

    # ------------------------------------------------------------------
    # Result formatting
    # ------------------------------------------------------------------

    def get_results(self, format: str = "json") -> str:
        """Get results in specified format: json | markdown | html | text."""
        if format == "json":
            return json.dumps([r.to_dict() for r in self.results], indent=2)

        elif format == "markdown":
            query = self.parameters.query if self.parameters else "N/A"
            md = f"# Research Results: {query}\n\n"
            md += f"**Total Results:** {len(self.results)}\n"
            md += f"**Average Relevance:** {self.stats['avg_relevance']:.2f}\n\n"
            for result in self.results:
                md += f"## {result.title}\n\n"
                md += f"**URL:** [{result.url}]({result.url})\n"
                md += f"**Source:** {result.source_id} | **Relevance:** {result.relevance_score:.2f}\n\n"
                md += f"{result.summary}\n\n"
                md += "---\n\n"
            return md

        elif format == "html":
            query = self.parameters.query if self.parameters else "N/A"
            html = f"<h1>Research Results: {query}</h1>"
            for result in self.results:
                html += "<div class='result'>"
                html += f"<h2>{result.title}</h2>"
                html += f"<p><strong>Source:</strong> {result.source_id} | <strong>Relevance:</strong> {result.relevance_score:.2f}</p>"
                html += f"<p>{result.summary}</p>"
                html += f"<a href='{result.url}'>Read more</a>"
                html += "</div>"
            return html

        else:  # text
            query = self.parameters.query if self.parameters else "N/A"
            text = f"Research Results: {query}\n\n"
            for result in self.results:
                text += f"{result.title}\n"
                text += f"URL: {result.url}\n"
                text += f"Source: {result.source_id} | Relevance: {result.relevance_score:.2f}\n"
                text += f"{result.summary}\n\n"
                text += "-" * 80 + "\n\n"
            return text

    def get_stats(self) -> dict[str, Any]:
        """Get current statistics."""
        return self.stats.copy()


class ContentBuilder:
    """Build structured content from research results."""

    def __init__(self, results: list[ResearchResult]):
        self.results = results

    def build_article(self, tone: str = "professional") -> str:
        """Build an article from research results."""
        if not self.results:
            return "# Research Article\n\nNo research results available to build content."

        article = "# Research Article\n\n"
        article += "## Introduction\n\n"
        article += "This article synthesizes findings from multiple research sources.\n\n"
        article += "## Key Findings\n\n"
        for i, result in enumerate(self.results[:5], 1):
            article += f"### Finding {i}: {result.title}\n\n"
            article += f"{result.summary}\n\n"
            article += f"*Source: [{result.url}]({result.url}) [{result.source_id}]*\n\n"
        article += "## Conclusion\n\n"
        article += "The research reveals important insights across multiple sources.\n\n"
        return article

    def build_report(self, tone: str = "academic") -> str:
        """Build a research report."""
        report = "# Research Report\n\n"
        report += f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n"
        report += f"**Total Sources:** {len(self.results)}\n\n"
        report += "## Executive Summary\n\n"
        if self.results:
            summaries = [r.summary.split(".")[0] for r in self.results[:3] if r.summary]
            report += ". ".join(summaries) + ".\n\n"
        report += "## Detailed Findings\n\n"
        for result in self.results:
            report += f"### {result.title}\n\n"
            report += f"**Source:** {result.source_id} | **Relevance Score:** {result.relevance_score:.2f}\n\n"
            report += f"{result.summary}\n\n"
        return report

    def build_summary(self) -> str:
        """Build an executive summary."""
        summary = "# Executive Summary\n\n"
        if self.results:
            avg_relevance = sum(r.relevance_score for r in self.results) / len(self.results)
            summary += f"Analyzed {len(self.results)} sources with average relevance of {avg_relevance:.2f}.\n\n"
            summary += "## Key Points\n\n"
            for result in self.results[:5]:
                first_sentence = result.summary.split(".")[0] if result.summary else result.title
                summary += f"- **{result.title}**: {first_sentence}.\n"
        else:
            summary += "No research results available.\n"
        return summary

    def build_presentation(self) -> str:
        """Build presentation content."""
        pres = "# Research Presentation\n\n"
        pres += "---\n\n## Overview\n\n"
        pres += f"- Total Sources: {len(self.results)}\n"
        pres += "- Research Scope: Comprehensive multi-source analysis\n\n"
        for i, result in enumerate(self.results[:5], 1):
            pres += f"---\n\n## Slide {i}: {result.title}\n\n"
            pres += f"*Source: {result.source_id}*\n\n"
            pres += f"{result.summary}\n\n"
        pres += "---\n\n## Thank You\n\nQuestions?\n\n"
        return pres
