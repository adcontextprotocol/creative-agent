"""Unit tests for preview generation functionality.

These tests use generated Pydantic schemas to ensure 100% spec compliance.
"""

import pytest

from creative_agent.data.standard_formats import AGENT_URL, get_format_by_id
from creative_agent.schemas.manifest import PreviewInput
from creative_agent.schemas_generated._schemas_v1_creative_preview_creative_request_json import (
    Assets as ImageAsset,
)
from creative_agent.schemas_generated._schemas_v1_creative_preview_creative_request_json import (
    Assets31 as UrlAsset,
)
from creative_agent.schemas_generated._schemas_v1_creative_preview_creative_request_json import (
    CreativeManifest,
    FormatId,
)
from creative_agent.storage import generate_preview_html


class TestGeneratePreviewHtml:
    """Tests for generate_preview_html function using spec-compliant schemas."""

    @pytest.fixture
    def display_format(self):
        """Get a display format for testing."""
        return get_format_by_id(FormatId(agent_url=AGENT_URL, id="display_300x250_image"))

    @pytest.fixture
    def spec_compliant_manifest_dict(self):
        """Create a spec-compliant manifest as dict (what server.py passes).

        This uses the exact structure that Pydantic expects, validated by schema.
        """
        # First create Pydantic objects to ensure schema compliance
        manifest_obj = CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="display_300x250_image"),
            assets={
                "banner_image": ImageAsset(
                    asset_type="image",
                    url="https://example.com/test.png",
                    width=300,
                    height=250,
                    format="png",
                ),
                "click_url": UrlAsset(asset_type="url", url="https://example.com/landing"),
            },
        )

        # Convert to dict (this is what server.py line 169 receives)
        return manifest_obj.model_dump(mode="json")

    @pytest.fixture
    def input_set(self):
        """Create a test input set."""
        return PreviewInput(name="Desktop", macros={"DEVICE_TYPE": "desktop"})

    def test_generate_html_with_spec_compliant_manifest(self, display_format, spec_compliant_manifest_dict, input_set):
        """Test that generate_preview_html works with spec-compliant dict manifests."""
        html = generate_preview_html(display_format, spec_compliant_manifest_dict, input_set)

        assert isinstance(html, str)
        assert len(html) > 0
        assert "<!DOCTYPE html>" in html
        assert "https://example.com/test.png" in html
        assert "Desktop" in html

    def test_generate_html_extracts_image_url(self, display_format, spec_compliant_manifest_dict, input_set):
        """Test that image URL is correctly extracted from manifest."""
        html = generate_preview_html(display_format, spec_compliant_manifest_dict, input_set)

        assert 'src="https://example.com/test.png"' in html

    def test_generate_html_extracts_click_url(self, display_format, spec_compliant_manifest_dict, input_set):
        """Test that click URL is correctly extracted from manifest."""
        html = generate_preview_html(display_format, spec_compliant_manifest_dict, input_set)

        assert 'window.open("https://example.com/landing"' in html

    def test_generate_html_includes_dimensions(self, display_format, spec_compliant_manifest_dict, input_set):
        """Test that format dimensions are included in HTML."""
        html = generate_preview_html(display_format, spec_compliant_manifest_dict, input_set)

        assert "width: 300px" in html
        assert "height: 250px" in html

    def test_generate_html_sanitizes_javascript_urls(self, display_format, input_set):
        """Test that javascript: URLs are sanitized for security."""
        # Create manifest with malicious URL (still needs to be schema-valid structure)
        manifest = CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="display_300x250_image"),
            assets={
                "banner_image": ImageAsset(
                    asset_type="image",
                    url="https://example.com/safe.png",  # Must pass Pydantic validation
                    width=300,
                    height=250,
                ),
                "click_url": UrlAsset(asset_type="url", url="https://example.com/landing"),
            },
        ).model_dump(mode="json")

        # Manually inject malicious URL after validation (simulates attack)
        manifest["assets"]["banner_image"]["url"] = "javascript:alert('xss')"

        html = generate_preview_html(display_format, manifest, input_set)

        # Should be sanitized to safe placeholder
        assert "javascript:" not in html
        assert 'src="#"' in html

    def test_generate_html_escapes_format_name(self, display_format, spec_compliant_manifest_dict, input_set):
        """Test that format name is HTML escaped."""
        html = generate_preview_html(display_format, spec_compliant_manifest_dict, input_set)

        # Format name should be present and properly escaped
        assert display_format.name in html or display_format.name.replace("&", "&amp;") in html

    def test_generate_html_with_different_input_names(self, display_format, spec_compliant_manifest_dict):
        """Test HTML generation with different input set names."""
        for name in ["Mobile", "Tablet", "Desktop", "Custom Device"]:
            input_set = PreviewInput(name=name, macros={})
            html = generate_preview_html(display_format, spec_compliant_manifest_dict, input_set)

            assert name in html

    def test_generate_html_with_video_format(self, input_set):
        """Test HTML generation with video format."""
        from creative_agent.schemas_generated._schemas_v1_creative_preview_creative_request_json import (
            Assets27 as VideoAsset,
        )

        video_format = get_format_by_id(FormatId(agent_url=AGENT_URL, id="video_standard_15s"))

        manifest = CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="video_standard_15s"),
            assets={
                "video_file": VideoAsset(
                    asset_type="video",
                    url="https://example.com/video.mp4",
                    width=1920,
                    height=1080,
                    duration_seconds=15.0,
                    format="mp4",
                ),
                "click_url": UrlAsset(asset_type="url", url="https://example.com/landing"),
            },
        ).model_dump(mode="json")

        html = generate_preview_html(video_format, manifest, input_set)

        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html

    def test_pydantic_validation_catches_invalid_dimensions(self):
        """Test that Pydantic validates image dimensions per schema."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            # Width must be >= 1 per schema
            ImageAsset(
                asset_type="image",
                url="https://example.com/test.png",
                width=0,  # Invalid!
                height=250,
            )

    def test_pydantic_validation_catches_invalid_urls(self):
        """Test that Pydantic validates URLs per schema."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            UrlAsset(
                asset_type="url",
                url="not-a-valid-url",  # Invalid URL format
            )

    def test_manifest_can_have_optional_assets_not_required_by_format(self, display_format, input_set):
        """Test that manifests can include optional assets beyond format requirements."""
        from creative_agent.schemas_generated._schemas_v1_creative_preview_creative_request_json import (
            Assets30 as TextAsset,
        )

        # Include optional headline text asset (not required by format)
        manifest = CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="display_300x250_image"),
            assets={
                "banner_image": ImageAsset(
                    asset_type="image",
                    url="https://example.com/test.png",
                    width=300,
                    height=250,
                ),
                "click_url": UrlAsset(asset_type="url", url="https://example.com/landing"),
                "optional_headline": TextAsset(asset_type="text", content="Buy Now!", format="plain"),
            },
        ).model_dump(mode="json")

        html = generate_preview_html(display_format, manifest, input_set)

        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html
