"""Build creative schemas for AdCP."""

from typing import Any, Literal

from pydantic import BaseModel, HttpUrl


class AssetReference(BaseModel):
    """Reference to an asset library."""

    library_id: str
    asset_ids: list[str] | None = None
    tags: list[str] | None = None
    filters: dict[str, Any] | None = None


class PreviewContext(BaseModel):
    """Context for preview generation."""

    name: str
    user_data: dict[str, Any]


class PreviewOptions(BaseModel):
    """Preview generation options."""

    contexts: list[PreviewContext] | None = None
    template_id: str | None = None


class BuildCreativeRequest(BaseModel):
    """Request to build a creative (AdCP spec)."""

    message: str  # Creative brief or refinement instructions
    target_format_id: str
    format_source: HttpUrl | None = None
    output_mode: Literal["manifest", "code"] = "manifest"
    context_id: str | None = None  # For iterative refinement
    assets: list[AssetReference] = []
    preview_options: PreviewOptions | None = None
    finalize: bool = False


class CreativeOutput(BaseModel):
    """Creative output (manifest or code)."""

    type: Literal["creative_manifest", "creative_code"]
    format_id: str
    output_format_ids: list[str] | None = None  # For generative formats: the output format IDs produced
    data: dict[str, Any]  # Manifest structure or code


class BuildCreativeResponse(BaseModel):
    """Response from build_creative (AdCP spec)."""

    message: str  # Agent's description
    context_id: str
    status: Literal["draft", "ready", "finalized"]
    creative_output: CreativeOutput
    preview: HttpUrl | None = None
    refinement_suggestions: list[str] = []
