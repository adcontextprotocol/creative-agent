"""FastMCP server for AdCP Creative Agent v1 - standalone entry point.

Focuses on:
1. list_creative_formats - Returns all AdCP creative formats
2. preview_creative - Generates previews from creative manifests
"""

import json
import sys
import uuid
from pathlib import Path

# Add src to path so we can import
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from creative_agent.data.standard_formats import STANDARD_FORMATS, get_format_by_id

mcp = FastMCP("adcp-creative-agent")


# Response models
class FormatWithExample(BaseModel):
    """Format definition with manifest example."""

    format_id: str = Field(description="Unique format identifier")
    name: str = Field(description="Human-readable format name")
    type: str = Field(description="Format type (display, video, audio, native, dooh)")
    description: str | None = Field(None, description="Format description")
    requirements: dict | None = Field(None, description="Format requirements and constraints")
    assets_required: list[dict] = Field(
        default_factory=list, description="Required and optional assets with specifications"
    )
    supported_macros: list[str] | None = Field(None, description="Supported macro substitutions")
    manifest_example: dict = Field(description="Complete working example of a valid manifest")


class ListFormatsResponse(BaseModel):
    """Response from list_creative_formats."""

    formats: list[FormatWithExample] = Field(description="List of available formats with examples")


class ValidationError(BaseModel):
    """Validation error with JSON Pointer path."""

    path: str = Field(description="JSON Pointer to the error location (e.g., /assets/banner_image)")
    message: str = Field(description="Human-readable error message")
    type: str = Field(description="Error type (e.g., missing_required_field, invalid_type)")
    hint: str | None = Field(None, description="Hint for fixing the error")
    example: dict | None = Field(None, description="Example of correct value")
    asset_type: str | None = Field(None, description="Required asset type")
    requirements: dict | None = Field(None, description="Asset requirements")


class PreviewErrorResponse(BaseModel):
    """Error response from preview_creative."""

    errors: list[ValidationError] = Field(description="List of validation errors")


class PreviewSuccessResponse(BaseModel):
    """Success response from preview_creative."""

    preview_id: str = Field(description="Unique preview identifier")
    format_id: str = Field(description="Format used for preview")
    preview_url: str = Field(description="URL to view the preview")
    iframe_html: str = Field(description="HTML iframe code for embedding the preview")
    manifest: dict = Field(description="The manifest that was used to generate the preview")


@mcp.tool()
def list_creative_formats() -> ListFormatsResponse:
    """List all available AdCP creative formats.

    Returns all standard creative formats defined in the AdCP spec including
    video, display, audio, DOOH, and foundational interactive formats.

    Each format includes:
    - format_id: Unique identifier for the format
    - name: Human-readable name
    - type: Format type (display, video, audio, native, dooh)
    - assets_required: Array of required and optional assets with:
      - asset_id: Key to use in manifest assets dictionary
      - asset_type: Type of asset (image, video, url, text, etc.)
      - required: Whether the asset is required
      - requirements: Constraints like dimensions, file size, formats
    - manifest_example: Complete working example of a valid manifest
    """
    formats_data = []
    for fmt in STANDARD_FORMATS:
        fmt_dict = fmt.model_dump(mode="json")

        # Add manifest example for this format
        manifest_example = {"format_id": fmt.format_id, "assets": {}}

        # Build example assets based on format requirements
        if fmt.assets_required:
            for asset_req in fmt.assets_required:
                asset_id = asset_req.asset_id
                asset_type = (
                    asset_req.asset_type.value if hasattr(asset_req.asset_type, "value") else asset_req.asset_type
                )

                # Provide concrete examples based on asset type
                if asset_type == "image":
                    manifest_example["assets"][asset_id] = {"url": "https://example.com/image.jpg"}
                elif asset_type == "video":
                    manifest_example["assets"][asset_id] = {"url": "https://example.com/video.mp4"}
                elif asset_type == "audio":
                    manifest_example["assets"][asset_id] = {"url": "https://example.com/audio.mp3"}
                elif asset_type == "url":
                    manifest_example["assets"][asset_id] = {"url": "https://example.com/landing"}
                elif asset_type == "text":
                    manifest_example["assets"][asset_id] = {"value": "Example text content"}
                elif asset_type == "html":
                    manifest_example["assets"][asset_id] = {"value": "<div>Example HTML</div>"}
                elif asset_type == "brand_manifest":
                    manifest_example["assets"][asset_id] = {"url": "https://example.com/brand.json"}

                # Skip if optional
                if not asset_req.required:
                    continue

        fmt_dict["manifest_example"] = manifest_example

        # Convert type enum to string for response
        if "type" in fmt_dict and hasattr(fmt_dict["type"], "value"):
            fmt_dict["type"] = fmt_dict["type"].value
        elif isinstance(fmt_dict.get("type"), object) and not isinstance(fmt_dict["type"], str):
            fmt_dict["type"] = str(fmt_dict["type"])

        formats_data.append(FormatWithExample(**fmt_dict))

    return ListFormatsResponse(formats=formats_data)


