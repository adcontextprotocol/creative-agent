"""Integration tests that validate tool responses match ADCP spec exactly.

These tests are written BY READING THE SPEC ONLY - not by looking at code.
They catch bugs like double-JSON-encoding, missing fields, wrong types, etc.

Tests verify that tools return ToolResult with:
- content: Human-readable message
- structured_content: ADCP schema-compliant data
"""

import json

import pytest

from creative_agent import server
from creative_agent.data.standard_formats import AGENT_URL
from creative_agent.schemas_generated._schemas_v1_creative_list_creative_formats_response_json import (
    ListCreativeFormatsResponseCreativeAgent as ListCreativeFormatsResponse,
)
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
from creative_agent.schemas_generated._schemas_v1_creative_preview_creative_response_json import (
    PreviewCreativeResponse,
)

# Get actual functions from FastMCP wrappers
list_creative_formats = server.list_creative_formats.fn
preview_creative = server.preview_creative.fn


class TestListCreativeFormatsResponseFormat:
    """Test that list_creative_formats returns valid ADCP ListCreativeFormatsResponse.

    Written by reading: schemas/v1/creative/list-creative-formats-response.json
    NOT by looking at server.py code.
    """

    def test_returns_tool_result_with_structured_content(self):
        """Tool must return ToolResult with structured_content."""
        result = list_creative_formats()

        # Verify ToolResult structure
        assert hasattr(result, "content"), "Must return ToolResult with content"
        assert hasattr(result, "structured_content"), "Must return ToolResult with structured_content"
        assert result.content, "Content must not be empty"
        assert result.structured_content, "Structured content must not be empty"

        # Verify content is human-readable message
        assert result.content[0].type == "text"
        assert "format" in result.content[0].text.lower(), "Content should mention formats"

    def test_structured_content_matches_adcp_schema(self):
        """Structured content must validate against ListCreativeFormatsResponse schema."""
        result = list_creative_formats()

        # Get structured_content (already a dict, no JSON parsing needed)
        result_dict = result.structured_content

        # This validates ALL fields, types, constraints per ADCP spec
        response = ListCreativeFormatsResponse.model_validate(result_dict)

        # Verify required fields per spec
        assert response.formats is not None, "'formats' field is required per ADCP spec"
        assert response.creative_agents is not None, "'creative_agents' field is required per ADCP spec"

    def test_formats_array_structure(self):
        """Per spec, formats must be array of Format objects with required fields."""
        result = list_creative_formats()
        response = ListCreativeFormatsResponse.model_validate(result.structured_content)

        assert isinstance(response.formats, list), "formats must be array per spec"
        assert len(response.formats) > 0, "formats array must not be empty"

        # Verify each format has required fields per Format schema
        for fmt in response.formats:
            assert fmt.format_id is not None, "format_id is required"
            assert fmt.format_id.agent_url is not None, "format_id.agent_url is required"
            assert fmt.format_id.id is not None, "format_id.id is required"
            assert fmt.type is not None, "type is required"
            assert fmt.name is not None, "name is required"

    def test_creative_agents_structure(self):
        """Per spec, creative_agents must be array with agent_url, agent_name, capabilities."""
        result = list_creative_formats()
        response = ListCreativeFormatsResponse.model_validate(result.structured_content)

        assert isinstance(response.creative_agents, list), "creative_agents must be array"
        assert len(response.creative_agents) > 0, "must include at least one creative agent"

        for agent in response.creative_agents:
            assert agent.agent_url is not None, "agent_url is required"
            assert agent.agent_name is not None, "agent_name is required"
            assert agent.capabilities is not None, "capabilities is required"
            assert isinstance(agent.capabilities, list), "capabilities must be array"

    def test_no_extra_wrapper_fields(self):
        """Structured content must match ADCP schema exactly with no wrappers."""
        result = list_creative_formats()
        result_dict = result.structured_content

        # These are common bugs - wrapping valid response in extra structure
        assert "result" not in result_dict or not isinstance(result_dict.get("result"), str), (
            "structured_content must not have JSON string in 'result' field"
        )
        assert "data" not in result_dict or result_dict.get("data") != result_dict, (
            "structured_content must not be wrapped in 'data' field"
        )

        # Top-level keys should match schema exactly
        expected_keys = {"formats", "creative_agents"}
        actual_keys = set(result_dict.keys())
        assert expected_keys.issubset(actual_keys), (
            f"Response must have required keys {expected_keys}, got {actual_keys}"
        )

    def test_assets_required_have_asset_id(self):
        """Per ADCP PR #135, all AssetsRequired must have asset_id field."""
        result = list_creative_formats()
        response = ListCreativeFormatsResponse.model_validate(result.structured_content)

        formats_with_assets = [fmt for fmt in response.formats if fmt.assets_required]
        assert len(formats_with_assets) > 0, "Should have formats with assets_required"

        for fmt in formats_with_assets:
            for asset in fmt.assets_required:
                # Access asset_id - will raise AttributeError if missing
                asset_dict = asset.model_dump() if hasattr(asset, "model_dump") else dict(asset)
                assert "asset_id" in asset_dict, f"Format {fmt.format_id.id} has asset without asset_id: {asset_dict}"
                assert asset_dict["asset_id"], f"Format {fmt.format_id.id} has empty asset_id: {asset_dict}"

    def test_accepts_format_ids_as_dicts(self):
        """Test that list_creative_formats accepts format_ids as FormatId objects (dicts)."""
        # Filter by format_ids using dict representation
        result = list_creative_formats(
            format_ids=[
                {"agent_url": str(AGENT_URL), "id": "display_300x250_image"},
                {"agent_url": str(AGENT_URL), "id": "display_728x90_image"},
            ]
        )

        response = ListCreativeFormatsResponse.model_validate(result.structured_content)
        assert len(response.formats) == 2
        format_ids = {fmt.format_id.id for fmt in response.formats}
        assert format_ids == {"display_300x250_image", "display_728x90_image"}

    def test_accepts_mixed_format_ids_strings_and_dicts(self):
        """Test that list_creative_formats accepts mixed string and dict format_ids."""
        result = list_creative_formats(
            format_ids=[
                "display_300x250_image",  # String
                {"agent_url": str(AGENT_URL), "id": "display_728x90_image"},  # Dict
            ]
        )

        response = ListCreativeFormatsResponse.model_validate(result.structured_content)
        assert len(response.formats) == 2
        format_ids = {fmt.format_id.id for fmt in response.formats}
        assert format_ids == {"display_300x250_image", "display_728x90_image"}


