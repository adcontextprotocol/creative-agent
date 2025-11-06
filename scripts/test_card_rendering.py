#!/usr/bin/env python3
"""Test script to render product and format cards locally.

This script generates HTML previews for testing card rendering without
needing to run the full MCP server or upload to S3.

Usage:
    uv run python scripts/test_card_rendering.py

Output files will be created in the output/ directory.
"""

import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from creative_agent.data.standard_formats import filter_formats
from creative_agent.renderers import FormatCardRenderer, ProductCardRenderer
from creative_agent.schemas_generated._schemas_v1_core_format_json import FormatId


def create_output_dir() -> Path:
    """Create output directory for HTML files."""
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


def test_product_card_standard() -> None:
    """Generate and save a product_card_standard preview."""
    print("Rendering product_card_standard...")

    # Get format
    format_id = FormatId(
        agent_url="https://creative.adcontextprotocol.org",
        id="product_card_standard",
    )
    formats = filter_formats(format_ids=[format_id])
    format_obj = formats[0]

    # Create sample manifest
    manifest = {
        "format_id": {"agent_url": "https://creative.adcontextprotocol.org", "id": "product_card_standard"},
        "assets": {
            "product": {
                "offering": {
                    "name": "Premium Wireless Headphones",
                    "description": "**Immersive Sound Quality**\n\nExperience crystal-clear audio with active noise cancellation and 30-hour battery life.\n\n*Perfect for music lovers and professionals.*",
                    "price": 299.99,
                    "currency": "USD",
                    "images": ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"],
                    "url": "https://example.com/headphones",
                    "categories": ["electronics", "audio"],
                },
                "brand": {
                    "name": "AudioTech",
                    "colors": {
                        "primary": "#FF6B6B",
                        "text": "#2C3E50",
                    },
                },
            }
        },
    }

    # Create input set
    input_set = type("InputSet", (), {"name": "Desktop"})()

    # Render
    renderer = ProductCardRenderer()
    html = renderer.render(format_obj, manifest, input_set)

    # Save
    output_dir = create_output_dir()
    output_file = output_dir / "product_card_standard.html"
    output_file.write_text(html)
    print(f"✓ Saved to {output_file}")


def test_product_card_detailed() -> None:
    """Generate and save a product_card_detailed preview."""
    print("Rendering product_card_detailed...")

    # Get format
    format_id = FormatId(
        agent_url="https://creative.adcontextprotocol.org",
        id="product_card_detailed",
    )
    formats = filter_formats(format_ids=[format_id])
    format_obj = formats[0]

    # Create sample manifest with multiple images
    manifest = {
        "format_id": {"agent_url": "https://creative.adcontextprotocol.org", "id": "product_card_detailed"},
        "assets": {
            "product": {
                "offering": {
                    "name": "Professional Camera Kit",
                    "description": """## Full-Frame Excellence

Capture stunning images with our professional camera system featuring:

- **42 Megapixel Sensor** - Incredible detail and dynamic range
- **5-Axis Image Stabilization** - Sharp shots even in low light
- **4K Video Recording** - Cinema-quality footage at 60fps
- **Weather-Sealed Body** - Built to withstand the elements

### Perfect For

Professional photographers, content creators, and serious enthusiasts who demand the best image quality.

### What's Included

Complete kit with body, 24-70mm lens, battery grip, and professional carrying case.""",
                    "price": 3499.00,
                    "currency": "USD",
                    "images": [
                        "https://images.unsplash.com/photo-1606980663614-0b7f2f4f3b66?w=800",
                        "https://images.unsplash.com/photo-1585459895799-12cbde16ad67?w=800",
                        "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=800",
                    ],
                    "url": "https://example.com/camera-kit",
                    "categories": ["photography", "professional", "cameras"],
                },
                "brand": {
                    "name": "VisionPro",
                    "colors": {
                        "primary": "#1E40AF",
                        "text": "#111827",
                    },
                },
            }
        },
    }

    # Create input set
    input_set = type("InputSet", (), {"name": "Desktop"})()

    # Render
    renderer = ProductCardRenderer()
    html = renderer.render(format_obj, manifest, input_set)

    # Save
    output_dir = create_output_dir()
    output_file = output_dir / "product_card_detailed.html"
    output_file.write_text(html)
    print(f"✓ Saved to {output_file}")


