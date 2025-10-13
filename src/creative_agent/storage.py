"""Tigris storage for preview HTML and assets."""

import os
from typing import Any

import boto3
from botocore.client import Config

# Get Tigris credentials from environment (set by Fly.io)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL_S3")
AWS_REGION = os.getenv("AWS_REGION", "auto")
BUCKET_NAME = os.getenv("BUCKET_NAME", "adcp-previews")


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
    """
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


def generate_preview_html(format_obj: Any, manifest: Any, input_set: Any) -> str:
    """Generate HTML preview content for a creative manifest.

    Args:
        format_obj: Format definition
        manifest: Creative manifest
        input_set: Preview input configuration

    Returns:
        HTML string ready to display in iframe
    """
    # Extract dimensions if available
    width = 300
    height = 250
    if format_obj.dimensions:
        parts = format_obj.dimensions.split("x")
        if len(parts) == 2:
            width = int(parts[0])
            height = int(parts[1])

    # Get primary image asset
    image_url = None
    for _asset_role, asset_data in manifest.assets.items():
        if isinstance(asset_data, dict) and asset_data.get("asset_type") == "image":
            image_url = asset_data.get("url")
            break

    # Get click URL
    click_url = None
    for _asset_role, asset_data in manifest.assets.items():
        if isinstance(asset_data, dict) and asset_data.get("asset_type") == "url":
            click_url = asset_data.get("url")
            break

    # Generate simple HTML preview
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{format_obj.name} - {input_set.name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            width: {width}px;
            height: {height}px;
            overflow: hidden;
            font-family: Arial, sans-serif;
        }}
        .creative-container {{
            width: 100%;
            height: 100%;
            position: relative;
            cursor: pointer;
        }}
        .creative-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .preview-label {{
            position: absolute;
            top: 5px;
            left: 5px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 2px 6px;
            font-size: 10px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="creative-container" onclick="handleClick()">
"""

    if image_url:
        html += f'        <img src="{image_url}" alt="{format_obj.name}">\n'
    else:
        html += f'        <div style="background: #f0f0f0; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #666;">{format_obj.name}</div>\n'

    html += f"""        <div class="preview-label">{input_set.name}</div>
    </div>
    <script>
        function handleClick() {{
"""

    if click_url:
        html += f'            window.open("{click_url}", "_blank");\n'
    else:
        html += '            console.log("Click registered - no URL configured");\n'

    html += """        }
    </script>
</body>
</html>"""

    return html
