"""
Asset Generator Module
Generate assets for multiple platforms: YouTube, Gumroad, Canva, Etsy, game engines, websites, etc.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import json
from datetime import datetime
from pathlib import Path


@dataclass
class AssetTemplate:
    """Base template for generated assets"""
    platform: str
    asset_type: str
    title: str
    description: str
    content: str
    metadata: Dict[str, Any]
    created_at: str


class YouTubeAssetGenerator:
    """Generate assets for YouTube content creation"""

    def generate_video_script(self, topic: str, duration: str = "10min", style: str = "educational") -> Dict[str, Any]:
        """Generate YouTube video script"""
        scripts = {
            "educational": self._educational_script,
            "entertainment": self._entertainment_script,
            "tutorial": self._tutorial_script,
            "review": self._review_script
        }

        script_gen = scripts.get(style, self._educational_script)
        return script_gen(topic, duration)

    def _educational_script(self, topic: str, duration: str) -> Dict[str, Any]:
        return {
            "title": f"Complete Guide to {topic}",
            "hook": f"In this video, we'll explore everything you need to know about {topic}",
            "introduction": f"Welcome back! Today we're diving deep into {topic}. By the end of this video, you'll have a complete understanding of...",
            "main_points": [
                f"What is {topic} and why it matters",
                f"Key concepts and fundamentals of {topic}",
                f"Practical applications and examples",
                f"Common mistakes to avoid",
                f"Advanced tips and best practices"
            ],
            "conclusion": f"That's everything you need to know about {topic}. If you found this helpful, don't forget to like and subscribe!",
            "call_to_action": "Subscribe for more educational content",
            "timestamps": self._generate_timestamps(duration)
        }

    def _entertainment_script(self, topic: str, duration: str) -> Dict[str, Any]:
        return {
            "title": f"Amazing Facts About {topic}",
            "hook": f"You won't believe these {topic} facts!",
            "segments": [
                {"type": "intro", "content": f"Let's talk about {topic}..."},
                {"type": "main", "content": f"Here's what makes {topic} so interesting..."},
                {"type": "outro", "content": "Thanks for watching!"}
            ]
        }

    def _tutorial_script(self, topic: str, duration: str) -> Dict[str, Any]:
        return {
            "title": f"How to Master {topic} - Step by Step Tutorial",
            "introduction": f"In this tutorial, I'll show you exactly how to {topic}",
            "steps": [
                f"Step 1: Understanding the basics of {topic}",
                f"Step 2: Setting up your workspace",
                f"Step 3: Implementing {topic}",
                f"Step 4: Testing and refinement",
                f"Step 5: Advanced techniques"
            ],
            "conclusion": "Now you know how to do it! Practice and you'll master it."
        }

    def _review_script(self, topic: str, duration: str) -> Dict[str, Any]:
        return {
            "title": f"{topic} Review - Is It Worth It?",
            "sections": [
                {"name": "Introduction", "content": f"Today I'm reviewing {topic}"},
                {"name": "Pros", "content": "Let's start with what I liked..."},
                {"name": "Cons", "content": "Now for the downsides..."},
                {"name": "Verdict", "content": "Final thoughts and recommendation"}
            ]
        }

    def _generate_timestamps(self, duration: str) -> List[str]:
        return [
            "0:00 - Introduction",
            "1:30 - Main Topic",
            "5:00 - Key Points",
            "8:00 - Conclusion"
        ]

    def generate_thumbnail_template(self, topic: str, style: str = "bold") -> Dict[str, Any]:
        """Generate YouTube thumbnail design specs"""
        return {
            "dimensions": "1280x720",
            "text": topic.upper(),
            "style": style,
            "color_scheme": self._get_color_scheme(style),
            "font_suggestions": ["Impact", "Montserrat Bold", "Bebas Neue"],
            "elements": [
                "Main text (large, bold)",
                "Supporting text or number",
                "High-contrast background",
                "Optional: Face or product image",
                "Optional: Arrow or highlight circle"
            ],
            "best_practices": [
                "Use high contrast colors",
                "Keep text readable on mobile",
                "Include faces if possible",
                "Use emotional expressions",
                "Add intrigue or curiosity elements"
            ]
        }

    def _get_color_scheme(self, style: str) -> Dict[str, str]:
        schemes = {
            "bold": {"primary": "#FF0000", "secondary": "#FFFF00", "background": "#000000"},
            "professional": {"primary": "#2C3E50", "secondary": "#3498DB", "background": "#ECF0F1"},
            "vibrant": {"primary": "#E74C3C", "secondary": "#9B59B6", "background": "#F39C12"},
            "minimal": {"primary": "#34495E", "secondary": "#7F8C8D", "background": "#FFFFFF"}
        }
        return schemes.get(style, schemes["bold"])

    def generate_video_description(self, topic: str, script: Dict[str, Any]) -> str:
        """Generate optimized YouTube video description"""
        description = f"""In this video, we cover {topic} in detail.

