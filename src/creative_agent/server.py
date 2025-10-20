"""AdCP Creative Agent MCP Server - Spec Compliant Implementation."""

import json
import os
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent

from .data.standard_formats import (
    AGENT_CAPABILITIES,
    AGENT_NAME,
    AGENT_URL,
    filter_formats,
    get_format_by_id,
)
from .schemas import (
    ListCreativeFormatsResponse,
    PreviewCreativeRequest,
)
from .schemas_generated._schemas_v1_core_format_json import FormatId
from .schemas_generated._schemas_v1_creative_preview_creative_response_json import (
    PreviewCreativeResponse,
)

mcp = FastMCP("adcp-creative-agent")


def normalize_format_id_for_comparison(format_id: FormatId | dict[str, Any] | str | Any) -> tuple[str, str]:
    """
    Normalize a format_id to (id, agent_url) tuple for comparison.

    Handles FormatId object, dict, or string representations.
    Strings are assumed to be from our agent (AGENT_URL).
    """
    if isinstance(format_id, FormatId):
        return (format_id.id, str(format_id.agent_url))
    if isinstance(format_id, dict):
        # Handle dict from JSON that has explicit id/agent_url
        if "id" in format_id and "agent_url" in format_id:
            return (format_id["id"], format_id["agent_url"])
        # Handle dict that has format_id as direct string value
        if "format_id" in format_id:
            return (format_id["format_id"], str(AGENT_URL))
        # Empty dict or missing keys
        return (format_id.get("id", ""), format_id.get("agent_url", ""))
    if isinstance(format_id, str):
        # Plain string format_id - assume it's from our agent
        return (format_id, str(AGENT_URL))
    return ("", "")


@mcp.tool()
def list_creative_formats(
    format_ids: list[str | dict[str, Any]] | None = None,
    type: str | None = None,
    asset_types: list[str] | None = None,
    dimensions: str | None = None,
    max_width: int | None = None,
    max_height: int | None = None,
    min_width: int | None = None,
    min_height: int | None = None,
    is_responsive: bool | None = None,
    name_search: str | None = None,
) -> ToolResult:
    """List all available AdCP creative formats with optional filtering.

    Args:
        format_ids: Return only these specific format IDs (strings or FormatId objects)
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
        ToolResult with human-readable message and structured ADCP data
    """
    try:
        # Convert format_ids to FormatId objects (handle both strings and dicts)
        format_id_objects = None
        if format_ids:
            format_id_objects = []
            for fid in format_ids:
                if isinstance(fid, str):
                    format_id_objects.append(FormatId(agent_url=AGENT_URL, id=fid))
                else:  # dict
                    format_id_objects.append(FormatId(**fid))

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

        # Return ToolResult with both human message and structured data
        format_count = len(response_formats)
        filter_desc = []
        if type:
            filter_desc.append(f"type={type}")
        if max_width or max_height:
            filter_desc.append(f"dimensions<={max_width or '∞'}x{max_height or '∞'}")

        message = f"Found {format_count} creative format{'s' if format_count != 1 else ''}"
        if filter_desc:
            message += f" matching filters ({', '.join(filter_desc)})"

        return ToolResult(
            content=[TextContent(type="text", text=message)],
            structured_content=response.model_dump(mode="json"),
        )
    except ValueError as e:
        error_response = {"error": f"Invalid input: {e}"}
        return ToolResult(
            content=[TextContent(type="text", text=f"Error: Invalid input - {e}")],
            structured_content=error_response,
        )
    except Exception as e:
        import traceback

        error_response = {"error": f"Server error: {e}", "traceback": traceback.format_exc()[-500:]}
        return ToolResult(
            content=[TextContent(type="text", text=f"Error: Server error - {e}")],
            structured_content=error_response,
        )


