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


def validate_asset(asset_data: dict[str, Any], asset_type: str, check_remote_mime: bool = False) -> None:
    """Validate a single asset based on its type.

    IMPORTANT: As of ADCP v2.0.0, asset_type is determined by the format specification,
    not included in the asset payload. The asset_type parameter comes from the format's
    assets_required definition for the given asset_id.

    Args:
        asset_data: Asset dictionary (WITHOUT asset_type field)
        asset_type: Expected asset type from format specification
        check_remote_mime: If True, verify MIME types for remote URLs (slower)

    Raises:
        AssetValidationError: If asset validation fails
    """
    if not isinstance(asset_data, dict):
        raise AssetValidationError("Asset must be a dictionary")

    if not asset_type:
        raise AssetValidationError("asset_type parameter is required for validation")

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

    elif asset_type == "vast":
        # VAST asset requires either url OR content (oneOf per ADCP spec)
        url = asset_data.get("url")
        content = asset_data.get("content")

        if not url and not content:
            raise AssetValidationError("VAST asset must have either url or content")

        if url and content:
            raise AssetValidationError("VAST asset must have url or content, not both")

        if url:
            if not isinstance(url, str):
                raise AssetValidationError("VAST url must be a string")
            validate_url(url)

        if content and not isinstance(content, str):
            raise AssetValidationError("VAST content must be a string")

    elif asset_type == "daast":
        # DAAST asset requires either url OR content (oneOf per ADCP spec)
        url = asset_data.get("url")
        content = asset_data.get("content")

        if not url and not content:
            raise AssetValidationError("DAAST asset must have either url or content")

        if url and content:
            raise AssetValidationError("DAAST asset must have url or content, not both")

        if url:
            if not isinstance(url, str):
                raise AssetValidationError("DAAST url must be a string")
            validate_url(url)

        if content and not isinstance(content, str):
            raise AssetValidationError("DAAST content must be a string")

    elif asset_type == "webhook":
        # Webhook validation
        url = asset_data.get("url")
        if not url:
            raise AssetValidationError("Webhook asset must have url")
        if not isinstance(url, str):
            raise AssetValidationError("Webhook url must be a string")
        validate_url(url)

    elif asset_type == "promoted_offerings":
        # Promoted offerings validation - used for generative creative formats
        # Contains brand manifest and product selectors
        # Per spec: can be inline object OR URL reference

        # Check if there's a brand_manifest field (can be URL or object)
        brand_manifest = asset_data.get("brand_manifest")
        if brand_manifest:
            if isinstance(brand_manifest, str):
                # URL reference to hosted manifest
                validate_url(brand_manifest)
            elif isinstance(brand_manifest, dict):
                # Inline brand manifest - must have url OR name
                url = brand_manifest.get("url")
                name = brand_manifest.get("name")
                if not url and not name:
                    raise AssetValidationError("Inline brand manifest must have either url or name")
                if url:
                    if not isinstance(url, str):
                        raise AssetValidationError("Brand manifest url must be a string")
                    validate_url(url)
                if name and not isinstance(name, str):
                    raise AssetValidationError("Brand manifest name must be a string")
            else:
                raise AssetValidationError("brand_manifest must be a URL string or object")

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

    # Build a map of asset_id -> asset_type from format if provided
    asset_type_map = {}
    if format_obj and hasattr(format_obj, "assets_required") and format_obj.assets_required:
        for required_asset in format_obj.assets_required:
            asset_id = getattr(required_asset, "asset_id", None)
            asset_type = getattr(required_asset, "asset_type", None)

            if asset_id and asset_type:
                # Handle enum or string asset_type
                if hasattr(asset_type, "value"):
                    asset_type_map[asset_id] = asset_type.value
                else:
                    asset_type_map[asset_id] = str(asset_type)

            # Check if this is a required (non-optional) asset
            is_required = getattr(required_asset, "required", True)
            if is_required and asset_id and asset_id not in assets:
                errors.append(f"Required asset missing: {asset_id}")

    # Validate each asset
    for asset_id, asset_data in assets.items():
        # Get expected asset type from format spec
        expected_type = asset_type_map.get(asset_id)

        if not expected_type:
            # No format provided or asset not in format spec
            # Try to infer type from asset data (for backward compatibility during transition)
            if "url" in asset_data and "width" in asset_data and "height" in asset_data:
                expected_type = "image"
            elif "url" in asset_data and "duration_seconds" in asset_data:
                expected_type = "video"  # or audio, hard to distinguish
            elif "content" in asset_data:
                expected_type = "text"  # could be html/js/css too
            elif "url" in asset_data:
                expected_type = "url"
            else:
                errors.append(
                    f"Asset '{asset_id}': Cannot determine asset type (format not provided or asset_id not in format spec)"
                )
                continue

        try:
            validate_asset(asset_data, expected_type, check_remote_mime=check_remote_mime)
        except AssetValidationError as e:
            errors.append(f"Asset '{asset_id}': {e}")

    return errors
