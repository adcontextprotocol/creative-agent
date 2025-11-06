"""Renderer for product card formats."""

import html as html_module
from typing import Any

import bleach
import markdown

from creative_agent.utils import sanitize_url

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


class ProductCardRenderer(BaseRenderer):
    """Renderer for product_card_standard and product_card_detailed formats."""

    def render(self, format_obj: Any, manifest: Any, input_set: Any, fragment: bool = True) -> str:
        """Generate HTML preview for product card formats.

        Args:
            format_obj: Format definition (product_card_standard or product_card_detailed)
            manifest: Creative manifest with individual product assets
            input_set: Preview input configuration
            fragment: If True (default), return HTML fragment. If False, return full document.

        Returns:
            HTML string with product card display
        """
        width, height = self.get_dimensions(format_obj)
        manifest_assets = self.get_manifest_assets(manifest)

        # Extract individual assets
        product_data = self._extract_product_data(manifest_assets)

        # Check if this is a detailed card (responsive)
        is_detailed = format_obj.format_id.id == "product_card_detailed"

        # Generate HTML
        if is_detailed:
            return self._render_detailed_card(format_obj, input_set, product_data, fragment)
        return self._render_standard_card(format_obj, input_set, product_data, width, height, fragment)

    def _extract_product_data(self, manifest_assets: dict[str, Any]) -> dict[str, Any]:
        """Extract product data from individual assets.

        Args:
            manifest_assets: Manifest assets dictionary

        Returns:
            Product data dictionary with fallback values
        """
        default: dict[str, Any] = {
            "name": "Media Product",
            "description": "Product description not available",
            "image_url": None,
            "pricing_model": None,
            "pricing_amount": None,
            "pricing_currency": None,
            "delivery_type": None,
            "primary_asset_type": None,
        }

        if not manifest_assets or not isinstance(manifest_assets, dict):
            return default

        # Extract text content helper
        def get_text_content(asset_id: str) -> str | None:
            asset = manifest_assets.get(asset_id)
            if isinstance(asset, dict):
                content = asset.get("content")
                if isinstance(content, str):
                    return content
            return None

        # Extract image URL helper
        def get_image_url(asset_id: str) -> str | None:
            asset = manifest_assets.get(asset_id)
            if isinstance(asset, dict):
                return asset.get("url") or asset.get("content")
            return None

        return {
            "name": get_text_content("product_name") or default["name"],
            "description": get_text_content("product_description") or default["description"],
            "image_url": get_image_url("product_image"),
            "pricing_model": get_text_content("pricing_model"),
            "pricing_amount": get_text_content("pricing_amount"),
            "pricing_currency": get_text_content("pricing_currency"),
            "delivery_type": get_text_content("delivery_type"),
            "primary_asset_type": get_text_content("primary_asset_type"),
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
        product_data: dict[str, Any],
        width: int,
        height: int,
        fragment: bool = True,
    ) -> str:
        """Render standard 300x400 product card.

        Args:
            format_obj: Format definition
            input_set: Preview input
            product_data: Product information
            width: Card width in pixels
            height: Card height in pixels

        Returns:
            HTML string
        """
        # Get image URL and sanitize it
        image_url = product_data.get("image_url")
        if image_url:
            image_url = sanitize_url(image_url)

        # Convert description markdown to safe HTML
        description = product_data.get("description", "")
        description_html = self._sanitize_markdown(description)

        # Format pricing
        price_str = ""
        pricing_model = product_data.get("pricing_model")
        pricing_amount = product_data.get("pricing_amount")
        pricing_currency = product_data.get("pricing_currency", "USD")
        if pricing_model and pricing_amount:
            price_str = f'<div class="price">{html_module.escape(pricing_model)} ${html_module.escape(pricing_amount)} {html_module.escape(pricing_currency)}</div>'

        # Build badges
        badges_html = ""
        delivery_type = product_data.get("delivery_type")
        primary_asset_type = product_data.get("primary_asset_type")
        if delivery_type or primary_asset_type:
            badges = []
            if delivery_type:
                badge_class = "badge-guaranteed" if delivery_type.lower() == "guaranteed" else "badge-bidded"
                badges.append(f'<span class="badge {badge_class}">{html_module.escape(delivery_type)}</span>')
            if primary_asset_type:
                badges.append(f'<span class="badge badge-asset-type">{html_module.escape(primary_asset_type)}</span>')
            badges_html = f'<div class="badges">{"".join(badges)}</div>'

        # Safe escape
        product_name = html_module.escape(product_data.get("name", "Media Product"))

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
        .product-card {{
            width: 100%;
            height: 100%;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}
        .product-image {{
            width: 100%;
            height: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            overflow: hidden;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .product-image img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .product-image.placeholder {{
            color: rgba(255,255,255,0.7);
            font-size: 12px;
        }}
        .product-info {{
            padding: 12px;
            flex: 1;
            display: flex;
            flex-direction: column;
        }}
        .product-name {{
            font-size: 16px;
            font-weight: 600;
            color: #111;
            margin-bottom: 6px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .badges {{
            display: flex;
            gap: 6px;
            margin-bottom: 8px;
            flex-wrap: wrap;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .badge-guaranteed {{
            background: #e6f7e6;
            color: #2d662d;
        }}
        .badge-bidded {{
            background: #fff4e6;
            color: #996633;
        }}
        .badge-asset-type {{
            background: #e6f0ff;
            color: #2563eb;
        }}
        .product-description {{
            font-size: 11px;
            color: #666;
            line-height: 1.4;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            flex: 1;
        }}
        .product-description p {{
            margin: 0;
        }}
        .price {{
            font-size: 13px;
            font-weight: 700;
            color: #111;
            margin-top: 8px;
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
    <div class="product-card">
        <div class="product-image{"placeholder" if not image_url else ""}">
"""

        if image_url:
            html += f'            <img src="{html_module.escape(image_url)}" alt="{product_name}">\n'
        else:
            html += "            No Image Available\n"

        html += f"""            <div class="preview-label">{html_module.escape(input_set.name)}</div>
        </div>
        <div class="product-info">
            <div class="product-name">{product_name}</div>
            {badges_html}
            <div class="product-description">{description_html}</div>
            {price_str}
        </div>
    </div>
</body>
</html>"""

        return html

    def _render_detailed_card(
        self,
        format_obj: Any,
        input_set: Any,
        product_data: dict[str, Any],
        fragment: bool = True,
    ) -> str:
        """Render detailed responsive product card.

        Args:
            format_obj: Format definition
            input_set: Preview input
            product_data: Product information

        Returns:
            HTML string
        """
        # Get image URL and sanitize it
        image_url = product_data.get("image_url")
        if image_url:
            image_url = sanitize_url(image_url)

        # Convert description markdown to safe HTML
        description = product_data.get("description", "")
        description_html = self._sanitize_markdown(description)

        # Format pricing
        price_str = ""
        pricing_model = product_data.get("pricing_model")
        pricing_amount = product_data.get("pricing_amount")
        pricing_currency = product_data.get("pricing_currency", "USD")
        if pricing_model and pricing_amount:
            price_str = f'<div class="price">{html_module.escape(pricing_model)} ${html_module.escape(pricing_amount)} {html_module.escape(pricing_currency)}</div>'

        # Build badges
        badges_html = ""
        delivery_type = product_data.get("delivery_type")
        primary_asset_type = product_data.get("primary_asset_type")
        if delivery_type or primary_asset_type:
            badges = []
            if delivery_type:
                badge_class = "badge-guaranteed" if delivery_type.lower() == "guaranteed" else "badge-bidded"
                badges.append(f'<span class="badge {badge_class}">{html_module.escape(delivery_type)}</span>')
            if primary_asset_type:
                badges.append(f'<span class="badge badge-asset-type">{html_module.escape(primary_asset_type)}</span>')
            badges_html = f'<div class="badges">{"".join(badges)}</div>'

        # Safe escape
        product_name = html_module.escape(product_data.get("name", "Media Product"))

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
        .product-card {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .product-header {{
            position: relative;
            width: 100%;
            height: 400px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .product-header img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .product-header.placeholder {{
            color: rgba(255,255,255,0.7);
            font-size: 16px;
        }}
        .product-content {{
            padding: 32px;
        }}
        .product-title-section {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 16px;
        }}
        .product-name {{
            font-size: 32px;
            font-weight: 700;
            color: #111;
        }}
        .price {{
            font-size: 20px;
            font-weight: 700;
            color: #111;
            white-space: nowrap;
            margin-left: 20px;
        }}
        .badges {{
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .badge {{
            display: inline-block;
            padding: 6px 14px;
            border-radius: 16px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .badge-guaranteed {{
            background: #e6f7e6;
            color: #2d662d;
        }}
        .badge-bidded {{
            background: #fff4e6;
            color: #996633;
        }}
        .badge-asset-type {{
            background: #e6f0ff;
            color: #2563eb;
        }}
        .product-description {{
            font-size: 16px;
            line-height: 1.6;
            color: #333;
        }}
        .product-description p {{
            margin-bottom: 12px;
        }}
        .product-description h1,
        .product-description h2,
        .product-description h3 {{
            margin-top: 20px;
            margin-bottom: 12px;
            color: #111;
        }}
        .product-description ul,
        .product-description ol {{
            margin-left: 20px;
            margin-bottom: 12px;
        }}
        .preview-label {{
            position: absolute;
            top: 16px;
            right: 16px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 6px 12px;
            font-size: 12px;
            border-radius: 6px;
            z-index: 10;
        }}
    </style>
</head>
<body>
    <div class="product-card">
        <div class="product-header{"placeholder" if not image_url else ""}">
"""

        if image_url:
            html += f'            <img src="{html_module.escape(image_url)}" alt="{product_name}">\n'
        else:
            html += "            No Image Available\n"

        html += f"""            <div class="preview-label">{html_module.escape(input_set.name)}</div>
        </div>
        <div class="product-content">
            <div class="product-title-section">
                <div class="product-name">{product_name}</div>
                {price_str}
            </div>
            {badges_html}
            <div class="product-description">{description_html}</div>
        </div>
    </div>
</body>
</html>"""

        return html
