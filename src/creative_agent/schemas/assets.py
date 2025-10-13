"""Asset type schemas for AdCP creative manifests."""

from typing import Any, Literal

from pydantic import BaseModel


class ImageAsset(BaseModel):
    """Image asset type."""

    asset_type: Literal["image"] = "image"
    url: str
    width: int
    height: int
    format: str  # jpg, png, gif, webp, etc.
    file_size: int | None = None  # bytes
    alt: str | None = None


class VideoAsset(BaseModel):
    """Video asset type."""

    asset_type: Literal["video"] = "video"
    url: str
    width: int
    height: int
    duration_seconds: int
    format: str  # mp4, mov, webm, etc.
    codec: str | None = None  # h264, h265, vp9, av1
    bitrate_mbps: float | None = None
    file_size: int | None = None  # bytes


class AudioAsset(BaseModel):
    """Audio asset type."""

    asset_type: Literal["audio"] = "audio"
    url: str
    duration_seconds: int
    format: str  # mp3, aac, wav, etc.
    codec: str | None = None
    bitrate_kbps: int | None = None
    sample_rate_hz: int | None = None
    channels: int | None = None  # 1 = mono, 2 = stereo
    file_size: int | None = None  # bytes


class VastTagAsset(BaseModel):
    """VAST tag asset type."""

    asset_type: Literal["vast_tag"] = "vast_tag"
    content: str  # VAST XML
    vast_version: str  # "2.0", "3.0", "4.0", "4.1", "4.2"
    vpaid_enabled: bool | None = None
    duration_seconds: int | None = None


class TextAsset(BaseModel):
    """Text asset type."""

    asset_type: Literal["text"] = "text"
    content: str
    length: int | None = None  # character count
    format: Literal["plain", "html", "markdown"] | None = "plain"


class UrlAsset(BaseModel):
    """URL asset type (for tracking pixels, clickthrough URLs, etc.)."""

    asset_type: Literal["url"] = "url"
    url: str
    url_purpose: str | None = None  # clickthrough, impression, tracking, etc.


class HtmlAsset(BaseModel):
    """HTML asset type (client-side third-party tags)."""

    asset_type: Literal["html"] = "html"
    content: str | None = None  # HTML content (if inline)
    url: str | None = None  # URL to HTML (if hosted)
    width: int | None = None
    height: int | None = None
    file_size: int | None = None  # bytes


class JavaScriptAsset(BaseModel):
    """JavaScript asset type (client-side third-party tags)."""

    asset_type: Literal["javascript"] = "javascript"
    content: str | None = None  # JS code (if inline)
    url: str | None = None  # URL to JS file (if hosted)
    inline: bool | None = None  # Whether JS should be inlined


class WebhookAsset(BaseModel):
    """Webhook asset type (server-side dynamic rendering)."""

    asset_type: Literal["webhook"] = "webhook"
    url: str
    method: Literal["GET", "POST"] | None = "POST"
    timeout_ms: int | None = 500
    response_type: str | None = "html"  # html, json, image, etc.
    supported_macros: list[str] | None = None
    security: dict[str, Any] | None = None  # HMAC, JWT, etc.
    fallback_required: bool | None = True


class PromotedOfferingsAsset(BaseModel):
    """Promoted offerings asset type (brand context for generative creatives)."""

    asset_type: Literal["promoted_offerings"] = "promoted_offerings"
    offerings: list[dict[str, Any]]  # Array of offering objects with name, description, assets


# Union type for all asset types
Asset = (
    ImageAsset
    | VideoAsset
    | AudioAsset
    | VastTagAsset
    | TextAsset
    | UrlAsset
    | HtmlAsset
    | JavaScriptAsset
    | WebhookAsset
    | PromotedOfferingsAsset
)