@mcp.tool()
def preview_creative(manifest_json: str) -> PreviewSuccessResponse | PreviewErrorResponse:
    """Generate a preview from a creative manifest.

    Takes a creative manifest and generates a rendered preview.
    Returns a URL or iframe HTML for viewing the creative.

    Args:
        manifest_json: JSON creative manifest with format_id and creative assets

    Returns:
        JSON with preview_url, iframe_html, and rendered creative details
        OR JSON with errors array containing validation failures

    Manifest structure:
        {
            "format_id": "display_300x250_image",
            "assets": {
                "banner_image": {
                    "url": "https://example.com/300x250.jpg"
                },
                "click_url": {
                    "url": "https://example.com/landing"
                }
            }
        }

    Notes:
    - assets must be a dictionary keyed by asset_id (not a list)
    - Each asset should have a "url" field (for media) or "value" field (for text/html)
    - Use list_creative_formats to see manifest_example for each format
    """
    try:
        manifest = json.loads(manifest_json)
    except json.JSONDecodeError as e:
        return PreviewErrorResponse(
            errors=[ValidationError(path="/", message=f"Invalid JSON: {e!s}", type="json_syntax_error")]
        )

    errors: list[ValidationError] = []

    # Validate format_id
    format_id = manifest.get("format_id")
    if not format_id:
        errors.append(
            ValidationError(path="/format_id", message="format_id is required", type="missing_required_field")
        )
        return PreviewErrorResponse(errors=errors)

    fmt = get_format_by_id(format_id)
    if not fmt:
        errors.append(
            ValidationError(
                path="/format_id",
                message=f"Format '{format_id}' not found",
                type="invalid_format_id",
                hint="Use list_creative_formats to see available formats",
            )
        )
        return PreviewErrorResponse(errors=errors)

    # Validate assets structure
    assets = manifest.get("assets")
    if assets is None:
        errors.append(
            ValidationError(path="/assets", message="assets field is required", type="missing_required_field")
        )
    elif not isinstance(assets, dict):
        errors.append(
            ValidationError(
                path="/assets",
                message=f"assets must be a dictionary, got {type(assets).__name__}",
                type="invalid_type",
                hint="Use asset_id as keys, e.g. {'banner_image': {'url': '...'}, 'click_url': {'url': '...'}}",
            )
        )
    # Validate required assets
    elif fmt.assets_required:
        for asset_req in fmt.assets_required:
            if not asset_req.required:
                continue

            asset_id = asset_req.asset_id
            if asset_id not in assets:
                errors.append(
                    ValidationError(
                        path=f"/assets/{asset_id}",
                        message=f"Required asset '{asset_id}' is missing",
                        type="missing_required_asset",
                        asset_type=asset_req.asset_type.value
                        if hasattr(asset_req.asset_type, "value")
                        else str(asset_req.asset_type),
                        requirements=asset_req.requirements
                        if hasattr(asset_req, "requirements") and asset_req.requirements
                        else {},
                    )
                )
                continue

            # Validate asset structure
            asset = assets[asset_id]
            if not isinstance(asset, dict):
                errors.append(
                    ValidationError(
                        path=f"/assets/{asset_id}",
                        message="Asset must be a dictionary with 'url' or 'value' field",
                        type="invalid_asset_structure",
                    )
                )
                continue

            # Check for url or value field
            asset_type = (
                asset_req.asset_type.value if hasattr(asset_req.asset_type, "value") else str(asset_req.asset_type)
            )
            if asset_type in ["image", "video", "audio", "url", "brand_manifest"]:
                if "url" not in asset:
                    errors.append(
                        ValidationError(
                            path=f"/assets/{asset_id}/url",
                            message=f"Asset of type '{asset_type}' requires a 'url' field",
                            type="missing_required_field",
                            example={"url": "https://example.com/asset.jpg"},
                        )
                    )
            elif asset_type in ["text", "html"]:
                if "value" not in asset:
                    errors.append(
                        ValidationError(
                            path=f"/assets/{asset_id}/value",
                            message=f"Asset of type '{asset_type}' requires a 'value' field",
                            type="missing_required_field",
                            example={"value": "Example content"},
                        )
                    )

    if errors:
        return PreviewErrorResponse(errors=errors)

    # Generate preview ID
    preview_id = str(uuid.uuid4())

    # Build iframe HTML based on format type
    try:
        type_value = fmt.type.value if hasattr(fmt.type, "value") else fmt.type

        if type_value == "display":
            # Extract dimensions from format requirements or manifest
            width = manifest.get("width")
            height = manifest.get("height")

            if not width or not height:
                if fmt.requirements and "dimensions" in fmt.requirements:
                    dims = fmt.requirements["dimensions"]
                    if "x" in dims:
                        parts = dims.split("x")
                        width = int(parts[0])
                        height = int(parts[1])

            width = width or 300
            height = height or 250

            # Get asset URLs from the new structure
            image_url = ""
            click_url = "#"

            for asset_id, asset_data in assets.items():
                if isinstance(asset_data, dict):
                    if "banner_image" in asset_id or "image" in asset_id:
                        image_url = asset_data.get("url", "")
                    elif "click_url" in asset_id:
                        click_url = asset_data.get("url", "#")

            iframe_html = f"""
<iframe width="{width}" height="{height}" style="border: 1px solid #ccc;">
    <a href="{click_url}" target="_blank">
        <img src="{image_url}" width="{width}" height="{height}" alt="Ad Creative" />
    </a>
</iframe>
""".strip()

        elif type_value == "video":
            width = manifest.get("width", 640)
            height = manifest.get("height", 360)

            video_url = ""
            for asset_id, asset_data in assets.items():
                if isinstance(asset_data, dict) and "video" in asset_id:
                    video_url = asset_data.get("url", "")
                    break

            iframe_html = f"""
<iframe width="{width}" height="{height}" style="border: 1px solid #ccc;">
    <video width="{width}" height="{height}" controls>
        <source src="{video_url}" type="video/mp4">
    </video>
</iframe>
""".strip()

        else:
            # Generic HTML preview
            iframe_html = f"<div>Preview for {fmt.name} (format_id: {format_id})</div>"

        return PreviewSuccessResponse(
            preview_id=preview_id,
            format_id=format_id,
            preview_url=f"https://preview.adcp.example.com/{preview_id}",
            iframe_html=iframe_html,
            manifest=manifest,
        )

    except Exception as e:
        return PreviewErrorResponse(
            errors=[
                ValidationError(path="/", message=f"Internal error generating preview: {e!s}", type="server_internal")
            ]
        )
