#!/usr/bin/env python3
"""
RIDICULOUS Platform Demo
Shows the research and content gathering system in action
"""

import asyncio
from research_engine import ResearchEngine, ResearchParameters

async def main():
    print("=" * 60)
    print("🚀 RIDICULOUS - Research & Content Gathering Platform")
    print("=" * 60)
    print()

    # Initialize engine
    engine = ResearchEngine()

    # Demo parameters
    params = ResearchParameters(
        query="artificial intelligence trends 2026",
        depth=3,
        max_results=5,
        relevance_threshold=0.3
    )

    print(f"🔍 Research Query: {params.query}")
    print(f"📊 Depth: {params.depth} | Max Results: {params.max_results}")
    print(f"🎯 Relevance Threshold: {params.relevance_threshold}")
    print()
    print("⏳ Starting research... (this may take a moment)")
    print()

    # Run research
    await engine.start_research(params)

    # Wait for results
    while engine.status == "running":
        await asyncio.sleep(1)
        print(f"  Progress: {engine.progress:.0f}% - Found {len(engine.results)} results")

    print()
    print("=" * 60)
    print(f"✅ Research Complete! Status: {engine.status}")
    print("=" * 60)
    print()

    # Display results
    if engine.results:
        print(f"📚 Found {len(engine.results)} high-quality results:\n")

        for i, result in enumerate(engine.results[:3], 1):
            print(f"{i}. {result.title}")
            print(f"   URL: {result.url}")
            print(f"   Relevance: {result.relevance_score:.2f}")
            print(f"   Sentiment: {result.analysis.get('sentiment', 'N/A')}")
            print(f"   Summary: {result.summary[:150]}...")
            print()

    # Show statistics
    stats = engine.get_statistics()
    print("📊 Statistics:")
    print(f"   Total Results: {stats['total_results']}")
    print(f"   Avg Relevance: {stats['average_relevance']:.2f}")
    print(f"   Sources Analyzed: {stats['sources_analyzed']}")
    print(f"   Processing Time: {stats['processing_time']:.1f}s")
    print()

    print("=" * 60)
    print("🎯 Platform Features Available:")
    print("=" * 60)
    print("✅ 47 MCP Tools")
    print("✅ 15+ Platform Support (YouTube, Instagram, TikTok, etc.)")
    print("✅ Advanced OSINT & Intelligence Analysis")
    print("✅ Semantic Search with TF-IDF")
    print("✅ Real-time Research with DuckDuckGo")
    print("✅ Multi-format Export (Markdown, HTML, JSON)")
    print()
    print("🌐 Servers Running:")
    print("   Web UI: http://127.0.0.1:3000/static/index.html")
    print("   MCP API: http://127.0.0.1:8000/mcp")
    print()
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