@mcp.tool()
def preview_creative(
    format_id: str | dict[str, Any],
    creative_manifest: dict[str, Any],
    inputs: list[dict[str, Any]] | None = None,
    template_id: str | None = None,
) -> ToolResult:
    """Generate preview renderings of a creative manifest.

    Args:
        format_id: Format identifier for rendering (string or FormatId object with agent_url and id)
        creative_manifest: Complete creative manifest with all required assets (including promoted_offerings if required by the format)
        inputs: Array of input sets for generating multiple preview variants
        template_id: Specific template for custom format rendering

    Returns:
        ToolResult with human-readable message and structured preview data
    """
    try:
        # Import schema types
        from .schemas.manifest import PreviewInput

        # Parse inputs if provided
        inputs_obj: list[PreviewInput] | None = None
        if inputs:
            inputs_obj = [PreviewInput(**inp) for inp in inputs]

        # Parse request (creative_manifest stays as dict)
        # Handle format_id as string or FormatId object (dict)
        if isinstance(format_id, str):
            fmt_id = FormatId(agent_url=AGENT_URL, id=format_id)
        else:  # dict
            fmt_id = FormatId(**format_id)
        request = PreviewCreativeRequest(
            format_id=fmt_id,
            creative_manifest=creative_manifest,
            inputs=inputs_obj,
            template_id=template_id,
        )

        # Validate format exists
        fmt = get_format_by_id(request.format_id)
        if not fmt:
            error_msg = f"Format {request.format_id} not found"
            return ToolResult(
                content=[TextContent(type="text", text=f"Error: {error_msg}")],
                structured_content={"error": error_msg},
            )

        # Validate manifest format_id matches
        manifest_format_id = request.creative_manifest.get("format_id")
        if manifest_format_id:
            # Normalize both for comparison
            manifest_norm = normalize_format_id_for_comparison(manifest_format_id)
            request_norm = normalize_format_id_for_comparison(request.format_id)
            if manifest_norm != request_norm:
                error_msg = (
                    f"Manifest format_id (id='{manifest_norm[0]}', agent_url='{manifest_norm[1]}') "
                    f"does not match request format_id (id='{request_norm[0]}', agent_url='{request_norm[1]}')"
                )
                return ToolResult(
                    content=[TextContent(type="text", text=f"Error: {error_msg}")],
                    structured_content={"error": error_msg},
                )

        # Validate manifest assets
        from .validation import validate_manifest_assets

        validation_errors = validate_manifest_assets(
            request.creative_manifest,
            check_remote_mime=False,
            format_obj=fmt,
        )
        if validation_errors:
            error_msg = "Asset validation failed"
            return ToolResult(
                content=[TextContent(type="text", text=f"Error: {error_msg}")],
                structured_content={"error": error_msg, "validation_errors": validation_errors},
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
                    error_msg = f"Preview validation failed for variant {idx + 1}"
                    return ToolResult(
                        content=[TextContent(type="text", text=f"Error: {error_msg}")],
                        structured_content={"error": error_msg, "validation_errors": e.errors()},
                    )

            interactive_url = AnyUrl(f"{AGENT_URL}/preview/{preview_id}/interactive")
        except ValidationError as e:
            error_msg = f"Invalid URL construction: {e}"
            return ToolResult(
                content=[TextContent(type="text", text=f"Error: {error_msg}")],
                structured_content={"error": error_msg},
            )

        response = PreviewCreativeResponse(
            previews=validated_previews,
            interactive_url=interactive_url,
            expires_at=expires_at,
        )

        # Return ToolResult with human message and structured data
        preview_count = len(validated_previews)
        format_id_str = fmt_id.id if hasattr(fmt_id, "id") else str(fmt_id)
        message = f"Generated {preview_count} preview{'s' if preview_count != 1 else ''} for {format_id_str}"

        return ToolResult(
            content=[TextContent(type="text", text=message)],
            structured_content=response.model_dump(mode="json"),
        )
    except ValueError as e:
        error_msg = f"Invalid input: {e}"
        return ToolResult(
            content=[TextContent(type="text", text=f"Error: {error_msg}")],
            structured_content={"error": error_msg},
        )
    except Exception as e:
        import traceback

        error_msg = f"Preview generation failed: {e}"
        return ToolResult(
            content=[TextContent(type="text", text=f"Error: {error_msg}")],
            structured_content={"error": error_msg, "traceback": traceback.format_exc()[-500:]},
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
    target_format_id: str | dict[str, Any],
    creative_manifest: dict[str, Any] | None = None,
    message: str | None = None,
) -> ToolResult:
    """Transform or generate a creative manifest using AI.

    Args:
        target_format_id: Format ID to generate (string or FormatId object with agent_url and id)
        creative_manifest: Source creative manifest with input assets (e.g., promoted_offerings for generative formats)
        message: Natural language instructions for transformation or generation

    Returns:
        ToolResult with creative_manifest in structured_content

    Note:
        Requires GEMINI_API_KEY environment variable to be set for generative formats.
    """
    try:
        # Parse target_format_id
        if isinstance(target_format_id, str):
            fmt_id = FormatId(agent_url=AGENT_URL, id=target_format_id)
        else:
            fmt_id = FormatId(**target_format_id)

        # Get format definition
        fmt = get_format_by_id(fmt_id)
        if not fmt:
            error_msg = f"Format {fmt_id} not found"
            return ToolResult(
                content=[TextContent(type="text", text=f"Error: {error_msg}")],
                structured_content={"error": error_msg},
            )

        # Initialize manifest if not provided
        if creative_manifest is None:
            creative_manifest = {"format_id": {"agent_url": str(AGENT_URL), "id": fmt_id.id}}

        # Ensure format_id is set in manifest
        if "format_id" not in creative_manifest:
            creative_manifest["format_id"] = {"agent_url": str(AGENT_URL), "id": fmt_id.id}

        # For generative formats, we need to generate the output creative
        is_generative = fmt.output_format_ids and len(fmt.output_format_ids) > 0

        if is_generative:
            # Get output format
            output_format_ids = fmt.output_format_ids
            if not output_format_ids:  # for mypy
                error_msg = "Format has no output_format_ids"
                return ToolResult(
                    content=[TextContent(type="text", text=f"Error: {error_msg}")],
                    structured_content={"error": error_msg},
                )
            output_fmt = get_format_by_id(output_format_ids[0])
            if not output_fmt:
                error_msg = f"Output format {output_format_ids[0]} not found"
                return ToolResult(
                    content=[TextContent(type="text", text=f"Error: {error_msg}")],
                    structured_content={"error": error_msg},
                )

            # Get Gemini API key from environment
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if not gemini_api_key:
                error_msg = "GEMINI_API_KEY environment variable is required for generative formats. Get a key at https://ai.google.dev/"
                return ToolResult(
                    content=[TextContent(type="text", text=f"Error: {error_msg}")],
                    structured_content={"error": error_msg},
                )

            # Extract input assets from manifest
            input_assets = creative_manifest.get("assets", {})

            # Extract promoted_offerings if present
            promoted_offerings = input_assets.get("promoted_offerings")
            generation_prompt_asset = input_assets.get("generation_prompt")

            # Build generation prompt
            if not message and generation_prompt_asset:
                message = generation_prompt_asset.get("content", "")

            if not message:
                error_msg = "message or generation_prompt asset is required for creative generation"
                return ToolResult(
                    content=[TextContent(type="text", text=f"Error: {error_msg}")],
                    structured_content={"error": error_msg},
                )

            # Generate creative using Gemini
            from google import genai

            client = genai.Client(api_key=gemini_api_key)

            # Build prompt
            format_spec = f"""Format: {output_fmt.name}
Type: {output_fmt.type.value}
Description: {output_fmt.description}
"""

            if output_fmt.renders and len(output_fmt.renders) > 0:
                render = output_fmt.renders[0]
                if render.dimensions.width and render.dimensions.height:
                    format_spec += f"Dimensions: {int(render.dimensions.width)}x{int(render.dimensions.height)}\n"

            format_spec += "\nRequired Assets:\n"
            if output_fmt.assets_required:
                from .schemas_generated._schemas_v1_core_format_json import AssetsRequired1

                for asset_req in output_fmt.assets_required:
                    if isinstance(asset_req, AssetsRequired1):
                        # Repeatable group
                        format_spec += f"- {asset_req.asset_group_id} (repeatable group)\n"
                    else:
                        # Regular asset
                        format_spec += f"- {asset_req.asset_id} ({asset_req.asset_type.value})\n"

            # Add brand context if provided
            brand_context = ""
            if promoted_offerings:
                brand_context = "\n\nBrand Context:\n"
                brand_manifest = promoted_offerings.get("brand_manifest", {})
                if "name" in brand_manifest:
                    brand_context += f"Brand: {brand_manifest['name']}\n"
                if "description" in brand_manifest:
                    brand_context += f"Description: {brand_manifest['description']}\n"
                if "tagline" in brand_manifest:
                    brand_context += f"Tagline: {brand_manifest['tagline']}\n"

            prompt = f"""You are a creative generation AI for advertising. Generate a creative manifest for the following request:

{format_spec}{brand_context}

User Request: {message}

Generate a JSON creative manifest with the following structure:
{{
  "format_id": "{output_fmt.format_id.id if hasattr(output_fmt.format_id, "id") else str(output_fmt.format_id)}",
  "assets": {{
    // Map each required asset_id to appropriate asset data
    // For text: {{"content": "..."}}
    // For urls: {{"url": "..."}}
  }}
}}

Return ONLY the JSON manifest, no additional text."""

            # Call Gemini
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt,
            )

            generated_text = ""
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.text:
                        generated_text += part.text

            # Extract JSON from response
            import re

            json_match = re.search(r"```json\s*(.*?)\s*```", generated_text, re.DOTALL)
            if json_match:
                manifest_json = json_match.group(1)
            else:
                manifest_json = generated_text.strip()

            # Parse generated manifest
            output_manifest = json.loads(manifest_json)

            # Validate against output format
            from .validation import validate_manifest_assets

            validation_errors = validate_manifest_assets(
                output_manifest,
                check_remote_mime=False,
                format_obj=output_fmt,
            )
            if validation_errors:
                error_msg = "AI-generated creative failed validation"
                return ToolResult(
                    content=[TextContent(type="text", text=f"Error: {error_msg}")],
                    structured_content={
                        "error": error_msg,
                        "validation_errors": validation_errors,
                    },
                )

            # Return the generated manifest
            return ToolResult(
                content=[TextContent(type="text", text=f"Generated {output_fmt.name} creative")],
                structured_content={"creative_manifest": output_manifest},
            )
        # Non-generative: return manifest as-is (or with minimal transformation)
        return ToolResult(
            content=[TextContent(type="text", text=f"Creative manifest for {fmt.name}")],
            structured_content={"creative_manifest": creative_manifest},
        )

    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse AI-generated creative: {e}"
        return ToolResult(
            content=[TextContent(type="text", text=f"Error: {error_msg}")],
            structured_content={"error": error_msg},
        )
    except ValueError as e:
        error_msg = f"Invalid input: {e}"
        return ToolResult(
            content=[TextContent(type="text", text=f"Error: {error_msg}")],
            structured_content={"error": error_msg},
        )
    except Exception as e:
        import traceback

        error_msg = f"Creative generation failed: {e}"
        return ToolResult(
            content=[TextContent(type="text", text=f"Error: {error_msg}")],
            structured_content={
                "error": error_msg,
                "traceback": traceback.format_exc()[-500:],
            },
        )


if __name__ == "__main__":
    # Check if we're in production (Fly.io)
    if os.getenv("PRODUCTION") == "true":
        port = int(os.getenv("PORT", "8080"))
        mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
    else:
        # Local development uses stdio
        mcp.run()
