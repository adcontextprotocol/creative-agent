"""Renderer for product card formats."""

import html as html_module
from typing import Any

import markdown  # type: ignore[import-untyped]

from .base import BaseRenderer


class ProductCardRenderer(BaseRenderer):
    """Renderer for product_card_standard and product_card_detailed formats."""

    def render(self, format_obj: Any, manifest: Any, input_set: Any) -> str:
        """Generate HTML preview for product card formats.

        Args:
            format_obj: Format definition (product_card_standard or product_card_detailed)
            manifest: Creative manifest with promoted_offerings asset
            input_set: Preview input configuration

        Returns:
            HTML string with product card display
        """
        width, height = self.get_dimensions(format_obj)
        manifest_assets = self.get_manifest_assets(manifest)
        asset_type_map = self.build_asset_type_map(format_obj)

        # Find promoted_offerings asset
        product_asset = self.find_asset_by_type(manifest_assets, asset_type_map, "promoted_offerings")

        # Extract product data
        product_data = self._extract_product_data(product_asset)
        brand_data = self._extract_brand_data(product_asset)

        # Check if this is a detailed card (responsive)
        is_detailed = format_obj.format_id.id == "product_card_detailed"

        # Generate HTML
        if is_detailed:
            return self._render_detailed_card(format_obj, input_set, product_data, brand_data)
        return self._render_standard_card(format_obj, input_set, product_data, brand_data, width, height)

    def _extract_product_data(self, product_asset: Any) -> dict[str, Any]:
        """Extract first product from promoted_offerings asset.

        Args:
            product_asset: promoted_offerings asset data

        Returns:
            Product data dictionary with fallback values
        """
        default: dict[str, Any] = {
            "name": "Product Name",
            "description": "Product description not available",
            "images": [],
            "price": None,
            "url": None,
        }

        if not product_asset or not isinstance(product_asset, dict):
            return default

        # Try to get offering data
        offering = product_asset.get("offering", {})
        if not isinstance(offering, dict):
            return default

        # Extract product fields
        return {
            "name": offering.get("name", default["name"]),
            "description": offering.get("description", default["description"]),
            "images": offering.get("images", []),
            "price": offering.get("price"),
            "currency": offering.get("currency"),
            "url": offering.get("url"),
            "categories": offering.get("categories", []),
        }

    def _extract_brand_data(self, product_asset: Any) -> dict[str, Any]:
        """Extract brand data from promoted_offerings asset.

        Args:
            product_asset: promoted_offerings asset data

        Returns:
            Brand data dictionary with fallback values
        """
        default: dict[str, Any] = {"name": None, "colors": {}, "logos": []}

        if not product_asset or not isinstance(product_asset, dict):
            return default

        brand = product_asset.get("brand", {})
        if not isinstance(brand, dict):
            return default

        return {
            "name": brand.get("name"),
            "colors": brand.get("colors", {}),
            "logos": brand.get("logos", []),
        }

    def _render_standard_card(
        self,
        format_obj: Any,
        input_set: Any,
        product_data: dict[str, Any],
        brand_data: dict[str, Any],
        width: int,
        height: int,
    ) -> str:
        """Render standard 300x400 product card.

        Args:
            format_obj: Format definition
            input_set: Preview input
            product_data: Product information
            brand_data: Brand information
            width: Card width in pixels
            height: Card height in pixels

        Returns:
            HTML string
        """
        # Get brand colors or use defaults
        colors = brand_data.get("colors", {})
        primary_color = colors.get("primary", "#333333")
        text_color = colors.get("text", "#000000")

        # Get first product image
        images = product_data.get("images", [])
        image_url = images[0] if images else None

        # Convert description markdown to HTML
        description = product_data.get("description", "")
        description_html = markdown.markdown(description, extensions=["extra", "nl2br"])

        # Format price
        price_str = ""
        if product_data.get("price"):
            currency = product_data.get("currency", "USD")
            price = product_data["price"]
            price_str = f'<div class="price">{currency} {price:.2f}</div>'

        # Safe escape
        product_name = html_module.escape(product_data.get("name", "Product"))
        product_url = product_data.get("url", "#")

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
            height: 60%;
            background: #f5f5f5;
            overflow: hidden;
            position: relative;
        }}
        .product-image img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .product-image.placeholder {{
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
            font-size: 14px;
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
            color: {text_color};
            margin-bottom: 6px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .product-description {{
            font-size: 12px;
            color: #666;
            line-height: 1.4;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            flex: 1;
        }}
        .product-description p {{
            margin: 0;
        }}
        .price {{
            font-size: 18px;
            font-weight: 700;
            color: {primary_color};
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
    <div class="product-card" onclick="window.open('{product_url}', '_blank')">
        <div class="product-image{"placeholder" if not image_url else ""}">
"""

        if image_url:
            html += f'            <img src="{image_url}" alt="{product_name}">\n'
        else:
            html += "            No Image Available\n"

        html += f"""            <div class="preview-label">{html_module.escape(input_set.name)}</div>
        </div>
        <div class="product-info">
            <div class="product-name">{product_name}</div>
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
        brand_data: dict[str, Any],
    ) -> str:
        """Render detailed responsive product card with carousel.

        Args:
            format_obj: Format definition
            input_set: Preview input
            product_data: Product information
            brand_data: Brand information

        Returns:
            HTML string
        """
        # Get brand colors or use defaults
        colors = brand_data.get("colors", {})
        primary_color = colors.get("primary", "#333333")
        text_color = colors.get("text", "#000000")

        # Get all product images
        images = product_data.get("images", [])
        has_multiple_images = len(images) > 1

        # Convert description markdown to HTML
        description = product_data.get("description", "")
        description_html = markdown.markdown(description, extensions=["extra", "nl2br"])

        # Format price
        price_str = ""
        if product_data.get("price"):
            currency = product_data.get("currency", "USD")
            price = product_data["price"]
            price_str = f'<div class="price">{currency} {price:.2f}</div>'

        # Safe escape
        product_name = html_module.escape(product_data.get("name", "Product"))
        product_url = product_data.get("url", "#")
        categories = product_data.get("categories", [])
        category_html = ""
        if categories:
            category_tags = " ".join(f'<span class="category">{html_module.escape(cat)}</span>' for cat in categories)
            category_html = f'<div class="categories">{category_tags}</div>'

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
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .carousel {{
            position: relative;
            width: 100%;
            height: 400px;
            background: #f5f5f5;
            overflow: hidden;
        }}
        .carousel-track {{
            display: flex;
            transition: transform 0.3s ease;
            height: 100%;
        }}
        .carousel-slide {{
            min-width: 100%;
            height: 100%;
        }}
        .carousel-slide img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .carousel-nav {{
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            width: 100%;
            display: flex;
            justify-content: space-between;
            padding: 0 10px;
            pointer-events: none;
        }}
        .carousel-btn {{
            pointer-events: all;
            background: rgba(0,0,0,0.5);
            color: white;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .carousel-btn:hover {{
            background: rgba(0,0,0,0.7);
        }}
        .carousel-dots {{
            position: absolute;
            bottom: 10px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 8px;
        }}
        .dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: rgba(255,255,255,0.5);
            cursor: pointer;
        }}
        .dot.active {{
            background: white;
        }}
        .product-content {{
            padding: 24px;
        }}
        .product-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 16px;
        }}
        .product-name {{
            font-size: 28px;
            font-weight: 700;
            color: {text_color};
        }}
        .price {{
            font-size: 24px;
            font-weight: 700;
            color: {primary_color};
            white-space: nowrap;
            margin-left: 16px;
        }}
        .categories {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 16px;
        }}
        .category {{
            display: inline-block;
            padding: 4px 12px;
            background: #f0f0f0;
            border-radius: 16px;
            font-size: 12px;
            color: #666;
        }}
        .product-description {{
            font-size: 16px;
            line-height: 1.6;
            color: #333;
            margin-bottom: 24px;
        }}
        .product-description p {{
            margin-bottom: 12px;
        }}
        .cta-button {{
            display: inline-block;
            padding: 12px 32px;
            background: {primary_color};
            color: white;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            cursor: pointer;
        }}
        .cta-button:hover {{
            opacity: 0.9;
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
        <div class="carousel">
            <div class="carousel-track" id="carouselTrack">
"""

        # Add carousel slides
        if images:
            for i, img_url in enumerate(images):
                html += f"""                <div class="carousel-slide">
                    <img src="{img_url}" alt="{product_name} - Image {i + 1}">
                </div>
"""
        else:
            html += """                <div class="carousel-slide" style="display: flex; align-items: center; justify-content: center; color: #999;">
                    No Images Available
                </div>
"""

        html += f"""            </div>
            <div class="preview-label">{html_module.escape(input_set.name)}</div>
"""

        # Add carousel navigation if multiple images
        if has_multiple_images:
            html += """            <div class="carousel-nav">
                <button class="carousel-btn" onclick="previousSlide()">&lsaquo;</button>
                <button class="carousel-btn" onclick="nextSlide()">&rsaquo;</button>
            </div>
            <div class="carousel-dots" id="carouselDots"></div>
"""

        html += f"""        </div>
        <div class="product-content">
            <div class="product-header">
                <div class="product-name">{product_name}</div>
                {price_str}
            </div>
            {category_html}
            <div class="product-description">{description_html}</div>
            <a href="{product_url}" class="cta-button" target="_blank">View Product</a>
        </div>
    </div>
"""

        # Add carousel JavaScript if multiple images
        if has_multiple_images:
            html += f"""    <script>
        let currentSlide = 0;
        const totalSlides = {len(images)};
        const track = document.getElementById('carouselTrack');
        const dotsContainer = document.getElementById('carouselDots');

        // Create dots
        for (let i = 0; i < totalSlides; i++) {{
            const dot = document.createElement('div');
            dot.className = 'dot' + (i === 0 ? ' active' : '');
            dot.onclick = () => goToSlide(i);
            dotsContainer.appendChild(dot);
        }}

        function updateCarousel() {{
            track.style.transform = `translateX(-${{currentSlide * 100}}%)`;
            const dots = dotsContainer.querySelectorAll('.dot');
            dots.forEach((dot, index) => {{
                dot.className = 'dot' + (index === currentSlide ? ' active' : '');
            }});
        }}

        function nextSlide() {{
            currentSlide = (currentSlide + 1) % totalSlides;
            updateCarousel();
        }}

        function previousSlide() {{
            currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
            updateCarousel();
        }}

        function goToSlide(index) {{
            currentSlide = index;
            updateCarousel();
        }}
    </script>
"""

        html += """</body>
</html>"""

        return html
