"""
Research & Content Gathering MCP Server
Advanced research engine with live parameter controls
"""

from mcp.server.fastmcp import FastMCP
from pydantic import Field
import mcp.types as types
import asyncio
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from research_engine import (
    ResearchEngine,
    ContentBuilder,
    ResearchParameters,
    ResearchResult
)
from asset_generator import AssetGeneratorManager
from intelligence_engine import (
    IntelligenceEngine,
    SemanticSearchEngine,
    SourceCredibilityScorer,
    KnowledgeGraphGenerator,
    SmartQueryExpander,
    ResearchSessionManager
)
from osint_engine import (
    OSINTEngine,
    SocialNetworkAnalyzer,
    DigitalFootprintTracker,
    TimelineAnalyzer,
    SentimentTrendAnalyzer,
    GeospatialAnalyzer,
    PatternRecognitionEngine
)

# Initialize MCP server
mcp = FastMCP("Research & Content Gathering Server", stateless_http=True)

# Global research engine instance
engine = ResearchEngine()
current_task: Optional[asyncio.Task] = None

# Global asset generator instance
asset_manager = AssetGeneratorManager()

# Global intelligence engine instance
intelligence_engine = IntelligenceEngine()

# Global OSINT engine instance
osint_engine = OSINTEngine()


# Serve static files
@mcp.resource(
    uri="static://index.html",
    name="Web Interface",
    description="Main web interface for the research app"
)
def get_web_interface() -> str:
    """Return the web interface HTML"""
    static_file = Path(__file__).parent / "static" / "index.html"
    if static_file.exists():
        return static_file.read_text()
    return "<h1>Web interface not found</h1>"


# Research Tools
@mcp.tool(
    title="Start Research",
    description="Start a research task with specified parameters"
)
async def start_research(
    query: str = Field(description="The research query or topic"),
    source_type: str = Field(default="all", description="Type of sources: all, academic, news, technical, social"),
    depth: int = Field(default=5, description="Research depth level (1-10)"),
    max_results: int = Field(default=20, description="Maximum number of results to gather"),
    relevance_threshold: float = Field(default=0.7, description="Minimum relevance score (0.0-1.0)"),
    detail_level: int = Field(default=5, description="Level of detail for content extraction (1-10)"),
    output_format: str = Field(default="markdown", description="Output format: markdown, html, json, text"),
    summary_length: str = Field(default="moderate", description="Summary length: brief, moderate, detailed")
) -> str:
    """Start a research task with the specified parameters"""
    global current_task, engine

    if engine.is_running:
        return json.dumps({
            "status": "error",
            "message": "A research task is already running. Please stop it first."
        })

    # Create parameters
    params = ResearchParameters(
        query=query,
        source_type=source_type,
        depth=depth,
        max_results=max_results,
        relevance_threshold=relevance_threshold,
        detail_level=detail_level,
        output_format=output_format,
        summary_length=summary_length
    )

    # Start research in background
    current_task = asyncio.create_task(engine.run_research(params))

    return json.dumps({
        "status": "started",
        "message": f"Research task started for query: {query}",
        "parameters": {
            "query": query,
            "source_type": source_type,
            "depth": depth,
            "max_results": max_results,
            "relevance_threshold": relevance_threshold,
            "detail_level": detail_level
        }
    })


@mcp.tool(
    title="Get Research Status",
    description="Get the current status of the research task"
)
def get_research_status() -> str:
    """Get the current status of the research task"""
    global engine

    status = {
        "is_running": engine.is_running,
        "is_paused": engine.is_paused,
        "progress": engine.progress,
        "results_count": len(engine.results),
        "stats": engine.get_stats()
    }

    return json.dumps(status, indent=2)


@mcp.tool(
    title="Pause Research",
    description="Pause the current research task"
)
def pause_research() -> str:
    """Pause the research task"""
    global engine

    if not engine.is_running:
        return json.dumps({"status": "error", "message": "No research task is running"})

    engine.pause()
    return json.dumps({"status": "paused", "message": "Research task paused"})


@mcp.tool(
    title="Resume Research",
    description="Resume the paused research task"
)
def resume_research() -> str:
    """Resume the research task"""
    global engine

    if not engine.is_paused:
        return json.dumps({"status": "error", "message": "Research task is not paused"})

    engine.resume()
    return json.dumps({"status": "resumed", "message": "Research task resumed"})


@mcp.tool(
    title="Stop Research",
    description="Stop the current research task"
)
def stop_research() -> str:
    """Stop the research task"""
    global engine, current_task

    if not engine.is_running:
        return json.dumps({"status": "error", "message": "No research task is running"})

    engine.stop()
    if current_task:
        current_task.cancel()

    return json.dumps({"status": "stopped", "message": "Research task stopped"})


