"""Tigris storage for preview HTML and assets."""

import os
from typing import Any

import boto3
from botocore.client import Config

from .renderers import FormatCardRenderer, ImageRenderer, ProductCardRenderer

# Get Tigris credentials from environment (set by Fly.io)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL_S3")
AWS_REGION = os.getenv("AWS_REGION", "auto")
BUCKET_NAME = os.getenv("BUCKET_NAME", "adcp-previews")


def _validate_s3_config() -> None:
    """Validate S3 configuration on module load.

    Only validates in production to allow tests without credentials.
    """
    if os.getenv("ENVIRONMENT") not in ("production", "prod"):
        return

    required = {
        "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
        "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
        "AWS_ENDPOINT_URL_S3": AWS_ENDPOINT_URL,
    }

    missing = [k for k, v in required.items() if not v]
    if missing:
        raise RuntimeError(f"Missing required S3 configuration: {', '.join(missing)}")


# Validate config on import (only in production)
_validate_s3_config()


def get_s3_client() -> Any:
    """Get configured S3 client for Tigris."""
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        config=Config(signature_version="s3v4"),
    )


def upload_preview_html(preview_id: str, variant_name: str, html_content: str) -> str:
    """Upload preview HTML to Tigris and return public URL.

    Args:
        preview_id: Unique preview session ID
        variant_name: Name of the variant (e.g., "mobile", "desktop")
        html_content: HTML content to upload

    Returns:
        Public URL to the uploaded HTML

    Raises:
        ValueError: If upload fails due to configuration or network issues
    """
    from botocore.exceptions import ClientError, NoCredentialsError

    try:
        s3 = get_s3_client()

        # Create S3 key: previews/{preview_id}/{variant_name}.html
        key = f"previews/{preview_id}/{variant_name}.html"

        # Upload with correct content type
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=html_content.encode("utf-8"),
            ContentType="text/html",
            CacheControl="public, max-age=3600",  # Cache for 1 hour
        )

        # For public buckets, use virtual-hosted-style URL format
        # Format: https://{bucket}.fly.storage.tigris.dev/{key}
        return f"https://{BUCKET_NAME}.fly.storage.tigris.dev/{key}"

    except NoCredentialsError as e:
        msg = "S3 credentials not configured. Check AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY."
        raise ValueError(msg) from e
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        raise ValueError(f"S3 upload failed ({error_code}): {e}") from e
    except Exception as e:
        raise ValueError(f"Unexpected error during S3 upload: {e}") from e


def generate_preview_html(format_obj: Any, manifest: Any, input_set: Any) -> str:
    """Generate HTML preview content for a creative manifest.

    Routes to specialized renderers based on format type.

    Args:
        format_obj: Format definition
        manifest: Creative manifest
        input_set: Preview input configuration

    Returns:
        HTML string ready to display in iframe
    """
    # Get format ID to determine which renderer to use
    format_id = format_obj.format_id.id if hasattr(format_obj.format_id, "id") else str(format_obj.format_id)

    # Route to specialized renderers
    if format_id in ("product_card_standard", "product_card_detailed"):
        renderer: ImageRenderer | ProductCardRenderer | FormatCardRenderer = ProductCardRenderer()
    elif format_id in ("format_card_standard", "format_card_detailed"):
        renderer = FormatCardRenderer()
    else:
        # Default to image renderer for all other formats
        renderer = ImageRenderer()

    return renderer.render(format_obj, manifest, input_set)
