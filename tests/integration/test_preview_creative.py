"""Integration tests for preview_creative tool."""

import json

import pytest
from pytest_mock import MockerFixture

from creative_agent.data.standard_formats import AGENT_URL
from creative_agent import server

# Get the actual function from the FastMCP wrapper
preview_creative = server.preview_creative.fn


@pytest.fixture
def mock_s3_upload(mocker: MockerFixture):
    """Mock S3 upload to avoid network calls."""
    mock_upload = mocker.patch("creative_agent.storage.upload_preview_html")
    mock_upload.return_value = "https://adcp-previews.fly.storage.tigris.dev/previews/test-id/desktop.html"
    return mock_upload


class TestPreviewCreativeIntegration:
    """Integration tests for the preview_creative tool."""

    def test_preview_creative_with_dict_manifest(self, mock_s3_upload):
        """Test preview_creative tool with dict manifest (ADCP compliant)."""
        result_json = preview_creative(
            format_id="display_300x250_image",
            creative_manifest={
                "format_id": {"agent_url": str(AGENT_URL), "id": "display_300x250_image"},
                "assets": {
                    "banner_image": {
                        "asset_type": "image",
                        "url": "https://example.com/banner.png",
                        "width": 300,
                        "height": 250,
                        "format": "png",
                    },
                    "landing_url": {
                        "asset_type": "url",
                        "url": "https://example.com/landing",
                    },
                },
            },
        )

        result = json.loads(result_json)

        # Verify response structure
        assert "previews" in result
        assert isinstance(result["previews"], list)
        assert len(result["previews"]) == 3  # desktop, mobile, tablet

        # Verify each preview variant
        for preview in result["previews"]:
            assert "preview_url" in preview
            assert "input" in preview
            assert "hints" in preview
            assert "embedding" in preview

        # Verify S3 upload was called
        assert mock_s3_upload.call_count == 3

    def test_preview_creative_with_custom_inputs(self, mock_s3_upload):
        """Test preview_creative with custom input variants."""
        result_json = preview_creative(
            format_id="display_300x250_image",
            creative_manifest={
                "format_id": {"agent_url": str(AGENT_URL), "id": "display_300x250_image"},
                "assets": {
                    "banner_image": {
                        "asset_type": "image",
                        "url": "https://example.com/banner.png",
                        "width": 300,
                        "height": 250,
                    }
                },
            },
            inputs=[
                {"name": "US Desktop", "macros": {"COUNTRY": "US", "DEVICE": "desktop"}},
                {"name": "UK Mobile", "macros": {"COUNTRY": "UK", "DEVICE": "mobile"}},
            ],
        )

        result = json.loads(result_json)

        assert len(result["previews"]) == 2
        assert result["previews"][0]["input"]["name"] == "US Desktop"
        assert result["previews"][1]["input"]["name"] == "UK Mobile"

    def test_preview_creative_validates_format_id_mismatch(self, mock_s3_upload):
        """Test that preview_creative rejects manifest with mismatched format_id."""
        result_json = preview_creative(
            format_id="display_300x250_image",
            creative_manifest={
                "format_id": {"agent_url": str(AGENT_URL), "id": "display_728x90_image"},
                "assets": {
                    "banner_image": {
                        "asset_type": "image",
                        "url": "https://example.com/banner.png",
                        "width": 728,
                        "height": 90,
                    }
                },
            },
        )

        result = json.loads(result_json)
        assert "error" in result
        assert "does not match" in result["error"]

    def test_preview_creative_validates_assets(self, mock_s3_upload):
        """Test that preview_creative validates manifest assets."""
        result_json = preview_creative(
            format_id="display_300x250_image",
            creative_manifest={
                "format_id": {"agent_url": str(AGENT_URL), "id": "display_300x250_image"},
                "assets": {
                    "banner_image": {
                        "asset_type": "image",
                        "url": "javascript:alert('xss')",  # Invalid URL
                        "width": 300,
                        "height": 250,
                    }
                },
            },
        )

        result = json.loads(result_json)
        assert "error" in result
        assert "validation" in result["error"].lower()

    def test_preview_creative_returns_interactive_url(self, mock_s3_upload):
        """Test that preview response includes interactive_url."""
        result_json = preview_creative(
            format_id="display_300x250_image",
            creative_manifest={
                "format_id": {"agent_url": str(AGENT_URL), "id": "display_300x250_image"},
                "assets": {
                    "banner_image": {
                        "asset_type": "image",
                        "url": "https://example.com/banner.png",
                        "width": 300,
                        "height": 250,
                    }
                },
            },
        )

        result = json.loads(result_json)
        assert "interactive_url" in result
        assert "preview/" in result["interactive_url"]

    def test_preview_creative_returns_expiration(self, mock_s3_upload):
        """Test that preview response includes expires_at timestamp."""
        result_json = preview_creative(
            format_id="display_300x250_image",
            creative_manifest={
                "format_id": {"agent_url": str(AGENT_URL), "id": "display_300x250_image"},
                "assets": {
                    "banner_image": {
                        "asset_type": "image",
                        "url": "https://example.com/banner.png",
                        "width": 300,
                        "height": 250,
                    }
                },
            },
        )

        result = json.loads(result_json)
        assert "expires_at" in result
        # Should be ISO 8601 format
        assert "T" in result["expires_at"]
        assert "Z" in result["expires_at"] or "+" in result["expires_at"]

    @pytest.mark.skip(reason="Known bug: format_obj.requirements attribute doesn't exist")
    def test_preview_creative_with_video_format(self, mock_s3_upload):
        """Test preview_creative with video format."""
        result_json = preview_creative(
            format_id="video_standard_15s",
            creative_manifest={
                "format_id": {"agent_url": str(AGENT_URL), "id": "video_standard_15s"},
                "assets": {
                    "video_file": {
                        "asset_type": "video",
                        "url": "https://example.com/video.mp4",
                        "width": 1920,
                        "height": 1080,
                        "duration_seconds": 15,
                        "format": "mp4",
                    }
                },
            },
        )

        result = json.loads(result_json)
        assert "previews" in result
        assert len(result["previews"]) == 3

        # Verify video-specific hints
        for preview in result["previews"]:
            assert preview["hints"]["primary_media_type"] == "video"
            assert preview["hints"]["contains_audio"] is True
            assert "estimated_duration_seconds" in preview["hints"]

    def test_preview_creative_rejects_unknown_format(self, mock_s3_upload):
        """Test that preview_creative rejects unknown format_id."""
        result_json = preview_creative(
            format_id="unknown_format_999",
            creative_manifest={
                "format_id": {"agent_url": str(AGENT_URL), "id": "unknown_format_999"},
                "assets": {},
            },
        )

        result = json.loads(result_json)
        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_preview_creative_includes_adcp_version(self, mock_s3_upload):
        """Test that response includes adcp_version field."""
        result_json = preview_creative(
            format_id="display_300x250_image",
            creative_manifest={
                "format_id": {"agent_url": str(AGENT_URL), "id": "display_300x250_image"},
                "assets": {
                    "banner_image": {
                        "asset_type": "image",
                        "url": "https://example.com/banner.png",
                        "width": 300,
                        "height": 250,
                    }
                },
            },
        )

        result = json.loads(result_json)
        assert "adcp_version" in result
        assert result["adcp_version"] == "1.0.0"
