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
            raise AssetValidationError("URL must have scheme and host")

        if parsed.scheme not in ["http", "https"]:
            raise AssetValidationError(f"URL scheme must be http or https, got: {parsed.scheme}")

    except AssetValidationError:
        raise
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

    else:
        raise AssetValidationError(f"Unknown asset_type: {asset_type}")


def validate_catalog(
    catalog_data: dict[str, Any],
    catalog_requirements: dict[str, Any] | None = None,
    check_remote_mime: bool = False,
) -> list[str]:
    """Validate a catalog entry against optional requirements.

    Args:
        catalog_data: Catalog dictionary with type, items, url, etc.
        catalog_requirements: CatalogRequirements dict to validate against (optional)
        check_remote_mime: If True, verify MIME types for remote URLs

    Returns:
        List of validation error messages (empty if all valid)
    """
    errors: list[str] = []

    # type is required on Catalog
    catalog_type = catalog_data.get("type")
    if not catalog_type:
        errors.append("Catalog must have a 'type' field")
        return errors

    from adcp import CatalogType

    valid_types = {ct.value for ct in CatalogType}
    if catalog_type not in valid_types:
        errors.append(f"Invalid catalog type: '{catalog_type}' (valid: {', '.join(sorted(valid_types))})")

    # Validate URL if provided
    catalog_url = catalog_data.get("url")
    if catalog_url:
        if not isinstance(catalog_url, str):
            errors.append("Catalog url must be a string")
        else:
            try:
                validate_url(catalog_url)
            except AssetValidationError as e:
                errors.append(f"Catalog url: {e}")

    # Validate optional enum fields
    feed_format = catalog_data.get("feed_format")
    if feed_format:
        from adcp import FeedFormat

        valid_feeds = {ff.value for ff in FeedFormat}
        if feed_format not in valid_feeds:
            errors.append(f"Invalid feed_format: '{feed_format}' (valid: {', '.join(sorted(valid_feeds))})")

    content_id_type = catalog_data.get("content_id_type")
    if content_id_type:
        from adcp import ContentIdType

        valid_cid = {c.value for c in ContentIdType}
        if content_id_type not in valid_cid:
            errors.append(f"Invalid content_id_type: '{content_id_type}' (valid: {', '.join(sorted(valid_cid))})")

    update_frequency = catalog_data.get("update_frequency")
    if update_frequency:
        from adcp import UpdateFrequency

        valid_uf = {u.value for u in UpdateFrequency}
        if update_frequency not in valid_uf:
            errors.append(f"Invalid update_frequency: '{update_frequency}' (valid: {', '.join(sorted(valid_uf))})")

    conversion_events = catalog_data.get("conversion_events")
    if conversion_events is not None:
        if not isinstance(conversion_events, list):
            errors.append("conversion_events must be a list")
        else:
            from adcp.types.generated_poc.enums.event_type import EventType

            valid_events = {e.value for e in EventType}
            for i, evt in enumerate(conversion_events):
                if evt not in valid_events:
                    errors.append(f"Invalid conversion_event[{i}]: '{evt}'")

    # Validate items if present
    items = catalog_data.get("items")
    if items is not None:
        if not isinstance(items, list):
            errors.append("Catalog items must be a list")
        elif catalog_requirements:
            # Check required_fields on each item
            required_fields = catalog_requirements.get("required_fields", []) or []
            for i, item in enumerate(items):
                if not isinstance(item, dict):
                    errors.append(f"Catalog item[{i}] must be a dictionary")
                    continue
                for field in required_fields:
                    if field not in item:
                        errors.append(f"Catalog item[{i}]: missing required field '{field}'")

    # Validate against requirements
    if catalog_requirements:
        # min_items constraint
        min_items = catalog_requirements.get("min_items")
        if min_items is not None and items is not None and isinstance(items, list):
            if len(items) < min_items:
                errors.append(f"Catalog requires at least {min_items} items, got {len(items)}")

        # offering_asset_constraints: validate item-level assets
        constraints = catalog_requirements.get("offering_asset_constraints", []) or []
        if constraints and items and isinstance(items, list):
            for i, item in enumerate(items):
                if not isinstance(item, dict):
                    continue
                item_assets = item.get("assets", {})
                if not isinstance(item_assets, dict):
                    continue

                for constraint in constraints:
                    group_id = constraint.get("asset_group_id")
                    if not group_id:
                        continue

                    is_required = constraint.get("required", True)
                    group_data = item_assets.get(group_id)

                    if group_data is None:
                        if is_required:
                            errors.append(f"Catalog item[{i}]: missing required asset group '{group_id}'")
                        continue

                    if not isinstance(group_data, list):
                        group_data = [group_data]

                    min_count = constraint.get("min_count")
                    max_count = constraint.get("max_count")
                    if min_count is not None and len(group_data) < min_count:
                        errors.append(
                            f"Catalog item[{i}] asset '{group_id}': requires at least {min_count} items, got {len(group_data)}"
                        )
                    if max_count is not None and len(group_data) > max_count:
                        errors.append(
                            f"Catalog item[{i}] asset '{group_id}': allows at most {max_count} items, got {len(group_data)}"
                        )

                    # Validate each item against the constraint's asset_type
                    constraint_type = constraint.get("asset_type")
                    if constraint_type:
                        ct_str = constraint_type.value if hasattr(constraint_type, "value") else str(constraint_type)
                        for j, asset_item in enumerate(group_data):
                            if not isinstance(asset_item, dict):
                                errors.append(f"Catalog item[{i}] asset '{group_id}[{j}]': must be a dictionary")
                                continue
                            try:
                                validate_asset(asset_item, ct_str, check_remote_mime=check_remote_mime)
                            except AssetValidationError as e:
                                errors.append(f"Catalog item[{i}] asset '{group_id}[{j}]': {e}")

    return errors