def test_format_card_standard() -> None:
    """Generate and save a format_card_standard preview."""
    print("Rendering format_card_standard...")

    # Get format
    format_id = FormatId(
        agent_url="https://creative.adcontextprotocol.org",
        id="format_card_standard",
    )
    formats = filter_formats(format_ids=[format_id])
    format_obj = formats[0]

    # Create sample manifest with format data
    format_spec = {
        "name": "Medium Rectangle - Image",
        "type": "display",
        "description": "**Standard IAB display format**\n\nThe most popular banner size for web advertising. Perfect for sidebar placements and in-content ads.",
        "renders": [{"dimensions": {"width": 300, "height": 250, "unit": "px"}}],
        "assets_required": [
            {
                "asset_id": "banner_image",
                "asset_type": "image",
                "required": True,
                "requirements": {
                    "width": 300,
                    "height": 250,
                    "max_file_size_mb": 0.2,
                    "description": "Banner image in JPG, PNG, GIF, or WebP format",
                },
            },
            {
                "asset_id": "click_url",
                "asset_type": "url",
                "required": True,
                "requirements": {"description": "Clickthrough destination URL"},
            },
        ],
        "supported_macros": ["MEDIA_BUY_ID", "CREATIVE_ID", "CACHEBUSTER", "CLICK_URL", "DEVICE_TYPE"],
    }

    manifest = {
        "format_id": {"agent_url": "https://creative.adcontextprotocol.org", "id": "format_card_standard"},
        "assets": {"format": {"content": json.dumps(format_spec)}},
    }

    # Create input set
    input_set = type("InputSet", (), {"name": "Desktop"})()

    # Render
    renderer = FormatCardRenderer()
    html = renderer.render(format_obj, manifest, input_set)

    # Save
    output_dir = create_output_dir()
    output_file = output_dir / "format_card_standard.html"
    output_file.write_text(html)
    print(f"✓ Saved to {output_file}")


def test_format_card_detailed() -> None:
    """Generate and save a format_card_detailed preview."""
    print("Rendering format_card_detailed...")

    # Get format
    format_id = FormatId(
        agent_url="https://creative.adcontextprotocol.org",
        id="format_card_detailed",
    )
    formats = filter_formats(format_ids=[format_id])
    format_obj = formats[0]

    # Create detailed format specification
    format_spec = {
        "name": "Full HD Video - 1920x1080",
        "type": "video",
        "description": """## Professional Video Format

High-quality video advertising format optimized for desktop and CTV platforms.

### Technical Specifications

- **Resolution:** 1920x1080 (16:9 aspect ratio)
- **Format:** MP4, MOV, or WebM
- **Max Duration:** 30 seconds (recommended)
- **File Size:** Up to 50MB

### Best Practices

1. Use high-quality source footage at native resolution
2. Encode with H.264 codec for maximum compatibility
3. Include burned-in captions for accessibility
4. Test playback across multiple devices

### Common Use Cases

- Pre-roll video ads on streaming platforms
- In-stream video content on publisher sites
- Connected TV (CTV) advertising campaigns
- High-impact video storytelling""",
        "renders": [{"dimensions": {"width": 1920, "height": 1080, "unit": "px"}}],
        "assets_required": [
            {
                "asset_id": "video_file",
                "asset_type": "video",
                "required": True,
                "requirements": {
                    "width": 1920,
                    "height": 1080,
                    "acceptable_formats": ["mp4", "mov", "webm"],
                    "description": "High-definition video file at 1920x1080 resolution",
                },
            },
        ],
        "supported_macros": [
            "MEDIA_BUY_ID",
            "CREATIVE_ID",
            "CACHEBUSTER",
            "CLICK_URL",
            "IMPRESSION_URL",
            "DEVICE_TYPE",
            "VIDEO_ID",
            "POD_POSITION",
            "CONTENT_GENRE",
            "PLAYER_SIZE",
            "GDPR",
            "GDPR_CONSENT",
            "US_PRIVACY",
            "GPP_STRING",
        ],
    }

    manifest = {
        "format_id": {"agent_url": "https://creative.adcontextprotocol.org", "id": "format_card_detailed"},
        "assets": {"format": {"content": json.dumps(format_spec)}},
    }

    # Create input set
    input_set = type("InputSet", (), {"name": "Desktop"})()

    # Render
    renderer = FormatCardRenderer()
    html = renderer.render(format_obj, manifest, input_set)

    # Save
    output_dir = create_output_dir()
    output_file = output_dir / "format_card_detailed.html"
    output_file.write_text(html)
    print(f"✓ Saved to {output_file}")


def main() -> None:
    """Run all card rendering tests."""
    print("=== Testing Card Rendering ===\n")

    test_product_card_standard()
    test_product_card_detailed()
    test_format_card_standard()
    test_format_card_detailed()

    output_dir = create_output_dir()
    print(f"\n✓ All cards rendered successfully!")
    print(f"\nOpen the HTML files in your browser to view:")
    print(f"  {output_dir.absolute()}/")
    print("\nTip: Open multiple files in tabs to compare rendering across card types.")


if __name__ == "__main__":
    main()
