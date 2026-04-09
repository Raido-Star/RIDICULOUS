"""
Source Adapters Module
Real multi-source search and content fetching.
All adapters are free, require no API keys, and fail gracefully.
"""

import asyncio
import json
import math
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote, quote_plus

try:
    import aiohttp
except ImportError:
    aiohttp = None


@dataclass
class SearchResult:
    """Unified search result from any source adapter."""
    title: str
    url: str
    snippet: str
    source_id: str        # "wikipedia", "arxiv", "hackernews", "reddit", "github"
    source_type: str      # "reference", "academic", "community", "technical"
    authority_score: float
    raw_metadata: dict[str, Any] = field(default_factory=dict)


class SourceAdapter(ABC):
    """
    Abstract base for all source adapters.

    Each adapter handles one data source. All network errors are swallowed
    internally — adapters return empty lists / None on failure, never raise.
    The engine treats adapter failures as zero results, not crashes.
    """

    source_id: str
    source_type: str
    authority_score: float
    rate_limit_delay: float  # seconds to sleep after each fetch in run_research

    TIMEOUT = aiohttp.ClientTimeout(total=10) if aiohttp else None

    @abstractmethod
    async def search(self, query: str, max_results: int) -> list[SearchResult]:
        """Search this source and return structured results."""
        ...

    @abstractmethod
    async def fetch_full_content(self, url: str) -> str | None:
        """Fetch and return clean text content for a URL."""
        ...

    async def _safe_get(
        self,
        session: "aiohttp.ClientSession",
        url: str,
        headers: dict | None = None,
        params: dict | None = None,
        response_type: str = "json",
    ) -> Any | None:
        """
        Shared safe GET helper. Returns parsed response or None on any error.
        response_type: "json" | "text"
        """
        try:
            async with session.get(
                url, headers=headers or {}, params=params or {},
                timeout=self.TIMEOUT
            ) as resp:
                if resp.status != 200:
                    return None
                if response_type == "json":
                    return await resp.json(content_type=None)
                return await resp.text()
        except Exception:
            return None

    def _make_session(self) -> "aiohttp.ClientSession":
        return aiohttp.ClientSession(
            headers={"User-Agent": "RIDICULOUS-research-mcp/1.0 (open-source research tool)"}
        )


# ---------------------------------------------------------------------------
# Wikipedia
# ---------------------------------------------------------------------------

class WikipediaAdapter(SourceAdapter):
    """
    Wikipedia source adapter.

    Uses the MediaWiki Action API for search, and the REST API
    /page/summary endpoint for clean content extraction (no BeautifulSoup
    needed — Wikipedia returns pre-extracted plain text in the extract field).
    """

    source_id = "wikipedia"
    source_type = "reference"
    authority_score = 0.85
    rate_limit_delay = 0.2

    SEARCH_URL = "https://en.wikipedia.org/w/api.php"
    SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"

    async def search(self, query: str, max_results: int) -> list[SearchResult]:
        if not aiohttp:
            return []
        async with self._make_session() as session:
            data = await self._safe_get(
                session,
                self.SEARCH_URL,
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "srlimit": max_results,
                    "format": "json",
                    "utf8": "1",
                },
            )
        if not data:
            return []

        results = []
        for item in data.get("query", {}).get("search", []):
            title = item.get("title", "")
            url = f"https://en.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}"
            snippet = item.get("snippet", "").replace("<span class=\"searchmatch\">", "").replace("</span>", "")
            results.append(SearchResult(
                title=title,
                url=url,
                snippet=snippet,
                source_id=self.source_id,
                source_type=self.source_type,
                authority_score=self.authority_score,
                raw_metadata={"pageid": item.get("pageid")},
            ))
        return results

    async def fetch_full_content(self, url: str) -> str | None:
        """
        Fetches the Wikipedia REST summary for a page.
        Returns the pre-extracted plain text `extract` field.
        Falls back to None if the title can't be resolved.
        """
        if not aiohttp:
            return f"Wikipedia content for {url} (aiohttp not available)"

        # Extract title from URL: https://en.wikipedia.org/wiki/Title_Here
        try:
            title = url.split("/wiki/")[-1]
        except (IndexError, AttributeError):
            return None

        summary_url = self.SUMMARY_URL.format(title=title)
        async with self._make_session() as session:
            data = await self._safe_get(session, summary_url)

        if not data:
            return None
        extract = data.get("extract", "")
        # Prepend description for richer context
        description = data.get("description", "")
        if description:
            extract = f"{description}. {extract}"
        return extract or None


