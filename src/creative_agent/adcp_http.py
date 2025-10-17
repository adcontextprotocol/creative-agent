"""ADCP-native HTTP endpoints (unwrapped, not MCP protocol).

These endpoints provide direct ADCP responses for clients that don't use MCP.
The MCP endpoint remains available at /mcp for MCP clients.
"""

from typing import Any, cast

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .server import build_creative as build_creative_fn
from .server import list_creative_formats as list_creative_formats_fn
from .server import preview_creative as preview_creative_fn

app = FastAPI(
    title="AdCP Creative Agent",
    description="ADCP-compliant HTTP endpoints for creative format management",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ListCreativeFormatsRequest(BaseModel):
    """Request to list creative formats."""

    format_ids: list[str] | None = None
    type: str | None = None
    asset_types: list[str] | None = None
    dimensions: str | None = None
    max_width: int | None = None
    max_height: int | None = None
    min_width: int | None = None
    min_height: int | None = None
    is_responsive: bool | None = None
    name_search: str | None = None


class PreviewCreativeRequest(BaseModel):
    """Request to preview a creative."""

    format_id: str
    creative_manifest: dict[str, Any]
    inputs: list[dict[str, Any]] | None = None
    template_id: str | None = None
    brand_card: dict[str, Any] | None = None
    promoted_products: dict[str, Any] | None = None
    asset_filters: dict[str, Any] | None = None


class BuildCreativeRequest(BaseModel):
    """Request to build a creative."""

    message: str
    format_id: str
    gemini_api_key: str
    format_source: str | None = None
    context_id: str | None = None
    assets: list[dict[str, Any]] | None = None
    brand_card: dict[str, Any] | None = None
    promoted_offerings: dict[str, Any] | None = None
    output_mode: str = "manifest"
    preview_options: dict[str, Any] | None = None
    finalize: bool = False


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint with API information."""
    return {
        "name": "AdCP Creative Agent",
        "version": "1.0.0",
        "protocol": "adcp",
        "endpoints": {
            "list_formats": "/list-creative-formats (GET or POST)",
            "preview": "/preview-creative (POST)",
            "build": "/build-creative (POST)",
            "health": "/health (GET)",
        },
        "mcp_endpoint": "/mcp (for MCP protocol clients)",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/list-creative-formats")
async def list_creative_formats_get(
    format_ids: str | None = None,
    type: str | None = None,
    asset_types: str | None = None,
    dimensions: str | None = None,
    max_width: int | None = None,
    max_height: int | None = None,
    min_width: int | None = None,
    min_height: int | None = None,
    is_responsive: bool | None = None,
    name_search: str | None = None,
) -> dict[str, Any]:
    """List creative formats (GET with query params)."""
    format_ids_list = format_ids.split(",") if format_ids else None
    asset_types_list = asset_types.split(",") if asset_types else None

    result = list_creative_formats_fn.fn(
        format_ids=format_ids_list,
        type=type,
        asset_types=asset_types_list,
        dimensions=dimensions,
        max_width=max_width,
        max_height=max_height,
        min_width=min_width,
        min_height=min_height,
        is_responsive=is_responsive,
        name_search=name_search,
    )

    return cast("dict[str, Any]", result.structured_content)


@app.post("/list-creative-formats")
async def list_creative_formats_post(request: ListCreativeFormatsRequest) -> dict[str, Any]:
    """List creative formats (POST with JSON body)."""
    result = list_creative_formats_fn.fn(
        format_ids=request.format_ids,
        type=request.type,
        asset_types=request.asset_types,
        dimensions=request.dimensions,
        max_width=request.max_width,
        max_height=request.max_height,
        min_width=request.min_width,
        min_height=request.min_height,
        is_responsive=request.is_responsive,
        name_search=request.name_search,
    )

    return cast("dict[str, Any]", result.structured_content)


@app.post("/preview-creative")
async def preview_creative(request: PreviewCreativeRequest) -> dict[str, Any]:
    """Generate creative preview."""
    result = preview_creative_fn.fn(
        format_id=request.format_id,
        creative_manifest=request.creative_manifest,
        inputs=request.inputs,
        template_id=request.template_id,
        brand_card=request.brand_card,
        promoted_products=request.promoted_products,
        asset_filters=request.asset_filters,
    )

    structured = cast("dict[str, Any]", result.structured_content)

    # Check if this is an error response
    if "error" in structured:
        raise HTTPException(status_code=400, detail=structured)

    return structured


@app.post("/build-creative")
async def build_creative(request: BuildCreativeRequest) -> dict[str, Any]:
    """Build a creative using AI."""
    result = build_creative_fn.fn(
        message=request.message,
        format_id=request.format_id,
        gemini_api_key=request.gemini_api_key,
        format_source=request.format_source,
        context_id=request.context_id,
        assets=request.assets,
        brand_card=request.brand_card,
        promoted_offerings=request.promoted_offerings,
        output_mode=request.output_mode,
        preview_options=request.preview_options,
        finalize=request.finalize,
    )

    structured = cast("dict[str, Any]", result.structured_content)

    # Check if this is an error response
    if "error" in structured:
        raise HTTPException(status_code=400, detail=structured)

    return structured
