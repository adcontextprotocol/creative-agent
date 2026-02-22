"""
AdCP schemas for creative agent.

This module re-exports official AdCP schemas from the adcp library,
providing a clean interface for the rest of the codebase.

All schemas come from the official adcp-client-python library:
https://pypi.org/project/adcp/
"""

# Core schemas from adcp library
from adcp import CreativeManifest, ListCreativeFormatsResponse
from adcp import Format as CreativeFormat

# Manifest/Preview schemas - agent-specific definitions
from .manifest import (
    PreviewCreativeRequest,
    PreviewCreativeResponse,
    PreviewEmbedding,
    PreviewHints,
    PreviewInput,
    PreviewVariant,
)

__all__ = [
    "CreativeFormat",
    "CreativeManifest",
    "ListCreativeFormatsResponse",
    "PreviewCreativeRequest",
    "PreviewCreativeResponse",
    "PreviewEmbedding",
    "PreviewHints",
    "PreviewInput",
    "PreviewVariant",
]