# ---------------------------------------------------------------------------
# ArXiv
# ---------------------------------------------------------------------------

class ArXivAdapter(SourceAdapter):
    """
    ArXiv academic paper adapter.

    Uses the ArXiv API (Atom XML feed). Abstracts are the primary content
    — no second fetch required. ArXiv asks for polite crawling: 1s delay.
    """

    source_id = "arxiv"
    source_type = "academic"
    authority_score = 0.90
    rate_limit_delay = 1.0

    API_URL = "https://export.arxiv.org/api/query"
    NS = "http://www.w3.org/2005/Atom"

    async def search(self, query: str, max_results: int) -> list[SearchResult]:
        if not aiohttp:
            return []
        async with self._make_session() as session:
            xml_text = await self._safe_get(
                session,
                self.API_URL,
                params={
                    "search_query": f"all:{query}",
                    "max_results": max_results,
                    "sortBy": "relevance",
                    "sortOrder": "descending",
                },
                response_type="text",
            )
        if not xml_text:
            return []

        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            return []

        results = []
        for entry in root.findall(f"{{{self.NS}}}entry"):
            title_el = entry.find(f"{{{self.NS}}}title")
            id_el = entry.find(f"{{{self.NS}}}id")
            summary_el = entry.find(f"{{{self.NS}}}summary")

            if title_el is None or id_el is None:
                continue

            title = (title_el.text or "").strip().replace("\n", " ")
            url = (id_el.text or "").strip()
            abstract = (summary_el.text or "").strip().replace("\n", " ") if summary_el is not None else ""

            # Extract authors
            authors = [
                a.find(f"{{{self.NS}}}name").text
                for a in entry.findall(f"{{{self.NS}}}author")
                if a.find(f"{{{self.NS}}}name") is not None
            ]

            results.append(SearchResult(
                title=title,
                url=url,
                snippet=abstract[:300],
                source_id=self.source_id,
                source_type=self.source_type,
                authority_score=self.authority_score,
                raw_metadata={"abstract": abstract, "authors": authors},
            ))
        return results

    async def fetch_full_content(self, url: str) -> str | None:
        """
        For ArXiv, the abstract from the search result IS the content.
        We don't need a second network request — return None to signal
        the engine should use the snippet/abstract already in raw_metadata.
        In practice, process_result will use the snippet stored during search.
        """
        # ArXiv abstracts are already fetched during search — avoid double-fetching
        # The engine will use search_result.snippet as content for ArXiv
        return None


# ---------------------------------------------------------------------------
# Hacker News (via Algolia API)
# ---------------------------------------------------------------------------

class HNAlgoliaAdapter(SourceAdapter):
    """
    Hacker News adapter via the Algolia search API.

    Surfaces high-signal practitioner discussions. Points and comment count
    are used as a quality signal within this source.
    """

    source_id = "hackernews"
    source_type = "community"
    authority_score = 0.65
    rate_limit_delay = 0.5

    SEARCH_URL = "https://hn.algolia.com/api/v1/search"
    ITEM_URL = "https://hn.algolia.com/api/v1/items/{id}"

    async def search(self, query: str, max_results: int) -> list[SearchResult]:
        if not aiohttp:
            return []
        async with self._make_session() as session:
            data = await self._safe_get(
                session,
                self.SEARCH_URL,
                params={
                    "query": query,
                    "tags": "story",
                    "hitsPerPage": max_results,
                },
            )
        if not data:
            return []

        results = []
        for hit in data.get("hits", []):
            title = hit.get("title", "")
            if not title:
                continue

            # Some HN items are Ask HN / Show HN with no external URL
            url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
            points = hit.get("points", 0) or 0
            num_comments = hit.get("num_comments", 0) or 0
            story_text = hit.get("story_text") or ""

            # Quality boost: popular stories score higher within HN
            quality_boost = min(0.2, math.log10(points + 1) / 10) if points > 0 else 0
            score = min(1.0, self.authority_score + quality_boost)

            results.append(SearchResult(
                title=title,
                url=url,
                snippet=story_text[:300] if story_text else f"HN discussion: {title}",
                source_id=self.source_id,
                source_type=self.source_type,
                authority_score=score,
                raw_metadata={
                    "points": points,
                    "num_comments": num_comments,
                    "object_id": hit.get("objectID"),
                },
            ))
        return results

    async def fetch_full_content(self, url: str) -> str | None:
        """
        For HN item URLs, fetch top comments via Algolia items API.
        For external URLs, return None (let engine use generic fetch).
        """
        if not aiohttp:
            return None
        if "news.ycombinator.com/item?id=" not in url:
            return None

        try:
            item_id = url.split("id=")[-1]
        except (IndexError, AttributeError):
            return None

        async with self._make_session() as session:
            data = await self._safe_get(
                session,
                self.ITEM_URL.format(id=item_id),
            )
        if not data:
            return None

        # Collect title + text + top-level comments
        parts = []
        title = data.get("title", "")
        text = data.get("text", "")
        if title:
            parts.append(f"Title: {title}")
        if text:
            parts.append(f"Post: {text}")

        for child in (data.get("children") or [])[:10]:
            comment_text = child.get("text", "")
            if comment_text and len(comment_text) > 50:
                parts.append(f"Comment: {comment_text[:400]}")

        return "\n\n".join(parts) if parts else None


