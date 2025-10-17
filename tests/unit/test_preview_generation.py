"""Unit tests for preview generation functionality."""

import pytest

from creative_agent.data.standard_formats import AGENT_URL, get_format_by_id
from creative_agent.schemas.manifest import PreviewInput
from creative_agent.schemas_generated._schemas_v1_core_format_json import FormatId
from creative_agent.storage import generate_preview_html


class TestGeneratePreviewHtml:
    """Tests for generate_preview_html function."""

    @pytest.fixture
    def display_format(self):
        """Get a display format for testing."""
        return get_format_by_id(FormatId(agent_url=AGENT_URL, id="display_300x250_image"))

    @pytest.fixture
    def dict_manifest(self):
        """Create a test manifest as a dict (ADCP compliant)."""
        return {
            "format_id": {"agent_url": str(AGENT_URL), "id": "display_300x250_image"},
            "assets": {
                "banner_image": {
                    "asset_type": "image",
                    "url": "https://example.com/test.png",
                    "width": 300,
                    "height": 250,
                    "format": "png",
                },
                "landing_url": {"asset_type": "url", "url": "https://example.com/landing"},
            },
        }

    @pytest.fixture
    def input_set(self):
        """Create a test input set."""
        return PreviewInput(name="Desktop", macros={"DEVICE_TYPE": "desktop"})

    def test_generate_html_with_dict_manifest(self, display_format, dict_manifest, input_set):
        """Test that generate_preview_html works with dict manifests (ADCP spec)."""
        html = generate_preview_html(display_format, dict_manifest, input_set)

        assert isinstance(html, str)
        assert len(html) > 0
        assert "<!DOCTYPE html>" in html
        assert "https://example.com/test.png" in html
        assert "Desktop" in html

    def test_generate_html_extracts_image_url(self, display_format, dict_manifest, input_set):
        """Test that image URL is correctly extracted from manifest."""
        html = generate_preview_html(display_format, dict_manifest, input_set)

        assert 'src="https://example.com/test.png"' in html

    def test_generate_html_extracts_click_url(self, display_format, dict_manifest, input_set):
        """Test that click URL is correctly extracted from manifest."""
        html = generate_preview_html(display_format, dict_manifest, input_set)

        assert 'window.open("https://example.com/landing"' in html

    def test_generate_html_includes_dimensions(self, display_format, dict_manifest, input_set):
        """Test that format dimensions are included in HTML."""
        html = generate_preview_html(display_format, dict_manifest, input_set)

        assert "width: 300px" in html
        assert "height: 250px" in html

    def test_generate_html_with_no_image(self, display_format, input_set):
        """Test HTML generation when manifest has no image asset."""
        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "display_300x250_image"},
            "assets": {
                "landing_url": {"asset_type": "url", "url": "https://example.com/landing"}
            },
        }

        html = generate_preview_html(display_format, manifest, input_set)

        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html
        # Should have placeholder div instead of image
        assert "background: #f0f0f0" in html

    def test_generate_html_with_no_click_url(self, display_format, input_set):
        """Test HTML generation when manifest has no click URL."""
        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "display_300x250_image"},
            "assets": {
                "banner_image": {
                    "asset_type": "image",
                    "url": "https://example.com/test.png",
                    "width": 300,
                    "height": 250,
                }
            },
        }

        html = generate_preview_html(display_format, manifest, input_set)

        assert isinstance(html, str)
        assert 'console.log("Click registered - no URL configured")' in html

    def test_generate_html_with_data_uri_image(self, display_format, input_set):
        """Test HTML generation with data URI image."""
        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "display_300x250_image"},
            "assets": {
                "banner_image": {
                    "asset_type": "image",
                    "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                    "width": 300,
                    "height": 250,
                }
            },
        }

        html = generate_preview_html(display_format, manifest, input_set)

        # Data URI should be blocked by sanitization
        assert 'src="#"' in html

    def test_generate_html_sanitizes_javascript_urls(self, display_format, input_set):
        """Test that javascript: URLs are sanitized."""
        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "display_300x250_image"},
            "assets": {
                "banner_image": {
                    "asset_type": "image",
                    "url": "javascript:alert('xss')",
                    "width": 300,
                    "height": 250,
                }
            },
        }

        html = generate_preview_html(display_format, manifest, input_set)

        assert "javascript:" not in html
        assert 'src="#"' in html

    def test_generate_html_escapes_format_name(self, display_format, input_set):
        """Test that format name is HTML escaped."""
        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "display_300x250_image"},
            "assets": {},
        }

        html = generate_preview_html(display_format, manifest, input_set)

        # Format name should be present and properly escaped
        assert display_format.name in html or display_format.name.replace("&", "&amp;") in html

    def test_generate_html_with_different_input_names(self, display_format, dict_manifest):
        """Test HTML generation with different input set names."""
        for name in ["Mobile", "Tablet", "Desktop", "Custom Device"]:
            input_set = PreviewInput(name=name, macros={})
            html = generate_preview_html(display_format, dict_manifest, input_set)

            assert name in html

    def test_generate_html_with_video_format(self, dict_manifest, input_set):
        """Test HTML generation with video format."""
        video_format = get_format_by_id(FormatId(agent_url=AGENT_URL, id="video_standard_15s"))

        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "video_standard_15s"},
            "assets": {
                "video_file": {
                    "asset_type": "video",
                    "url": "https://example.com/video.mp4",
                    "width": 1920,
                    "height": 1080,
                    "duration_seconds": 15,
                }
            },
        }

        html = generate_preview_html(video_format, manifest, input_set)

        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html

    def test_generate_html_handles_empty_assets(self, display_format, input_set):
        """Test that empty assets dict doesn't crash."""
        manifest = {
            "format_id": {"agent_url": str(AGENT_URL), "id": "display_300x250_image"},
            "assets": {},
        }

        html = generate_preview_html(display_format, manifest, input_set)

        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html
