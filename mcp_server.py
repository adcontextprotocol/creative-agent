"""FastMCP server for AdCP Creative Agent v1 - standalone entry point.

Focuses on:
1. list_creative_formats - Returns all AdCP creative formats
2. preview_creative - Generates previews from creative manifests
"""

import json
import sys
import uuid
from pathlib import Path

# Add src to path so we can import
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastmcp import FastMCP

from creative_agent.data.formats import STANDARD_FORMATS, get_format_by_id

mcp = FastMCP("adcp-creative-agent")


@mcp.tool()
def list_creative_formats() -> str:
    """List all available AdCP creative formats.

    Returns all standard creative formats defined in the AdCP spec including
    video, display, audio, DOOH, and foundational interactive formats.

    Returns:
        JSON array of creative format objects with format_id, name, type, dimensions, etc.
    """
    formats_data = [fmt.model_dump(mode="json") for fmt in STANDARD_FORMATS]
    return json.dumps(formats_data, indent=2)


@mcp.tool()
def preview_creative(manifest_json: str) -> str:
    """Generate a preview from a creative manifest.

    Takes a creative manifest and generates a rendered preview.
    Returns a URL or iframe HTML for viewing the creative.

    Args:
        manifest_json: JSON creative manifest with format_id and creative assets

    Returns:
        JSON with preview_url, iframe_html, and rendered creative details

    Example manifest:
        {
            "format_id": "display_banner",
            "assets": {
                "image": "https://example.com/banner.jpg",
                "click_url": "https://example.com/landing"
            },
            "width": 300,
            "height": 250
        }
    """
    try:
        manifest = json.loads(manifest_json)

        # Validate format exists
        format_id = manifest.get("format_id")
        if not format_id:
            return json.dumps({"error": "format_id is required in manifest"})

        fmt = get_format_by_id(format_id)
        if not fmt:
            return json.dumps({"error": f"Format {format_id} not found"})

        # Generate preview ID
        preview_id = str(uuid.uuid4())

        # Build iframe HTML based on format type
        if fmt.type == "display":
            width = manifest.get("width", fmt.width or 300)
            height = manifest.get("height", fmt.height or 250)
            image_url = manifest.get("assets", {}).get("image", "")
            click_url = manifest.get("assets", {}).get("click_url", "#")

            iframe_html = f"""
<iframe width="{width}" height="{height}" style="border: 1px solid #ccc;">
    <a href="{click_url}" target="_blank">
        <img src="{image_url}" width="{width}" height="{height}" alt="Ad Creative" />
    </a>
</iframe>
""".strip()

        elif fmt.type == "video":
            width = manifest.get("width", fmt.width or 640)
            height = manifest.get("height", fmt.height or 360)
            video_url = manifest.get("assets", {}).get("video", "")

            iframe_html = f"""
<iframe width="{width}" height="{height}" style="border: 1px solid #ccc;">
    <video width="{width}" height="{height}" controls>
        <source src="{video_url}" type="video/mp4">
    </video>
</iframe>
""".strip()

        else:
            # Generic HTML preview
            iframe_html = f"<div>Preview for {fmt.name} (format_id: {format_id})</div>"

        response = {
            "preview_id": preview_id,
            "format_id": format_id,
            "preview_url": f"https://preview.adcp.example.com/{preview_id}",
            "iframe_html": iframe_html,
            "manifest": manifest,
        }

        return json.dumps(response, indent=2)

    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON: {e!s}"})
    except Exception as e:
        return json.dumps({"error": str(e)})