📌 What You'll Learn:
"""
        if "main_points" in script:
            for point in script["main_points"]:
                description += f"✓ {point}\n"

        description += f"""

⏱️ Timestamps:
"""
        if "timestamps" in script:
            for timestamp in script["timestamps"]:
                description += f"{timestamp}\n"

        description += """

🔔 Subscribe for more content!
👍 Like if you found this helpful!
💬 Comment your thoughts below!

#tutorial #howto #educational

---
📧 Business inquiries: contact@example.com
🌐 Website: https://example.com
"""
        return description

    def generate_tags(self, topic: str, category: str = "education") -> List[str]:
        """Generate SEO-optimized tags"""
        base_tags = [
            topic.lower(),
            f"{topic} tutorial",
            f"how to {topic}",
            f"{topic} guide",
            f"learn {topic}"
        ]

        category_tags = {
            "education": ["educational", "learning", "tutorial", "guide"],
            "entertainment": ["fun", "interesting", "amazing", "facts"],
            "gaming": ["gameplay", "gaming", "playthrough", "walkthrough"],
            "tech": ["technology", "tech", "review", "unboxing"]
        }

        return base_tags + category_tags.get(category, [])


class GumroadAssetGenerator:
    """Generate assets for Gumroad digital products"""

    def generate_product_listing(self, product_name: str, product_type: str = "ebook") -> Dict[str, Any]:
        """Generate Gumroad product listing"""
        return {
            "name": product_name,
            "type": product_type,
            "description": self._create_product_description(product_name, product_type),
            "price_suggestion": self._suggest_pricing(product_type),
            "cover_image_specs": {
                "dimensions": "1600x1200 (4:3 ratio)",
                "format": "PNG or JPG",
                "tips": [
                    "Use high-quality mockups",
                    "Show product preview",
                    "Include benefit text",
                    "Professional typography"
                ]
            },
            "content_checklist": self._get_content_checklist(product_type),
            "marketing_copy": self._generate_marketing_copy(product_name)
        }

    def _create_product_description(self, name: str, ptype: str) -> str:
        templates = {
            "ebook": f"""📚 {name}

A comprehensive guide that will transform your understanding of the topic.

What's Inside:
• In-depth chapters covering all aspects
• Practical examples and case studies
• Step-by-step implementation guides
• Bonus resources and templates

Perfect for anyone looking to master this subject!""",

            "template": f"""🎨 {name}

Professional-grade templates ready to use immediately.

Includes:
• Multiple variations and styles
• Easy to customize
• Compatible with popular software
• Full commercial license
• Free updates

Save hours of work with these ready-made templates!""",

            "course": f"""🎓 {name}

Complete course with everything you need to succeed.

Course Includes:
• Video lessons (HD quality)
• Downloadable resources
• Practice exercises
• Certificate of completion
• Lifetime access

