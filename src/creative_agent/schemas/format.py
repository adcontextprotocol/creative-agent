"""Creative format schemas for AdCP."""

from typing import Literal

from pydantic import BaseModel


class AssetRequirement(BaseModel):
    """Requirement for a single asset in a format."""

    asset_role: str  # e.g., "hero_image", "headline"
    asset_type: str  # image, video, audio, text, etc.
    required: bool = True
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
    """Complete creative format definition."""

    format_id: str
    agent_url: str  # Authoritative source for this format
    name: str
    type: Literal["video", "display", "audio", "native", "dooh", "generative"]
    category: str | None = None  # standard, custom, etc.
    is_standard: bool | None = None
    description: str | None = None
    iab_specification: str | None = None  # URL to IAB spec
    accepts_3p_tags: bool | None = False
    dimensions: str | None = None  # "300x250", "728x90", etc.
    supported_macros: list[str] | None = None
    requirements: FormatRequirements | None = None
    assets_required: list[AssetRequirement]
    output_format: str | None = None  # For generative formats: the format_id this produces


class ListCreativeFormatsRequest(BaseModel):
    """Request for list_creative_formats task."""

    format_ids: list[str] | None = None
    type: Literal["audio", "video", "display", "dooh", "native", "interactive"] | None = None
    asset_types: list[str] | None = None
    dimensions: str | None = None
    name_search: str | None = None


class ListCreativeFormatsResponse(BaseModel):
    """Response from list_creative_formats task."""

    adcp_version: str = "1.0.0"
    agent_url: str
    agent_name: str
    capabilities: list[str]  # validation, assembly, generation, preview
    formats: list[CreativeFormat]
    creative_agents: list[str] | None = None  # URLs to other creative agents
