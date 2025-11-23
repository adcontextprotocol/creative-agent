"""Tests for product card renderer."""

from adcp import FormatId

from creative_agent.data.standard_formats import AGENT_URL, filter_formats
from creative_agent.renderers.product_card_renderer import ProductCardRenderer


class TestProductCardStandardRendering:
    """Test rendering of product_card_standard format."""

    def test_renders_basic_product_card(self):
        """Render a basic product card with minimal data."""
        renderer = ProductCardRenderer()

        # Get the format
        format_id = FormatId(agent_url=AGENT_URL, id="product_card_standard")
        formats = filter_formats(format_ids=[format_id])
        assert len(formats) == 1
        format_obj = formats[0]

        # Create manifest with individual product assets
        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "product_card_standard"},
            "assets": {
                "product_image": {"url": "https://example.com/product.jpg"},
                "product_name": {"content": "Test Product"},
                "product_description": {"content": "A great product for testing"},
                "pricing_model": {"content": "CPM"},
                "pricing_amount": {"content": "29.99"},
                "pricing_currency": {"content": "USD"},
                "delivery_type": {"content": "guaranteed"},
                "primary_asset_type": {"content": "display"},
            },
        }

        # Create input set
        input_set = type("InputSet", (), {"name": "Desktop"})()

        # Render
        html = renderer.render(format_obj, manifest, input_set)

        # Verify HTML structure
        assert "<!DOCTYPE html>" in html
        assert "Test Product" in html
        assert "A great product for testing" in html
        assert "CPM $29.99 USD" in html
        assert "https://example.com/product.jpg" in html
        assert "300px" in html  # Standard card width
        assert "400px" in html  # Standard card height
        assert "guaranteed" in html
        assert "display" in html

    def test_renders_card_with_markdown_description(self):
        """Render product card with markdown in description."""
        renderer = ProductCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="product_card_standard")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "product_card_standard"},
            "assets": {
                "product_name": {"content": "Markdown Product"},
                "product_description": {"content": "**Bold text** and *italic text*\n\nNew paragraph"},
            },
        }

        input_set = type("InputSet", (), {"name": "Mobile"})()
        html = renderer.render(format_obj, manifest, input_set)

        # Verify markdown was converted to HTML
        assert "<strong>Bold text</strong>" in html
        assert "<em>italic text</em>" in html
        assert "<p>" in html

    def test_renders_card_without_image(self):
        """Render product card when no image is available."""
        renderer = ProductCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="product_card_standard")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "product_card_standard"},
            "assets": {
                "product_name": {"content": "No Image Product"},
                "product_description": {"content": "Test"},
            },
        }

        input_set = type("InputSet", (), {"name": "Desktop"})()
        html = renderer.render(format_obj, manifest, input_set)

        # Verify placeholder is shown
        assert "No Image Available" in html
        assert "No Image Product" in html


class TestProductCardDetailedRendering:
    """Test rendering of product_card_detailed format."""

    def test_renders_detailed_card_with_all_data(self):
        """Render detailed card with complete product data."""
        renderer = ProductCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="product_card_detailed")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "product_card_detailed"},
            "assets": {
                "product_image": {"url": "https://example.com/detailed.jpg"},
                "product_name": {"content": "Premium Product"},
                "product_description": {"content": "## Features\n\n- Feature 1\n- Feature 2\n\n**Bold statement**"},
                "pricing_model": {"content": "CPM"},
                "pricing_amount": {"content": "45.00"},
                "pricing_currency": {"content": "USD"},
                "delivery_type": {"content": "bidded"},
                "primary_asset_type": {"content": "video"},
            },
        }

        input_set = type("InputSet", (), {"name": "Desktop"})()
        html = renderer.render(format_obj, manifest, input_set)

        # Verify detailed card structure
        assert "Premium Product" in html
        assert "CPM $45.00 USD" in html
        assert "bidded" in html
        assert "video" in html
        assert "<h2>" in html or "<H2>" in html  # Markdown heading
        assert "Feature 1" in html
        assert "<strong>Bold statement</strong>" in html

    def test_renders_detailed_card_without_optional_data(self):
        """Render detailed card with minimal data."""
        renderer = ProductCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="product_card_detailed")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "product_card_detailed"},
            "assets": {
                "product_name": {"content": "Simple Product"},
                "product_description": {"content": "Just a description"},
            },
        }

        input_set = type("InputSet", (), {"name": "Desktop"})()
        html = renderer.render(format_obj, manifest, input_set)

        # Should render without pricing or badges
        assert "Simple Product" in html
        assert "Just a description" in html
        # No badge elements shown when data is missing (class definitions in CSS don't count)
        assert '<span class="badge' not in html

    def test_renders_detailed_card_responsive(self):
        """Verify detailed card is responsive (no fixed dimensions)."""
        renderer = ProductCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="product_card_detailed")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "product_card_detailed"},
            "assets": {
                "product_name": {"content": "Test"},
                "product_description": {"content": "Test"},
            },
        }

        input_set = type("InputSet", (), {"name": "Desktop"})()
        html = renderer.render(format_obj, manifest, input_set)

        # Verify responsive styling
        assert "max-width" in html or "min-height" in html
        # Should not have fixed width/height on body like standard card
        assert "width: 300px" not in html
        assert "width: 400px" not in html


class TestProductCardFallbacks:
    """Test fallback behavior when data is missing."""

    def test_handles_missing_product_data(self):
        """Render card when product data is missing."""
        renderer = ProductCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="product_card_standard")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        # Manifest with empty assets
        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "product_card_standard"},
            "assets": {},
        }

        input_set = type("InputSet", (), {"name": "Desktop"})()
        html = renderer.render(format_obj, manifest, input_set)

        # Should render with defaults
        assert "<!DOCTYPE html>" in html
        assert "Media Product" in html  # Default name
        assert "Product description not available" in html

    def test_handles_none_manifest(self):
        """Render card when manifest is None."""
        renderer = ProductCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="product_card_standard")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        input_set = type("InputSet", (), {"name": "Desktop"})()
        html = renderer.render(format_obj, manifest=None, input_set=input_set)

        # Should render with defaults
        assert "<!DOCTYPE html>" in html
        assert "Media Product" in html

    def test_handles_incomplete_pricing(self):
        """Render card when pricing data is incomplete."""
        renderer = ProductCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="product_card_standard")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "product_card_standard"},
            "assets": {
                "product_name": {"content": "Test Product"},
                "product_description": {"content": "Description"},
                "pricing_model": {"content": "CPM"},
                # Missing pricing_amount - should not show price
            },
        }

        input_set = type("InputSet", (), {"name": "Desktop"})()
        html = renderer.render(format_obj, manifest, input_set)

        # Should not show incomplete pricing
        assert "CPM $" not in html
        assert "Test Product" in html
