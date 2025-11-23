"""Integration tests for HTML output and batch preview modes."""

import pytest
from adcp import FormatId, PreviewCreativeResponse

from creative_agent import server
from creative_agent.data.standard_formats import AGENT_URL
from creative_agent.schemas import CreativeManifest

# Get the actual function from the FastMCP wrapper
preview_creative = server.preview_creative.fn


class TestHTMLOutputMode:
    """Test HTML output format."""

    @pytest.fixture(autouse=True)
    def mock_s3_upload(self, mocker):
        """Mock S3 upload for all tests."""
        return mocker.patch(
            "creative_agent.storage.upload_preview_html",
            return_value="https://adcp-previews.fly.storage.tigris.dev/previews/test-id/desktop.html",
        )

    def test_html_output_returns_preview_html(self):
        """Test that output_format='html' returns preview_html field."""
        manifest = CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="display_300x250_image"),
            assets={
                "banner_image": {
                    "url": "https://example.com/banner.png",
                    "width": 300,
                    "height": 250,
                },
                "click_url": {"url": "https://example.com/landing"},
            },
        )

        result = preview_creative(
            format_id="display_300x250_image",
            creative_manifest=manifest.model_dump(mode="json"),
            output_format="html",
        )

        structured = result.structured_content

        # Check for errors first
        if "error" in structured:
            pytest.fail(f"Preview failed with error: {structured['error']}")

        # Validate response structure
        response = PreviewCreativeResponse.model_validate(structured)
        assert hasattr(response.root, "previews")

        # Check that preview_html is present
        first_preview = response.root.previews[0]
        first_render = first_preview.renders[0]
        assert first_render.preview_html is not None
        assert isinstance(first_render.preview_html, str)
        assert len(first_render.preview_html) > 0

        # Verify output_format discriminator
        assert first_render.output_format == "html"
        # With discriminated unions, preview_url field doesn't exist for "html" variant
        assert not hasattr(first_render, "preview_url")

        # HTML should contain expected elements
        assert "<div" in first_render.preview_html or "<html" in first_render.preview_html

    def test_html_output_does_not_upload_to_s3(self, mock_s3_upload):
        """Test that HTML output mode doesn't upload to S3."""
        manifest = CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="display_300x250_image"),
            assets={
                "banner_image": {
                    "url": "https://example.com/banner.png",
                    "width": 300,
                    "height": 250,
                },
                "click_url": {"url": "https://example.com/landing"},
            },
        )

        preview_creative(
            format_id="display_300x250_image",
            creative_manifest=manifest.model_dump(mode="json"),
            output_format="html",
        )

        # S3 upload should not be called for HTML output
        mock_s3_upload.assert_not_called()

    def test_url_output_still_works(self, mock_s3_upload):
        """Test that default URL output mode still works."""
        manifest = CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="display_300x250_image"),
            assets={
                "banner_image": {
                    "url": "https://example.com/banner.png",
                    "width": 300,
                    "height": 250,
                },
                "click_url": {"url": "https://example.com/landing"},
            },
        )

        result = preview_creative(
            format_id="display_300x250_image",
            creative_manifest=manifest.model_dump(mode="json"),
            output_format="url",
        )

        structured = result.structured_content

        # Validate response structure
        response = PreviewCreativeResponse.model_validate(structured)
        first_preview = response.root.previews[0]
        first_render = first_preview.renders[0]

        # URL mode should have preview_url
        assert first_render.preview_url is not None
        assert str(first_render.preview_url).startswith("https://")

        # Verify output_format discriminator
        assert first_render.output_format == "url"
        # With discriminated unions, preview_html field doesn't exist for "url" variant
        assert not hasattr(first_render, "preview_html")

        # S3 upload should be called 3 times (desktop, mobile, tablet)
        assert mock_s3_upload.call_count == 3


