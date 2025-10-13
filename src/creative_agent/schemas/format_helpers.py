"""Helper classes for defining creative formats (not part of AdCP spec)."""

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