class TestPreviewCreativeResponseFormat:
    """Test that preview_creative returns valid ADCP PreviewCreativeResponse.

    Written by reading: schemas/v1/creative/preview-creative-response.json
    NOT by looking at server.py code.
    """

    @pytest.fixture
    def valid_manifest(self):
        """Create a valid manifest per ADCP spec."""
        return CreativeManifest(
            format_id=FormatId(agent_url=AGENT_URL, id="display_300x250_image"),
            assets={
                "banner_image": ImageAsset(
                    asset_type="image",
                    url="https://example.com/test.png",
                    width=300,
                    height=250,
                ),
                "click_url": UrlAsset(
                    asset_type="url",
                    url="https://example.com/landing",
                ),
            },
        )

    @pytest.fixture
    def mock_s3(self, mocker):
        """Mock S3 to avoid network calls."""
        mock = mocker.patch("creative_agent.storage.upload_preview_html")
        mock.return_value = "https://adcp-previews.fly.storage.tigris.dev/test.html"
        return mock

    def test_returns_tool_result(self, valid_manifest, mock_s3):
        """Tool must return ToolResult with structured content."""
        result = preview_creative(
            format_id="display_300x250_image",
            creative_manifest=valid_manifest.model_dump(mode="json"),
        )

        assert hasattr(result, "content"), "Must return ToolResult with content"
        assert hasattr(result, "structured_content"), "Must return ToolResult with structured_content"
        assert result.structured_content, "Structured content must not be empty"

    def test_structured_content_matches_adcp_schema(self, valid_manifest, mock_s3):
        """Structured content must validate against PreviewCreativeResponse schema."""
        result = preview_creative(
            format_id="display_300x250_image",
            creative_manifest=valid_manifest.model_dump(mode="json"),
        )

        # This validates ALL fields per ADCP spec
        response = PreviewCreativeResponse.model_validate(result.structured_content)

        # Verify required fields per spec
        assert response.previews is not None, "'previews' is required per spec"
        assert response.expires_at is not None, "'expires_at' is required per spec"

    def test_previews_array_structure(self, valid_manifest, mock_s3):
        """Per spec, previews must be array of Preview objects with renders."""
        result = preview_creative(
            format_id="display_300x250_image",
            creative_manifest=valid_manifest.model_dump(mode="json"),
        )
        response = PreviewCreativeResponse.model_validate(result.structured_content)

        assert isinstance(response.previews, list), "previews must be array"
        assert len(response.previews) > 0, "must return at least one preview"

        for preview in response.previews:
            # Per spec, each Preview must have:
            assert preview.preview_id is not None, "preview_id is required per spec"
            assert preview.renders is not None, "renders is required per spec"
            assert len(preview.renders) > 0, "renders must have at least one render"

            # Check first render
            render = preview.renders[0]
            assert render.preview_url is not None, "render.preview_url is required"
            assert str(render.preview_url).startswith("http"), "preview_url must be valid HTTP(S) URL"

    def test_error_responses_have_structured_content(self, mock_s3):
        """Even error responses must have structured content."""
        # Test with invalid format_id
        result = preview_creative(
            format_id="nonexistent_format",
            creative_manifest={"format_id": {}, "assets": {}},
        )

        assert hasattr(result, "structured_content"), "Error must have structured_content"
        assert hasattr(result, "content"), "Error must have content"

        # Error responses should have 'error' field in structured_content
        assert "error" in result.structured_content, "Error responses should have 'error' field"
        assert isinstance(result.structured_content["error"], str), "Error must be a string description"

        # Content should mention error
        assert "error" in result.content[0].text.lower(), "Content should indicate error"


