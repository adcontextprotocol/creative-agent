"""FastAPI HTTP server for AdCP Creative Agent (Fly.io deployment)."""

import os
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .data.formats import STANDARD_FORMATS, get_format_by_id

app = FastAPI(title="AdCP Creative Agent", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PreviewRequest(BaseModel):
    """Request to generate creative preview."""

    format_id: str
    width: int | None = None
    height: int | None = None
    assets: dict[str, Any]


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint."""
    return {
        "name": "AdCP Creative Agent",
        "version": "1.0.0",
        "endpoints": {
            "formats": "/formats",
            "preview": "/preview (POST)",
        },
    }


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/formats")
async def list_formats() -> list[dict[str, Any]]:
    """List all available creative formats."""
    return [fmt.model_dump() for fmt in STANDARD_FORMATS]


@app.get("/formats/{format_id}")
async def get_format(format_id: str) -> dict[str, Any]:
    """Get a specific format."""
    fmt = get_format_by_id(format_id)
    if not fmt:
        raise HTTPException(status_code=404, detail=f"Format {format_id} not found")
    result: dict[str, Any] = fmt.model_dump()
    return result


@app.post("/preview")
async def preview_creative(request: PreviewRequest) -> dict[str, Any]:
    """Generate preview from creative manifest."""
    # Validate format exists
    fmt = get_format_by_id(request.format_id)
    if not fmt:
        raise HTTPException(status_code=404, detail=f"Format {request.format_id} not found")

    # Generate preview ID
    preview_id = str(uuid.uuid4())

    # Build iframe HTML based on format type
    if fmt.type == "display":
        width = request.width or fmt.width or 300
        height = request.height or fmt.height or 250
        image_url = request.assets.get("image", "")
        click_url = request.assets.get("click_url", "#")

        iframe_html = f"""
<iframe width="{width}" height="{height}" style="border: 1px solid #ccc;">
    <a href="{click_url}" target="_blank">
        <img src="{image_url}" width="{width}" height="{height}" alt="Ad Creative" />
    </a>
</iframe>
""".strip()

    elif fmt.type == "video":
        width = request.width or fmt.width or 640
        height = request.height or fmt.height or 360
        video_url = request.assets.get("video", "")

        iframe_html = f"""
<iframe width="{width}" height="{height}" style="border: 1px solid #ccc;">
    <video width="{width}" height="{height}" controls>
        <source src="{video_url}" type="video/mp4">
    </video>
</iframe>
""".strip()

    else:
        # Generic HTML preview
        iframe_html = f"<div>Preview for {fmt.name} (format_id: {request.format_id})</div>"

    return {
        "preview_id": preview_id,
        "format_id": request.format_id,
        "preview_url": f"https://creative.adcontextprotocol.org/previews/{preview_id}",
        "iframe_html": iframe_html,
        "manifest": request.model_dump(),
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
