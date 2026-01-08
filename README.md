# Research & Content Gathering App

A powerful, full-featured research and content gathering application with live parameter adjustment capabilities. Built with Python and FastMCP, this app provides an intuitive web interface for conducting research, gathering content, and building structured outputs.

## Features

### Core Capabilities
- **Full Research Engine**: Advanced web scraping and content gathering
- **Live Parameter Adjustment**: Modify research parameters in real-time while tasks are running
- **Content Analysis**: Automatic relevance scoring, summarization, and topic extraction
- **Content Building**: Generate articles, reports, summaries, and presentations from research
- **Real-time Progress Tracking**: Monitor research progress with live updates
- **Multiple Output Formats**: Export as Markdown, HTML, JSON, or plain text
- **Configuration Management**: Save and load research configurations

### Multi-Platform Asset Generation
Generate professional assets for 11+ platforms:

**Video & Content Platforms:**
- **YouTube**: Video scripts, thumbnail templates, descriptions, SEO tags
- **TikTok**: Video scripts with hooks, hashtags, engagement tactics
- **Gumroad**: Product listings, pricing strategies, marketing copy
- **Etsy**: Optimized product listings, tags, descriptions, SEO

**Social Media Platforms:**
- **Instagram**: Feed posts, Stories, Reels, Carousels with full specs
- **Twitter/X**: Engaging threads, single tweets, timing strategies
- **LinkedIn**: Professional posts, storytelling, listicles
- **Pinterest**: Pin designs, SEO optimization, board strategies

**Development & Design:**
- **Websites**: Landing pages, blog posts, SEO elements, conversion optimization
- **Game Development**: Complete design documents, mechanics, story structures
- **Canva**: Template specifications, design guides, color palettes

**Campaign Tools:**
- **Multi-Platform Packages**: Complete product launch assets
- **Social Media Campaigns**: Cross-platform content strategies

### Web Interface Features
- Beautiful, responsive UI with gradient design
- Real-time parameter sliders (depth, max results, relevance threshold, detail level)
- Interactive tabs for Results, Statistics, Logs, and Content Builder
- Live progress bar and status indicators
- Activity logging with timestamps
- Statistics dashboard with quality metrics

### MCP Tools (30+ Available)

**Research Tools (14):**
1. **start_research** - Start research with customizable parameters
2. **get_research_status** - Check current task status and progress
3. **pause_research** - Pause running research tasks
4. **resume_research** - Resume paused tasks
5. **stop_research** - Stop current research
6. **update_parameters** - Live parameter updates while running
7. **get_results** - Retrieve results in various formats
8. **export_results** - Export to files
9. **build_content** - Generate structured content (articles, reports, etc.)
10. **analyze_results** - Get detailed analysis and insights
11. **get_statistics** - View session statistics
12. **search_results** - Search within collected results
13. **save_configuration** - Save research settings
14. **load_configuration** - Load saved settings

**Platform Asset Tools (14):**
15. **generate_youtube_assets** - Video scripts, thumbnails, descriptions, tags
16. **generate_gumroad_listing** - Product listings for Gumroad
17. **generate_etsy_listing** - Optimized Etsy product listings
18. **generate_web_assets** - Landing pages and blog templates
19. **generate_game_assets** - Game design documents
20. **generate_canva_specs** - Canva template specifications
21. **generate_instagram_assets** - Instagram posts, stories, reels, carousels
22. **generate_tiktok_script** - TikTok video scripts and specs
23. **generate_twitter_thread** - Twitter/X threads with engagement tactics
24. **generate_linkedin_post** - Professional LinkedIn content
25. **generate_pinterest_pin** - Pinterest pin designs and SEO
26. **generate_social_campaign** - Multi-platform social media campaigns
27. **list_platforms** - Show all supported platforms
28. **generate_multi_platform_package** - Complete product launch packages

**Prompts (2):**
29. **research_prompt** - Generate research prompts
30. **content_prompt** - Generate content creation prompts

## Installation

### Prerequisites
- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager

### Quick Start

Run the automated setup script:
```bash
./quickstart.sh
```

This will:
- Install Python and dependencies
- Create necessary directories
- Validate all files
- Show you how to get started

### Manual Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd RIDICULOUS
```

2. Install Python version and dependencies:
```bash
uv python install
uv sync --locked
```

3. Create directories:
```bash
mkdir -p configs generated_assets social_campaigns
```

## Usage

### Starting the Server

Run the server on port 3000:
```bash
uv run main.py
```

The server will start and display:
```
Starting Research & Content Gathering Server...
Web interface will be available at: http://127.0.0.1:3000/
To access the web UI, open: http://127.0.0.1:3000/static/index.html
```

### Using the Web Interface

1. Open your browser to `http://127.0.0.1:3000/static/index.html`
2. Enter your research topic in the query field
3. Adjust parameters using the live sliders:
   - **Depth Level** (1-10): How deep to research
   - **Max Results** (5-100): Maximum number of results
   - **Relevance Threshold** (0.0-1.0): Minimum quality score
   - **Content Detail** (1-10): Amount of content to extract
