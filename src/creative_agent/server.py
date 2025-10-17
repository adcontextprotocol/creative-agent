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
from .schemas import (
    BuildCreativeRequest,
    BuildCreativeResponse,
    CreativeOutput,
    ListCreativeFormatsResponse,
    PreviewCreativeRequest,
)
from .schemas_generated._schemas_v1_core_format_json import FormatId
from .schemas_generated._schemas_v1_creative_preview_creative_response_json import (
    PreviewCreativeResponse,
)

mcp = FastMCP("adcp-creative-agent")


def normalize_format_id_for_comparison(format_id: FormatId | dict[str, Any] | Any) -> tuple[str, str]:
    """
    Normalize a format_id to (id, agent_url) tuple for comparison.

    Handles FormatId object or dict representations.
    """
    if isinstance(format_id, FormatId):
        return (format_id.id, str(format_id.agent_url))
    if isinstance(format_id, dict):
        # Handle dict from JSON (e.g., from manifest)
        return (format_id.get("id", ""), format_id.get("agent_url", ""))
    return ("", "")


@mcp.tool()
def list_creative_formats(
    format_ids: list[str] | None = None,
    type: str | None = None,
    asset_types: list[str] | None = None,
    dimensions: str | None = None,
    max_width: int | None = None,
    max_height: int | None = None,
    min_width: int | None = None,
    min_height: int | None = None,
    is_responsive: bool | None = None,
    name_search: str | None = None,
) -> str:
    """List all available AdCP creative formats with optional filtering.

    Args:
        format_ids: Return only these specific format IDs
        type: Filter by format type (audio, video, display, dooh, native, interactive)
        asset_types: Filter to formats that include these asset types
        dimensions: (Deprecated) Filter to formats with specific dimensions (e.g., "300x250"). Use min/max filters instead.
        max_width: Maximum width in pixels (inclusive). Returns formats with width <= this value.
        max_height: Maximum height in pixels (inclusive). Returns formats with height <= this value.
        min_width: Minimum width in pixels (inclusive). Returns formats with width >= this value.
        min_height: Minimum height in pixels (inclusive). Returns formats with height >= this value.
        is_responsive: Filter to responsive formats (adapt to container size)
        name_search: Search for formats by name (case-insensitive partial match)

    Returns:
        JSON string with format list response
    """
    try:
        # Convert string format_ids to FormatId objects (assume they're from our agent)
        format_id_objects = None
        if format_ids:
            format_id_objects = [FormatId(agent_url=AGENT_URL, id=fid) for fid in format_ids]

        # Cast asset_types to the expected type (filter_formats accepts str or AssetType)
        formats = filter_formats(
            format_ids=format_id_objects,
            type=type,
            asset_types=asset_types,  # type: ignore[arg-type]  # filter_formats accepts list[str]
            dimensions=dimensions,
            max_width=max_width,
            max_height=max_height,
            min_width=min_width,
            min_height=min_height,
            is_responsive=is_responsive,
            name_search=name_search,
        )

        # Import required types
        from .schemas_generated._schemas_v1_creative_list_creative_formats_response_json import (
            Capability,
            CreativeAgent,
        )
        from .schemas_generated._schemas_v1_creative_list_creative_formats_response_json import (
            Format as ResponseFormat,
        )

        # Convert capability strings to Capability enum
        capabilities_enum = [Capability(cap) for cap in AGENT_CAPABILITIES]

        # Convert core Format objects to response Format objects
        response_formats = [ResponseFormat(**fmt.model_dump(mode="json", exclude_unset=True)) for fmt in formats]

        response = ListCreativeFormatsResponse(
            formats=response_formats,
            creative_agents=[
                CreativeAgent(
                    agent_url=AGENT_URL,
                    agent_name=AGENT_NAME,
                    capabilities=capabilities_enum,
                )
            ],
        )

        return response.model_dump_json(indent=2)
    except ValueError as e:
        return json.dumps({"error": f"Invalid input: {e}"}, indent=2)
    except Exception as e:
        import traceback

        return json.dumps({"error": f"Server error: {e}", "traceback": traceback.format_exc()[-500:]}, indent=2)


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
        from .schemas.manifest import PreviewInput

        # Parse inputs if provided
        inputs_obj: list[PreviewInput] | None = None
        if inputs:
            inputs_obj = [PreviewInput(**inp) for inp in inputs]

        # Parse request (creative_manifest stays as dict)
        # Convert string format_id to FormatId object
        fmt_id = FormatId(agent_url=AGENT_URL, id=format_id)
        request = PreviewCreativeRequest(
            format_id=fmt_id,
            creative_manifest=creative_manifest,
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
        manifest_format_id = request.creative_manifest.get("format_id")
        if manifest_format_id:
            # Normalize both for comparison
            manifest_norm = normalize_format_id_for_comparison(manifest_format_id)
            request_norm = normalize_format_id_for_comparison(request.format_id)
            if manifest_norm != request_norm:
                return json.dumps(
                    {
                        "error": f"Manifest format_id '{manifest_format_id}' does not match request format_id '{request.format_id}'"
                    },
                    indent=2,
                )

        # Validate manifest assets
        from .validation import validate_manifest_assets

        validation_errors = validate_manifest_assets(
            request.creative_manifest,
            check_remote_mime=False,
            format_obj=fmt,
        )
        if validation_errors:
            return json.dumps(
                {
                    "error": "Asset validation failed",
                    "validation_errors": validation_errors,
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
        expires_at = datetime.now(UTC) + timedelta(hours=24)

        from pydantic import AnyUrl, ValidationError

        from .schemas_generated._schemas_v1_creative_preview_creative_response_json import (
            Preview,
        )

        # Validate previews with detailed error reporting
        try:
            validated_previews = []
            for idx, preview_dict in enumerate(previews):
                try:
                    validated_previews.append(Preview.model_validate(preview_dict))
                except ValidationError as e:
                    return json.dumps(
                        {
                            "error": f"Preview validation failed for variant {idx + 1}",
                            "validation_errors": e.errors(),
                        },
                        indent=2,
                    )

            interactive_url = AnyUrl(f"{AGENT_URL}/preview/{preview_id}/interactive")
        except ValidationError as e:
            return json.dumps({"error": f"Invalid URL construction: {e}"}, indent=2)

        response = PreviewCreativeResponse(
            previews=validated_previews,
            interactive_url=interactive_url,
            expires_at=expires_at,
        )

        return response.model_dump_json(indent=2)
    except ValueError as e:
        return json.dumps({"error": f"Invalid input: {e}"}, indent=2)
    except Exception as e:
        import traceback

        return json.dumps(
            {"error": f"Preview generation failed: {e}", "traceback": traceback.format_exc()[-500:]},
            indent=2,
        )


def _generate_preview_variant(
    format_obj: Any,
    manifest: Any,
    input_set: Any,
    preview_id: str,
    preview_url: str,
) -> dict[str, Any]:
    """Generate a single preview variant per ADCP spec.

    Returns a Preview dict with:
    - preview_id (required)
    - renders array (required)
    - input (required)
    """
    from .schemas_generated._schemas_v1_core_format_json import Type
    from .schemas_generated._schemas_v1_creative_preview_creative_response_json import (
        Dimensions,
        Embedding,
        Input,
        Preview,
        Render,
    )

    # Extract dimensions from format
    dimensions = None
    if format_obj.renders and len(format_obj.renders) > 0:
        primary_render = format_obj.renders[0]
        if primary_render.dimensions and primary_render.dimensions.width and primary_render.dimensions.height:
            dimensions = Dimensions(
                width=float(primary_render.dimensions.width),
                height=float(primary_render.dimensions.height),
            )

    # Build embedding metadata
    embedding = Embedding(
        recommended_sandbox="allow-scripts allow-same-origin",
        requires_https=False,
        supports_fullscreen=format_obj.type in [Type.video, Type.rich_media],
    )

    # Create the single render (all formats render as HTML pages)
    from pydantic import AnyUrl as PydanticUrl
    from pydantic import ValidationError

    try:
        render = Render(
            render_id=f"{preview_id}-primary",
            preview_url=PydanticUrl(preview_url),
            role="primary",
            dimensions=dimensions,
            embedding=embedding,
        )
    except ValidationError as e:
        raise ValueError(f"Invalid preview URL '{preview_url}': {e}") from e

    # Create input echo
    input_echo = Input(
        name=input_set.name,
        macros=input_set.macros,
        context_description=input_set.context_description if hasattr(input_set, "context_description") else None,
    )

    # Build Preview per spec
    preview = Preview(
        preview_id=preview_id,
        renders=[render],
        input=input_echo,
    )

    return preview.model_dump(mode="json")


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
        # Validate message length
        if not message or len(message) > 10000:
            return json.dumps(
                {"error": "Message must be between 1 and 10000 characters"},
                indent=2,
            )

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
        # Convert string format_id to FormatId object
        fmt_id = FormatId(agent_url=AGENT_URL, id=request.format_id)
        fmt = get_format_by_id(fmt_id)
        if not fmt:
            return json.dumps(
                {"error": f"Format {request.format_id} not found"},
                indent=2,
            )

        # For generative formats (identified by having output_format_ids),
        # get the output format for asset requirements
        output_fmt = fmt
        if fmt.output_format_ids and len(fmt.output_format_ids) > 0:
            # Use the first output format ID
            output_fmt_result = get_format_by_id(fmt.output_format_ids[0])
            if not output_fmt_result:
                return json.dumps(
                    {"error": f"Output format {fmt.output_format_ids[0]} not found"},
                    indent=2,
                )
            output_fmt = output_fmt_result

        # Initialize Gemini with user's API key using newer google-genai package
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=request.gemini_api_key)

        # Build prompt for creative generation
        # For generative formats, describe what we're generating (the output format)
        is_generative = fmt.output_format_ids and len(fmt.output_format_ids) > 0
        target_format = output_fmt if is_generative else fmt

        format_spec = f"""Format: {fmt.name}
Type: {fmt.type.value}
Description: {fmt.description}
"""

        if is_generative:
            format_spec += f"\nThis will generate a: {output_fmt.name}\n"
            if output_fmt.renders and len(output_fmt.renders) > 0:
                render = output_fmt.renders[0]
                if render.dimensions.width and render.dimensions.height:
                    format_spec += f"Dimensions: {int(render.dimensions.width)}x{int(render.dimensions.height)}\n"

        format_spec += "\nRequired Assets:\n"

        if target_format.assets_required:
            from .schemas_generated._schemas_v1_core_format_json import AssetsRequired1

            for asset_req in target_format.assets_required:
                # Handle both AssetsRequired and AssetsRequired1 (repeatable groups)
                if isinstance(asset_req, AssetsRequired1):
                    # This is a repeatable group (AssetsRequired1)
                    format_spec += f"- {asset_req.asset_group_id} (repeatable group, {asset_req.min_count}-{asset_req.max_count} items)\n"
                    for asset in asset_req.assets:
                        format_spec += f"  - {asset.asset_id} ({asset.asset_type.value})"
                        if asset.requirements:
                            width = asset.requirements.get("width")
                            height = asset.requirements.get("height")
                            if width and height:
                                format_spec += f" - {width}x{height}"
                            desc = asset.requirements.get("description")
                            if desc:
                                format_spec += f": {desc}"
                        format_spec += "\n"
                else:
                    # This is a regular asset (AssetsRequired)
                    format_spec += f"- {asset_req.asset_id} ({asset_req.asset_type.value})"
                    if asset_req.requirements:
                        width = asset_req.requirements.get("width")
                        height = asset_req.requirements.get("height")
                        if width and height:
                            format_spec += f" - {width}x{height}"
                        desc = asset_req.requirements.get("description")
                        if desc:
                            format_spec += f": {desc}"
                    format_spec += "\n"

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

        # Import Type and AssetType enums for comparisons
        from .schemas_generated._schemas_v1_core_format_json import AssetType, Type

        # Check if we need to generate images (check target format, not input generative format)
        generate_images = False
        if target_format.assets_required:
            generate_images = target_format.type == Type.display and any(
                req.asset_type == AssetType.image for req in target_format.assets_required if hasattr(req, "asset_type")
            )

        # The format_id in the output manifest should be the OUTPUT format
        # Extract string ID from FormatId object if needed
        if is_generative:
            output_format_id: str = (
                output_fmt.format_id.id if hasattr(output_fmt.format_id, "id") else str(output_fmt.format_id)
            )
        else:
            output_format_id = request.format_id

        if generate_images:
            prompt = f"""You are a creative generation AI for advertising.

{format_spec}{brand_context}

User Request: {request.message}

IMPORTANT: Generate actual images for the required image assets. Use the brand assets provided as style references.
After generating the images, output ONLY a JSON creative manifest with this structure:

{{
  "format_id": "{output_format_id}",
  "assets": {{
    // Map each required asset_id to appropriate asset data
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
    // Map each required asset_id to appropriate asset data
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
        import ipaddress
        from urllib.parse import urlparse

        import httpx

        def is_safe_url(url: str) -> bool:
            """Validate URL is safe to fetch (no localhost, private IPs, etc.)."""
            try:
                parsed = urlparse(url)
                if parsed.scheme not in ["http", "https"]:
                    return False

                hostname = parsed.hostname
                if not hostname:
                    return False

                # Block localhost
                if hostname.lower() in ["localhost", "127.0.0.1", "::1"]:
                    return False

                # Block private IP ranges
                try:
                    ip = ipaddress.ip_address(hostname)
                    if ip.is_private or ip.is_loopback or ip.is_link_local:
                        return False
                except ValueError:
                    # Hostname is not an IP, that's fine
                    pass

                return True
            except Exception:
                return False

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
                    if not is_safe_url(img_url):
                        print(f"Warning: Blocked potentially unsafe URL: {img_url}")
                        continue
                    try:
                        # Fetch image from URL
                        img_response = httpx.get(img_url, timeout=10.0, follow_redirects=False)
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
            for _asset_id, asset_data in manifest_data["assets"].items():
                if isinstance(asset_data, dict) and asset_data.get("asset_type") == "image":
                    if image_index < len(generated_images):
                        # Use generated image as data URI
                        asset_data["url"] = generated_images[image_index]
                        image_index += 1

        # Validate generated manifest assets
        from .validation import validate_manifest_assets

        validation_errors = validate_manifest_assets(
            manifest_data,
            check_remote_mime=False,
            format_obj=target_format,
        )
        if validation_errors:
            return json.dumps(
                {
                    "error": "AI-generated creative failed validation",
                    "validation_errors": validation_errors,
                    "hint": "The AI generated invalid assets. Please try again with more specific instructions.",
                },
                indent=2,
            )

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

        # Build output_format_ids list for generative formats
        output_format_ids_list = fmt.output_format_ids if is_generative else None

        # Build response
        build_response = BuildCreativeResponse(
            message=f"Generated {fmt.name} creative based on your request. {'Finalized and ready to use.' if request.finalize else 'Review and refine as needed.'}",
            context_id=session_context_id,
            status=status,
            creative_output=CreativeOutput(
                type="creative_manifest",
                format_id=output_format_id,
                output_format_ids=output_format_ids_list,
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
            {
                "error": f"Failed to parse AI-generated creative: {e}",
                "context": {"line": e.lineno, "column": e.colno, "format_id": format_id},
            },
            indent=2,
        )
    except ValueError as e:
        return json.dumps({"error": f"Invalid input: {e}"}, indent=2)
    except Exception as e:
        import traceback

        return json.dumps(
            {
                "error": f"Creative generation failed: {e}",
                "context": {"format_id": format_id, "traceback": traceback.format_exc()[-500:]},
            },
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
