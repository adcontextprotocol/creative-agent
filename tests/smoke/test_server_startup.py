"""Smoke test to verify server can start."""

import pytest


@pytest.mark.smoke
def test_server_imports():
    """Verify server module can be imported."""
    from src.creative_agent import server

    assert server.mcp is not None
    assert server.mcp.name == "adcp-creative-agent"


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_v1_tools_defined():
    """Verify v1 tools are defined."""
    from src.creative_agent.server import mcp

    tools_list = await mcp._list_tools()
    tools = {tool.name: tool for tool in tools_list}

    # Verify v1 tools exist
    assert "list_creative_formats" in tools
    assert "preview_creative" in tools

    # Verify tool descriptions
    assert "AdCP creative formats" in tools["list_creative_formats"].description
    assert "preview" in tools["preview_creative"].description.lower()


@pytest.mark.smoke
def test_list_creative_formats():
    """Verify list_creative_formats returns AdCP formats."""
    from src.creative_agent.data.standard_formats import STANDARD_FORMATS

    # Verify formats are loaded
    assert len(STANDARD_FORMATS) > 0

    # Check for specific AdCP formats
    format_ids = [fmt.format_id for fmt in STANDARD_FORMATS]
    assert "video_standard_15s" in format_ids
    assert "video_standard_30s" in format_ids
    assert "display_300x250_image" in format_ids
    assert "display_300x250_html" in format_ids


@pytest.mark.smoke
def test_preview_creative_logic():
    """Verify preview generation logic works."""
    from src.creative_agent.data.standard_formats import get_format_by_id

    # Verify display format exists
    fmt = get_format_by_id("display_300x250_image")
    assert fmt is not None
    assert fmt.type.value == "display"

    # Verify video format exists
    fmt = get_format_by_id("video_standard_15s")
    assert fmt is not None
    assert fmt.type.value == "video"