def validate_manifest_assets(
    manifest: Any,
    check_remote_mime: bool = False,
    format_obj: Any = None,
) -> list[str]:
    """Validate all assets and catalogs in a creative manifest.

    Args:
        manifest: Creative manifest (should be dictionary with assets and/or catalogs field)
        check_remote_mime: If True, verify MIME types for remote URLs (slower)
        format_obj: Format object to validate required assets against (optional)

    Returns:
        List of validation error messages (empty if all valid)
    """
    errors: list[str] = []

    if not isinstance(manifest, dict):
        return ["Manifest must be a dictionary"]

    # Check whether format requires catalogs
    has_catalog_requirements = False
    catalog_req_list: list[dict[str, Any]] = []
    if format_obj:
        raw_reqs = getattr(format_obj, "catalog_requirements", None) or []
        for req in raw_reqs:
            req_dict = req.model_dump(exclude_none=True) if hasattr(req, "model_dump") else dict(req)
            catalog_req_list.append(req_dict)
        has_catalog_requirements = len(catalog_req_list) > 0

    # Validate catalogs if format requires them
    if has_catalog_requirements:
        catalogs = manifest.get("catalogs", [])
        if not catalogs:
            for req in catalog_req_list:
                is_required = req.get("required", True)
                if is_required is not False:
                    errors.append(f"Required catalog missing for type: {req.get('catalog_type', 'unknown')}")
        elif isinstance(catalogs, list):
            # Build lookup of catalogs by type
            catalog_by_type: dict[str, dict[str, Any]] = {}
            for catalog in catalogs:
                if isinstance(catalog, dict) and "type" in catalog:
                    catalog_by_type[catalog["type"]] = catalog

            for req in catalog_req_list:
                req_type = req.get("catalog_type")
                if not req_type:
                    continue
                req_type_str = req_type.value if hasattr(req_type, "value") else str(req_type)
                is_required = req.get("required", True)

                matching_catalog = catalog_by_type.get(req_type_str)
                if not matching_catalog:
                    if is_required is not False:
                        errors.append(f"Required catalog missing for type: {req_type_str}")
                    continue

                catalog_errors = validate_catalog(matching_catalog, req, check_remote_mime=check_remote_mime)
                errors.extend(catalog_errors)

                # Check feed_format compatibility
                req_feed_formats = req.get("feed_formats")
                catalog_feed = matching_catalog.get("feed_format")
                if req_feed_formats and catalog_feed:
                    allowed = [ff.value if hasattr(ff, "value") else str(ff) for ff in req_feed_formats]
                    if catalog_feed not in allowed:
                        errors.append(f"Catalog feed_format '{catalog_feed}' not in required formats: {allowed}")

            # Validate any catalogs not covered by requirements
            req_types: set[str] = set()
            for r in catalog_req_list:
                ct = r.get("catalog_type")
                if ct is not None:
                    req_types.add(ct.value if hasattr(ct, "value") else str(ct))
            for catalog in catalogs:
                if isinstance(catalog, dict):
                    ct = catalog.get("type")
                    if ct and ct not in req_types:
                        catalog_errors = validate_catalog(catalog, check_remote_mime=check_remote_mime)
                        errors.extend(catalog_errors)

    assets = manifest.get("assets")
    if not assets and not has_catalog_requirements:
        return ["Manifest must contain assets field"]

    if not assets:
        return errors

    if not isinstance(assets, dict):
        errors.append("Manifest assets must be a dictionary")
        return errors

    # Build maps from format spec if provided:
    #   asset_type_map: (asset_id or asset_group_id) -> content type string
    #   group_counts:   asset_group_id -> (min_count, max_count)
    asset_type_map: dict[str, str] = {}
    group_counts: dict[str, tuple[int | None, int | None]] = {}

    if format_obj:
        from adcp import get_format_assets, get_required_assets

        for asset in get_format_assets(format_obj):
            asset_id = getattr(asset, "asset_id", None)
            asset_type = getattr(asset, "asset_type", None)
            if asset_id and asset_type:
                asset_type_map[asset_id] = asset_type.value if hasattr(asset_type, "value") else str(asset_type)
                continue

            asset_group_id = getattr(asset, "asset_group_id", None)
            if asset_group_id:
                inner_assets = getattr(asset, "assets", [])
                if inner_assets:
                    inner_type = getattr(inner_assets[0], "asset_type", None)
                    if inner_type:
                        asset_type_map[asset_group_id] = (
                            inner_type.value if hasattr(inner_type, "value") else str(inner_type)
                        )
                group_counts[asset_group_id] = (
                    getattr(asset, "min_count", None),
                    getattr(asset, "max_count", None),
                )

        # Check required assets are present in manifest
        for required_asset in get_required_assets(format_obj):
            asset_id = getattr(required_asset, "asset_id", None) or getattr(required_asset, "asset_group_id", None)
            if asset_id and asset_id not in assets:
                errors.append(f"Required asset missing: {asset_id}")

    # Validate each asset
    for asset_id, asset_data in assets.items():
        expected_type = asset_type_map.get(asset_id)

        if isinstance(asset_data, list):
            # Repeatable group: validate count constraints and each item
            min_c, max_c = group_counts.get(asset_id, (None, None))
            if min_c is not None and len(asset_data) < min_c:
                errors.append(f"Asset '{asset_id}': requires at least {min_c} items, got {len(asset_data)}")
            if max_c is not None and len(asset_data) > max_c:
                errors.append(f"Asset '{asset_id}': allows at most {max_c} items, got {len(asset_data)}")

            for i, item in enumerate(asset_data):
                if not isinstance(item, dict) or len(item) != 1:
                    errors.append(
                        f"Asset '{asset_id}[{i}]': each item must be a single-key dict like {{\"text\": {{...}}}}"
                    )
                    continue
                item_type_key, item_data = next(iter(item.items()))
                validate_type = expected_type or item_type_key
                try:
                    validate_asset(item_data, validate_type, check_remote_mime=check_remote_mime)
                except AssetValidationError as e:
                    errors.append(f"Asset '{asset_id}[{i}]': {e}")

        else:
            # Individual asset
            if not expected_type:
                # Try to infer type from asset data
                if "url" in asset_data and "width" in asset_data and "height" in asset_data:
                    expected_type = "image"
                elif "url" in asset_data and "duration_seconds" in asset_data:
                    expected_type = "video"
                elif "content" in asset_data:
                    expected_type = "text"
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