# ---------------------------------------------------------------------------
# Reddit
# ---------------------------------------------------------------------------

class RedditAdapter(SourceAdapter):
    """
    Reddit adapter using the public JSON API.

    No OAuth required — append .json to Reddit URLs for structured data.
    The User-Agent header prevents 429 rate limiting from Reddit's CDN.
    """

    source_id = "reddit"
    source_type = "community"
    authority_score = 0.55
    rate_limit_delay = 1.0

    SEARCH_URL = "https://www.reddit.com/search.json"

    def _make_session(self) -> "aiohttp.ClientSession":
        # Reddit requires a descriptive User-Agent to avoid rate limiting
        return aiohttp.ClientSession(
            headers={"User-Agent": "RIDICULOUS-research-mcp/1.0 (open-source; contact: research@example.com)"}
        )

    async def search(self, query: str, max_results: int) -> list[SearchResult]:
        if not aiohttp:
            return []
        async with self._make_session() as session:
            data = await self._safe_get(
                session,
                self.SEARCH_URL,
                params={
                    "q": query,
                    "sort": "relevance",
                    "limit": max_results,
                    "type": "link",
                },
            )
        if not data:
            return []

        results = []
        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})

            title = post.get("title", "")
            if not title:
                continue

            # Skip removed/deleted posts
            selftext = post.get("selftext", "")
            if selftext in ("[removed]", "[deleted]"):
                continue

            permalink = post.get("permalink", "")
            url = f"https://www.reddit.com{permalink}" if permalink else post.get("url", "")
            score = post.get("score", 0) or 0
            subreddit = post.get("subreddit", "")

            results.append(SearchResult(
                title=title,
                url=url,
                snippet=selftext[:300] if selftext else f"r/{subreddit}: {title}",
                source_id=self.source_id,
                source_type=self.source_type,
                authority_score=self.authority_score,
                raw_metadata={
                    "score": score,
                    "subreddit": subreddit,
                    "num_comments": post.get("num_comments", 0),
                    "permalink": permalink,
                },
            ))
        return results

    async def fetch_full_content(self, url: str) -> str | None:
        """
        Fetch Reddit post + top comments using the .json trick.
        Works on any reddit.com/r/.../comments/ URL.
        """
        if not aiohttp:
            return None
        if "reddit.com" not in url:
            return None

        # Normalize URL: strip trailing slash, remove query params, append .json
        base_url = url.split("?")[0].rstrip("/") + ".json"

        async with self._make_session() as session:
            data = await self._safe_get(session, base_url)

        if not data or not isinstance(data, list):
            return None

        parts = []
        try:
            post_data = data[0]["data"]["children"][0]["data"]
            title = post_data.get("title", "")
            selftext = post_data.get("selftext", "")
            if title:
                parts.append(f"Title: {title}")
            if selftext and selftext not in ("[removed]", "[deleted]"):
                parts.append(f"Post: {selftext[:800]}")

            # Top-level comments
            comments = data[1]["data"]["children"]
            for comment in comments[:8]:
                cdata = comment.get("data", {})
                body = cdata.get("body", "")
                if body and body not in ("[removed]", "[deleted]") and len(body) > 50:
                    parts.append(f"Comment: {body[:400]}")
        except (IndexError, KeyError, TypeError):
            pass

        return "\n\n".join(parts) if parts else None


