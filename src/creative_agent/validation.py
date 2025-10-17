"""Asset validation for creative manifests."""

import re
from typing import Any
from urllib.parse import urlparse

import httpx


class AssetValidationError(ValueError):
    """Raised when asset validation fails."""


def validate_html_content(content: str) -> None:
    """Validate HTML content is actually HTML.

    Args:
        content: HTML string to validate

    Raises:
        AssetValidationError: If content is not valid HTML
    """
    if not content or not isinstance(content, str):
        raise AssetValidationError("HTML content cannot be empty")

    content_lower = content.lower().strip()

    # Check for basic HTML structure
    has_html_tag = "<html" in content_lower or "<!doctype html>" in content_lower
    has_body_tag = "<body" in content_lower
    has_any_html_tag = bool(re.search(r"<[a-z][\s\S]*?>", content_lower))

    if not has_any_html_tag:
        raise AssetValidationError("HTML content must contain valid HTML tags")

    # If it claims to be a full document, validate structure
    if has_html_tag and not has_body_tag:
        raise AssetValidationError("HTML document must contain <body> tag")


def validate_css_content(content: str) -> None:
    """Validate CSS content has basic CSS syntax.

    Args:
        content: CSS string to validate

    Raises:
        AssetValidationError: If content is not valid CSS
    """
    if not content or not isinstance(content, str):
        raise AssetValidationError("CSS content cannot be empty")

    # Basic CSS syntax check - look for selectors and rules
    has_rule = bool(re.search(r"[^{}]+\{[^{}]*\}", content))

    if not has_rule:
        raise AssetValidationError("CSS content must contain at least one valid rule")


def validate_javascript_content(content: str) -> None:
    """Validate JavaScript content is not empty and looks like JS.

    Args:
        content: JavaScript string to validate

    Raises:
        AssetValidationError: If content is not valid JavaScript
    """
    if not content or not isinstance(content, str):
        raise AssetValidationError("JavaScript content cannot be empty")

    # Very basic check - must have some code-like content
    content_stripped = content.strip()
    if len(content_stripped) < 5:
        raise AssetValidationError("JavaScript content is too short to be valid")


def validate_text_content(content: str) -> None:
    """Validate text content is not empty.

    Args:
        content: Text string to validate

    Raises:
        AssetValidationError: If content is invalid
    """
    if not isinstance(content, str):
        raise AssetValidationError("Text content must be a string")

    if not content.strip():
        raise AssetValidationError("Text content cannot be empty")


def validate_url(url: str) -> None:
    """Validate URL is properly formatted and safe.

    Args:
        url: URL string to validate

    Raises:
        AssetValidationError: If URL is invalid or unsafe
    """
    if not url or not isinstance(url, str):
        raise AssetValidationError("URL cannot be empty")

    # Block dangerous URL schemes
    url_lower = url.lower()
    if url_lower.startswith(("javascript:", "vbscript:", "file:", "about:")):
        raise AssetValidationError(f"URL scheme not allowed: {url.split(':')[0]}")

    # Parse URL structure
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            # Allow data URIs for images
            if url_lower.startswith("data:image/"):
                validate_data_uri(url)
                return
            raise AssetValidationError("URL must have scheme and host")

        if parsed.scheme not in ["http", "https"]:
            raise AssetValidationError(f"URL scheme must be http or https, got: {parsed.scheme}")

    except Exception as e:
        raise AssetValidationError(f"Invalid URL format: {e}") from e


def validate_data_uri(uri: str) -> None:
    """Validate data URI format and size.

    Args:
        uri: Data URI to validate

    Raises:
        AssetValidationError: If data URI is invalid
    """
    if not uri.startswith("data:"):
        raise AssetValidationError("Data URI must start with 'data:'")

    # Check format: data:MIME;encoding,data
    if "," not in uri:
        raise AssetValidationError("Data URI must contain comma separator")

    header, data = uri.split(",", 1)

    # Validate MIME type for images
    mime_part = header.split(";")[0].replace("data:", "")
    allowed_image_mimes = ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp", "image/svg+xml"]

    if not any(mime_part == mime for mime in allowed_image_mimes):
        raise AssetValidationError(f"Data URI MIME type not allowed: {mime_part}")

    # Check size (limit to 10MB for data URIs)
    if len(data) > 10 * 1024 * 1024:
        raise AssetValidationError("Data URI exceeds 10MB size limit")


