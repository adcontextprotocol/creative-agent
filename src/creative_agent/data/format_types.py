"""Type definitions for building Format objects.

These types mirror the structure expected by Format.assets_required and Format.renders,
but are defined locally since the adcp library uses flexible Any types for these fields.

Note: While Format (from adcp library v1.6+) inherits from AdCPBaseModel which applies
exclude_none=True by default, that only works for Pydantic model fields. Since
assets_required and renders are typed as Any[], they hold raw dicts. We must apply
exclude_none=True when converting these helper models to dicts before passing them to Format.
"""

from enum import Enum

from pydantic import BaseModel, Field


class Type(Enum):
    """Media type of creative format."""

    audio = "audio"
    video = "video"
    display = "display"
    native = "native"
    dooh = "dooh"
    rich_media = "rich_media"
    universal = "universal"


class AssetType(Enum):
    """Type of asset required by a format."""

    image = "image"
    video = "video"
    audio = "audio"
    vast = "vast"
    daast = "daast"
    text = "text"
    markdown = "markdown"
    html = "html"
    css = "css"
    javascript = "javascript"
    url = "url"
    webhook = "webhook"
    promoted_offerings = "promoted_offerings"


class Unit(Enum):
    """Measurement unit for dimensions."""

    px = "px"
    dp = "dp"
    inches = "inches"
    cm = "cm"


class Responsive(BaseModel):
    """Responsive sizing flags."""

    width: bool
    height: bool


class Dimensions(BaseModel):
    """Dimensions specification for a render."""

    width: float | None = Field(None, description="Fixed width in specified units", ge=0.0)
    height: float | None = Field(None, description="Fixed height in specified units", ge=0.0)
    responsive: Responsive
    unit: Unit


class Render(BaseModel):
    """Specification for a single rendered piece."""

    role: str = Field(description="Semantic role (e.g., 'primary', 'companion')")
    dimensions: Dimensions


class AssetsRequired(BaseModel):
    """Specification for a required asset."""

    asset_id: str = Field(description="Identifier for this asset")
    asset_type: AssetType
    required: bool = True
    requirements: dict[str, str | int | float | bool | list[str]] | None = None