@mcp.tool(
    title="Update Research Parameters",
    description="Update research parameters while task is running"
)
def update_parameters(
    depth: Optional[int] = Field(default=None, description="Research depth level (1-10)"),
    max_results: Optional[int] = Field(default=None, description="Maximum number of results"),
    relevance_threshold: Optional[float] = Field(default=None, description="Minimum relevance score"),
    detail_level: Optional[int] = Field(default=None, description="Level of detail (1-10)")
) -> str:
    """Update parameters of the running research task"""
    global engine

    updates = {}
    if depth is not None:
        updates["depth"] = depth
    if max_results is not None:
        updates["max_results"] = max_results
    if relevance_threshold is not None:
        updates["relevance_threshold"] = relevance_threshold
    if detail_level is not None:
        updates["detail_level"] = detail_level

    engine.update_parameters(**updates)

    return json.dumps({
        "status": "updated",
        "message": "Parameters updated successfully",
        "updates": updates
    })


@mcp.tool(
    title="Get Research Results",
    description="Get the current research results"
)
def get_results(
    format: str = Field(default="json", description="Output format: json, markdown, html, text"),
    limit: Optional[int] = Field(default=None, description="Limit number of results returned")
) -> str:
    """Get the research results in specified format"""
    global engine

    if not engine.results:
        return json.dumps({"status": "empty", "message": "No results available yet"})

    results = engine.results[:limit] if limit else engine.results

    if format == "json":
        return json.dumps({
            "status": "success",
            "count": len(results),
            "results": [r.to_dict() for r in results]
        }, indent=2)
    else:
        # Create temporary engine with limited results
        temp_engine = ResearchEngine()
        temp_engine.results = results
        temp_engine.parameters = engine.parameters
        temp_engine.stats = engine.stats

        return temp_engine.get_results(format)


@mcp.tool(
    title="Export Results",
    description="Export research results to a file"
)
def export_results(
    filename: str = Field(description="Output filename"),
    format: str = Field(default="markdown", description="Export format: markdown, html, json, text")
) -> str:
    """Export research results to a file"""
    global engine

    if not engine.results:
        return json.dumps({"status": "error", "message": "No results to export"})

    try:
        content = engine.get_results(format)

        output_path = Path(filename)
        output_path.write_text(content)

        return json.dumps({
            "status": "success",
            "message": f"Results exported to {filename}",
            "path": str(output_path.absolute()),
            "format": format,
            "results_count": len(engine.results)
        })

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Export failed: {str(e)}"
        })


# Content Building Tools
@mcp.tool(
    title="Build Content",
    description="Build structured content from research results"
)
def build_content(
    content_type: str = Field(description="Type of content: article, report, summary, presentation"),
    tone: str = Field(default="professional", description="Tone: professional, academic, casual, technical"),
    output_file: Optional[str] = Field(default=None, description="Optional output file path")
) -> str:
    """Build structured content from research results"""
    global engine

    if not engine.results:
        return json.dumps({"status": "error", "message": "No research results available"})

    builder = ContentBuilder(engine.results)

    # Build content based on type
    if content_type == "article":
        content = builder.build_article(tone)
    elif content_type == "report":
        content = builder.build_report(tone)
    elif content_type == "summary":
        content = builder.build_summary()
    elif content_type == "presentation":
        content = builder.build_presentation()
    else:
        return json.dumps({"status": "error", "message": f"Unknown content type: {content_type}"})

    # Save to file if specified
    if output_file:
        try:
            Path(output_file).write_text(content)
            return json.dumps({
                "status": "success",
                "message": f"Content built and saved to {output_file}",
                "content_type": content_type,
                "tone": tone,
                "path": output_file
            })
        except Exception as e:
            return json.dumps({"status": "error", "message": f"Failed to save: {str(e)}"})

    return json.dumps({
        "status": "success",
        "message": "Content built successfully",
        "content_type": content_type,
        "tone": tone,
        "content": content
    })


# Analysis Tools
@mcp.tool(
    title="Analyze Results",
    description="Analyze research results and provide insights"
)
def analyze_results() -> str:
    """Analyze research results and provide insights"""
    global engine

    if not engine.results:
        return json.dumps({"status": "error", "message": "No results to analyze"})

    analysis = {
        "total_results": len(engine.results),
        "avg_relevance": sum(r.relevance_score for r in engine.results) / len(engine.results),
        "source_distribution": {},
        "avg_word_count": 0,
        "top_topics": [],
        "quality_score": 0.0
    }

    # Source distribution
    for result in engine.results:
        source = result.source_type
        analysis["source_distribution"][source] = analysis["source_distribution"].get(source, 0) + 1

    # Average word count
    total_words = sum(result.metadata.get("word_count", 0) for result in engine.results)
    analysis["avg_word_count"] = total_words // len(engine.results) if engine.results else 0

    # Aggregate topics
    topic_freq = {}
    for result in engine.results:
        for topic, freq in result.metadata.get("key_topics", [])[:5]:
            topic_freq[topic] = topic_freq.get(topic, 0) + freq

    analysis["top_topics"] = sorted(topic_freq.items(), key=lambda x: x[1], reverse=True)[:10]

    # Quality score
    relevance_score = analysis["avg_relevance"]
    diversity_score = len(analysis["source_distribution"]) / 5.0  # Max 5 source types
    quantity_score = min(1.0, len(engine.results) / 20.0)

    analysis["quality_score"] = (relevance_score * 0.5 + diversity_score * 0.3 + quantity_score * 0.2)

    return json.dumps(analysis, indent=2)


