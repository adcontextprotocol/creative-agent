"""Creative format schemas for AdCP."""

from typing import Any, Literal

from pydantic import BaseModel, HttpUrl


class AssetRequirement(BaseModel):
    """Requirement for a single asset in a format."""

    asset_id: str  # Identifier for this asset in the format
    asset_type: Literal["image", "video", "audio", "text", "html", "javascript", "url", "brand_manifest"]
    asset_role: str | None = None  # e.g., "hero_image", "headline"
    required: bool = True
    requirements: dict[str, Any] | None = None  # Technical requirements (dimensions, file size, duration, etc.)
    # Legacy fields for backward compatibility
    width: int | None = None
    height: int | None = None
    duration_seconds: int | None = None
    max_file_size_mb: float | None = None
    acceptable_formats: list[str] | None = None
    description: str | None = None


class FormatRequirements(BaseModel):
    """Technical requirements for a format."""

    duration_seconds: int | None = None
    max_file_size_mb: float | None = None
    acceptable_formats: list[str] | None = None
    aspect_ratios: list[str] | None = None
    min_bitrate_kbps: int | None = None
    max_bitrate_kbps: int | None = None


class CreativeFormat(BaseModel):
    """Complete creative format definition (AdCP v1.7.0)."""

    format_id: str
    agent_url: HttpUrl | str  # Authoritative source for this format
    name: str
    type: Literal["audio", "video", "display", "native", "dooh", "rich_media", "universal"]
    category: Literal["standard", "custom"] | None = None
    is_standard: bool | None = None
    description: str | None = None
    preview_image: HttpUrl | None = None  # Preview image URL for format browsing/discovery UI
    example_url: HttpUrl | None = None  # URL to showcase page with examples and demos
    requirements: dict[str, Any] | FormatRequirements | None = (
        None  # Technical specifications (dimensions, duration, file size, codecs)
    )
    assets_required: list[AssetRequirement]
    delivery: dict[str, Any] | None = None  # Delivery method specifications (hosted, VAST, third-party tags)
    accepts_3p_tags: bool | None = False
    supported_macros: list[str] | None = None
    output_format_ids: list[str] | None = None  # For generative formats: format IDs this can generate
    # Legacy fields for backward compatibility
    iab_specification: str | None = None  # URL to IAB spec
    dimensions: str | None = None  # "300x250", "728x90", etc.


class ListCreativeFormatsRequest(BaseModel):
    """Request for list_creative_formats task (AdCP v1.6.0)."""

    adcp_version: str = "1.6.0"
    format_ids: list[str] | None = None
    type: Literal["audio", "video", "display", "dooh"] | None = None
    asset_types: list[Literal["image", "video", "audio", "text", "html", "javascript", "url"]] | None = None
    dimensions: str | None = None
    name_search: str | None = None


class CreativeAgentInfo(BaseModel):
    """Information about a creative agent."""

    agent_url: HttpUrl
    agent_name: str | None = None
    capabilities: list[Literal["validation", "assembly", "generation", "preview"]] | None = None


class ListCreativeFormatsResponse(BaseModel):
    """Response from list_creative_formats task (AdCP v1.7.0)."""

    adcp_version: str = "1.7.0"
    status: Literal["pending", "in_progress", "completed", "failed"] = "completed"
    formats: list[CreativeFormat]
    creative_agents: list[CreativeAgentInfo] | None = None
    errors: list[dict[str, Any]] | None = None
