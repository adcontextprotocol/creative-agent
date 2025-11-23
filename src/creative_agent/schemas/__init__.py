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

# Build schemas (agent-specific, not part of AdCP)
from .build import (
    AssetReference,
    BuildCreativeRequest,
    BuildCreativeResponse,
    CreativeOutput,
    PreviewContext,
    PreviewOptions,
)

# Format helpers (agent-specific, not part of AdCP)
from .format_helpers import AssetRequirement, FormatRequirements

# Manifest/Preview schemas - these need manual definitions as they're agent-specific
from .manifest import (
    PreviewCreativeRequest,
    PreviewCreativeResponse,
    PreviewEmbedding,
    PreviewHints,
    PreviewInput,
    PreviewVariant,
)

__all__ = [
    "AssetReference",
    "AssetRequirement",
    "BuildCreativeRequest",
    "BuildCreativeResponse",
    "CreativeFormat",
    "CreativeManifest",
    "CreativeOutput",
    "FormatRequirements",
    "ListCreativeFormatsResponse",
    "PreviewContext",
    "PreviewCreativeRequest",
    "PreviewCreativeResponse",
    "PreviewEmbedding",
    "PreviewHints",
    "PreviewInput",
    "PreviewOptions",
    "PreviewVariant",
]
