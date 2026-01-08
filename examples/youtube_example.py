"""
Example: Generate YouTube Video Assets
Demonstrates how to create complete YouTube video content package
"""

import asyncio
import json
from pathlib import Path

# Simulate MCP tool calls
async def generate_youtube_package(topic: str):
    """Generate complete YouTube video package"""

    print(f"🎬 Generating YouTube Assets for: {topic}\n")

    # Simulate generating different assets
    assets = {
        "script": {
            "title": f"Complete Guide to {topic}",
            "hook": f"In this video, we'll explore everything you need to know about {topic}",
            "introduction": f"Welcome! Today we're diving into {topic}...",
            "main_points": [
                f"What is {topic} and why it matters",
                "Key concepts and fundamentals",
                "Practical applications",
                "Pro tips and best practices"
            ]
        },
        "thumbnail": {
            "text": topic.upper(),
            "style": "bold",
            "dimensions": "1280x720",
            "color_scheme": {
                "primary": "#FF0000",
                "secondary": "#FFFF00",
                "background": "#000000"
            }
        },
        "description": f"Learn all about {topic} in this comprehensive guide!",
        "tags": [topic.lower(), f"{topic} tutorial", "how to", "guide"]
    }

    # Save to file
    output_dir = Path("examples/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"youtube_{topic.replace(' ', '_')}.json"
    output_file.write_text(json.dumps(assets, indent=2))

    print(f"✅ Script generated")
    print(f"✅ Thumbnail specs created")
    print(f"✅ Description optimized")
    print(f"✅ Tags generated\n")
    print(f"📁 Saved to: {output_file}\n")

    return assets


async def main():
    """Run the example"""
    topics = [
        "Python Programming",
        "Digital Marketing",
        "Content Creation"
    ]

    print("=" * 60)
    print("YouTube Asset Generation Example")
    print("=" * 60 + "\n")

    for topic in topics:
        await generate_youtube_package(topic)
        print("-" * 60 + "\n")

    print("✨ All packages generated successfully!")
    print("\nNext steps:")
    print("1. Review the generated assets in examples/output/")
    print("2. Customize the content for your needs")
    print("3. Use the scripts for your YouTube videos!")


if __name__ == "__main__":
    asyncio.run(main())