Start learning today!"""
        }
        return templates.get(ptype, templates["ebook"])

    def _suggest_pricing(self, product_type: str) -> Dict[str, Any]:
        pricing = {
            "ebook": {"min": 9, "suggested": 29, "max": 99},
            "template": {"min": 5, "suggested": 19, "max": 49},
            "course": {"min": 49, "suggested": 149, "max": 499},
            "bundle": {"min": 29, "suggested": 99, "max": 299}
        }
        return pricing.get(product_type, {"min": 10, "suggested": 30, "max": 100})

    def _get_content_checklist(self, product_type: str) -> List[str]:
        checklists = {
            "ebook": [
                "Cover design",
                "Table of contents",
                "Chapters written and edited",
                "Images and graphics",
                "PDF formatted",
                "Preview pages (first chapter)"
            ],
            "template": [
                "Template files",
                "Documentation/instructions",
                "Preview images",
                "Example usage",
                "License information"
            ],
            "course": [
                "Video lessons recorded",
                "Course outline/curriculum",
                "Downloadable resources",
                "Exercises/assignments",
                "Quiz or assessment",
                "Certificate template"
            ]
        }
        return checklists.get(product_type, [])

    def _generate_marketing_copy(self, product_name: str) -> Dict[str, str]:
        return {
            "headline": f"Transform Your Skills with {product_name}",
            "subheadline": "Everything you need to succeed, all in one place",
            "benefits": [
                "Save time and effort",
                "Learn from experts",
                "Immediate access",
                "Lifetime updates",
                "Money-back guarantee"
            ],
            "cta": "Get Instant Access Now",
            "guarantee": "30-day money-back guarantee - no questions asked"
        }


class EtsyAssetGenerator:
    """Generate assets for Etsy shop products"""

    def generate_product_listing(self, product_name: str, category: str = "digital") -> Dict[str, Any]:
        """Generate Etsy product listing"""
        return {
            "title": self._optimize_title(product_name, category),
            "description": self._create_description(product_name, category),
            "tags": self._generate_tags(product_name, category),
            "images": self._image_requirements(),
            "pricing": self._pricing_guide(category),
            "shipping": self._shipping_info(category),
            "seo_tips": self._seo_optimization_tips()
        }

    def _optimize_title(self, name: str, category: str) -> str:
        # Etsy titles should be descriptive and keyword-rich (max 140 chars)
        return f"{name} | {category.title()} Download | Printable | Instant Download"

    def _create_description(self, name: str, category: str) -> str:
        return f"""✨ {name} ✨

⭐ WHAT YOU GET:
• High-quality digital files
• Instant download after purchase
• Multiple file formats included
• Easy to use and customize

📋 DETAILS:
• Category: {category.title()}
• Format: PDF, PNG, SVG (if applicable)
• Size: Standard/Custom
• Commercial use allowed (check license)

💡 HOW IT WORKS:
1. Purchase and download files
2. Open in your favorite software
3. Customize if needed
4. Print or use digitally

🎁 PERFECT FOR:
• Personal projects
• Gifts
• Business use
• Special occasions

❓ QUESTIONS?
Feel free to message me anytime!

⚡ INSTANT DOWNLOAD - No shipping, no waiting!

