"""
Example: Generate Social Media Campaign
Creates content for Instagram, TikTok, Twitter, LinkedIn, and Pinterest
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime


async def generate_social_campaign(topic: str, platforms: list):
    """Generate multi-platform social media campaign"""

    print(f"📱 Creating Social Media Campaign for: {topic}")
    print(f"📍 Platforms: {', '.join(platforms)}\n")

    campaign = {
        "topic": topic,
        "created_at": datetime.now().isoformat(),
        "platforms": {}
    }

    for platform in platforms:
        print(f"  ⚙️  Generating {platform} content...")

        if platform == "instagram":
            campaign["platforms"]["instagram"] = {
                "feed_post": {
                    "caption": f"✨ {topic} ✨\n\nEverything you need to know!\n\n#" + topic.replace(' ', ''),
                    "hashtags": ["#instagood", "#viral", "#trending"]
                },
                "story": {
                    "text": f"Quick tip about {topic}!",
                    "dimensions": "1080x1920px"
                },
                "reel": {
                    "hook": f"3 things about {topic}",
                    "duration": "30 seconds"
                }
            }

        elif platform == "tiktok":
            campaign["platforms"]["tiktok"] = {
                "script": {
                    "hook": f"Wait until you hear about {topic}...",
                    "content": "Mind-blowing insights coming up!",
                    "cta": "Follow for more!"
                },
                "hashtags": ["#fyp", "#viral", "#learnontiktok"]
            }

        elif platform == "twitter":
            campaign["platforms"]["twitter"] = {
                "thread": [
                    f"🧵 Let's talk about {topic}",
                    f"1/ What is {topic}? Here's what you need to know...",
                    f"2/ Why {topic} matters in 2024",
                    "3/ That's it! Like/RT if helpful"
                ]
            }

        elif platform == "linkedin":
            campaign["platforms"]["linkedin"] = {
                "post": f"Thoughts on {topic}:\n\nHere's what I've learned...",
                "hashtags": ["#ProfessionalDevelopment", "#Industry"]
            }

        elif platform == "pinterest":
            campaign["platforms"]["pinterest"] = {
                "title": f"Ultimate Guide to {topic}",
                "description": f"Discover everything about {topic}!",
                "dimensions": "1000x1500px"
            }

    # Save campaign
    output_dir = Path("examples/output/campaigns")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{topic.replace(' ', '_')}_campaign.json"
    output_file.write_text(json.dumps(campaign, indent=2))

    print(f"\n✅ Campaign generated for {len(platforms)} platforms")
    print(f"📁 Saved to: {output_file}\n")

    return campaign


async def main():
    """Run the example"""
    campaigns = [
        {
            "topic": "AI and Machine Learning",
            "platforms": ["instagram", "tiktok", "twitter", "linkedin"]
        },
        {
            "topic": "Sustainable Living",
            "platforms": ["instagram", "pinterest", "twitter"]
        },
        {
            "topic": "Productivity Hacks",
            "platforms": ["linkedin", "twitter", "instagram", "tiktok", "pinterest"]
        }
    ]

    print("=" * 70)
    print("Social Media Campaign Generator")
    print("=" * 70 + "\n")

    for campaign_config in campaigns:
        await generate_social_campaign(
            campaign_config["topic"],
            campaign_config["platforms"]
        )
        print("-" * 70 + "\n")

    print("✨ All campaigns generated successfully!")
    print("\nWhat you got:")
    print("  • Instagram: Feed posts, Stories, Reels")
    print("  • TikTok: Video scripts with hooks")
    print("  • Twitter: Engaging threads")
    print("  • LinkedIn: Professional posts")
    print("  • Pinterest: Pin designs and SEO")
    print("\nNext steps:")
    print("1. Review campaigns in examples/output/campaigns/")
    print("2. Customize content for your brand voice")
    print("3. Schedule posts across platforms")
    print("4. Track engagement and optimize!")


if __name__ == "__main__":
    asyncio.run(main())