def validate_image_url(url: str, check_mime: bool = False) -> None:
    """Validate image URL and optionally verify MIME type.

    Args:
        url: Image URL to validate
        check_mime: If True, make HTTP HEAD request to verify content-type

    Raises:
        AssetValidationError: If image URL is invalid
    """
    # Handle data URIs
    if url.startswith("data:"):
        validate_data_uri(url)
        return

    # Validate URL structure
    validate_url(url)

    # Optional MIME type verification
    if check_mime:
        try:
            response = httpx.head(url, timeout=5.0, follow_redirects=True)
            content_type = response.headers.get("content-type", "").lower()

            if not content_type.startswith("image/"):
                raise AssetValidationError(f"URL does not return image content-type: {content_type}")

        except httpx.TimeoutException as e:
            raise AssetValidationError(f"Timeout verifying image URL: {url}") from e
        except httpx.HTTPError as e:
            raise AssetValidationError(f"Error verifying image URL: {e}") from e


def validate_asset(asset_data: dict[str, Any], check_remote_mime: bool = False) -> None:
    """Validate a single asset based on its type.

    Args:
        asset_data: Asset dictionary with asset_type and content
        check_remote_mime: If True, verify MIME types for remote URLs (slower)

    Raises:
        AssetValidationError: If asset validation fails
    """
    if not isinstance(asset_data, dict):
        raise AssetValidationError("Asset must be a dictionary")

    asset_type = asset_data.get("asset_type")
    if not asset_type:
        raise AssetValidationError("Asset must have asset_type field")

    # Validate based on asset type
    if asset_type == "html":
        content = asset_data.get("content")
        if not isinstance(content, str):
            raise AssetValidationError("HTML asset must have string content")
        validate_html_content(content)

    elif asset_type == "css":
        content = asset_data.get("content")
        if not isinstance(content, str):
            raise AssetValidationError("CSS asset must have string content")
        validate_css_content(content)

    elif asset_type == "javascript":
        content = asset_data.get("content")
        if not isinstance(content, str):
            raise AssetValidationError("JavaScript asset must have string content")
        validate_javascript_content(content)

    elif asset_type == "text":
        content = asset_data.get("content")
        if not isinstance(content, str):
            raise AssetValidationError("Text asset must have string content")
        validate_text_content(content)

    elif asset_type == "url":
        url = asset_data.get("url")
        if not isinstance(url, str):
            raise AssetValidationError("URL asset must have string url")
        validate_url(url)

    elif asset_type == "image":
        url = asset_data.get("url")
        if not isinstance(url, str):
            raise AssetValidationError("Image asset must have string url")
        validate_image_url(url, check_mime=check_remote_mime)

        # Validate dimensions if provided
        width = asset_data.get("width")
        height = asset_data.get("height")

        if width is not None and (not isinstance(width, int) or width < 1):
            raise AssetValidationError("Image width must be a positive integer")

        if height is not None and (not isinstance(height, int) or height < 1):
            raise AssetValidationError("Image height must be a positive integer")

        # Validate format if provided
        img_format = asset_data.get("format")
        if img_format:
            allowed_formats = ["jpg", "jpeg", "png", "gif", "webp", "svg"]
            if img_format.lower() not in allowed_formats:
                raise AssetValidationError(f"Image format not allowed: {img_format}")

    elif asset_type in ("video", "audio"):
        url = asset_data.get("url")
        if not isinstance(url, str):
            raise AssetValidationError(f"{asset_type.capitalize()} asset must have string url")
        validate_url(url)

    else:
        raise AssetValidationError(f"Unknown asset_type: {asset_type}")


def validate_manifest_assets(
    manifest: Any,
    check_remote_mime: bool = False,
    format_obj: Any = None,
) -> list[str]:
    """Validate all assets in a creative manifest.

    Args:
        manifest: Creative manifest (should be dictionary with assets field)
        check_remote_mime: If True, verify MIME types for remote URLs (slower)
        format_obj: Format object to validate required assets against (optional)

    Returns:
        List of validation error messages (empty if all valid)
    """
    errors: list[str] = []

    if not isinstance(manifest, dict):
        return ["Manifest must be a dictionary"]

    assets = manifest.get("assets")
    if not assets:
        return ["Manifest must contain assets field"]

    if not isinstance(assets, dict):
        return ["Manifest assets must be a dictionary"]

    # Check required assets if format provided
    if format_obj and hasattr(format_obj, "assets_required") and format_obj.assets_required:
        for required_asset in format_obj.assets_required:
            # Check if this is a required (non-optional) asset
            is_required = getattr(required_asset, "required", True)
            asset_id = getattr(required_asset, "asset_id", None)

            if is_required and asset_id and asset_id not in assets:
                asset_type = getattr(required_asset, "asset_type", "asset")
                errors.append(f"Missing required {asset_type} asset: '{asset_id}'")

    # Validate each asset
    for asset_id, asset_data in assets.items():
        try:
            validate_asset(asset_data, check_remote_mime=check_remote_mime)
        except AssetValidationError as e:
            errors.append(f"Asset '{asset_id}': {e}")

    return errors
