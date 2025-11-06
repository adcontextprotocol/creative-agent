"""Tests for product card renderer."""

from creative_agent.data.standard_formats import AGENT_URL, filter_formats
from creative_agent.renderers.product_card_renderer import ProductCardRenderer
from creative_agent.schemas_generated._schemas_v1_core_format_json import FormatId


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

        # Create manifest with product data
        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "product_card_standard"},
            "assets": {
                "product": {
                    "offering": {
                        "name": "Test Product",
                        "description": "A great product for testing",
                        "price": 29.99,
                        "currency": "USD",
                        "images": ["https://example.com/product.jpg"],
                        "url": "https://example.com/product",
                    },
                    "brand": {"name": "Test Brand", "colors": {"primary": "#FF6B6B"}},
                }
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
        assert "USD 29.99" in html
        assert "https://example.com/product.jpg" in html
        assert "300px" in html  # Standard card width
        assert "400px" in html  # Standard card height

    def test_renders_card_with_markdown_description(self):
        """Render product card with markdown in description."""
        renderer = ProductCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="product_card_standard")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "product_card_standard"},
            "assets": {
                "product": {
                    "offering": {
                        "name": "Markdown Product",
                        "description": "**Bold text** and *italic text*\n\nNew paragraph",
                        "images": [],
                    },
                    "brand": {},
                }
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
                "product": {
                    "offering": {"name": "No Image Product", "description": "Test", "images": []},
                    "brand": {},
                }
            },
        }

        input_set = type("InputSet", (), {"name": "Desktop"})()
        html = renderer.render(format_obj, manifest, input_set)

        # Verify placeholder is shown
        assert "No Image Available" in html or "placeholder" in html

    def test_renders_card_with_brand_colors(self):
        """Render product card using brand colors."""
        renderer = ProductCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="product_card_standard")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "product_card_standard"},
            "assets": {
                "product": {
                    "offering": {"name": "Branded Product", "description": "Test"},
                    "brand": {"colors": {"primary": "#1E40AF", "text": "#111827"}},
                }
            },
        }

        input_set = type("InputSet", (), {"name": "Desktop"})()
        html = renderer.render(format_obj, manifest, input_set)

        # Verify brand colors are applied
        assert "#1E40AF" in html
        assert "#111827" in html


class TestProductCardDetailedRendering:
    """Test rendering of product_card_detailed format."""

    def test_renders_detailed_card_with_carousel(self):
        """Render detailed card with multiple images in carousel."""
        renderer = ProductCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="product_card_detailed")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "product_card_detailed"},
            "assets": {
                "product": {
                    "offering": {
                        "name": "Premium Product",
                        "description": "## Features\n\n- Feature 1\n- Feature 2\n- Feature 3",
                        "price": 99.99,
                        "currency": "EUR",
                        "images": [
                            "https://example.com/img1.jpg",
                            "https://example.com/img2.jpg",
                            "https://example.com/img3.jpg",
                        ],
                        "url": "https://example.com/premium",
                        "categories": ["electronics", "premium"],
                    },
                    "brand": {"name": "Premium Brand"},
                }
            },
        }

        input_set = type("InputSet", (), {"name": "Desktop"})()
        html = renderer.render(format_obj, manifest, input_set)

        # Verify detailed card structure
        assert "Premium Product" in html
        assert "EUR 99.99" in html
        assert "carousel" in html.lower()
        assert "https://example.com/img1.jpg" in html
        assert "https://example.com/img2.jpg" in html
        assert "https://example.com/img3.jpg" in html

        # Verify carousel JavaScript is included
        assert "nextSlide" in html
        assert "previousSlide" in html
        assert "currentSlide" in html

        # Verify categories are shown
        assert "electronics" in html
        assert "premium" in html

        # Verify markdown heading was converted
        assert "<h2>" in html or "<H2>" in html  # Case insensitive check
        assert "Features" in html

    def test_renders_detailed_card_without_carousel(self):
        """Render detailed card with single image (no carousel needed)."""
        renderer = ProductCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="product_card_detailed")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "product_card_detailed"},
            "assets": {
                "product": {
                    "offering": {
                        "name": "Single Image Product",
                        "description": "Only one image",
                        "images": ["https://example.com/single.jpg"],
                    },
                    "brand": {},
                }
            },
        }

        input_set = type("InputSet", (), {"name": "Desktop"})()
        html = renderer.render(format_obj, manifest, input_set)

        # Verify no carousel navigation for single image
        assert "nextSlide" not in html
        assert "previousSlide" not in html

    def test_renders_detailed_card_responsive(self):
        """Verify detailed card is responsive (no fixed dimensions)."""
        renderer = ProductCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="product_card_detailed")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "product_card_detailed"},
            "assets": {"product": {"offering": {"name": "Test", "description": "Test"}, "brand": {}}},
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
        """Render card when product data is missing or malformed."""
        renderer = ProductCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="product_card_standard")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        # Manifest with empty product
        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "product_card_standard"},
            "assets": {"product": {}},
        }

        input_set = type("InputSet", (), {"name": "Desktop"})()
        html = renderer.render(format_obj, manifest, input_set)

        # Should render with defaults
        assert "<!DOCTYPE html>" in html
        assert "Product Name" in html  # Default name

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
        assert "Product Name" in html

    def test_handles_missing_price(self):
        """Render card when price is not provided."""
        renderer = ProductCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="product_card_standard")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "product_card_standard"},
            "assets": {
                "product": {
                    "offering": {"name": "No Price Product", "description": "Test"},
                    "brand": {},
                }
            },
        }

        input_set = type("InputSet", (), {"name": "Desktop"})()
        html = renderer.render(format_obj, manifest, input_set)

        # Should render without price section
        assert "No Price Product" in html
        assert html.count('<div class="price">') == 0 or "USD" not in html
