"""Manage creative library schemas for AdCP."""

from typing import Any, Literal

from pydantic import BaseModel, HttpUrl


class AssetMetadata(BaseModel):
    """Asset metadata."""

    width: int | None = None
    height: int | None = None
    duration: float | None = None  # seconds
    file_size: int | None = None  # bytes
    mime_type: str | None = None
    alt_text: str | None = None


class Asset(BaseModel):
    """Creative asset."""

    asset_id: str | None = None  # Auto-generated if not provided
    name: str
    type: Literal["image", "video", "audio", "text", "logo"]
    url: HttpUrl | None = None
    content: str | None = None  # For text assets
    metadata: AssetMetadata | None = None
    tags: list[str] = []
    usage_rights: Literal["unlimited", "limited", "exclusive"] | None = None
    expires_at: str | None = None  # ISO date


class SearchFilters(BaseModel):
    """Filters for asset search."""

    type: str | None = None
    tags: list[str] = []
    usage_rights: str | None = None


class ManageCreativeLibraryRequest(BaseModel):
    """Request to manage creative library (AdCP spec)."""

    action: Literal["add", "update", "remove", "list", "search"]
    library_id: str
    asset: Asset | None = None  # Required for add/update
    assets: list[Asset] | None = None  # For bulk add
    asset_id: str | None = None  # Required for update/remove
    tags: list[str] = []  # For filtering/updating
    search_query: str | None = None
    filters: SearchFilters | None = None


class ManageCreativeLibraryResponse(BaseModel):
    """Response from manage_creative_library (AdCP spec)."""

    message: str
    success: bool
    result: Any  # Varies by action: asset, list of assets, etc.
