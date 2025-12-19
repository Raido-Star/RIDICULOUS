"""
Research Engine Module
Handles web scraping, content gathering, and analysis
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from urllib.parse import urlparse, urljoin
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
    """Represents a single research finding"""
    id: str
    title: str
    url: str
    content: str
    summary: str
    relevance_score: float
    source_type: str
    timestamp: str
    metadata: Dict[str, Any]

    def to_dict(self):
        return asdict(self)


@dataclass
class ResearchParameters:
    """Parameters for research task"""
    query: str
    source_type: str = "all"
    depth: int = 5
    max_results: int = 20
    relevance_threshold: float = 0.7
    detail_level: int = 5
    output_format: str = "markdown"
    summary_length: str = "moderate"


class ResearchEngine:
    """Main research engine for content gathering and analysis"""

    def __init__(self):
        self.results: List[ResearchResult] = []
        self.parameters: Optional[ResearchParameters] = None
        self.is_running = False
        self.is_paused = False
        self.progress = 0
        self.stats = {
            "total_queries": 0,
            "total_results": 0,
            "avg_relevance": 0.0,
            "processing_time": 0.0,
            "sources_analyzed": 0,
            "errors": 0
        }

    async def search_web(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Simulate web search (placeholder for real implementation)
        In production, integrate with search APIs like Google, Bing, DuckDuckGo, etc.
        """
        results = []
        base_urls = [
            "https://en.wikipedia.org/wiki/",
            "https://arxiv.org/abs/",
            "https://news.ycombinator.com/item?id=",
            "https://github.com/topics/",
            "https://medium.com/topic/"
        ]

        for i in range(min(max_results, 10)):
            result = {
                "title": f"{query} - Result {i+1}",
                "url": f"{base_urls[i % len(base_urls)]}{query.replace(' ', '_')}_{i}",
                "snippet": f"This is a snippet for {query}. Contains relevant information about the topic.",
                "source": base_urls[i % len(base_urls)].split('/')[2]
            }
            results.append(result)

        return results

    async def fetch_content(self, url: str) -> Optional[str]:
        """
        Fetch content from a URL
        """
        if not aiohttp:
            return f"Sample content from {url}\n\nThis is placeholder content that would be fetched from the actual URL in production."

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        return await response.text()
                    return None
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None

    def extract_text(self, html: str) -> str:
        """
        Extract text from HTML content
        """
        if not BeautifulSoup:
            # Simple HTML tag removal
            return re.sub(r'<[^>]+>', '', html)

        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text

    def calculate_relevance(self, text: str, query: str) -> float:
        """
        Calculate relevance score for content
        """
        query_terms = set(query.lower().split())
        text_lower = text.lower()

        # Count occurrences
        matches = sum(text_lower.count(term) for term in query_terms)

        # Normalize by text length
        text_length = len(text.split())
        if text_length == 0:
            return 0.0

        # Calculate score
        score = min(1.0, (matches / len(query_terms)) * 0.1)

        # Boost if query terms appear close together
        query_phrase = query.lower()
        if query_phrase in text_lower:
            score += 0.3

        return min(1.0, score)

    def generate_summary(self, text: str, length: str = "moderate") -> str:
        """
        Generate summary of text
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        length_map = {
            "brief": 2,
            "moderate": 5,
            "detailed": 10
        }

        num_sentences = min(len(sentences), length_map.get(length, 5))

        # Take first N sentences (in production, use extractive/abstractive summarization)
        summary = '. '.join(sentences[:num_sentences])
        if summary and not summary.endswith('.'):
            summary += '.'

        return summary

    def analyze_content(self, text: str, query: str, detail_level: int) -> Dict[str, Any]:
        """
        Analyze content and extract insights
        """
        analysis = {
            "word_count": len(text.split()),
            "sentiment": "neutral",  # Placeholder
            "key_topics": [],
            "entities": [],
            "readability_score": 0.0
        }

        # Extract key topics (simple word frequency)
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = {}
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}

        for word in words:
            if len(word) > 3 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Top topics
        analysis["key_topics"] = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]

        return analysis

    async def process_result(self, search_result: Dict[str, Any], params: ResearchParameters) -> Optional[ResearchResult]:
        """
        Process a single search result
        """
        try:
            # Fetch content
            html = await self.fetch_content(search_result["url"])
            if not html:
                return None

            # Extract text
            text = self.extract_text(html)
            if len(text) < 100:  # Too short
                return None

            # Calculate relevance
            relevance = self.calculate_relevance(text, params.query)
            if relevance < params.relevance_threshold:
                return None

            # Generate summary
            summary = self.generate_summary(text, params.summary_length)

            # Analyze content
            metadata = self.analyze_content(text, params.query, params.detail_level)

            # Create result
            result_id = hashlib.md5(search_result["url"].encode()).hexdigest()[:12]

            result = ResearchResult(
                id=result_id,
                title=search_result["title"],
                url=search_result["url"],
                content=text[:1000 * params.detail_level],  # Limit by detail level
                summary=summary,
                relevance_score=relevance,
                source_type=params.source_type,
                timestamp=datetime.now().isoformat(),
                metadata=metadata
            )

            return result

        except Exception as e:
            self.stats["errors"] += 1
            print(f"Error processing result: {str(e)}")
            return None

    async def run_research(self, params: ResearchParameters) -> List[ResearchResult]:
        """
        Run the research process
        """
        self.parameters = params
        self.is_running = True
        self.results = []
        self.progress = 0
        self.stats["total_queries"] += 1

        start_time = datetime.now()

        try:
            # Search for content
            search_results = await self.search_web(params.query, params.max_results * 2)
            self.stats["sources_analyzed"] = len(search_results)

            total_tasks = len(search_results)

            # Process results
            for i, search_result in enumerate(search_results):
                if not self.is_running:
                    break

                while self.is_paused:
                    await asyncio.sleep(0.1)

                result = await self.process_result(search_result, params)

                if result:
                    self.results.append(result)
                    self.stats["total_results"] += 1

                self.progress = int((i + 1) / total_tasks * 100)

                # Limit by max_results
                if len(self.results) >= params.max_results:
                    break

                # Simulate processing time
                await asyncio.sleep(0.1)

            # Calculate stats
            if self.results:
                self.stats["avg_relevance"] = sum(r.relevance_score for r in self.results) / len(self.results)

            processing_time = (datetime.now() - start_time).total_seconds()
            self.stats["processing_time"] = processing_time

        finally:
            self.is_running = False
            self.is_paused = False

        return self.results

    def stop(self):
        """Stop the research process"""
        self.is_running = False
        self.is_paused = False

    def pause(self):
        """Pause the research process"""
        self.is_paused = True

    def resume(self):
        """Resume the research process"""
        self.is_paused = False

    def update_parameters(self, **kwargs):
        """Update parameters while running"""
        if self.parameters:
            for key, value in kwargs.items():
                if hasattr(self.parameters, key):
                    setattr(self.parameters, key, value)

    def get_results(self, format: str = "json") -> str:
        """Get results in specified format"""
        if format == "json":
            return json.dumps([r.to_dict() for r in self.results], indent=2)

        elif format == "markdown":
            md = f"# Research Results: {self.parameters.query if self.parameters else 'N/A'}\n\n"
            md += f"**Total Results:** {len(self.results)}\n"
            md += f"**Average Relevance:** {self.stats['avg_relevance']:.2f}\n\n"

            for result in self.results:
                md += f"## {result.title}\n\n"
                md += f"**URL:** [{result.url}]({result.url})\n"
                md += f"**Relevance:** {result.relevance_score:.2f}\n\n"
                md += f"{result.summary}\n\n"
                md += "---\n\n"

            return md

        elif format == "html":
            html = f"<h1>Research Results: {self.parameters.query if self.parameters else 'N/A'}</h1>"
            for result in self.results:
                html += f"<div class='result'>"
                html += f"<h2>{result.title}</h2>"
                html += f"<p><strong>Relevance:</strong> {result.relevance_score:.2f}</p>"
                html += f"<p>{result.summary}</p>"
                html += f"<a href='{result.url}'>Read more</a>"
                html += f"</div>"

            return html

        else:  # text
            text = f"Research Results: {self.parameters.query if self.parameters else 'N/A'}\n\n"
            for result in self.results:
                text += f"{result.title}\n"
                text += f"URL: {result.url}\n"
                text += f"Relevance: {result.relevance_score:.2f}\n"
                text += f"{result.summary}\n\n"
                text += "-" * 80 + "\n\n"

            return text

    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        return self.stats.copy()


class ContentBuilder:
    """Build structured content from research results"""

    def __init__(self, results: List[ResearchResult]):
        self.results = results

    def build_article(self, tone: str = "professional") -> str:
        """Build an article from research results"""
        if not self.results:
            return "No research results available to build content."

        article = "# Research Article\n\n"

        # Introduction
        article += "## Introduction\n\n"
        article += "This article synthesizes findings from multiple research sources.\n\n"

        # Main content
        article += "## Key Findings\n\n"
        for i, result in enumerate(self.results[:5], 1):
            article += f"### Finding {i}: {result.title}\n\n"
            article += f"{result.summary}\n\n"
            article += f"*Source: [{result.url}]({result.url})*\n\n"

        # Conclusion
        article += "## Conclusion\n\n"
        article += "The research reveals important insights across multiple sources.\n\n"

        return article

    def build_report(self, tone: str = "academic") -> str:
        """Build a research report"""
        report = "# Research Report\n\n"
        report += f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n"
        report += f"**Total Sources:** {len(self.results)}\n\n"

        report += "## Executive Summary\n\n"
        # Combine first sentences from top results
        summaries = [r.summary.split('.')[0] for r in self.results[:3]]
        report += '. '.join(summaries) + ".\n\n"

        report += "## Detailed Findings\n\n"
        for result in self.results:
            report += f"### {result.title}\n\n"
            report += f"**Relevance Score:** {result.relevance_score:.2f}\n\n"
            report += f"{result.summary}\n\n"

        return report

    def build_summary(self) -> str:
        """Build an executive summary"""
        summary = "# Executive Summary\n\n"

        if self.results:
            avg_relevance = sum(r.relevance_score for r in self.results) / len(self.results)
            summary += f"Analyzed {len(self.results)} sources with average relevance of {avg_relevance:.2f}.\n\n"

            summary += "## Key Points\n\n"
            for result in self.results[:5]:
                summary += f"- {result.title}: {result.summary.split('.')[0]}.\n"

        return summary

    def build_presentation(self) -> str:
        """Build presentation content"""
        pres = "# Research Presentation\n\n"

        pres += "---\n\n## Overview\n\n"
        pres += f"- Total Sources: {len(self.results)}\n"
        pres += f"- Research Scope: Comprehensive analysis\n\n"

        for i, result in enumerate(self.results[:5], 1):
            pres += f"---\n\n## Slide {i}: {result.title}\n\n"
            pres += f"{result.summary}\n\n"

        pres += "---\n\n## Thank You\n\n"
        pres += "Questions?\n\n"

        return pres