@mcp.tool(
    title="Get Statistics",
    description="Get detailed statistics about the research session"
)
def get_statistics() -> str:
    """Get detailed statistics"""
    global engine

    stats = engine.get_stats()
    stats["current_results"] = len(engine.results)

    if engine.parameters:
        stats["current_query"] = engine.parameters.query
        stats["current_settings"] = {
            "depth": engine.parameters.depth,
            "max_results": engine.parameters.max_results,
            "relevance_threshold": engine.parameters.relevance_threshold
        }

    return json.dumps(stats, indent=2)


# Search Tools
@mcp.tool(
    title="Search Results",
    description="Search within collected research results"
)
def search_results(
    query: str = Field(description="Search query"),
    min_relevance: float = Field(default=0.0, description="Minimum relevance score")
) -> str:
    """Search within collected results"""
    global engine

    if not engine.results:
        return json.dumps({"status": "error", "message": "No results to search"})

    query_lower = query.lower()
    matches = []

    for result in engine.results:
        if result.relevance_score < min_relevance:
            continue

        # Search in title, summary, and content
        if (query_lower in result.title.lower() or
            query_lower in result.summary.lower() or
            query_lower in result.content.lower()):
            matches.append(result.to_dict())

    return json.dumps({
        "status": "success",
        "query": query,
        "matches": len(matches),
        "results": matches
    }, indent=2)


# Configuration Tools
@mcp.tool(
    title="Save Configuration",
    description="Save current research configuration"
)
def save_configuration(
    name: str = Field(description="Configuration name"),
    description: str = Field(default="", description="Configuration description")
) -> str:
    """Save current configuration"""
    global engine

    if not engine.parameters:
        return json.dumps({"status": "error", "message": "No active configuration"})

    config = {
        "name": name,
        "description": description,
        "parameters": {
            "query": engine.parameters.query,
            "source_type": engine.parameters.source_type,
            "depth": engine.parameters.depth,
            "max_results": engine.parameters.max_results,
            "relevance_threshold": engine.parameters.relevance_threshold,
            "detail_level": engine.parameters.detail_level,
            "output_format": engine.parameters.output_format,
            "summary_length": engine.parameters.summary_length
        }
    }

    config_dir = Path("configs")
    config_dir.mkdir(exist_ok=True)

    config_file = config_dir / f"{name}.json"
    config_file.write_text(json.dumps(config, indent=2))

    return json.dumps({
        "status": "success",
        "message": f"Configuration saved as {name}",
        "path": str(config_file.absolute())
    })