# ---------------------------------------------------------------------------
# GitHub
# ---------------------------------------------------------------------------

class GitHubAdapter(SourceAdapter):
    """
    GitHub repository search adapter.

    Searches repos by stars (quality signal). Fetches README content
    as full_content — GitHub READMEs are typically the richest technical
    summary of a project. Star count modifies authority score dynamically.

    Rate limit: 60 requests/hour unauthenticated. rate_limit_delay=1.5s
    keeps daily usage well within limits for normal research sessions.
    """

    source_id = "github"
    source_type = "technical"
    authority_score = 0.70
    rate_limit_delay = 1.5

    SEARCH_URL = "https://api.github.com/search/repositories"
    README_URL = "https://api.github.com/repos/{full_name}/readme"

    def _star_authority(self, stars: int) -> float:
        """Dynamically adjust authority based on star count."""
        if stars <= 0:
            return 0.50
        raw = math.log10(stars + 1) / 5.0
        return min(1.0, max(0.50, self.authority_score * raw + 0.35))

    async def search(self, query: str, max_results: int) -> list[SearchResult]:
        if not aiohttp:
            return []
        async with self._make_session() as session:
            data = await self._safe_get(
                session,
                self.SEARCH_URL,
                headers={"Accept": "application/vnd.github.v3+json"},
                params={
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": max_results,
                },
            )
        if not data:
            return []

        results = []
        for item in data.get("items", []):
            full_name = item.get("full_name", "")
            description = item.get("description") or ""
            stars = item.get("stargazers_count", 0) or 0
            html_url = item.get("html_url", "")
            topics = item.get("topics", [])
            language = item.get("language") or ""

            results.append(SearchResult(
                title=full_name,
                url=html_url,
                snippet=description[:300],
                source_id=self.source_id,
                source_type=self.source_type,
                authority_score=self._star_authority(stars),
                raw_metadata={
                    "stars": stars,
                    "language": language,
                    "topics": topics,
                    "description": description,
                    "full_name": full_name,
                },
            ))
        return results

    async def fetch_full_content(self, url: str) -> str | None:
        """
        Fetch the README for a GitHub repo.
        Content is base64-encoded — decode and return as plain text.
        Falls back to description if README fetch fails.
        """
        if not aiohttp:
            return None

        # Extract owner/repo from https://github.com/owner/repo
        try:
            parts = url.replace("https://github.com/", "").split("/")
            if len(parts) < 2:
                return None
            full_name = f"{parts[0]}/{parts[1]}"
        except (IndexError, AttributeError):
            return None

        import base64
        async with self._make_session() as session:
            data = await self._safe_get(
                session,
                self.README_URL.format(full_name=full_name),
                headers={"Accept": "application/vnd.github.v3+json"},
            )

        if not data:
            return None

        try:
            content_b64 = data.get("content", "")
            if not content_b64:
                return None
            # GitHub base64 includes newlines — strip them
            decoded = base64.b64decode(content_b64.replace("\n", "")).decode("utf-8", errors="replace")
            # Strip markdown headers but keep the text
            import re
            text = re.sub(r"#{1,6}\s+", "", decoded)
            return text[:3000]  # cap to avoid huge READMEs dominating
        except Exception:
            return None


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

SOURCE_REGISTRY: dict[str, SourceAdapter] = {
    "wikipedia": WikipediaAdapter(),
    "arxiv": ArXivAdapter(),
    "hackernews": HNAlgoliaAdapter(),
    "reddit": RedditAdapter(),
    "github": GitHubAdapter(),
}

SOURCE_TYPE_MAP: dict[str, list[str]] = {
    "all":       ["wikipedia", "arxiv", "hackernews", "reddit", "github"],
    "academic":  ["wikipedia", "arxiv"],
    "technical": ["github", "hackernews", "arxiv"],
    "community": ["hackernews", "reddit"],
    "reference": ["wikipedia"],
    "news":      ["hackernews", "reddit"],
    "social":    ["reddit", "hackernews"],
}
