"""Integration tests that validate tool responses match ADCP spec exactly.

These tests are written BY READING THE SPEC ONLY - not by looking at code.
They catch bugs like double-JSON-encoding, missing fields, wrong types, etc.

Tests verify that tools return ToolResult with:
- content: Human-readable message
- structured_content: ADCP schema-compliant data
"""

import json

import pytest
from adcp import (
    FormatId,
    ListCreativeFormatsResponse,
    PreviewCreativeResponse,
    get_required_assets,
)
from adcp.types import GetAdcpCapabilitiesResponse

from creative_agent import server
from creative_agent.data.standard_formats import AGENT_URL
from creative_agent.schemas import CreativeManifest

# Get actual functions from FastMCP wrappers
list_creative_formats = server.list_creative_formats.fn
preview_creative = server.preview_creative.fn
get_adcp_capabilities = server.get_adcp_capabilities.fn


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
            # Library uses flexible types - agent could be dict or object
            agent_url = agent.get("agent_url") if isinstance(agent, dict) else getattr(agent, "agent_url", None)
            agent_name = agent.get("agent_name") if isinstance(agent, dict) else getattr(agent, "agent_name", None)
            capabilities = (
                agent.get("capabilities") if isinstance(agent, dict) else getattr(agent, "capabilities", None)
            )

            assert agent_url is not None, "agent_url is required"
            assert agent_name is not None, "agent_name is required"
            assert capabilities is not None, "capabilities is required"
            assert isinstance(capabilities, list), "capabilities must be array"

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

    def test_assets_have_asset_id(self):
        """Per ADCP PR #135, all assets must have asset_id field."""
        result = list_creative_formats()
        response = ListCreativeFormatsResponse.model_validate(result.structured_content)

        formats_with_assets = [fmt for fmt in response.formats if get_required_assets(fmt)]
        assert len(formats_with_assets) > 0, "Should have formats with required assets"

        for fmt in formats_with_assets:
            for asset in get_required_assets(fmt):
                # Access asset_id - will raise AttributeError if missing
                asset_dict = asset.model_dump() if hasattr(asset, "model_dump") else dict(asset)
                assert "asset_id" in asset_dict, f"Format {fmt.format_id.id} has asset without asset_id: {asset_dict}"
                assert asset_dict["asset_id"], f"Format {fmt.format_id.id} has empty asset_id: {asset_dict}"

    def test_backward_compat_assets_required_field(self):
        """For 2.5.x client compatibility, formats must include assets_required field."""
        result = list_creative_formats()
        result_dict = result.structured_content

        # Find a format that has assets
        formats_with_assets = [f for f in result_dict["formats"] if f.get("assets")]
        assert len(formats_with_assets) > 0, "Should have formats with assets"

        for fmt in formats_with_assets:
            # assets_required must be present for backward compatibility
            assert "assets_required" in fmt, (
                f"Format {fmt.get('format_id', {}).get('id')} missing assets_required for 2.5.x compatibility"
            )
            # assets_required should only contain assets where required=True
            for asset in fmt["assets_required"]:
                assert asset.get("required", False) is True, (
                    f"assets_required should only contain required assets, got: {asset}"
                )

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
                "banner_image": {
                    "url": "https://example.com/test.png",
                    "width": 300,
                    "height": 250,
                },
                "click_url": {
                    "url": "https://example.com/landing",
                },
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

        # Verify required fields per spec - PreviewCreativeResponse is a union, access via .root
        assert hasattr(response.root, "previews"), "'previews' is required per spec"
        assert response.root.previews is not None, "'previews' is required per spec"
        assert response.root.expires_at is not None, "'expires_at' is required per spec"

    def test_previews_array_structure(self, valid_manifest, mock_s3):
        """Per spec, previews must be array of Preview objects with renders."""
        result = preview_creative(
            format_id="display_300x250_image",
            creative_manifest=valid_manifest.model_dump(mode="json"),
        )
        response = PreviewCreativeResponse.model_validate(result.structured_content)

        # Access previews directly - PreviewCreativeResponse is a union, access via .root
        assert isinstance(response.root.previews, list), "previews must be array"
        assert len(response.root.previews) > 0, "must return at least one preview"

        for preview in response.root.previews:
            # Per spec, each Preview must have:
            # Handle both dict and object access
            preview_id = (
                preview.get("preview_id") if isinstance(preview, dict) else getattr(preview, "preview_id", None)
            )
            renders = preview.get("renders") if isinstance(preview, dict) else getattr(preview, "renders", None)

            assert preview_id is not None, "preview_id is required per spec"
            assert renders is not None, "renders is required per spec"
            assert len(renders) > 0, "renders must have at least one render"

            # Check first render
            render = renders[0]
            # PreviewRender is a RootModel in adcp 2.18.0, access fields via .root
            if isinstance(render, dict):
                preview_url = render.get("preview_url")
            elif hasattr(render, "root"):
                preview_url = getattr(render.root, "preview_url", None)
            else:
                preview_url = getattr(render, "preview_url", None)
            assert preview_url is not None, "render.preview_url is required"
            assert str(preview_url).startswith("http"), "preview_url must be valid HTTP(S) URL"

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
                "banner_image": {
                    "url": "https://example.com/test.png",
                    "width": 300,
                    "height": 250,
                },
                "click_url": {"url": "https://example.com/landing"},
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


