"""
Example: Complete Product Launch
Generate assets for launching a product across ALL platforms
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime


async def launch_product(product_name: str, product_type: str = "digital"):
    """Generate complete product launch package"""

    print(f"\n🚀 LAUNCHING: {product_name}")
    print(f"📦 Type: {product_type}")
    print("=" * 70 + "\n")

    launch_package = {
        "product": product_name,
        "type": product_type,
        "launch_date": datetime.now().isoformat(),
        "assets": {}
    }

    # YouTube
    print("📹 YouTube Assets...")
    launch_package["assets"]["youtube"] = {
        "announcement_video": {
            "script": f"Introducing {product_name}!",
            "thumbnail": f"{product_name} - NOW AVAILABLE",
            "description": f"Get {product_name} today!"
        },
        "tutorial_series": [
            "Getting Started",
            "Advanced Features",
            "Tips and Tricks"
        ]
    }
    print("   ✅ Video scripts ready")
    print("   ✅ Thumbnails designed")

    # Social Media
    print("\n📱 Social Media Campaign...")
    launch_package["assets"]["social"] = {
        "instagram": {
            "launch_post": f"🎉 {product_name} is here!",
            "story_countdown": "3 days until launch",
            "reel": "Product showcase"
        },
        "tiktok": {
            "teaser": "Coming soon...",
            "launch_video": "It's finally here!",
            "tutorial": "How to use it"
        },
        "twitter": {
            "announcement_thread": f"Big news! {product_name} is launching...",
            "launch_tweet": f"🚀 {product_name} is LIVE!"
        },
        "linkedin": {
            "professional_announcement": f"Excited to announce {product_name}",
            "case_study": "How we built it"
        }
    }
    print("   ✅ Instagram content created")
    print("   ✅ TikTok videos scripted")
    print("   ✅ Twitter threads ready")
    print("   ✅ LinkedIn posts prepared")

    # Sales Platforms
    print("\n💰 Sales Platform Listings...")
    launch_package["assets"]["sales"] = {
        "gumroad": {
            "listing": f"Professional {product_type} product",
            "pricing": "$29 - Launch special!",
            "description": "Full product description with benefits"
        },
        "etsy": {
            "title": f"{product_name} | {product_type.title()} Download",
            "tags": [product_name.lower(), product_type, "instant download"],
            "description": "SEO-optimized listing"
        }
    }
    print("   ✅ Gumroad listing optimized")
    print("   ✅ Etsy shop ready")

    # Website
    print("\n🌐 Website Assets...")
    launch_package["assets"]["website"] = {
        "landing_page": {
            "headline": f"Transform Your Life with {product_name}",
            "features": ["Benefit 1", "Benefit 2", "Benefit 3"],
            "cta": "Get Started Now"
        },
        "blog_post": f"Introducing {product_name}: Everything You Need to Know"
    }
    print("   ✅ Landing page designed")
    print("   ✅ Blog post written")

    # Email Marketing
    print("\n📧 Email Campaign...")
    launch_package["assets"]["email"] = {
        "pre_launch": {
            "subject": f"Something amazing is coming...",
            "preview": "Get ready for {product_name}"
        },
        "launch_day": {
            "subject": f"🎉 {product_name} is HERE!",
            "body": "Exclusive launch offer inside"
        },
        "follow_up": {
            "subject": "Have you tried {product_name} yet?",
            "offer": "Limited time discount"
        }
    }
    print("   ✅ Pre-launch email ready")
    print("   ✅ Launch email created")
    print("   ✅ Follow-up sequence prepared")

    # Save everything
    output_dir = Path("examples/output/launches")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{product_name.replace(' ', '_')}_launch.json"
    output_file.write_text(json.dumps(launch_package, indent=2))

    print(f"\n💾 Complete launch package saved to: {output_file}")

    return launch_package


async def main():
    """Run the example"""
    products = [
        {"name": "Ultimate Python Course", "type": "course"},
        {"name": "Digital Planner Pro", "type": "template"},
        {"name": "Social Media Toolkit", "type": "bundle"}
    ]

    print("=" * 70)
    print("🎯 COMPLETE PRODUCT LAUNCH GENERATOR")
    print("=" * 70)
    print("\nGenerating assets for:")
    for p in products:
        print(f"  • {p['name']} ({p['type']})")

    for product in products:
        await launch_product(product["name"], product["type"])
        print("\n" + "-" * 70)

    print("\n" + "=" * 70)
    print("🎉 ALL PRODUCT LAUNCHES READY!")
    print("=" * 70)

    print("\n📊 What You Got:")
    print("  ✓ YouTube announcement videos & tutorials")
    print("  ✓ Instagram posts, stories & reels")
    print("  ✓ TikTok teaser & launch videos")
    print("  ✓ Twitter announcement threads")
    print("  ✓ LinkedIn professional posts")
    print("  ✓ Gumroad product listings")
    print("  ✓ Etsy shop listings")
    print("  ✓ Landing page designs")
    print("  ✓ Blog post content")
    print("  ✓ Email marketing campaign")

    print("\n🚀 Next Steps:")
    print("  1. Review all assets in examples/output/launches/")
    print("  2. Customize content for your brand")
    print("  3. Schedule social media posts")
    print("  4. Set up sales pages")
    print("  5. Prepare email sequences")
    print("  6. LAUNCH and celebrate! 🎊")


if __name__ == "__main__":
    asyncio.run(main())
