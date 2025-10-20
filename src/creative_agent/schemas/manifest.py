"""Creative manifest schemas for AdCP."""

from typing import Any

from pydantic import BaseModel

from ..schemas_generated._schemas_v1_core_format_json import FormatId

# CreativeManifest is imported from AdCP schemas via __init__.py
# (uses CreativeAsset from AdCP as the base)


class PreviewInput(BaseModel):
    """Input set for preview generation."""

    name: str  # Human-readable name
    macros: dict[str, str] | None = None  # Macro values to apply
    context_description: str | None = None  # Natural language context for AI


class PreviewCreativeRequest(BaseModel):
    """Request for preview_creative task."""

    format_id: FormatId
    creative_manifest: dict[str, Any]  # AdCP CreativeAsset structure (including promoted_offerings if required)
    inputs: list[PreviewInput] | None = None
    template_id: str | None = None


class PreviewHints(BaseModel):
    """Optimization metadata for preview content."""

    primary_media_type: str | None = None  # image, video, audio
    estimated_dimensions: dict[str, int] | None = None  # width, height
    estimated_duration_seconds: int | None = None
    contains_audio: bool | None = None
    requires_interaction: bool | None = None


class PreviewEmbedding(BaseModel):
    """Security metadata for embedding preview content."""

    recommended_sandbox: str | None = None  # e.g., "allow-scripts allow-same-origin"
    requires_https: bool | None = None
    supports_fullscreen: bool | None = None
    csp_policy: str | None = None


class PreviewVariant(BaseModel):
    """A single preview variant - always returns HTML page for iframe embedding."""

    preview_url: str  # URL to HTML page
    input: PreviewInput | None = None  # The input set that generated this preview
    hints: PreviewHints | None = None  # Optional optimization metadata
    embedding: PreviewEmbedding | None = None  # Optional security metadata


class PreviewCreativeResponse(BaseModel):
    """Response from preview_creative task."""

    adcp_version: str = "1.0.0"
    previews: list[PreviewVariant]
    interactive_url: str | None = None
    expires_at: str | None = None  # ISO 8601 timestamp
