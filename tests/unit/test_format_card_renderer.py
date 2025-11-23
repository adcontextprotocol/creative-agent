"""Tests for format card renderer."""

import json

from adcp import FormatId

from creative_agent.data.standard_formats import AGENT_URL, filter_formats
from creative_agent.renderers.format_card_renderer import FormatCardRenderer


class TestFormatCardStandardRendering:
    """Test rendering of format_card_standard format."""

    def test_renders_basic_format_card(self):
        """Render a basic format card with minimal data."""
        renderer = FormatCardRenderer()

        # Get the format
        format_id = FormatId(agent_url=AGENT_URL, id="format_card_standard")
        formats = filter_formats(format_ids=[format_id])
        assert len(formats) == 1
        format_obj = formats[0]

        # Create manifest with format data as JSON
        format_spec = {
            "name": "Test Format",
            "type": "display",
            "description": "A test format for unit testing",
            "renders": [{"dimensions": {"width": 728, "height": 90}}],
        }

        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "format_card_standard"},
            "assets": {"format": {"content": json.dumps(format_spec)}},
        }

        # Create input set
        input_set = type("InputSet", (), {"name": "Desktop"})()

        # Render
        html = renderer.render(format_obj, manifest, input_set)

        # Verify HTML structure
        assert "<!DOCTYPE html>" in html
        assert "Test Format" in html
        assert "728x90" in html
        assert "display" in html
        assert "300px" in html  # Standard card width
        assert "400px" in html  # Standard card height

    def test_renders_card_with_markdown_description(self):
        """Render format card with markdown in description."""
        renderer = FormatCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="format_card_standard")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        format_spec = {
            "name": "Markdown Format",
            "description": "**Bold** and *italic* formatting\n\nNew paragraph",
            "type": "video",
        }

        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "format_card_standard"},
            "assets": {"format": {"content": json.dumps(format_spec)}},
        }

        input_set = type("InputSet", (), {"name": "Mobile"})()
        html = renderer.render(format_obj, manifest, input_set)

        # Verify markdown was converted
        assert "<strong>Bold</strong>" in html
        assert "<em>italic</em>" in html

    def test_renders_responsive_format(self):
        """Render format card for responsive format."""
        renderer = FormatCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="format_card_standard")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        format_spec = {
            "name": "Responsive Format",
            "description": "A format that adapts to viewport",
            "renders": [{"dimensions": {"responsive": {"width": True, "height": True}}}],
        }

        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "format_card_standard"},
            "assets": {"format": {"content": json.dumps(format_spec)}},
        }

        input_set = type("InputSet", (), {"name": "Desktop"})()
        html = renderer.render(format_obj, manifest, input_set)

        # Verify responsive label
        assert "Responsive" in html


class TestFormatCardDetailedRendering:
    """Test rendering of format_card_detailed format."""

    def test_renders_detailed_card_with_assets(self):
        """Render detailed card with asset requirements table."""
        renderer = FormatCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="format_card_detailed")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        format_spec = {
            "name": "Complex Format",
            "description": "## Features\n\n- Feature 1\n- Feature 2",
            "type": "display",
            "renders": [{"dimensions": {"width": 300, "height": 600}}],
            "assets_required": [
                {
                    "asset_id": "banner_image",
                    "asset_type": "image",
                    "required": True,
                    "requirements": {"description": "Main banner image"},
                },
                {
                    "asset_id": "logo",
                    "asset_type": "image",
                    "required": False,
                    "requirements": {"description": "Optional brand logo"},
                },
            ],
            "supported_macros": ["CLICK_URL", "DEVICE_TYPE", "CACHEBUSTER"],
        }

        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "format_card_detailed"},
            "assets": {"format": {"content": json.dumps(format_spec)}},
        }

        input_set = type("InputSet", (), {"name": "Desktop"})()
        html = renderer.render(format_obj, manifest, input_set)

        # Verify detailed card structure
        assert "Complex Format" in html
        assert "300x600" in html
        assert "Assets Required" in html
        assert "banner_image" in html
        assert "logo" in html
        assert "Required" in html
        assert "Optional" in html

        # Verify macros section
        assert "Supported Macros" in html
        assert "CLICK_URL" in html
        assert "DEVICE_TYPE" in html

        # Verify markdown heading was converted
        assert "<h2>" in html or "<H2>" in html
        assert "Features" in html

    def test_renders_detailed_card_without_assets(self):
        """Render detailed card with minimal format data."""
        renderer = FormatCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="format_card_detailed")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        format_spec = {
            "name": "Simple Format",
            "description": "Just a description",
        }

        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "format_card_detailed"},
            "assets": {"format": {"content": json.dumps(format_spec)}},
        }

        input_set = type("InputSet", (), {"name": "Desktop"})()
        html = renderer.render(format_obj, manifest, input_set)

        # Should render without assets or macros sections
        assert "Simple Format" in html
        assert "Just a description" in html
        # No sections shown when empty
        assert html.count("Assets Required") == 0 or html.count("<table") == 0

    def test_renders_detailed_card_responsive(self):
        """Verify detailed card is responsive (no fixed dimensions)."""
        renderer = FormatCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="format_card_detailed")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        format_spec = {"name": "Test", "description": "Test"}

        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "format_card_detailed"},
            "assets": {"format": {"content": json.dumps(format_spec)}},
        }

        input_set = type("InputSet", (), {"name": "Desktop"})()
        html = renderer.render(format_obj, manifest, input_set)

        # Verify responsive styling
        assert "max-width" in html or "min-height" in html
        # Should not have fixed width/height on body like standard card
        assert "width: 300px" not in html
        assert "width: 400px" not in html


class TestFormatCardFallbacks:
    """Test fallback behavior when data is missing."""

    def test_handles_missing_format_data(self):
        """Render card when format data is missing."""
        renderer = FormatCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="format_card_standard")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        # Manifest with empty format
        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "format_card_standard"},
            "assets": {"format": {}},
        }

        input_set = type("InputSet", (), {"name": "Desktop"})()
        html = renderer.render(format_obj, manifest, input_set)

        # Should render with defaults
        assert "<!DOCTYPE html>" in html
        assert "Creative Format" in html  # Default name

    def test_handles_none_manifest(self):
        """Render card when manifest is None."""
        renderer = FormatCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="format_card_standard")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        input_set = type("InputSet", (), {"name": "Desktop"})()
        html = renderer.render(format_obj, manifest=None, input_set=input_set)

        # Should render with defaults
        assert "<!DOCTYPE html>" in html
        assert "Creative Format" in html

    def test_handles_plain_text_description(self):
        """Render card when content is plain text, not JSON."""
        renderer = FormatCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="format_card_standard")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "format_card_standard"},
            "assets": {"format": {"content": "This is just plain text, not JSON"}},
        }

        input_set = type("InputSet", (), {"name": "Desktop"})()
        html = renderer.render(format_obj, manifest, input_set)

        # Should render with text as description
        assert "This is just plain text, not JSON" in html

    def test_handles_invalid_json(self):
        """Render card gracefully when JSON is malformed."""
        renderer = FormatCardRenderer()

        format_id = FormatId(agent_url=AGENT_URL, id="format_card_standard")
        formats = filter_formats(format_ids=[format_id])
        format_obj = formats[0]

        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "format_card_standard"},
            "assets": {"format": {"content": "{invalid json}}"}},
        }

        input_set = type("InputSet", (), {"name": "Desktop"})()
        html = renderer.render(format_obj, manifest, input_set)

        # Should render without crashing
        assert "<!DOCTYPE html>" in html