4. Select source type and output format
5. Click "Start Research" to begin
6. Adjust parameters in real-time while research runs
7. Use Pause/Resume/Stop controls as needed
8. View results in the Results tab
9. Check Statistics for insights
10. Build content from research in the Content Builder tab

### Using MCP Tools

You can also interact with the server programmatically through MCP tools:

```python
# Example: Start research via MCP tool
await start_research(
    query="Latest developments in AI",
    source_type="academic",
    depth=7,
    max_results=30,
    relevance_threshold=0.8,
    detail_level=6
)

# Update parameters while running
await update_parameters(
    depth=9,
    max_results=50
)

# Get results
results = await get_results(format="markdown")

# Build content
content = await build_content(
    content_type="article",
    tone="professional",
    output_file="research_article.md"
)

# Generate YouTube assets
youtube_script = await generate_youtube_assets(
    topic="AI Research Trends",
    asset_type="video_script",
    duration="15min",
    style="educational"
)

# Generate multi-platform package
package = await generate_multi_platform_package(
    project_name="My New Product",
    platforms="youtube,gumroad,etsy,web",
    save_to_file=True
)
```

### Generating Assets for Different Platforms

**YouTube Content Creation:**
```python
# Video script
script = await generate_youtube_assets(
    topic="How to Build a Web App",
    asset_type="video_script",
    style="tutorial"
)

# Thumbnail design specs
thumbnail = await generate_youtube_assets(
    topic="Web Development",
    asset_type="thumbnail_template",
    style="bold"
)

# SEO tags
tags = await generate_youtube_assets(
    topic="Web Development Tutorial",
    asset_type="tags",
    category="tech"
)
```

**Gumroad Product Launch:**
```python
listing = await generate_gumroad_listing(
    product_name="Ultimate Python Course",
    product_type="course"
)
```

**Etsy Shop:**
```python
product = await generate_etsy_listing(
    product_name="Digital Planner Template",
    category="planner"
)
```

**Website Development:**
```python
# Landing page
landing = await generate_web_assets(
    product_name="SaaS Product",
    asset_type="landing_page",
    purpose="sales"
)

# Blog post template
blog = await generate_web_assets(
    product_name="My Blog",
    asset_type="blog_post_template",
    topic="Getting Started with Python"
)
```

**Social Media Content:**
```python
# Instagram posts
instagram = await generate_instagram_assets(
    topic="Productivity Tips",
    post_type="reel"  # or "feed", "story", "carousel"
)

# TikTok videos
tiktok = await generate_tiktok_script(
    topic="Coding Tutorial",
    style="educational"  # or "entertainment", "tutorial"
)

# Twitter threads
twitter = await generate_twitter_thread(
    topic="AI Trends 2024"
)

# LinkedIn posts
linkedin = await generate_linkedin_post(
    topic="Career Growth",
    post_type="storytelling"  # or "professional", "listicle"
)

# Pinterest pins
pinterest = await generate_pinterest_pin(
    topic="Home Decor Ideas",
    pin_type="infographic"  # or "how_to", "product", "quote"
)

# Complete social campaign
campaign = await generate_social_campaign(
    topic="Product Launch",
    platforms="instagram,tiktok,twitter,linkedin,pinterest",
    save_to_file=True
)
```

**Game Development:**
```python
gdd = await generate_game_assets(
    game_name="Space Adventure",
    genre="action"
)
```

### Running Examples

Check out the example scripts:

```bash
# YouTube asset generation
python3 examples/youtube_example.py

# Social media campaign
python3 examples/social_campaign_example.py

# Complete product launch
python3 examples/product_launch_example.py
```

### Testing with MCP Inspector

1. Install Node.js (^22.7.5)
2. Run the inspector:
```bash
npx @modelcontextprotocol/inspector
```
3. Open `http://localhost:6274`
4. Configure:
   - Transport Type: Streamable HTTP
   - URL: http://127.0.0.1:3000/mcp

## Project Structure

```
RIDICULOUS/
├── main.py                  # MCP server with 30+ tools
├── research_engine.py       # Core research engine
├── asset_generator.py       # Multi-platform asset generators
├── quickstart.sh            # Quick setup script
├── static/
│   └── index.html          # Web interface
├── examples/                # Example usage scripts
│   ├── youtube_example.py
│   ├── social_campaign_example.py
│   └── product_launch_example.py
├── configs/                 # Saved configurations (auto-created)
├── generated_assets/        # Generated assets (auto-created)
├── social_campaigns/        # Social campaigns (auto-created)
├── pyproject.toml          # Dependencies
├── uv.lock                 # Lock file
└── README.md               # This file
```

