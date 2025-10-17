"""Integration tests for preview_creative tool.

All tests use generated Pydantic schemas to ensure 100% ADCP spec compliance.
"""

from datetime import UTC, datetime

import pytest
from pytest_mock import MockerFixture

from creative_agent import server
from creative_agent.data.standard_formats import AGENT_URL
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

# Get the actual function from the FastMCP wrapper
preview_creative = server.preview_creative.fn


@pytest.fixture
def mock_s3_upload(mocker: MockerFixture):
    """Mock S3 upload to avoid network calls."""
    mock_upload = mocker.patch("creative_agent.storage.upload_preview_html")
    mock_upload.return_value = "https://adcp-previews.fly.storage.tigris.dev/previews/test-id/desktop.html"
    return mock_upload


class TestPreviewCreativeIntegration:
    """Integration tests for the preview_creative tool using spec-compliant schemas."""

    def test_preview_creative_with_spec_compliant_manifest(self, mock_s3_upload):
        """Test preview_creative tool with fully spec-compliant manifest."""
        # Create spec-compliant Pydantic manifest
        manifest = CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="display_300x250_image"),
            assets={
                "banner_image": ImageAsset(
                    asset_type="image",
                    url="https://example.com/banner.png",
                    width=300,
                    height=250,
                    format="png",
                ),
                "click_url": UrlAsset(
                    asset_type="url",
                    url="https://example.com/landing",
                ),
            },
        )

        # Convert to dict as server.py does
        result = preview_creative(
            format_id="display_300x250_image",
            creative_manifest=manifest.model_dump(mode="json"),
        )

        structured = result.structured_content

        # Verify response structure
        assert "previews" in structured
        assert isinstance(structured["previews"], list)
        assert len(structured["previews"]) == 3  # desktop, mobile, tablet

        # Verify each preview variant per ADCP spec
        for preview in structured["previews"]:
            assert "preview_id" in preview, "preview_id is required per spec"
            assert "renders" in preview, "renders is required per spec"
            assert len(preview["renders"]) > 0, "must have at least one render"
            assert "input" in preview, "input is required per spec"

        # Verify S3 upload was called
        assert mock_s3_upload.call_count == 3

    def test_preview_creative_with_custom_inputs(self, mock_s3_upload):
        """Test preview_creative with custom input variants."""
        manifest = CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="display_300x250_image"),
            assets={
                "banner_image": ImageAsset(
                    asset_type="image",
                    url="https://example.com/banner.png",
                    width=300,
                    height=250,
                ),
                "click_url": UrlAsset(asset_type="url", url="https://example.com/landing"),
            },
        )

        result = preview_creative(
            format_id="display_300x250_image",
            creative_manifest=manifest.model_dump(mode="json"),
            inputs=[
                {"name": "US Desktop", "macros": {"COUNTRY": "US", "DEVICE": "desktop"}},
                {"name": "UK Mobile", "macros": {"COUNTRY": "UK", "DEVICE": "mobile"}},
            ],
        )

        structured = result.structured_content

        assert len(structured["previews"]) == 2
        assert structured["previews"][0]["input"]["name"] == "US Desktop"
        assert structured["previews"][1]["input"]["name"] == "UK Mobile"

    def test_preview_creative_validates_format_id_mismatch(self, mock_s3_upload):
        """Test that preview_creative rejects manifest with mismatched format_id."""
        # Create manifest with DIFFERENT format_id than request
        manifest = CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="display_728x90_image"),
            assets={
                "banner_image": ImageAsset(
                    asset_type="image",
                    url="https://example.com/banner.png",
                    width=728,
                    height=90,
                ),
                "click_url": UrlAsset(asset_type="url", url="https://example.com/landing"),
            },
        )

        result = preview_creative(
            format_id="display_300x250_image",  # Different!
            creative_manifest=manifest.model_dump(mode="json"),
        )

        structured = result.structured_content
        assert "error" in structured
        assert "does not match" in structured["error"]

    def test_preview_creative_validates_malicious_urls(self, mock_s3_upload):
        """Test that preview_creative validates and sanitizes malicious URLs."""
        manifest = CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="display_300x250_image"),
            assets={
                "banner_image": ImageAsset(
                    asset_type="image",
                    url="https://example.com/banner.png",
                    width=300,
                    height=250,
                ),
                "click_url": UrlAsset(asset_type="url", url="https://example.com/landing"),
            },
        ).model_dump(mode="json")

        # Inject malicious URL after validation
        manifest["assets"]["banner_image"]["url"] = "javascript:alert('xss')"

        result = preview_creative(
            format_id="display_300x250_image",
            creative_manifest=manifest,
        )

        structured = result.structured_content
        assert "error" in structured
        assert "validation" in structured["error"].lower()

    def test_preview_creative_returns_interactive_url(self, mock_s3_upload):
        """Test that preview response includes interactive_url."""
        manifest = CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="display_300x250_image"),
            assets={
                "banner_image": ImageAsset(
                    asset_type="image",
                    url="https://example.com/banner.png",
                    width=300,
                    height=250,
                ),
                "click_url": UrlAsset(asset_type="url", url="https://example.com/landing"),
            },
        )

        result = preview_creative(
            format_id="display_300x250_image",
            creative_manifest=manifest.model_dump(mode="json"),
        )

        structured = result.structured_content
        assert "interactive_url" in structured
        assert "preview/" in structured["interactive_url"]

    def test_preview_creative_returns_expiration(self, mock_s3_upload):
        """Test that preview response includes expires_at timestamp."""
        manifest = CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="display_300x250_image"),
            assets={
                "banner_image": ImageAsset(
                    asset_type="image",
                    url="https://example.com/banner.png",
                    width=300,
                    height=250,
                ),
                "click_url": UrlAsset(asset_type="url", url="https://example.com/landing"),
            },
        )

        result = preview_creative(
            format_id="display_300x250_image",
            creative_manifest=manifest.model_dump(mode="json"),
        )

        structured = result.structured_content
        assert "expires_at" in structured
        # Should be ISO 8601 format
        assert "T" in structured["expires_at"]
        assert "Z" in structured["expires_at"] or "+" in structured["expires_at"]

    def test_preview_creative_rejects_unknown_format(self, mock_s3_upload):
        """Test that preview_creative rejects unknown format_id."""
        manifest = CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="display_300x250_image"),
            assets={
                "banner_image": ImageAsset(
                    asset_type="image",
                    url="https://example.com/banner.png",
                    width=300,
                    height=250,
                ),
                "click_url": UrlAsset(asset_type="url", url="https://example.com/landing"),
            },
        )

        result = preview_creative(
            format_id="unknown_format_999",
            creative_manifest=manifest.model_dump(mode="json"),
        )

        structured = result.structured_content
        assert "error" in structured
        assert "not found" in structured["error"].lower()

    def test_preview_creative_returns_spec_compliant_response(self, mock_s3_upload):
        """Test that response matches ADCP PreviewCreativeResponse spec exactly."""
        from creative_agent.schemas_generated._schemas_v1_creative_preview_creative_response_json import (
            PreviewCreativeResponse,
        )

        manifest = CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="display_300x250_image"),
            assets={
                "banner_image": ImageAsset(
                    asset_type="image",
                    url="https://example.com/banner.png",
                    width=300,
                    height=250,
                ),
                "click_url": UrlAsset(asset_type="url", url="https://example.com/landing"),
            },
        )

        result = preview_creative(
            format_id="display_300x250_image",
            creative_manifest=manifest.model_dump(mode="json"),
        )

        structured = result.structured_content

        # Validate against actual ADCP spec
        response = PreviewCreativeResponse.model_validate(structured)

        # Spec requires these fields
        assert response.previews is not None
        assert response.expires_at is not None
        assert len(response.previews) == 3  # desktop, mobile, tablet

    def test_preview_expiration_is_valid_iso8601_timestamp(self, mock_s3_upload):
        """Test that expires_at is a valid ISO 8601 timestamp in the future."""
        manifest = CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="display_300x250_image"),
            assets={
                "banner_image": ImageAsset(
                    asset_type="image",
                    url="https://example.com/banner.png",
                    width=300,
                    height=250,
                    format="png",
                ),
                "click_url": UrlAsset(
                    asset_type="url",
                    url="https://example.com/landing",
                ),
            },
        )

        result = preview_creative(
            format_id="display_300x250_image",
            creative_manifest=manifest.model_dump(mode="json"),
        )

        structured = result.structured_content

        # Verify expires_at exists and is a string
        assert "expires_at" in structured
        expires_at_str = structured["expires_at"]
        assert isinstance(expires_at_str, str)

        # Verify it's valid ISO 8601 and in the future
        expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
        now = datetime.now(UTC)
        assert expires_at > now, "expires_at must be in the future"

        # Verify reasonable expiration duration (between 1 min and 48 hours)
        time_until_expiry = (expires_at - now).total_seconds()
        assert 60 <= time_until_expiry <= 48 * 3600, "expiration should be reasonable duration"

    def test_preview_creative_fails_with_missing_required_asset(self, mock_s3_upload):
        """Test that preview_creative returns clear error when required asset is missing."""
        # Create manifest missing required click_url
        manifest = CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="display_300x250_image"),
            assets={
                "banner_image": ImageAsset(
                    asset_type="image",
                    url="https://example.com/banner.png",
                    width=300,
                    height=250,
                ),
                # Missing required click_url!
            },
        )

        result = preview_creative(
            format_id="display_300x250_image",
            creative_manifest=manifest.model_dump(mode="json"),
        )

        structured = result.structured_content

        # Must return error, not crash
        assert "error" in structured, "Should return error for missing required asset"
        assert "validation" in structured["error"].lower(), "Error should mention validation"

        # Should have specific validation errors
        assert "validation_errors" in structured, "Should include validation_errors array"
        errors = structured["validation_errors"]
        assert len(errors) > 0, "Should have at least one validation error"

        # Should mention the missing asset
        error_messages = [str(err) for err in errors]
        assert any("click_url" in str(msg).lower() for msg in error_messages), "Should mention missing click_url"
