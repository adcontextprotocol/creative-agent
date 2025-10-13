"""Brand card schema for AdCP creative agent."""

from pydantic import BaseModel, HttpUrl


class BrandAsset(BaseModel):
    """Brand asset with URL and metadata."""

    asset_id: str
    asset_type: str  # "image", "video", "logo", etc.
    url: HttpUrl
    tags: list[str] = []
    width: int | None = None
    height: int | None = None
    description: str | None = None


class BrandCard(BaseModel):
    """Brand card containing brand identity and assets."""

    brand_url: HttpUrl
    brand_name: str | None = None
    brand_description: str | None = None
    assets: list[BrandAsset] = []
    product_catalog_url: HttpUrl | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
