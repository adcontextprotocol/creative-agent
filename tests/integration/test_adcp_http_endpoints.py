"""Integration tests for ADCP HTTP endpoints (not MCP wrapped).

These tests verify that the /adcp/* endpoints return clean ADCP responses
without MCP protocol wrapping.
"""

import json

import pytest
from fastapi.testclient import TestClient

from creative_agent.combined_server import app

client = TestClient(app)


class TestADCPHTTPEndpoints:
    """Test ADCP-native HTTP endpoints return unwrapped responses."""

    def test_list_formats_returns_clean_adcp_response(self):
        """GET /adcp/list-creative-formats returns ADCP schema without MCP wrapping."""
        response = client.get("/adcp/list-creative-formats")
        assert response.status_code == 200

        data = response.json()

        # Verify clean ADCP response structure
        assert "formats" in data, "Must have 'formats' field per ADCP spec"
        assert "creative_agents" in data, "Must have 'creative_agents' field per ADCP spec"

        # Verify NO MCP wrapping
        assert "result" not in data, "Must NOT have MCP 'result' wrapper"
        assert "content" not in data, "Must NOT have MCP 'content' wrapper"

        # Verify formats is an array with proper structure
        assert isinstance(data["formats"], list)
        assert len(data["formats"]) > 0

        # Check first format has required ADCP fields
        fmt = data["formats"][0]
        assert "format_id" in fmt
        assert "name" in fmt
        assert "type" in fmt

    def test_list_formats_post_with_filters(self):
        """POST /adcp/list-creative-formats with filters works."""
        response = client.post(
            "/adcp/list-creative-formats",
            json={"type": "display", "max_width": 300},
        )
        assert response.status_code == 200

        data = response.json()
        assert "formats" in data
        assert isinstance(data["formats"], list)

        # Verify filters were applied
        for fmt in data["formats"]:
            assert fmt["type"] == "display"

    def test_preview_creative_error_returns_http_400(self):
        """Preview with invalid format returns HTTP 400, not MCP error structure."""
        response = client.post(
            "/adcp/preview-creative",
            json={
                "format_id": "nonexistent_format",
                "creative_manifest": {"format_id": {}, "assets": {}},
            },
        )

        # Should return HTTP error, not 200 with MCP error structure
        assert response.status_code == 400

        # Error detail should be in HTTP response, not MCP wrapper
        assert "detail" in response.json()

    def test_root_redirects_to_adcp_docs(self):
        """Root / redirects to /adcp/ for documentation."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code in [307, 308]  # Redirect
        assert "/adcp" in response.headers["location"]

    def test_adcp_root_shows_api_info(self):
        """GET /adcp/ returns API information."""
        response = client.get("/adcp/")
        assert response.status_code == 200

        data = response.json()
        assert data["protocol"] == "adcp"
        assert "endpoints" in data

    def test_no_double_json_encoding(self):
        """Verify response is not double-JSON-encoded."""
        response = client.get("/adcp/list-creative-formats")
        assert response.status_code == 200

        data = response.json()

        # Check that no field contains JSON strings
        # (double-encoding would have string values that parse as JSON)
        def check_for_json_strings(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    check_for_json_strings(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj[:3]):  # Check first 3 items
                    check_for_json_strings(item, f"{path}[{i}]")
            elif isinstance(obj, str) and len(obj) > 10:
                # If it's a string that looks like JSON, try parsing
                if obj.startswith(("{", "[")):
                    try:
                        json.loads(obj)
                        pytest.fail(f"Found double-encoded JSON string at {path}: {obj[:100]}")
                    except json.JSONDecodeError:
                        pass  # Not JSON, that's fine

        check_for_json_strings(data)