---
© All rights reserved. For personal and commercial use.
Please do not resell or redistribute files.
"""

    def _generate_tags(self, name: str, category: str) -> List[str]:
        base_tags = [
            "digital download",
            "printable",
            "instant download",
            name.lower()
        ]

        category_tags = {
            "art": ["wall art", "printable art", "digital print", "home decor"],
            "planner": ["planner", "organizer", "productivity", "planning"],
            "wedding": ["wedding", "bridal", "invitation", "celebrate"],
            "craft": ["diy", "craft", "handmade", "creative"]
        }

        tags = base_tags + category_tags.get(category, [])
        return tags[:13]  # Etsy allows max 13 tags

    def _image_requirements(self) -> Dict[str, Any]:
        return {
            "count": "At least 5-10 images recommended",
            "dimensions": "2000x2000px minimum",
            "format": "JPG, PNG",
            "tips": [
                "First image is most important (thumbnail)",
                "Show product in use/context",
                "Include size comparison",
                "Show different variations",
                "Use lifestyle shots",
                "Include text overlay with features"
            ]
        }

    def _pricing_guide(self, category: str) -> Dict[str, Any]:
        return {
            "digital": {"min": 2, "suggested": 8, "max": 50},
            "physical": {"min": 10, "suggested": 30, "max": 200}
        }

    def _shipping_info(self, category: str) -> str:
        if category == "digital":
            return "Digital download - no shipping required. Files available immediately after purchase."
        return "Standard shipping: 3-5 business days. Expedited shipping available."

    def _seo_optimization_tips(self) -> List[str]:
        return [
            "Use all 13 tags",
            "Include long-tail keywords in title",
            "Write detailed descriptions (min 200 words)",
            "Use natural language, not keyword stuffing",
            "Update listings regularly to boost visibility",
            "Respond to reviews and questions quickly",
            "Offer variations when possible"
        ]


class WebAssetGenerator:
    """Generate assets for websites"""

    def generate_landing_page(self, product_name: str, purpose: str = "sales") -> Dict[str, Any]:
        """Generate landing page structure"""
        return {
            "structure": self._page_structure(purpose),
            "copy": self._landing_page_copy(product_name, purpose),
            "design_specs": self._design_specifications(),
            "seo": self._seo_elements(product_name),
            "conversion_elements": self._conversion_optimization()
        }

    def _page_structure(self, purpose: str) -> List[str]:
        structures = {
            "sales": [
                "Hero section with headline",
                "Problem/solution statement",
                "Features and benefits",
                "Social proof (testimonials)",
                "Pricing table",
                "FAQ section",
                "Strong CTA",
                "Footer"
            ],
            "portfolio": [
                "Hero with introduction",
                "Skills/services overview",
                "Project showcase",
                "About section",
                "Testimonials",
                "Contact form"
            ],
            "blog": [
                "Header with navigation",
                "Featured post",
                "Post grid",
                "Sidebar with categories",
                "Newsletter signup",
                "Footer"
            ]
        }
        return structures.get(purpose, structures["sales"])

    def _landing_page_copy(self, product: str, purpose: str) -> Dict[str, str]:
        return {
            "headline": f"The Ultimate {product} You've Been Looking For",
            "subheadline": "Solve your problems and achieve your goals faster than ever",
            "features": [
                "Easy to use and implement",
                "Professional quality results",
                "Save time and money",
                "Backed by experts"
            ],
            "cta_primary": "Get Started Now",
            "cta_secondary": "Learn More"
        }

    def _design_specifications(self) -> Dict[str, Any]:
        return {
            "color_palette": {
                "primary": "#2563EB",
                "secondary": "#7C3AED",
                "accent": "#F59E0B",
                "background": "#FFFFFF",
                "text": "#1F2937"
            },
            "typography": {
                "heading_font": "Inter, Montserrat, or Poppins",
                "body_font": "Inter, Open Sans, or Roboto",
                "sizes": {
                    "h1": "48-64px",
                    "h2": "36-48px",
                    "h3": "24-32px",
                    "body": "16-18px"
                }
            },
            "spacing": {
                "section_padding": "80-120px vertical",
                "container_max_width": "1200px",
                "grid_gap": "24-32px"
            }
        }

    def _seo_elements(self, product: str) -> Dict[str, str]:
        return {
            "title": f"{product} - Your Solution for Success",
            "meta_description": f"Discover {product} and transform the way you work. Professional quality, easy to use, and proven results.",
            "og_title": f"{product} - Get Started Today",
            "og_description": f"Join thousands of satisfied users who chose {product}",
            "keywords": [product.lower(), "solution", "professional", "quality"]
        }

    def _conversion_optimization(self) -> List[str]:
        return [
            "Clear value proposition above the fold",
            "Use contrasting CTA buttons",
            "Include trust badges and security seals",
            "Add countdown timers for urgency",
            "Display customer testimonials",
            "Show real-time social proof",
            "Minimize form fields",
            "Add exit-intent popups",
            "Use A/B testing"
        ]

    def generate_blog_post_template(self, topic: str) -> Dict[str, Any]:
        """Generate blog post outline and template"""
        return {
            "title": f"The Complete Guide to {topic}",
            "structure": [
                "Introduction - Hook and preview",
                "What is {topic}?",
                "Why {topic} matters",
                "How to implement {topic}",
                "Common mistakes to avoid",
                "Best practices and tips",
                "Conclusion and next steps"
            ],
            "meta_description": f"Learn everything about {topic} in this comprehensive guide. Includes tips, examples, and best practices.",
            "seo_tips": [
                f"Use '{topic}' in first 100 words",
                "Include internal and external links",
                "Add images with alt text",
                "Use header tags (H2, H3)",
                "Aim for 1500+ words",
                "Include FAQ section"
            ],
            "call_to_action": "Subscribe to our newsletter for more guides like this!"
        }


class GameAssetGenerator:
    """Generate assets for game development"""

    def generate_game_design_document(self, game_name: str, genre: str = "action") -> Dict[str, Any]:
        """Generate game design document structure"""
        return {
            "concept": self._game_concept(game_name, genre),
            "mechanics": self._game_mechanics(genre),
            "story": self._story_structure(),
            "characters": self._character_templates(),
            "levels": self._level_design_framework(),
            "ui_ux": self._ui_specifications(),
            "monetization": self._monetization_strategies()
        }

    def _game_concept(self, name: str, genre: str) -> Dict[str, Any]:
        return {
            "title": name,
            "genre": genre,
            "platform": ["PC", "Mobile", "Console"],
            "target_audience": "Ages 13+",
            "unique_selling_point": f"Innovative {genre} gameplay with unique mechanics",
            "elevator_pitch": f"{name} is a {genre} game that combines exciting gameplay with immersive storytelling"
        }

    def _game_mechanics(self, genre: str) -> List[str]:
        mechanics = {
            "action": [
                "Combat system",
                "Movement mechanics",
                "Power-ups and abilities",
                "Health and damage system",
                "Enemy AI behavior"
            ],
            "puzzle": [
                "Core puzzle mechanic",
                "Difficulty progression",
                "Hint system",
                "Time limits or moves",
                "Combo system"
            ],
            "rpg": [
                "Character progression",
                "Inventory system",
                "Quest system",
                "Dialogue trees",
                "Combat mechanics"
            ]
        }
        return mechanics.get(genre, mechanics["action"])

    def _story_structure(self) -> Dict[str, str]:
        return {
            "premise": "The main story concept and setting",
            "protagonist": "Main character background and motivation",
            "antagonist": "Main villain or opposing force",
            "conflict": "Central conflict driving the story",
            "resolution": "How the story concludes",
            "themes": "Core themes and messages"
        }

    def _character_templates(self) -> List[Dict[str, str]]:
        return [
            {
                "name": "Protagonist",
                "role": "Main playable character",
                "abilities": "List of skills and powers",
                "backstory": "Character history",
                "personality": "Character traits"
            },
            {
                "name": "Companion",
                "role": "Supporting character",
                "relationship": "Connection to protagonist",
                "abilities": "Support skills"
            }
        ]

    def _level_design_framework(self) -> Dict[str, Any]:
        return {
            "level_count": "10-15 levels recommended",
            "progression": "Easy → Medium → Hard → Boss",
            "level_structure": [
                "Introduction/tutorial area",
                "Main gameplay section",
                "Challenge/puzzle element",
                "Reward/checkpoint",
                "Boss or finale"
            ],
            "pacing": "Balance action and exploration"
        }

    def _ui_specifications(self) -> Dict[str, List[str]]:
        return {
            "main_menu": [
                "Play/Start",
                "Settings",
                "Achievements",
                "Quit"
            ],
            "hud_elements": [
                "Health bar",
                "Score/points",
                "Mini-map",
                "Ability cooldowns",
                "Objective tracker"
            ],
            "design_principles": [
                "Clear visual hierarchy",
                "Consistent styling",
                "Accessibility options",
                "Responsive to different screen sizes"
            ]
        }

    def _monetization_strategies(self) -> List[str]:
        return [
            "Premium (paid upfront)",
            "Free-to-play with ads",
            "In-app purchases (cosmetics)",
            "Battle pass system",
            "Expansion packs/DLC"
        ]


class CanvaAssetGenerator:
    """Generate templates and assets for Canva"""

    def generate_template_specs(self, template_type: str = "social") -> Dict[str, Any]:
        """Generate Canva template specifications"""
        specs = {
            "social": {
                "instagram_post": {"size": "1080x1080px", "format": "Square"},
                "instagram_story": {"size": "1080x1920px", "format": "Vertical"},
                "facebook_post": {"size": "1200x630px", "format": "Landscape"},
                "twitter_post": {"size": "1200x675px", "format": "Landscape"},
                "pinterest_pin": {"size": "1000x1500px", "format": "Vertical"}
            },
            "marketing": {
                "flyer": {"size": "8.5x11in", "format": "Letter"},
                "business_card": {"size": "3.5x2in", "format": "Standard"},
                "brochure": {"size": "11x8.5in", "format": "Tri-fold"},
                "poster": {"size": "24x36in", "format": "Large"}
            },
            "presentation": {
                "slide_deck": {"size": "1920x1080px", "format": "16:9"},
                "infographic": {"size": "800x2000px", "format": "Vertical"}
            }
        }

        return {
            "specifications": specs.get(template_type, specs["social"]),
            "design_tips": self._design_tips(),
            "color_palettes": self._color_palettes(),
            "font_pairings": self._font_pairings()
        }

    def _design_tips(self) -> List[str]:
        return [
            "Use high contrast for readability",
            "Maintain consistent spacing",
            "Limit fonts to 2-3 families",
            "Use white space effectively",
            "Align elements to a grid",
            "Use hierarchy to guide the eye",
            "Include clear calls-to-action"
        ]

    def _color_palettes(self) -> List[Dict[str, str]]:
        return [
            {"name": "Modern Blue", "colors": ["#2563EB", "#60A5FA", "#DBEAFE", "#1E3A8A"]},
            {"name": "Warm Sunset", "colors": ["#F59E0B", "#EF4444", "#FEE2E2", "#7C2D12"]},
            {"name": "Fresh Green", "colors": ["#10B981", "#6EE7B7", "#D1FAE5", "#065F46"]},
            {"name": "Professional Gray", "colors": ["#374151", "#6B7280", "#E5E7EB", "#111827"]}
        ]

    def _font_pairings(self) -> List[Dict[str, str]]:
        return [
            {"heading": "Montserrat Bold", "body": "Open Sans"},
            {"heading": "Playfair Display", "body": "Source Sans Pro"},
            {"heading": "Bebas Neue", "body": "Roboto"},
            {"heading": "Raleway", "body": "Lato"}
        ]


class AssetGeneratorManager:
    """Main manager for all asset generators"""

    def __init__(self):
        self.youtube = YouTubeAssetGenerator()
        self.gumroad = GumroadAssetGenerator()
        self.etsy = EtsyAssetGenerator()
        self.web = WebAssetGenerator()
        self.game = GameAssetGenerator()
        self.canva = CanvaAssetGenerator()

    def generate_asset(self, platform: str, asset_type: str, **kwargs) -> Dict[str, Any]:
        """Generate asset for specified platform"""
        generators = {
            "youtube": self.youtube,
            "gumroad": self.gumroad,
            "etsy": self.etsy,
            "web": self.web,
            "game": self.game,
            "canva": self.canva
        }

        generator = generators.get(platform.lower())
        if not generator:
            return {"error": f"Unknown platform: {platform}"}

        # Call appropriate method based on asset_type
        method_name = f"generate_{asset_type}"
        if hasattr(generator, method_name):
            method = getattr(generator, method_name)
            return method(**kwargs)

        return {"error": f"Asset type '{asset_type}' not found for platform '{platform}'"}

    def get_available_platforms(self) -> List[str]:
        """Get list of supported platforms"""
        return ["youtube", "gumroad", "etsy", "web", "game", "canva"]

    def get_asset_types(self, platform: str) -> List[str]:
        """Get available asset types for a platform"""
        asset_types = {
            "youtube": ["video_script", "thumbnail_template", "video_description", "tags"],
            "gumroad": ["product_listing"],
            "etsy": ["product_listing"],
            "web": ["landing_page", "blog_post_template"],
            "game": ["game_design_document"],
            "canva": ["template_specs"]
        }
        return asset_types.get(platform.lower(), [])
