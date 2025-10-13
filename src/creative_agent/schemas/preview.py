"""Preview creative schemas for AdCP."""

from pydantic import BaseModel, HttpUrl

from .brand_card import BrandCard


class PreviewVariant(BaseModel):
    """Request for a specific preview variant."""

    variant_id: str
    device_type: str | None = None  # "desktop", "mobile", "tablet"
    country: str | None = None
    region: str | None = None
    context_description: str | None = None
    macro_values: dict[str, str] = {}


class PreviewCreativeRequest(BaseModel):
    """Request to preview a creative with variants."""

    format_id: str
    brand_card: BrandCard
    promoted_products: list[str] = []  # SKUs or product IDs
    creative_html: str | None = None  # If providing existing creative
    creative_url: HttpUrl | None = None  # If creative is hosted
    variants: list[PreviewVariant] = []
    ai_api_key: str | None = None  # For AI-generated previews


class PreviewResponse(BaseModel):
    """Single preview response."""

    variant_id: str
    preview_url: HttpUrl
    preview_html: str | None = None
    screenshot_url: HttpUrl | None = None
    macros_applied: dict[str, str] = {}


class PreviewCreativeResponse(BaseModel):
    """Response with multiple preview variants."""

    format_id: str
    previews: list[PreviewResponse]
