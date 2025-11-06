"""Renderer for format card formats."""

import html as html_module
import json
from typing import Any

import bleach
import markdown

from .base import BaseRenderer

# Allowed HTML tags and attributes for markdown content
ALLOWED_TAGS = [
    "p",
    "br",
    "strong",
    "em",
    "u",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "blockquote",
    "code",
    "pre",
]
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
    "code": ["class"],
}
ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


class FormatCardRenderer(BaseRenderer):
    """Renderer for format_card_standard and format_card_detailed formats."""

    def render(self, format_obj: Any, manifest: Any, input_set: Any, fragment: bool = True) -> str:
        """Generate HTML preview for format card formats.

        Args:
            format_obj: Format definition (format_card_standard or format_card_detailed)
            manifest: Creative manifest with format specification as text asset
            input_set: Preview input configuration

        Returns:
            HTML string with format card display
        """
        width, height = self.get_dimensions(format_obj)
        manifest_assets = self.get_manifest_assets(manifest)
        asset_type_map = self.build_asset_type_map(format_obj)

        # Find format text asset
        format_asset = self.find_asset_by_type(manifest_assets, asset_type_map, "text")

        # Extract format data
        format_data = self._extract_format_data(format_asset)

        # Check if this is a detailed card (responsive)
        is_detailed = format_obj.format_id.id == "format_card_detailed"

        # Generate HTML
        if is_detailed:
            return self._render_detailed_card(format_obj, input_set, format_data)
        return self._render_standard_card(format_obj, input_set, format_data, width, height)

    def _extract_format_data(self, format_asset: Any) -> dict[str, Any]:
        """Extract format specification from text asset.

        Args:
            format_asset: Text asset containing format data (JSON or plain text)

        Returns:
            Format data dictionary with fallback values
        """
        default: dict[str, Any] = {
            "name": "Creative Format",
            "description": "Format description not available",
            "type": "display",
            "dimensions": "N/A",
            "assets_required": [],
            "supported_macros": [],
        }

        if not format_asset or not isinstance(format_asset, dict):
            return default

        # Try to parse as JSON if it has content field
        content = format_asset.get("content", "")
        if isinstance(content, str) and content.strip():
            try:
                # Try parsing as JSON
                format_json = json.loads(content)
                if isinstance(format_json, dict):
                    return self._parse_format_json(format_json)
            except json.JSONDecodeError:
                # Not JSON, treat as plain text description
                return {**default, "description": content}

        return default

    def _parse_format_json(self, format_json: dict[str, Any]) -> dict[str, Any]:
        """Parse format JSON into display-friendly structure.

        Args:
            format_json: Format specification as JSON

        Returns:
            Parsed format data
        """
        # Extract dimensions from renders
        dimensions_str = "N/A"
        renders = format_json.get("renders", [])
        if renders and len(renders) > 0:
            first_render = renders[0]
            if isinstance(first_render, dict) and "dimensions" in first_render:
                dims = first_render["dimensions"]
                width = dims.get("width")
                height = dims.get("height")
                if width and height:
                    dimensions_str = f"{int(width)}x{int(height)}"
                elif dims.get("responsive", {}).get("width") or dims.get("responsive", {}).get("height"):
                    dimensions_str = "Responsive"

        # Extract asset requirements
        assets_required = []
        for asset in format_json.get("assets_required", []):
            if isinstance(asset, dict):
                asset_info = {
                    "id": asset.get("asset_id", "unknown"),
                    "type": asset.get("asset_type", "unknown"),
                    "required": asset.get("required", True),
                    "description": asset.get("requirements", {}).get("description", ""),
                }
                assets_required.append(asset_info)

        return {
            "name": format_json.get("name", "Format"),
            "description": format_json.get("description", ""),
            "type": format_json.get("type", "display"),
            "dimensions": dimensions_str,
            "assets_required": assets_required,
            "supported_macros": format_json.get("supported_macros", []),
        }

    def _sanitize_markdown(self, markdown_text: str) -> str:
        """Convert markdown to safe HTML, sanitizing any potentially dangerous content.

        Args:
            markdown_text: Markdown-formatted text

        Returns:
            Sanitized HTML string
        """
        # Convert markdown to HTML
        html = markdown.markdown(markdown_text, extensions=["extra", "nl2br"])

        # Sanitize HTML to prevent XSS
        return str(
            bleach.clean(
                html,
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRIBUTES,
                protocols=ALLOWED_PROTOCOLS,
                strip=True,
            )
        )

    def _render_standard_card(
        self,
        format_obj: Any,
        input_set: Any,
        format_data: dict[str, Any],
        width: int,
        height: int,
    ) -> str:
        """Render standard 300x400 format card.

        Args:
            format_obj: Format definition
            input_set: Preview input
            format_data: Format information
            width: Card width in pixels
            height: Card height in pixels

        Returns:
            HTML string
        """
        # Convert description markdown to safe HTML
        description = format_data.get("description", "")
        description_html = self._sanitize_markdown(description)

        # Safe escape
        format_name = html_module.escape(format_data.get("name", "Format"))
        format_type = html_module.escape(str(format_data.get("type", "display")))
        dimensions = html_module.escape(str(format_data.get("dimensions", "N/A")))

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html_module.escape(format_obj.name)}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            width: {width}px;
            height: {height}px;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        .format-card {{
            width: 100%;
            height: 100%;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}
        .format-preview {{
            width: 100%;
            height: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 14px;
            font-weight: 600;
            text-align: center;
            padding: 20px;
            position: relative;
        }}
        .format-info {{
            padding: 12px;
            flex: 1;
            display: flex;
            flex-direction: column;
        }}
        .format-name {{
            font-size: 16px;
            font-weight: 600;
            color: #111;
            margin-bottom: 4px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .format-meta {{
            font-size: 11px;
            color: #666;
            margin-bottom: 8px;
        }}
        .format-meta span {{
            margin-right: 12px;
        }}
        .format-description {{
            font-size: 12px;
            color: #666;
            line-height: 1.4;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            flex: 1;
        }}
        .format-description p {{
            margin: 0;
        }}
        .preview-label {{
            position: absolute;
            top: 8px;
            right: 8px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 4px 8px;
            font-size: 10px;
            border-radius: 4px;
            z-index: 10;
        }}
    </style>
</head>
<body>
    <div class="format-card">
        <div class="format-preview">
            <div>
                <div style="font-size: 24px; margin-bottom: 8px;">{dimensions}</div>
                <div style="font-size: 12px; opacity: 0.9;">{format_type}</div>
            </div>
            <div class="preview-label">{html_module.escape(input_set.name)}</div>
        </div>
        <div class="format-info">
            <div class="format-name">{format_name}</div>
            <div class="format-meta">
                <span><strong>Type:</strong> {format_type}</span>
                <span><strong>Size:</strong> {dimensions}</span>
            </div>
            <div class="format-description">{description_html}</div>
        </div>
    </div>
</body>
</html>"""

        return html  # noqa: RET504

    def _render_detailed_card(
        self,
        format_obj: Any,
        input_set: Any,
        format_data: dict[str, Any],
    ) -> str:
        """Render detailed responsive format card.

        Args:
            format_obj: Format definition
            input_set: Preview input
            format_data: Format information

        Returns:
            HTML string
        """
        # Convert description markdown to safe HTML
        description = format_data.get("description", "")
        description_html = self._sanitize_markdown(description)

        # Safe escape
        format_name = html_module.escape(format_data.get("name", "Format"))
        format_type = html_module.escape(str(format_data.get("type", "display")))
        dimensions = html_module.escape(str(format_data.get("dimensions", "N/A")))

        # Build assets required table
        assets_html = ""
        assets_required = format_data.get("assets_required", [])
        if assets_required:
            assets_html = '<div class="section"><h3>Assets Required</h3><table class="assets-table">'
            assets_html += (
                "<thead><tr><th>Asset ID</th><th>Type</th><th>Required</th><th>Description</th></tr></thead><tbody>"
            )
            for asset in assets_required:
                required_badge = (
                    '<span class="badge badge-required">Required</span>'
                    if asset.get("required")
                    else '<span class="badge badge-optional">Optional</span>'
                )
                assets_html += f"""<tr>
                    <td><code>{html_module.escape(asset.get("id", "N/A"))}</code></td>
                    <td><code>{html_module.escape(asset.get("type", "N/A"))}</code></td>
                    <td>{required_badge}</td>
                    <td>{html_module.escape(asset.get("description", ""))}</td>
                </tr>"""
            assets_html += "</tbody></table></div>"

        # Build supported macros
        macros_html = ""
        supported_macros = format_data.get("supported_macros", [])
        if supported_macros:
            macro_tags = " ".join(
                f'<code class="macro">{html_module.escape(macro)}</code>' for macro in supported_macros[:10]
            )
            if len(supported_macros) > 10:
                macro_tags += f' <span class="more">+{len(supported_macros) - 10} more</span>'
            macros_html = f'<div class="section"><h3>Supported Macros</h3><div class="macros">{macro_tags}</div></div>'

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html_module.escape(format_obj.name)}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f9f9f9;
            padding: 20px;
            min-height: 100vh;
        }}
        .format-card {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .format-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            position: relative;
        }}
        .format-title {{
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 12px;
        }}
        .format-meta {{
            font-size: 16px;
            opacity: 0.95;
        }}
        .format-meta span {{
            margin-right: 20px;
        }}
        .format-dimensions {{
            position: absolute;
            top: 20px;
            right: 40px;
            font-size: 48px;
            font-weight: 700;
            opacity: 0.3;
        }}
        .format-content {{
            padding: 32px 40px;
        }}
        .section {{
            margin-bottom: 32px;
        }}
        .section:last-child {{
            margin-bottom: 0;
        }}
        h3 {{
            font-size: 18px;
            font-weight: 600;
            color: #111;
            margin-bottom: 16px;
        }}
        .format-description {{
            font-size: 16px;
            line-height: 1.6;
            color: #333;
        }}
        .format-description p {{
            margin-bottom: 12px;
        }}
        .assets-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        .assets-table th {{
            text-align: left;
            padding: 12px;
            background: #f5f5f5;
            font-weight: 600;
            border-bottom: 2px solid #e0e0e0;
        }}
        .assets-table td {{
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        .assets-table code {{
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 13px;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        }}
        .badge-required {{
            background: #fee;
            color: #c33;
        }}
        .badge-optional {{
            background: #eff;
            color: #369;
        }}
        .macros {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .macros code {{
            background: #f5f5f5;
            padding: 6px 12px;
            border-radius: 4px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 13px;
        }}
        .more {{
            color: #666;
            font-size: 13px;
        }}
        .preview-label {{
            position: absolute;
            top: 20px;
            left: 40px;
            background: rgba(0,0,0,0.3);
            color: white;
            padding: 6px 12px;
            font-size: 12px;
            border-radius: 6px;
        }}
    </style>
</head>
<body>
    <div class="format-card">
        <div class="format-header">
            <div class="preview-label">{html_module.escape(input_set.name)}</div>
            <div class="format-dimensions">{dimensions}</div>
            <div class="format-title">{format_name}</div>
            <div class="format-meta">
                <span><strong>Type:</strong> {format_type}</span>
                <span><strong>Dimensions:</strong> {dimensions}</span>
            </div>
        </div>
        <div class="format-content">
            <div class="section">
                <h3>Description</h3>
                <div class="format-description">{description_html}</div>
            </div>
            {assets_html}
            {macros_html}
        </div>
    </div>
</body>
</html>"""

        return html  # noqa: RET504