@mcp.tool(
    title="Load Configuration",
    description="Load a saved research configuration"
)
def load_configuration(
    name: str = Field(description="Configuration name")
) -> str:
    """Load a saved configuration"""
    config_file = Path("configs") / f"{name}.json"

    if not config_file.exists():
        return json.dumps({"status": "error", "message": f"Configuration {name} not found"})

    try:
        config = json.loads(config_file.read_text())
        return json.dumps({
            "status": "success",
            "message": f"Configuration {name} loaded",
            "config": config
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Failed to load: {str(e)}"})


# Asset Generation Tools
@mcp.tool(
    title="Generate YouTube Assets",
    description="Generate assets for YouTube content creation"
)
def generate_youtube_assets(
    topic: str = Field(description="Video topic or subject"),
    asset_type: str = Field(description="Asset type: video_script, thumbnail_template, video_description, tags"),
    duration: str = Field(default="10min", description="Video duration (for scripts)"),
    style: str = Field(default="educational", description="Style: educational, entertainment, tutorial, review"),
    category: str = Field(default="education", description="Category for tags")
) -> str:
    """Generate YouTube content assets"""
    global asset_manager

    try:
        if asset_type == "video_script":
            result = asset_manager.youtube.generate_video_script(topic, duration, style)
        elif asset_type == "thumbnail_template":
            result = asset_manager.youtube.generate_thumbnail_template(topic, style)
        elif asset_type == "video_description":
            script = asset_manager.youtube.generate_video_script(topic, duration, style)
            result = asset_manager.youtube.generate_video_description(topic, script)
        elif asset_type == "tags":
            result = asset_manager.youtube.generate_tags(topic, category)
        else:
            return json.dumps({"error": f"Unknown asset type: {asset_type}"})

        return json.dumps({
            "status": "success",
            "platform": "youtube",
            "asset_type": asset_type,
            "topic": topic,
            "result": result
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Generate Gumroad Product Listing",
    description="Generate complete product listing for Gumroad"
)
def generate_gumroad_listing(
    product_name: str = Field(description="Name of the product"),
    product_type: str = Field(default="ebook", description="Product type: ebook, template, course, bundle")
) -> str:
    """Generate Gumroad product listing"""
    global asset_manager

    try:
        result = asset_manager.gumroad.generate_product_listing(product_name, product_type)
        return json.dumps({
            "status": "success",
            "platform": "gumroad",
            "product_name": product_name,
            "listing": result
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Generate Etsy Product Listing",
    description="Generate optimized product listing for Etsy"
)
def generate_etsy_listing(
    product_name: str = Field(description="Name of the product"),
    category: str = Field(default="digital", description="Category: digital, art, planner, wedding, craft, etc.")
) -> str:
    """Generate Etsy product listing"""
    global asset_manager

    try:
        result = asset_manager.etsy.generate_product_listing(product_name, category)
        return json.dumps({
            "status": "success",
            "platform": "etsy",
            "product_name": product_name,
            "listing": result
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Generate Website Assets",
    description="Generate website components and content"
)
def generate_web_assets(
    product_name: str = Field(description="Product or website name"),
    asset_type: str = Field(description="Asset type: landing_page, blog_post_template"),
    purpose: str = Field(default="sales", description="Purpose: sales, portfolio, blog"),
    topic: str = Field(default="", description="Blog post topic (if applicable)")
) -> str:
    """Generate website assets"""
    global asset_manager

    try:
        if asset_type == "landing_page":
            result = asset_manager.web.generate_landing_page(product_name, purpose)
        elif asset_type == "blog_post_template":
            blog_topic = topic or product_name
            result = asset_manager.web.generate_blog_post_template(blog_topic)
        else:
            return json.dumps({"error": f"Unknown asset type: {asset_type}"})

        return json.dumps({
            "status": "success",
            "platform": "web",
            "asset_type": asset_type,
            "result": result
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Generate Game Design Document",
    description="Generate game design documentation and assets"
)
def generate_game_assets(
    game_name: str = Field(description="Name of the game"),
    genre: str = Field(default="action", description="Game genre: action, puzzle, rpg, strategy, etc.")
) -> str:
    """Generate game design document"""
    global asset_manager

    try:
        result = asset_manager.game.generate_game_design_document(game_name, genre)
        return json.dumps({
            "status": "success",
            "platform": "game",
            "game_name": game_name,
            "genre": genre,
            "design_document": result
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Generate Canva Template Specs",
    description="Generate Canva template specifications and design guides"
)
def generate_canva_specs(
    template_type: str = Field(default="social", description="Template type: social, marketing, presentation")
) -> str:
    """Generate Canva template specifications"""
    global asset_manager

    try:
        result = asset_manager.canva.generate_template_specs(template_type)
        return json.dumps({
            "status": "success",
            "platform": "canva",
            "template_type": template_type,
            "specifications": result
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="List Available Platforms",
    description="Get list of all supported asset generation platforms"
)
def list_platforms() -> str:
    """List all available platforms"""
    global asset_manager

    platforms = asset_manager.get_available_platforms()
    platform_info = {}

    for platform in platforms:
        asset_types = asset_manager.get_asset_types(platform)
        platform_info[platform] = {
            "available_asset_types": asset_types,
            "description": f"Asset generation for {platform.title()}"
        }

    return json.dumps({
        "status": "success",
        "platforms": platform_info
    }, indent=2)


@mcp.tool(
    title="Generate Multi-Platform Package",
    description="Generate a complete asset package for launching on multiple platforms"
)
def generate_multi_platform_package(
    project_name: str = Field(description="Name of the project/product"),
    platforms: str = Field(description="Comma-separated list of platforms: youtube,gumroad,etsy,web"),
    save_to_file: bool = Field(default=False, description="Save results to file")
) -> str:
    """Generate assets for multiple platforms at once"""
    global asset_manager

    try:
        platform_list = [p.strip().lower() for p in platforms.split(",")]
        results = {}

        for platform in platform_list:
            if platform == "youtube":
                results["youtube"] = {
                    "script": asset_manager.youtube.generate_video_script(project_name, "10min", "educational"),
                    "thumbnail": asset_manager.youtube.generate_thumbnail_template(project_name),
                    "tags": asset_manager.youtube.generate_tags(project_name)
                }
            elif platform == "gumroad":
                results["gumroad"] = asset_manager.gumroad.generate_product_listing(project_name, "ebook")
            elif platform == "etsy":
                results["etsy"] = asset_manager.etsy.generate_product_listing(project_name, "digital")
            elif platform == "web":
                results["web"] = {
                    "landing_page": asset_manager.web.generate_landing_page(project_name, "sales"),
                    "blog_post": asset_manager.web.generate_blog_post_template(project_name)
                }
            elif platform == "game":
                results["game"] = asset_manager.game.generate_game_design_document(project_name, "action")
            elif platform == "canva":
                results["canva"] = asset_manager.canva.generate_template_specs("social")

        if save_to_file:
            output_dir = Path("generated_assets")
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / f"{project_name.replace(' ', '_')}_assets.json"
            output_file.write_text(json.dumps(results, indent=2))

            return json.dumps({
                "status": "success",
                "message": "Multi-platform package generated",
                "project_name": project_name,
                "platforms": platform_list,
                "saved_to": str(output_file.absolute()),
                "results": results
            }, indent=2)

        return json.dumps({
            "status": "success",
            "message": "Multi-platform package generated",
            "project_name": project_name,
            "platforms": platform_list,
            "results": results
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


# Social Media Asset Tools
@mcp.tool(
    title="Generate Instagram Assets",
    description="Generate Instagram content (posts, stories, reels, carousels)"
)
def generate_instagram_assets(
    topic: str = Field(description="Post topic or subject"),
    post_type: str = Field(default="feed", description="Post type: feed, story, reel, carousel")
) -> str:
    """Generate Instagram content"""
    global asset_manager

    try:
        result = asset_manager.social.generate_instagram_post(topic, post_type)
        return json.dumps({
            "status": "success",
            "platform": "instagram",
            "post_type": post_type,
            "topic": topic,
            "result": result
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Generate TikTok Video Script",
    description="Generate TikTok video script and specifications"
)
def generate_tiktok_script(
    topic: str = Field(description="Video topic"),
    style: str = Field(default="educational", description="Style: educational, entertainment, tutorial")
) -> str:
    """Generate TikTok video content"""
    global asset_manager

    try:
        result = asset_manager.social.generate_tiktok_video(topic, style)
        return json.dumps({
            "status": "success",
            "platform": "tiktok",
            "topic": topic,
            "style": style,
            "result": result
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Generate Twitter Thread",
    description="Generate Twitter/X thread with engagement tactics"
)
def generate_twitter_thread(
    topic: str = Field(description="Thread topic")
) -> str:
    """Generate Twitter thread"""
    global asset_manager

    try:
        result = asset_manager.social.generate_twitter_thread(topic)
        return json.dumps({
            "status": "success",
            "platform": "twitter",
            "topic": topic,
            "result": result
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Generate LinkedIn Post",
    description="Generate LinkedIn professional content"
)
def generate_linkedin_post(
    topic: str = Field(description="Post topic"),
    post_type: str = Field(default="professional", description="Type: professional, storytelling, listicle")
) -> str:
    """Generate LinkedIn post"""
    global asset_manager

    try:
        result = asset_manager.social.generate_linkedin_post(topic, post_type)
        return json.dumps({
            "status": "success",
            "platform": "linkedin",
            "topic": topic,
            "post_type": post_type,
            "result": result
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Generate Pinterest Pin",
    description="Generate Pinterest pin design and SEO specs"
)
def generate_pinterest_pin(
    topic: str = Field(description="Pin topic"),
    pin_type: str = Field(default="infographic", description="Pin type: infographic, how_to, product, quote")
) -> str:
    """Generate Pinterest pin specifications"""
    global asset_manager

    try:
        result = asset_manager.social.generate_pinterest_pin(topic, pin_type)
        return json.dumps({
            "status": "success",
            "platform": "pinterest",
            "topic": topic,
            "pin_type": pin_type,
            "result": result
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Generate Social Media Campaign",
    description="Generate complete social media campaign across multiple platforms"
)
def generate_social_campaign(
    topic: str = Field(description="Campaign topic"),
    platforms: str = Field(default="instagram,tiktok,twitter", description="Comma-separated platforms"),
    save_to_file: bool = Field(default=False, description="Save results to file")
) -> str:
    """Generate multi-platform social media campaign"""
    global asset_manager

    try:
        platform_list = [p.strip().lower() for p in platforms.split(",")]
        campaign = {
            "topic": topic,
            "platforms": {}
        }

        for platform in platform_list:
            if platform == "instagram":
                campaign["platforms"]["instagram"] = {
                    "feed_post": asset_manager.social.generate_instagram_post(topic, "feed"),
                    "story": asset_manager.social.generate_instagram_post(topic, "story"),
                    "reel": asset_manager.social.generate_instagram_post(topic, "reel")
                }
            elif platform == "tiktok":
                campaign["platforms"]["tiktok"] = asset_manager.social.generate_tiktok_video(topic, "educational")
            elif platform == "twitter":
                campaign["platforms"]["twitter"] = asset_manager.social.generate_twitter_thread(topic)
            elif platform == "linkedin":
                campaign["platforms"]["linkedin"] = asset_manager.social.generate_linkedin_post(topic, "professional")
            elif platform == "pinterest":
                campaign["platforms"]["pinterest"] = asset_manager.social.generate_pinterest_pin(topic, "infographic")

        if save_to_file:
            output_dir = Path("social_campaigns")
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / f"{topic.replace(' ', '_')}_campaign.json"
            output_file.write_text(json.dumps(campaign, indent=2))

            return json.dumps({
                "status": "success",
                "message": "Social media campaign generated",
                "topic": topic,
                "platforms": platform_list,
                "saved_to": str(output_file.absolute()),
                "campaign": campaign
            }, indent=2)

        return json.dumps({
            "status": "success",
            "message": "Social media campaign generated",
            "topic": topic,
            "platforms": platform_list,
            "campaign": campaign
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


# Audio Content Tools
@mcp.tool(
    title="Generate Beat/Music Specifications",
    description="Generate professional beat and music production specs"
)
def generate_beat_specs(
    genre: str = Field(default="hiphop", description="Music genre: hiphop, trap, edm, pop, lofi, drill, afrobeat, reggaeton"),
    mood: str = Field(default="energetic", description="Mood: energetic, chill, dark, happy, melancholic, aggressive")
) -> str:
    """Generate beat and music specifications"""
    global asset_manager

    try:
        result = asset_manager.audio.generate_beat_specs(genre, mood)
        return json.dumps({
            "status": "success",
            "platform": "audio/music",
            "genre": genre,
            "mood": mood,
            "result": result
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Generate Voiceover Script",
    description="Generate voiceover script with professional specifications"
)
def generate_voiceover_script(
    content_type: str = Field(default="commercial", description="Type: commercial, explainer, tutorial, podcast_intro, audiobook"),
    duration: int = Field(default=30, description="Duration in seconds")
) -> str:
    """Generate voiceover script and technical specs"""
    global asset_manager

    try:
        result = asset_manager.audio.generate_voiceover_script(content_type, duration)
        return json.dumps({
            "status": "success",
            "platform": "audio/voiceover",
            "content_type": content_type,
            "duration": duration,
            "result": result
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Generate Podcast Assets",
    description="Generate complete podcast production package"
)
def generate_podcast_assets(
    podcast_name: str = Field(description="Name of the podcast"),
    episode_topic: str = Field(description="Episode topic or title")
) -> str:
    """Generate podcast intro, outro, and production specs"""
    global asset_manager

    try:
        result = asset_manager.audio.generate_podcast_assets(podcast_name, episode_topic)
        return json.dumps({
            "status": "success",
            "platform": "podcast",
            "podcast_name": podcast_name,
            "episode_topic": episode_topic,
            "result": result
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Generate Audio Advertisement",
    description="Generate audio ad script for radio/podcast"
)
def generate_audio_ad(
    product: str = Field(description="Product or service name"),
    duration: int = Field(default=30, description="Duration: 15, 30, or 60 seconds")
) -> str:
    """Generate audio advertisement script"""
    global asset_manager

    try:
        result = asset_manager.audio.generate_audio_ad_script(product, duration)
        return json.dumps({
            "status": "success",
            "platform": "audio/advertising",
            "product": product,
            "duration": duration,
            "result": result
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


# Intelligence Engine Tools
@mcp.tool(
    title="Semantic Search",
    description="Perform semantic search using TF-IDF and cosine similarity"
)
def semantic_search(
    query: str = Field(description="Search query"),
    top_k: int = Field(default=10, description="Number of results to return")
) -> str:
    """Semantic search across research results"""
    global engine, intelligence_engine

    if not engine.results:
        return json.dumps({"status": "error", "message": "No research results available for search"})

    try:
        # Build documents from results
        documents = []
        for result in engine.results:
            doc = {
                "text": f"{result.title} {result.summary} {result.content}",
                "metadata": {
                    "title": result.title,
                    "url": result.url,
                    "relevance_score": result.relevance_score
                }
            }
            documents.append(doc)

        # Perform semantic search
        search_results = intelligence_engine.semantic_search(query, documents, top_k)

        return json.dumps({
            "status": "success",
            "query": query,
            "results_count": len(search_results),
            "results": search_results
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Score Source Credibility",
    description="Analyze and score the credibility of a source"
)
def score_source_credibility(
    url: str = Field(description="URL of the source to analyze"),
    title: str = Field(default="", description="Title of the source"),
    content: str = Field(default="", description="Content to analyze")
) -> str:
    """Score source credibility using multiple factors"""
    global intelligence_engine

    try:
        # Find matching result if content not provided
        if not content:
            global engine
            for result in engine.results:
                if result.url == url:
                    title = result.title
                    content = result.content
                    break

        if not content:
            return json.dumps({"status": "error", "message": "Source not found in results. Provide content parameter."})

        metadata = {"timestamp": ""}
        credibility_score = intelligence_engine.score_credibility(url, title, content, metadata)

        return json.dumps({
            "status": "success",
            "url": url,
            "credibility": credibility_score
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Build Knowledge Graph",
    description="Generate a knowledge graph from research results"
)
def build_knowledge_graph() -> str:
    """Extract entities and relationships to build knowledge graph"""
    global engine, intelligence_engine

    if not engine.results:
        return json.dumps({"status": "error", "message": "No research results available"})

    try:
        # Prepare documents
        documents = []
        for result in engine.results:
            doc = {
                "title": result.title,
                "content": result.content,
                "url": result.url
            }
            documents.append(doc)

        # Build knowledge graph
        knowledge_graph = intelligence_engine.build_knowledge_graph(documents)

        return json.dumps({
            "status": "success",
            "knowledge_graph": knowledge_graph
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Expand Query",
    description="Generate query expansions and related search suggestions"
)
def expand_query(
    query: str = Field(description="Query to expand"),
    use_results: bool = Field(default=False, description="Use research results for context")
) -> str:
    """Expand query with synonyms and generate related searches"""
    global engine, intelligence_engine

    try:
        results_context = []
        if use_results and engine.results:
            results_context = [
                {"title": r.title, "content": r.summary}
                for r in engine.results[:10]
            ]

        expansion = intelligence_engine.expand_query(query, results_context)

        return json.dumps({
            "status": "success",
            "original_query": query,
            "expansion": expansion
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Save Research Session",
    description="Save current research session to database"
)
def save_research_session(
    session_name: str = Field(description="Name for this research session")
) -> str:
    """Save research session with all results"""
    global engine, intelligence_engine

    if not engine.results or not engine.parameters:
        return json.dumps({"status": "error", "message": "No active research session to save"})

    try:
        session_id = intelligence_engine.save_session(
            session_name,
            engine.parameters.query,
            [r.to_dict() for r in engine.results]
        )

        return json.dumps({
            "status": "success",
            "message": f"Session saved as '{session_name}'",
            "session_id": session_id
        })

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="List Research Sessions",
    description="List all saved research sessions"
)
def list_research_sessions() -> str:
    """List all saved sessions"""
    global intelligence_engine

    try:
        sessions = intelligence_engine.list_sessions()

        return json.dumps({
            "status": "success",
            "sessions_count": len(sessions),
            "sessions": sessions
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Load Research Session",
    description="Load a previously saved research session"
)
def load_research_session(
    session_id: str = Field(description="Session ID to load")
) -> str:
    """Load saved research session"""
    global intelligence_engine

    try:
        session = intelligence_engine.get_session(session_id)

        if not session:
            return json.dumps({"status": "error", "message": f"Session {session_id} not found"})

        return json.dumps({
            "status": "success",
            "session": session
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


# OSINT Engine Tools
@mcp.tool(
    title="Analyze Social Network",
    description="Analyze social network connections and influence"
)
def analyze_social_network(
    entities: str = Field(description="JSON array of entities with connections"),
) -> str:
    """Analyze social network to find influential nodes and communities"""
    global osint_engine

    try:
        # Parse entities JSON
        entities_data = json.loads(entities)

        # Analyze network
        analysis = osint_engine.analyze_social_network(entities_data)

        return json.dumps({
            "status": "success",
            "network_analysis": analysis
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Track Digital Footprint",
    description="Track and analyze digital footprint across platforms"
)
def track_digital_footprint(
    entity_name: str = Field(description="Entity name to track"),
    footprints: str = Field(description="JSON array of digital footprints")
) -> str:
    """Analyze digital presence across multiple platforms"""
    global osint_engine

    try:
        # Parse footprints JSON
        footprints_data = json.loads(footprints)

        # Analyze footprint
        analysis = osint_engine.track_digital_footprint(entity_name, footprints_data)

        return json.dumps({
            "status": "success",
            "entity": entity_name,
            "footprint_analysis": analysis
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Analyze Timeline",
    description="Analyze timeline of events to detect patterns and clusters"
)
def analyze_timeline(
    events: str = Field(description="JSON array of events with timestamps")
) -> str:
    """Analyze timeline for clusters, patterns, and anomalies"""
    global osint_engine

    try:
        # Parse events JSON
        events_data = json.loads(events)

        # Analyze timeline
        analysis = osint_engine.analyze_timeline(events_data)

        return json.dumps({
            "status": "success",
            "timeline_analysis": analysis
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Analyze Sentiment Trends",
    description="Track sentiment trends over time and detect shifts"
)
def analyze_sentiment_trends(
    sentiment_data: str = Field(description="JSON array of sentiment data points")
) -> str:
    """Analyze sentiment trends and detect significant shifts"""
    global osint_engine

    try:
        # Parse sentiment data JSON
        data = json.loads(sentiment_data)

        # Analyze trends
        analysis = osint_engine.analyze_sentiment_trends(data)

        return json.dumps({
            "status": "success",
            "sentiment_analysis": analysis
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Extract Geospatial Intelligence",
    description="Extract and analyze location data from text"
)
def extract_geospatial_intelligence(
    text: str = Field(description="Text to analyze for locations"),
    use_research_results: bool = Field(default=False, description="Analyze all research results")
) -> str:
    """Extract locations and analyze geospatial patterns"""
    global engine, osint_engine

    try:
        if use_research_results and engine.results:
            # Analyze all research results
            all_text = " ".join([f"{r.title} {r.content}" for r in engine.results])
            analysis = osint_engine.extract_geospatial_intelligence(all_text)
        else:
            analysis = osint_engine.extract_geospatial_intelligence(text)

        return json.dumps({
            "status": "success",
            "geospatial_analysis": analysis
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Detect Patterns",
    description="Detect numerical patterns, trends, cycles, and anomalies"
)
def detect_patterns(
    data: str = Field(description="JSON array of numerical data points"),
    pattern_types: str = Field(default="all", description="Types: all, trends, cycles, anomalies")
) -> str:
    """Detect patterns in numerical data"""
    global osint_engine

    try:
        # Parse data JSON
        data_points = json.loads(data)

        # Detect patterns
        analysis = osint_engine.detect_numerical_patterns(data_points, pattern_types)

        return json.dumps({
            "status": "success",
            "pattern_analysis": analysis
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Get Intelligence Score",
    description="Calculate overall intelligence quality score for research"
)
def get_intelligence_score() -> str:
    """Calculate comprehensive intelligence score"""
    global engine, osint_engine

    if not engine.results:
        return json.dumps({"status": "error", "message": "No research results available"})

    try:
        results_data = [r.to_dict() for r in engine.results]
        score = osint_engine.get_intelligence_score(results_data)

        return json.dumps({
            "status": "success",
            "intelligence_score": score
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool(
    title="Comprehensive Intelligence Analysis",
    description="Run complete intelligence analysis on research results"
)
def comprehensive_intelligence_analysis() -> str:
    """Perform comprehensive intelligence and OSINT analysis"""
    global engine, intelligence_engine, osint_engine

    if not engine.results:
        return json.dumps({"status": "error", "message": "No research results available"})

    try:
        # Prepare data
        documents = [
            {
                "text": f"{r.title} {r.summary} {r.content}",
                "title": r.title,
                "content": r.content,
                "url": r.url,
                "metadata": r.metadata
            }
            for r in engine.results
        ]

        results_data = [r.to_dict() for r in engine.results]

        # Run comprehensive analysis
        analysis = {
            "semantic_insights": intelligence_engine.comprehensive_analysis(
                engine.parameters.query if engine.parameters else "",
                documents
            ),
            "osint_intelligence": osint_engine.comprehensive_analysis(results_data),
            "overall_quality": osint_engine.get_intelligence_score(results_data)
        }

        return json.dumps({
            "status": "success",
            "comprehensive_analysis": analysis
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


# Prompts
@mcp.prompt("research_prompt")
def research_prompt(
    topic: str = Field(description="Research topic"),
    focus: str = Field(default="general", description="Research focus area")
) -> str:
    """Generate a research prompt"""
    return f"""Please conduct comprehensive research on the following topic:

Topic: {topic}
Focus: {focus}

Instructions:
1. Gather information from multiple reliable sources
2. Analyze the relevance and quality of each source
3. Synthesize findings into a coherent overview
4. Identify key insights and trends
5. Provide citations and references

Please ensure the research is thorough, balanced, and well-documented."""


@mcp.prompt("content_prompt")
def content_prompt(
    content_type: str = Field(description="Type of content to create"),
    audience: str = Field(default="general", description="Target audience"),
    tone: str = Field(default="professional", description="Content tone")
) -> str:
    """Generate a content creation prompt"""
    return f"""Please create {content_type} content based on the research results.

Target Audience: {audience}
Tone: {tone}

Requirements:
1. Use findings from the research results
2. Structure the content appropriately for {content_type}
3. Maintain a {tone} tone throughout
4. Include relevant citations and references
5. Ensure clarity and coherence

Please create engaging, well-structured content that effectively communicates the research findings."""


if __name__ == "__main__":
    print("Starting Research & Content Gathering Server...")
    print("Server will be available at: http://127.0.0.1:8000/")
    print("\nTo access the web UI, open: http://127.0.0.1:8000/static/index.html")
    print("MCP endpoint: http://127.0.0.1:8000/mcp")
    mcp.run(transport="streamable-http")
