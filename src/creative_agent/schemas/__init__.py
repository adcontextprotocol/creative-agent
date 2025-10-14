"""
AdCP schemas for creative agent.

This module re-exports official AdCP schemas from the auto-generated schemas_generated/
directory, providing a clean interface for the rest of the codebase.

All schemas are generated from https://adcontextprotocol.org/schemas/v1/
"""

# Asset schemas
from ..schemas_generated._schemas_v1_core_assets_audio_asset_json import AudioAsset
from ..schemas_generated._schemas_v1_core_assets_css_asset_json import CssAsset
from ..schemas_generated._schemas_v1_core_assets_html_asset_json import HtmlAsset
from ..schemas_generated._schemas_v1_core_assets_image_asset_json import ImageAsset
from ..schemas_generated._schemas_v1_core_assets_javascript_asset_json import (
    JavascriptAsset as JavaScriptAsset,
)
from ..schemas_generated._schemas_v1_core_assets_promoted_offerings_asset_json import (
    PromotedOfferingsAsset,
)
from ..schemas_generated._schemas_v1_core_assets_text_asset_json import TextAsset
from ..schemas_generated._schemas_v1_core_assets_url_asset_json import UrlAsset
from ..schemas_generated._schemas_v1_core_assets_video_asset_json import VideoAsset

# Preview schemas (using AdCP creative asset as manifest base)
from ..schemas_generated._schemas_v1_core_creative_asset_json import CreativeAsset as CreativeManifest

# Format schemas
from ..schemas_generated._schemas_v1_core_format_json import Format as CreativeFormat
from ..schemas_generated._schemas_v1_creative_list_creative_formats_response_json import (
    ListCreativeFormatsResponseCreativeAgent as ListCreativeFormatsResponse,
)

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
    "AudioAsset",
    "BuildCreativeRequest",
    "BuildCreativeResponse",
    "CreativeFormat",
    "CreativeManifest",
    "CreativeOutput",
    "CssAsset",
    "FormatRequirements",
    "HtmlAsset",
    "ImageAsset",
    "JavaScriptAsset",
    "ListCreativeFormatsResponse",
    "PreviewContext",
    "PreviewCreativeRequest",
    "PreviewCreativeResponse",
    "PreviewEmbedding",
    "PreviewHints",
    "PreviewInput",
    "PreviewOptions",
    "PreviewVariant",
    "PromotedOfferingsAsset",
    "TextAsset",
    "UrlAsset",
    "VideoAsset",
]
