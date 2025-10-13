"""AdCP Creative Agent MCP Server - Spec Compliant Implementation."""

import json
import os
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from fastmcp import FastMCP

from .data.standard_formats import (
    AGENT_CAPABILITIES,
    AGENT_NAME,
    AGENT_URL,
    filter_formats,
    get_format_by_id,
)
from .schemas.build import BuildCreativeRequest, BuildCreativeResponse, CreativeOutput
from .schemas.format import ListCreativeFormatsResponse
from .schemas.manifest import PreviewCreativeRequest, PreviewCreativeResponse, PreviewVariant

mcp = FastMCP("adcp-creative-agent")


@mcp.tool()
def list_creative_formats(
    format_ids: list[str] | None = None,
    type: str | None = None,
    asset_types: list[str] | None = None,
    dimensions: str | None = None,
    name_search: str | None = None,
) -> str:
    """List all available AdCP creative formats with optional filtering.

    Args:
        format_ids: Return only these specific format IDs
        type: Filter by format type (audio, video, display, dooh, native, interactive)
        asset_types: Filter to formats that include these asset types
        dimensions: Filter to formats with specific dimensions (e.g., "300x250")
        name_search: Search for formats by name (case-insensitive partial match)

    Returns:
        JSON string with format list response
    """
    try:
        formats = filter_formats(
            format_ids=format_ids,
            type=type,
            asset_types=asset_types,
            dimensions=dimensions,
            name_search=name_search,
        )

        response = ListCreativeFormatsResponse(
            agent_url=AGENT_URL,
            agent_name=AGENT_NAME,
            capabilities=AGENT_CAPABILITIES,
            formats=formats,
        )

        return response.model_dump_json(indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def preview_creative(
    format_id: str,
    creative_manifest: dict[str, Any],
    inputs: list[dict[str, Any]] | None = None,
    template_id: str | None = None,
    brand_card: dict[str, Any] | None = None,
    promoted_products: dict[str, Any] | None = None,
    asset_filters: dict[str, Any] | None = None,
) -> str:
    """Generate preview renderings of a creative manifest.

    Args:
        format_id: Format identifier for rendering
        creative_manifest: Complete creative manifest with all required assets
        inputs: Array of input sets for generating multiple preview variants
        template_id: Specific template for custom format rendering
        brand_card: Brand information manifest providing context for dynamic previews
        promoted_products: Products/offerings being promoted
        asset_filters: Filters to select specific assets from brand card (tags, asset_types, exclude_tags)

    Returns:
        JSON string with preview response containing array of preview variants
    """
    try:
        # Import schema types
        from .schemas.manifest import CreativeManifest, PreviewInput

        # Parse manifest dict into CreativeManifest
        manifest_obj = CreativeManifest(**creative_manifest)

        # Parse inputs if provided
        inputs_obj: list[PreviewInput] | None = None
        if inputs:
            inputs_obj = [PreviewInput(**inp) for inp in inputs]

        # Parse request
        request = PreviewCreativeRequest(
            format_id=format_id,
            creative_manifest=manifest_obj,
            inputs=inputs_obj,
            template_id=template_id,
            brand_card=brand_card,
            promoted_products=promoted_products,
            asset_filters=asset_filters,
        )

        # Validate format exists
        fmt = get_format_by_id(request.format_id)
        if not fmt:
            return json.dumps(
                {"error": f"Format {request.format_id} not found"},
                indent=2,
            )

        # Validate manifest format_id matches
        if request.creative_manifest.format_id != request.format_id:
            return json.dumps(
                {
                    "error": f"Manifest format_id '{request.creative_manifest.format_id}' does not match request format_id '{request.format_id}'"
                },
                indent=2,
            )

        # Generate preview variants
        previews = []
        preview_id = str(uuid.uuid4())

        # If no inputs provided, generate default variants (desktop, mobile, tablet)
        if not request.inputs:
            request.inputs = [
                PreviewInput(name="Desktop", macros={"DEVICE_TYPE": "desktop"}),
                PreviewInput(name="Mobile", macros={"DEVICE_TYPE": "mobile"}),
                PreviewInput(name="Tablet", macros={"DEVICE_TYPE": "tablet"}),
            ]

        # Generate a preview for each input set
        from .storage import generate_preview_html, upload_preview_html

        for input_set in request.inputs:
            # Generate HTML content
            html_content = generate_preview_html(fmt, request.creative_manifest, input_set)

            # Upload to Tigris and get public URL
            variant_name = input_set.name.lower().replace(" ", "-")
            preview_url = upload_preview_html(preview_id, variant_name, html_content)

            # Create preview variant with actual URL
            preview = _generate_preview_variant(
                format_obj=fmt,
                manifest=request.creative_manifest,
                input_set=input_set,
                preview_id=preview_id,
                preview_url=preview_url,
            )
            previews.append(preview)

        # Calculate expiration (24 hours from now)
        expires_at = (datetime.now(UTC) + timedelta(hours=24)).isoformat()

        response = PreviewCreativeResponse(
            previews=previews,
            interactive_url=f"{AGENT_URL}/preview/{preview_id}/interactive",
            expires_at=expires_at,
        )

        return response.model_dump_json(indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def _generate_preview_variant(
    format_obj: Any,
    manifest: Any,
    input_set: Any,
    preview_id: str,
    preview_url: str,
) -> PreviewVariant:
    """Generate a single preview variant - always returns HTML page."""
    from .schemas.manifest import PreviewEmbedding, PreviewHints

    # Build hints based on format type
    hints = PreviewHints()

    if format_obj.type == "video":
        hints.primary_media_type = "video"
        hints.contains_audio = True
        if format_obj.requirements and format_obj.requirements.duration_seconds:
            hints.estimated_duration_seconds = format_obj.requirements.duration_seconds
    elif format_obj.type == "audio":
        hints.primary_media_type = "audio"
        hints.contains_audio = True
        if format_obj.requirements and format_obj.requirements.duration_seconds:
            hints.estimated_duration_seconds = format_obj.requirements.duration_seconds
    elif format_obj.type in ["display", "native", "dooh"]:
        hints.primary_media_type = "image"
        hints.contains_audio = False
    else:
        hints.requires_interaction = True

    # Extract dimensions if available
    if format_obj.dimensions:
        parts = format_obj.dimensions.split("x")
        if len(parts) == 2:
            hints.estimated_dimensions = {"width": int(parts[0]), "height": int(parts[1])}

    # Build embedding security metadata
    embedding = PreviewEmbedding(
        recommended_sandbox="allow-scripts allow-same-origin",
        requires_https=False,
        supports_fullscreen=format_obj.type in ["video", "interactive"],
    )

    return PreviewVariant(
        preview_url=preview_url,
        input=input_set,
        hints=hints,
        embedding=embedding,
    )


@mcp.tool()
def build_creative(
    message: str,
    format_id: str,
    gemini_api_key: str,
    format_source: str | None = None,
    context_id: str | None = None,
    assets: list[dict[str, Any]] | None = None,
    brand_card: dict[str, Any] | None = None,
    promoted_offerings: dict[str, Any] | None = None,
    output_mode: str = "manifest",
    preview_options: dict[str, Any] | None = None,
    finalize: bool = False,
) -> str:
    """Build a creative manifest using AI generation (requires user's Gemini API key).

    Args:
        message: Creative brief or refinement instructions
        format_id: Format identifier to build for (use generative formats like display_300x250_generative)
        gemini_api_key: User's Gemini API key (REQUIRED - we don't store or pay for API calls)
        format_source: Optional sales agent URL for custom format lookup
        context_id: Session ID for iterative refinement
        assets: Optional asset library references
        brand_card: (Deprecated) Brand information - use promoted_offerings instead
        promoted_offerings: Brand and product information for AI generation (replaces brand_card)
        output_mode: "manifest" for static creative or "code" for dynamic
        preview_options: Preview generation options
        finalize: Set to true to finalize the creative

    Returns:
        JSON string with build response containing creative manifest
    """
    try:
        # Validate API key is provided
        if not gemini_api_key:
            return json.dumps(
                {
                    "error": "gemini_api_key is required. Please provide your own Gemini API key. "
                    "Get one at https://ai.google.dev/"
                },
                indent=2,
            )

        # Import schema types
        from pydantic import HttpUrl

        from .schemas.build import AssetReference
        from .schemas.build import PreviewOptions as PreviewOptionsModel

        # Parse assets into AssetReference objects
        asset_refs: list[AssetReference] = []
        if assets:
            asset_refs = [AssetReference(**asset) for asset in assets]

        # Parse format_source into HttpUrl if provided
        format_source_url: HttpUrl | None = None
        if format_source:
            format_source_url = HttpUrl(format_source)

        # Parse preview_options into PreviewOptions object
        preview_opts: PreviewOptionsModel | None = None
        if preview_options:
            preview_opts = PreviewOptionsModel(**preview_options)

        # Validate output_mode
        if output_mode not in ["manifest", "code"]:
            return json.dumps(
                {"error": f"Invalid output_mode '{output_mode}'. Must be 'manifest' or 'code'"},
                indent=2,
            )

        # Parse request
        request = BuildCreativeRequest(
            message=message,
            format_id=format_id,
            format_source=format_source_url,
            context_id=context_id,
            assets=asset_refs,
            output_mode=output_mode,  # type: ignore[arg-type]
            preview_options=preview_opts,
            finalize=finalize,
            gemini_api_key=gemini_api_key,
        )

        # Get format definition
        fmt = get_format_by_id(request.format_id)
        if not fmt:
            return json.dumps(
                {"error": f"Format {request.format_id} not found"},
                indent=2,
            )

        # For generative formats, get the output format for asset requirements
        output_fmt = fmt
        if fmt.type == "generative" and fmt.output_format:
            output_fmt_result = get_format_by_id(fmt.output_format)
            if not output_fmt_result:
                return json.dumps(
                    {"error": f"Output format {fmt.output_format} not found"},
                    indent=2,
                )
            output_fmt = output_fmt_result

        # Initialize Gemini with user's API key using newer google-genai package
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=request.gemini_api_key)

        # Build prompt for creative generation
        # For generative formats, describe what we're generating (the output format)
        target_format = output_fmt if fmt.type == "generative" else fmt

        format_spec = f"""Format: {fmt.name}
Type: {fmt.type}
Description: {fmt.description}
"""

        if fmt.type == "generative":
            format_spec += f"\nThis will generate a: {output_fmt.name}\n"
            if output_fmt.dimensions:
                format_spec += f"Dimensions: {output_fmt.dimensions}\n"

        format_spec += "\nRequired Assets:\n"

        for asset_req in target_format.assets_required:
            format_spec += f"- {asset_req.asset_role} ({asset_req.asset_type})"
            if asset_req.width and asset_req.height:
                format_spec += f" - {asset_req.width}x{asset_req.height}"
            format_spec += f": {asset_req.description or 'N/A'}\n"

        # Add brand context if provided (support both promoted_offerings and deprecated brand_card)
        brand_data = promoted_offerings or brand_card
        brand_context = ""
        if brand_data:
            brand_context = "\n\nBrand Context:\n"

            # Handle promoted_offerings structure
            if "offerings" in brand_data:
                for offering in brand_data["offerings"]:
                    if "name" in offering:
                        brand_context += f"- Product: {offering['name']}\n"
                    if "description" in offering:
                        brand_context += f"  Description: {offering['description']}\n"
                    if "assets" in offering:
                        brand_context += f"  Assets: {len(offering['assets'])} available\n"

            # Handle brand_card structure (backward compatibility)
            if "url" in brand_data:
                brand_context += f"- Brand Website: {brand_data['url']}\n"
            if "colors" in brand_data:
                brand_context += f"- Brand Colors: {', '.join(brand_data['colors'])}\n"
            if "fonts" in brand_data:
                brand_context += f"- Brand Fonts: {', '.join(brand_data['fonts'])}\n"
            if "tone" in brand_data:
                brand_context += f"- Brand Tone: {brand_data['tone']}\n"
            if "assets" in brand_data and len(brand_data["assets"]) > 0:
                brand_context += f"- Available Brand Assets: {len(brand_data['assets'])} assets (logos, images, etc.)\n"

        # Check if we need to generate images (check target format, not input generative format)
        generate_images = target_format.type == "display" and any(
            req.asset_type == "image" for req in target_format.assets_required
        )

        # The format_id in the output manifest should be the OUTPUT format
        output_format_id = output_fmt.format_id if fmt.type == "generative" else request.format_id

        if generate_images:
            prompt = f"""You are a creative generation AI for advertising.

{format_spec}{brand_context}

User Request: {request.message}

IMPORTANT: Generate actual images for the required image assets. Use the brand assets provided as style references.
After generating the images, output ONLY a JSON creative manifest with this structure:

{{
  "format_id": "{output_format_id}",
  "assets": {{
    // Map each required asset_role to appropriate asset data
    // For images: {{"asset_type": "image", "url": "GENERATED_IMAGE_PLACEHOLDER", "width": X, "height": Y, "format": "png"}}
    // For text: {{"asset_type": "text", "content": "..."}}
    // For urls: {{"asset_type": "url", "url": "..."}}
  }},
  "metadata": {{
    "generated_by": "AdCP Creative Agent",
    "timestamp": "{datetime.now(UTC).isoformat()}"
  }}
}}

Generate images first, then return the JSON manifest."""
        else:
            prompt = f"""You are a creative generation AI for advertising. Generate a creative manifest for the following request:

{format_spec}{brand_context}

User Request: {request.message}

Generate a JSON creative manifest with the following structure:
{{
  "format_id": "{output_format_id}",
  "assets": {{
    // Map each required asset_role to appropriate asset data
    // For text: {{"asset_type": "text", "content": "..."}}
    // For urls: {{"asset_type": "url", "url": "..."}}
  }},
  "metadata": {{
    "generated_by": "AdCP Creative Agent",
    "timestamp": "{datetime.now(UTC).isoformat()}"
  }}
}}

Return ONLY the JSON manifest, no additional text."""

        # Prepare contents array with prompt and optional brand asset images
        contents: list[Any] = [prompt]

        # Add brand asset images if provided (from promoted_offerings or brand_card)
        import httpx

        # Collect all image assets from various sources
        image_assets = []

        if brand_data:
            # Get images from promoted_offerings offerings
            if "offerings" in brand_data:
                for offering in brand_data["offerings"]:
                    if "assets" in offering:
                        image_assets.extend(offering["assets"])

            # Get images from brand_card assets (backward compatibility)
            if "assets" in brand_data:
                image_assets.extend(brand_data["assets"])

        # Fetch and add all image assets
        for asset in image_assets:
            if isinstance(asset, dict) and asset.get("asset_type") == "image":
                img_url = asset.get("url")
                if img_url:
                    try:
                        # Fetch image from URL
                        img_response = httpx.get(img_url, timeout=10.0)
                        img_response.raise_for_status()
                        img_bytes = img_response.content

                        # Determine mime type from content-type header or URL
                        mime_type = img_response.headers.get("content-type", "image/png")
                        if not mime_type.startswith("image/"):
                            mime_type = "image/png"

                        # Add image as Part
                        contents.append(types.Part.from_bytes(data=img_bytes, mime_type=mime_type))
                    except Exception as e:
                        # Log error but continue with other images
                        print(f"Warning: Failed to fetch brand asset image {img_url}: {e}")

        if generate_images:
            # Use image generation model
            response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=contents,
            )
        else:
            # Use text-only model
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=contents,
            )

        generated_text = ""
        generated_images = []

        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    generated_text += part.text
                elif part.inline_data is not None and part.inline_data.data is not None:
                    # Save generated image
                    import base64
                    from io import BytesIO

                    from PIL import Image

                    image = Image.open(BytesIO(part.inline_data.data))
                    # Convert to base64 data URI
                    buffered = BytesIO()
                    image.save(buffered, format="PNG")
                    img_data = base64.b64encode(buffered.getvalue()).decode()
                    generated_images.append(f"data:image/png;base64,{img_data}")

        # Extract JSON from response (handle markdown code blocks)
        import re

        json_match = re.search(r"```json\s*(.*?)\s*```", generated_text, re.DOTALL)
        if json_match:
            manifest_json = json_match.group(1)
        else:
            # Try to find JSON directly
            manifest_json = generated_text.strip()

        # Parse the generated manifest
        manifest_data = json.loads(manifest_json)

        # If we generated images, inject them into the manifest
        if generated_images and "assets" in manifest_data:
            image_index = 0
            for _asset_role, asset_data in manifest_data["assets"].items():
                if isinstance(asset_data, dict) and asset_data.get("asset_type") == "image":
                    if image_index < len(generated_images):
                        # Use generated image as data URI
                        asset_data["url"] = generated_images[image_index]
                        image_index += 1

        # Generate session context ID
        session_context_id = request.context_id or str(uuid.uuid4())

        # Determine status - must be one of the literal types
        from typing import Literal

        status: Literal["draft", "ready", "finalized"]
        if request.finalize:
            status = "finalized"
        elif "ready" in request.message.lower():
            status = "ready"
        else:
            status = "draft"

        # Build response
        build_response = BuildCreativeResponse(
            message=f"Generated {fmt.name} creative based on your request. {'Finalized and ready to use.' if request.finalize else 'Review and refine as needed.'}",
            context_id=session_context_id,
            status=status,
            creative_output=CreativeOutput(
                type="creative_manifest",
                format_id=output_format_id,
                data=manifest_data,
            ),
            preview=None,  # Could integrate with preview_creative here
            refinement_suggestions=[
                "Consider A/B testing different headlines",
                "Test various CTA button colors",
                "Try different image crops for mobile vs desktop",
            ]
            if not request.finalize
            else [],
        )

        return build_response.model_dump_json(indent=2)

    except json.JSONDecodeError as e:
        return json.dumps(
            {"error": f"Failed to parse generated creative: {e!s}"},
            indent=2,
        )
    except Exception as e:
        return json.dumps(
            {"error": f"Creative generation failed: {e!s}"},
            indent=2,
        )


if __name__ == "__main__":
    # Check if we're in production (Fly.io)
    if os.getenv("PRODUCTION") == "true":
        port = int(os.getenv("PORT", "8080"))
        mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
    else:
        # Local development uses stdio
        mcp.run()