class TestBatchPreviewMode:
    """Test batch preview mode."""

    @pytest.fixture(autouse=True)
    def mock_s3_upload(self, mocker):
        """Mock S3 upload for all tests."""
        return mocker.patch(
            "creative_agent.storage.upload_preview_html",
            return_value="https://adcp-previews.fly.storage.tigris.dev/previews/test-id/desktop.html",
        )

    def test_batch_mode_with_multiple_requests(self):
        """Test batch mode with multiple preview requests."""
        manifest1 = CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="display_300x250_image"),
            assets={
                "banner_image": {
                    "url": "https://example.com/banner1.png",
                    "width": 300,
                    "height": 250,
                },
                "click_url": {"url": "https://example.com/landing1"},
            },
        )

        manifest2 = CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="display_728x90_image"),
            assets={
                "banner_image": {
                    "url": "https://example.com/banner2.png",
                    "width": 728,
                    "height": 90,
                },
                "click_url": {"url": "https://example.com/landing2"},
            },
        )

        result = preview_creative(
            requests=[
                {
                    "format_id": "display_300x250_image",
                    "creative_manifest": manifest1.model_dump(mode="json"),
                },
                {
                    "format_id": "display_728x90_image",
                    "creative_manifest": manifest2.model_dump(mode="json"),
                },
            ]
        )

        structured = result.structured_content

        # Batch response should have results array
        assert "results" in structured
        assert len(structured["results"]) == 2

        # Both should succeed
        assert structured["results"][0]["success"] is True
        assert structured["results"][1]["success"] is True

        # Each result should have a valid response
        assert "response" in structured["results"][0]
        assert "response" in structured["results"][1]

        # Each response should have previews
        assert "previews" in structured["results"][0]["response"]
        assert "previews" in structured["results"][1]["response"]

    def test_batch_mode_with_html_output(self):
        """Test batch mode with HTML output format."""
        manifest = CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="display_300x250_image"),
            assets={
                "banner_image": {
                    "url": "https://example.com/banner.png",
                    "width": 300,
                    "height": 250,
                },
                "click_url": {"url": "https://example.com/landing"},
            },
        )

        result = preview_creative(
            requests=[
                {
                    "format_id": "display_300x250_image",
                    "creative_manifest": manifest.model_dump(mode="json"),
                }
            ],
            output_format="html",
        )

        structured = result.structured_content

        # Check HTML is returned
        first_result = structured["results"][0]
        assert first_result["success"] is True
        first_preview = first_result["response"]["previews"][0]
        first_render = first_preview["renders"][0]
        assert "preview_html" in first_render
        assert isinstance(first_render["preview_html"], str)
        assert len(first_render["preview_html"]) > 0

        # Verify output_format discriminator
        assert first_render["output_format"] == "html"
        assert "preview_url" not in first_render or first_render.get("preview_url") is None

    def test_batch_mode_handles_errors_gracefully(self):
        """Test that batch mode handles individual request errors."""
        valid_manifest = CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="display_300x250_image"),
            assets={
                "banner_image": {
                    "url": "https://example.com/banner.png",
                    "width": 300,
                    "height": 250,
                },
                "click_url": {"url": "https://example.com/landing"},
            },
        )

        # Second request has invalid format
        result = preview_creative(
            requests=[
                {
                    "format_id": "display_300x250_image",
                    "creative_manifest": valid_manifest.model_dump(mode="json"),
                },
                {
                    "format_id": "nonexistent_format",
                    "creative_manifest": valid_manifest.model_dump(mode="json"),
                },
            ]
        )

        structured = result.structured_content

        # Should have 2 results
        assert len(structured["results"]) == 2

        # First should succeed
        assert structured["results"][0]["success"] is True

        # Second should fail
        assert structured["results"][1]["success"] is False
        assert "error" in structured["results"][1]
        assert "message" in structured["results"][1]["error"]

    def test_batch_mode_per_request_output_format_override(self):
        """Test that individual requests can override batch output_format."""
        manifest = CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="display_300x250_image"),
            assets={
                "banner_image": {
                    "url": "https://example.com/banner.png",
                    "width": 300,
                    "height": 250,
                },
                "click_url": {"url": "https://example.com/landing"},
            },
        )

        result = preview_creative(
            requests=[
                {
                    "format_id": "display_300x250_image",
                    "creative_manifest": manifest.model_dump(mode="json"),
                    "output_format": "url",  # Override to URL
                },
                {
                    "format_id": "display_300x250_image",
                    "creative_manifest": manifest.model_dump(mode="json"),
                    # Uses default HTML from batch level
                },
            ],
            output_format="html",  # Batch level default
        )

        structured = result.structured_content

        # First request should have URL (overridden)
        first_render = structured["results"][0]["response"]["previews"][0]["renders"][0]
        assert "preview_url" in first_render
        assert first_render["output_format"] == "url"

        # Second request should have HTML (default)
        second_render = structured["results"][1]["response"]["previews"][0]["renders"][0]
        assert "preview_html" in second_render
        assert second_render["output_format"] == "html"