class TestToolResponseConsistency:
    """Test that all tools follow consistent response format patterns."""

    def test_all_tools_return_tool_result(self):
        """All tools must return ToolResult objects with structured_content."""
        # Test list_creative_formats
        result = list_creative_formats()
        assert hasattr(result, "structured_content"), "list_creative_formats must return ToolResult"
        assert hasattr(result, "content"), "ToolResult must have content"

    def test_structured_content_not_double_encoded(self, mocker):
        """structured_content should be objects, not JSON strings."""
        mocker.patch("creative_agent.storage.upload_preview_html", return_value="https://test.com")

        # Test list_creative_formats
        result = list_creative_formats()
        structured = result.structured_content

        # structured_content should be a dict, not a string
        assert isinstance(structured, dict), "structured_content must be dict, not JSON string"

        # Values should not be JSON strings (no double-encoding)
        for key, value in structured.items():
            if isinstance(value, str) and value.startswith(("{", "[")):
                # Try to parse it - if it parses, we have double-encoding
                try:
                    json.loads(value)
                    pytest.fail(f"Found double-encoded JSON in field '{key}': {value[:100]}")
                except json.JSONDecodeError:
                    pass  # Not JSON, that's fine

        # Test preview_creative
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
            },
        )
        result = preview_creative(
            format_id="display_300x250_image",
            creative_manifest=manifest.model_dump(mode="json"),
        )
        structured = result.structured_content
        assert isinstance(structured, dict), "structured_content must be dict"

        for key, value in structured.items():
            if isinstance(value, str) and value.startswith(("{", "[")):
                try:
                    json.loads(value)
                    pytest.fail(f"Found double-encoded JSON in field '{key}': {value[:100]}")
                except json.JSONDecodeError:
                    pass