## Research Parameters

### Query Options
- **query**: Research topic (required)
- **source_type**: all, academic, news, technical, social
- **depth**: Research depth level (1-10)
- **max_results**: Maximum results to gather (5-100)
- **relevance_threshold**: Minimum quality score (0.0-1.0)
- **detail_level**: Content extraction detail (1-10)
- **output_format**: markdown, html, json, text
- **summary_length**: brief, moderate, detailed

## Content Building Options

Build different types of content from research:
- **Article**: Structured article with introduction and conclusions
- **Report**: Formal research report with executive summary
- **Summary**: Brief executive summary of findings
- **Presentation**: Slide-formatted content

### Tone Options
- Professional
- Academic
- Casual
- Technical

## Statistics & Analytics

The app tracks comprehensive statistics:
- Total queries performed
- Total results gathered
- Average relevance score
- Processing time
- Sources analyzed
- Error count
- Quality score (composite metric)
- Topic distribution
- Source type distribution

## Live Parameter Adjustment

One of the key features is the ability to adjust parameters while research is running:

1. Start a research task
2. Move sliders in the sidebar
3. Parameters update automatically
4. Research adapts to new settings in real-time

This allows you to:
- Increase depth if initial results are shallow
- Raise/lower relevance threshold to filter results
- Adjust max results to gather more or less data
- Change detail level for more/less content

## Export & Sharing

Export research results in multiple formats:
- **Markdown**: Perfect for documentation
- **HTML**: Ready for web publishing
- **JSON**: For programmatic processing
- **Text**: Simple plain text format

Save configurations for reuse:
```python
# Save current settings
await save_configuration(
    name="ai_research_config",
    description="Settings for AI research tasks"
)

# Load later
config = await load_configuration(name="ai_research_config")
```

## Development

### Adding Custom Search Providers

Edit `research_engine.py` to add real search integrations:

```python
async def search_web(self, query: str, max_results: int = 10):
    # Add integrations with:
    # - Google Custom Search API
    # - Bing Search API
    # - DuckDuckGo
    # - Academic databases (arXiv, PubMed, etc.)
    # - News APIs
    pass
```

### Extending Content Builders

Add new content types in `research_engine.py`:

```python
class ContentBuilder:
    def build_whitepaper(self, tone: str = "technical") -> str:
        # Your custom content builder
        pass
```

Then register in `main.py`:

```python
elif content_type == "whitepaper":
    content = builder.build_whitepaper(tone)
```

### Custom Analysis Tools

Add specialized analysis in the research engine:

```python
def analyze_sentiment(self, text: str) -> Dict[str, Any]:
    # Custom sentiment analysis
    pass

def extract_entities(self, text: str) -> List[str]:
    # Named entity recognition
    pass
```

## Architecture

### Research Engine
- Asynchronous research execution
- Parallel content fetching
- Real-time parameter updates
- Pause/resume capability
- Progress tracking

### Content Processing
1. Web search and URL discovery
2. Content fetching (with timeout handling)
3. HTML parsing and text extraction
4. Relevance scoring
5. Summarization
6. Topic analysis
7. Quality metrics

### MCP Integration
- FastMCP server with streamable HTTP transport
- 15+ tools for comprehensive research control
- Resource serving for web interface
- Prompt templates for research and content generation

## Performance

The app is designed for efficiency:
- Asynchronous I/O for parallel processing
- Smart throttling to avoid rate limits
- Configurable timeouts
- Progress tracking without blocking
- Memory-efficient result storage

## Limitations & Future Enhancements

Current limitations:
- Web search uses placeholder (requires API integration)
- Basic text extraction (can be enhanced with ML models)
- Simple relevance scoring (can use embeddings/semantic search)

Planned enhancements:
- Integration with real search APIs
- Advanced NLP for better summarization
- Semantic similarity scoring
- Citation network analysis
- Multi-language support
- Database storage for large result sets
- WebSocket for true real-time updates
- Collaborative research sessions

## Troubleshooting

### Port already in use
```bash
# Find process using port 3000
lsof -i :3000
# Kill it or use a different port in main.py
```

### Dependencies issues
```bash
# Reinstall dependencies
uv sync --locked --reinstall
```

### Web interface not loading
- Check that static/index.html exists
- Ensure server is running on port 3000
- Try accessing http://127.0.0.1:3000 directly

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review MCP documentation at https://modelcontextprotocol.io

## Credits

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [aiohttp](https://docs.aiohttp.org/) - Async HTTP client
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- [Python Markdown](https://python-markdown.github.io/) - Markdown processing

---

**Happy Researching!** 🔬📚✨
