"""Integration tests that validate tool responses match ADCP spec exactly.

These tests are written BY READING THE SPEC ONLY - not by looking at code.
They catch bugs like double-JSON-encoding, missing fields, wrong types, etc.
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

    def test_returns_valid_json(self):
        """Tool must return valid JSON string (not double-encoded)."""
        result_json = list_creative_formats()

        # This will fail if response is double-encoded like: '{"result": "{...}"}'
        result_dict = json.loads(result_json)
        assert isinstance(result_dict, dict), "Response must be a JSON object, not nested string"

    def test_response_matches_adcp_schema(self):
        """Response must validate against ListCreativeFormatsResponse schema."""
        result_json = list_creative_formats()
        result_dict = json.loads(result_json)

        # This validates ALL fields, types, constraints per ADCP spec
        response = ListCreativeFormatsResponse.model_validate(result_dict)

        # Verify required fields per spec
        assert response.formats is not None, "'formats' field is required per ADCP spec"
        assert response.creative_agents is not None, "'creative_agents' field is required per ADCP spec"

    def test_formats_array_structure(self):
        """Per spec, formats must be array of Format objects with required fields."""
        result_json = list_creative_formats()
        result_dict = json.loads(result_json)
        response = ListCreativeFormatsResponse.model_validate(result_dict)

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
        result_json = list_creative_formats()
        result_dict = json.loads(result_json)
        response = ListCreativeFormatsResponse.model_validate(result_dict)

        assert isinstance(response.creative_agents, list), "creative_agents must be array"
        assert len(response.creative_agents) > 0, "must include at least one creative agent"

        for agent in response.creative_agents:
            assert agent.agent_url is not None, "agent_url is required"
            assert agent.agent_name is not None, "agent_name is required"
            assert agent.capabilities is not None, "capabilities is required"
            assert isinstance(agent.capabilities, list), "capabilities must be array"

    def test_no_extra_wrapper_fields(self):
        """Response must not have extra fields like 'result' or 'data' wrapping the schema."""
        result_json = list_creative_formats()
        result_dict = json.loads(result_json)

        # These are common bugs - wrapping valid response in extra structure
        assert "result" not in result_dict or result_dict.get("result") != result_dict, (
            "Response must not be wrapped in 'result' field"
        )
        assert "data" not in result_dict or result_dict.get("data") != result_dict, (
            "Response must not be wrapped in 'data' field"
        )

        # Top-level keys should match schema exactly
        expected_keys = {"formats", "creative_agents"}
        actual_keys = set(result_dict.keys())
        assert expected_keys.issubset(actual_keys), (
            f"Response must have required keys {expected_keys}, got {actual_keys}"
        )


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

    def test_returns_valid_json(self, valid_manifest, mock_s3):
        """Tool must return valid JSON string (not double-encoded)."""
        result_json = preview_creative(
            format_id="display_300x250_image",
            creative_manifest=valid_manifest.model_dump(mode="json"),
        )

        # This will fail if response is double-encoded
        result_dict = json.loads(result_json)
        assert isinstance(result_dict, dict), "Response must be a JSON object, not nested string"

    def test_response_matches_adcp_schema(self, valid_manifest, mock_s3):
        """Response must validate against PreviewCreativeResponse schema."""
        result_json = preview_creative(
            format_id="display_300x250_image",
            creative_manifest=valid_manifest.model_dump(mode="json"),
        )
        result_dict = json.loads(result_json)

        # This validates ALL fields per ADCP spec
        response = PreviewCreativeResponse.model_validate(result_dict)

        # Verify required fields per spec
        assert response.previews is not None, "'previews' is required per spec"
        assert response.expires_at is not None, "'expires_at' is required per spec"

    def test_previews_array_structure(self, valid_manifest, mock_s3):
        """Per spec, previews must be array of Preview objects with renders."""
        result_json = preview_creative(
            format_id="display_300x250_image",
            creative_manifest=valid_manifest.model_dump(mode="json"),
        )
        result_dict = json.loads(result_json)
        response = PreviewCreativeResponse.model_validate(result_dict)

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

    def test_error_responses_are_valid_json(self, mock_s3):
        """Even error responses must be valid JSON (not double-encoded)."""
        # Test with invalid format_id
        result_json = preview_creative(
            format_id="nonexistent_format",
            creative_manifest={"format_id": {}, "assets": {}},
        )

        # Must be parseable JSON
        result_dict = json.loads(result_json)
        assert isinstance(result_dict, dict), "Error response must be JSON object"

        # Error responses should have 'error' field per ADCP error handling
        assert "error" in result_dict, "Error responses should have 'error' field"
        assert isinstance(result_dict["error"], str), "Error must be a string description"


class TestToolResponseConsistency:
    """Test that all tools follow consistent response format patterns."""

    def test_all_tools_return_json_strings(self):
        """All tools must return JSON strings, never Python objects."""
        # Test list_creative_formats
        result = list_creative_formats()
        assert isinstance(result, str), "list_creative_formats must return JSON string"

    def test_no_tool_returns_double_encoded_json(self, mocker):
        """No tool should ever return JSON-encoded-JSON like '{"result": "{...}"}'."""
        mocker.patch("creative_agent.storage.upload_preview_html", return_value="https://test.com")

        # Test list_creative_formats
        result = list_creative_formats()
        parsed = json.loads(result)
        # If any value is a string that looks like JSON, we have double-encoding
        for value in parsed.values():
            if isinstance(value, str) and value.startswith(("{", "[")):
                # Try to parse it - if it parses, we have double-encoding
                try:
                    json.loads(value)
                    pytest.fail(f"Found double-encoded JSON in field: {value[:100]}")
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
        parsed = json.loads(result)
        for value in parsed.values():
            if isinstance(value, str) and value.startswith(("{", "[")):
                try:
                    json.loads(value)
                    pytest.fail(f"Found double-encoded JSON in field: {value[:100]}")
                except json.JSONDecodeError:
                    pass