class TestGetAdcpCapabilitiesResponseFormat:
    """Test that get_adcp_capabilities returns valid ADCP GetAdcpCapabilitiesResponse.

    Written by reading the ADCP spec - GetAdcpCapabilitiesResponse schema.
    NOT by looking at server.py code.

    Required fields per spec:
    - adcp: object with major_versions array
    - supported_protocols: array of protocol names (media_buy, signals, etc.)
    """

    def test_returns_tool_result_with_structured_content(self):
        """Tool must return ToolResult with structured_content."""
        result = get_adcp_capabilities()

        # Verify ToolResult structure
        assert hasattr(result, "content"), "Must return ToolResult with content"
        assert hasattr(result, "structured_content"), "Must return ToolResult with structured_content"
        assert result.content, "Content must not be empty"
        assert result.structured_content, "Structured content must not be empty"

        # Verify content is human-readable message
        assert result.content[0].type == "text"
        assert "capabilit" in result.content[0].text.lower(), "Content should mention capabilities"

    def test_structured_content_matches_adcp_schema(self):
        """Structured content must validate against GetAdcpCapabilitiesResponse schema."""
        result = get_adcp_capabilities()

        # Get structured_content (already a dict, no JSON parsing needed)
        result_dict = result.structured_content

        # This validates ALL fields, types, constraints per ADCP spec
        response = GetAdcpCapabilitiesResponse.model_validate(result_dict)

        # Verify required fields per spec
        assert response.adcp is not None, "'adcp' field is required per ADCP spec"
        assert response.supported_protocols is not None, "'supported_protocols' field is required per ADCP spec"

    def test_adcp_field_structure(self):
        """Per spec, adcp must have major_versions array with at least one version."""
        result = get_adcp_capabilities()
        response = GetAdcpCapabilitiesResponse.model_validate(result.structured_content)

        assert response.adcp is not None, "adcp is required"
        assert response.adcp.major_versions is not None, "adcp.major_versions is required"
        assert isinstance(response.adcp.major_versions, list), "major_versions must be array"
        assert len(response.adcp.major_versions) >= 1, "must have at least one major version"
        # Version must be positive integer (may be wrapped in MajorVersion type)
        for version in response.adcp.major_versions:
            # Handle MajorVersion wrapper type that has .root attribute
            version_int = version.root if hasattr(version, "root") else version
            assert isinstance(version_int, int), f"major_version must be integer, got {type(version_int)}"
            assert version_int >= 1, "major_version must be >= 1"

    def test_supported_protocols_structure(self):
        """Per spec, supported_protocols must be array of valid protocol names."""
        result = get_adcp_capabilities()
        response = GetAdcpCapabilitiesResponse.model_validate(result.structured_content)

        assert isinstance(response.supported_protocols, list), "supported_protocols must be array"
        assert len(response.supported_protocols) >= 1, "must support at least one protocol"

        # Valid protocols per ADCP spec
        valid_protocols = {"media_buy", "signals", "governance", "sponsored_intelligence", "creative"}
        for protocol in response.supported_protocols:
            # Handle both string and enum
            protocol_str = protocol.value if hasattr(protocol, "value") else str(protocol)
            assert protocol_str in valid_protocols, f"Invalid protocol: {protocol_str}"

    def test_creative_agent_supports_creative_protocol(self):
        """A creative agent must support the creative protocol."""
        result = get_adcp_capabilities()
        response = GetAdcpCapabilitiesResponse.model_validate(result.structured_content)

        protocol_strs = [p.value if hasattr(p, "value") else str(p) for p in response.supported_protocols]
        assert "creative" in protocol_strs, "Creative agent must support creative protocol"

    def test_no_extra_wrapper_fields(self):
        """Structured content must match ADCP schema exactly with no wrappers."""
        result = get_adcp_capabilities()
        result_dict = result.structured_content

        # These are common bugs - wrapping valid response in extra structure
        assert "result" not in result_dict or not isinstance(result_dict.get("result"), str), (
            "structured_content must not have JSON string in 'result' field"
        )
        assert "data" not in result_dict or result_dict.get("data") != result_dict, (
            "structured_content must not be wrapped in 'data' field"
        )

        # Top-level keys should include required schema keys
        required_keys = {"adcp", "supported_protocols"}
        actual_keys = set(result_dict.keys())
        assert required_keys.issubset(actual_keys), (
            f"Response must have required keys {required_keys}, got {actual_keys}"
        )

    def test_protocols_filter_works(self):
        """If protocols param is provided, should filter to those protocols."""
        result = get_adcp_capabilities(protocols=["creative"])

        response = GetAdcpCapabilitiesResponse.model_validate(result.structured_content)
        # Should still have required fields
        assert response.adcp is not None
        assert response.supported_protocols is not None

    def test_protocols_filter_with_unsupported_protocol_returns_error(self):
        """If protocols param contains only unsupported protocols, returns error."""
        result = get_adcp_capabilities(protocols=["media_buy"])  # This agent only supports creative

        # ADCP schema requires at least one protocol, so filtering to unsupported
        # protocols results in a validation error
        assert "error" in result.structured_content
