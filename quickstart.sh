#!/bin/bash

# Research & Content Gathering App - Quick Start Script

echo "=================================="
echo "Research & Content Gathering App"
echo "Quick Start Setup"
echo "=================================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed!"
    echo "📥 Please install uv first: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

echo "✅ uv found"
echo ""

# Install Python and dependencies
echo "📦 Installing Python and dependencies..."
uv python install
uv sync --locked

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"
echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p configs
mkdir -p generated_assets
mkdir -p social_campaigns
mkdir -p examples/output
echo "✅ Directories created"
echo ""

# Test syntax
echo "🔍 Testing Python files..."
python3 -m py_compile main.py research_engine.py asset_generator.py

if [ $? -ne 0 ]; then
    echo "❌ Syntax errors found"
    exit 1
fi

echo "✅ All files valid"
echo ""

echo "=================================="
echo "✨ Setup Complete!"
echo "=================================="
echo ""
echo "🚀 To start the server:"
echo "   uv run main.py"
echo ""
echo "🌐 Then access:"
echo "   Web UI: http://127.0.0.1:3000/static/index.html"
echo "   MCP Server: http://127.0.0.1:3000/mcp"
echo ""
echo "📚 Run examples:"
echo "   python3 examples/youtube_example.py"
echo "   python3 examples/social_campaign_example.py"
echo "   python3 examples/product_launch_example.py"
echo ""
echo "🎯 Available Features:"
echo "   • Research & content gathering with live parameter adjustment"
echo "   • Multi-platform asset generation (11+ platforms)"
echo "   • Social media campaign creation"
echo "   • Product launch packages"
echo "   • 30+ MCP tools"
echo ""
echo "Happy creating! 🎨"
