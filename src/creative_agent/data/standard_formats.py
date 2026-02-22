"""Standard AdCP creative formats."""

# mypy: disable-error-code="call-arg"
# Pydantic models with extra='forbid' trigger false positives when optional fields aren't passed

import typing
from typing import Any

from adcp import CatalogRequirements, CatalogType, FormatCategory, FormatId, get_required_assets
from adcp.types.generated_poc.core.format import Format as _LibFormat
from adcp.types.generated_poc.core.format import Renders as LibRender
from adcp.types.generated_poc.enums.format_id_parameter import FormatIdParameter
from pydantic import AnyUrl

from ..schemas import CreativeFormat
from .format_types import (
    AssetType,
)

# Build asset type -> class mappings dynamically from the Format model's discriminated union.
# This avoids hardcoding numbered class names (Assets, Assets5, etc.) which change between
# adcp library versions.
_list_type = typing.get_args(typing.get_args(_LibFormat.model_fields["assets"].annotation)[0])
_union_members = typing.get_args(_list_type[0]) if _list_type else ()

_INDIVIDUAL_ASSET_MAP: dict[str, type] = {}
_REPEATABLE_GROUP_CLASS: type | None = None
_INNER_ASSET_MAP: dict[str, type] = {}

for _cls in _union_members:
    if not hasattr(_cls, "model_fields"):
        continue
    if "asset_group_id" in _cls.model_fields:
        _REPEATABLE_GROUP_CLASS = _cls
        # Build inner asset mapping from the group's assets field
        _inner_ann = _cls.model_fields["assets"].annotation
        _inner_args = typing.get_args(_inner_ann)
        _inner_union = typing.get_args(_inner_args[0]) if _inner_args else ()
        for _inner_cls in _inner_union:
            if hasattr(_inner_cls, "model_fields") and "asset_type" in _inner_cls.model_fields:
                _lit = typing.get_args(_inner_cls.model_fields["asset_type"].annotation)
                if _lit:
                    _INNER_ASSET_MAP[_lit[0]] = _inner_cls
        continue
    at_field = _cls.model_fields.get("asset_type")
    if at_field:
        _lit = typing.get_args(at_field.annotation)
        if _lit:
            _INDIVIDUAL_ASSET_MAP[_lit[0]] = _cls

# Fail fast if the introspection didn't find expected types
if not _INDIVIDUAL_ASSET_MAP:
    raise ImportError("No individual asset classes found in adcp Format schema")
if _REPEATABLE_GROUP_CLASS is None:
    raise ImportError("No repeatable group class found in adcp Format schema")

# Agent configuration
AGENT_URL = "https://creative.adcontextprotocol.org"
AGENT_NAME = "AdCP Standard Creative Agent"
AGENT_CAPABILITIES = ["validation", "assembly", "generation", "preview"]

# Common macros supported across all formats
COMMON_MACROS: list[str | Any] = [
    "MEDIA_BUY_ID",
    "CREATIVE_ID",
    "CACHEBUSTER",
    "CLICK_URL",
    "DEVICE_TYPE",
    "GDPR",
    "GDPR_CONSENT",
    "US_PRIVACY",
    "GPP_STRING",
]


def create_format_id(format_name: str) -> FormatId:
    """Create a FormatId object with agent URL and format name."""
    return FormatId(agent_url=AnyUrl(AGENT_URL), id=format_name)


def create_asset(
    asset_id: str,
    asset_type: AssetType,
    required: bool = True,
    requirements: Any = None,
) -> Any:
    """Create an individual asset using the correct typed model for the given asset_type.

    The adcp library uses a discriminated union for assets — each asset_type has its own
    Pydantic model with type-specific requirements. This function resolves the correct
    class dynamically from the Format schema.
    """
    cls = _INDIVIDUAL_ASSET_MAP.get(asset_type.value)
    if cls is None:
        raise ValueError(f"Unknown asset type: {asset_type.value}")

    return cls(
        asset_id=asset_id,
        asset_type=asset_type.value,
        required=required,
        requirements=requirements,
        item_type="individual",
    )


def create_repeatable_group(
    asset_group_id: str,
    asset_type: AssetType,
    required: bool,
    min_count: int,
    max_count: int,
    requirements: Any = None,
) -> Any:
    """Create a repeatable group asset that allows multiple values of the same type.

    Used for asset pools like headlines (up to 15) or images (up to 20), where
    publishers pick the best combination for each placement.

    Each group instance contains a single inner asset whose asset_id matches the
    content type string (e.g. "text", "image", "video").
    """
    if _REPEATABLE_GROUP_CLASS is None:
        raise RuntimeError("Repeatable group class not found in adcp format schema")

    inner_cls = _INNER_ASSET_MAP.get(asset_type.value)
    if inner_cls is None:
        raise ValueError(f"Unknown inner asset type: {asset_type.value}")

    inner = inner_cls(
        asset_id=asset_type.value,
        asset_type=asset_type.value,
        required=True,
        requirements=requirements,
    )
    return _REPEATABLE_GROUP_CLASS(
        asset_group_id=asset_group_id,
        assets=[inner],
        item_type="repeatable_group",
        min_count=min_count,
        max_count=max_count,
        required=required,
    )


def create_impression_tracker_asset() -> Any:
    """Create an optional impression tracker asset for 3rd party tracking.

    This creates a URL asset with url_type='tracker_pixel' that can be used
    for third-party impression tracking pixels.
    """
    return create_asset(
        asset_id="impression_tracker",
        asset_type=AssetType.url,
        required=False,
        requirements={
            "url_type": "tracker_pixel",
            "description": "3rd party impression tracking pixel URL",
        },
    )


def create_click_url_asset() -> Any:
    """Create a required clickthrough URL asset.

    This creates a URL asset with url_type='clickthrough' for the landing page
    destination when users click on the ad.
    """
    return create_asset(
        asset_id="click_url",
        asset_type=AssetType.url,
        required=True,
        requirements={
            "url_type": "clickthrough",
            "description": "Clickthrough destination URL",
        },
    )


def create_fixed_render(width: int, height: int, role: str = "primary") -> LibRender:
    """Create a render with fixed dimensions (non-responsive).

    Returns the library's Pydantic model which automatically handles
    exclude_none serialization.
    """
    from adcp.types.generated_poc.core.format import Dimensions as LibDimensions
    from adcp.types.generated_poc.core.format import Responsive

    return LibRender(
        role=role,
        dimensions=LibDimensions(
            width=width,
            height=height,
            responsive=Responsive(width=False, height=False),
        ),
    )


def create_responsive_render(
    role: str = "primary",
    min_width: int | None = None,
    max_width: int | None = None,
    min_height: int | None = None,
    max_height: int | None = None,
) -> LibRender:
    """Create a render with responsive dimensions.

    Returns the library's Pydantic model which automatically handles
    exclude_none serialization.
    """
    from adcp.types.generated_poc.core.format import Dimensions as LibDimensions
    from adcp.types.generated_poc.core.format import Responsive

    return LibRender(
        role=role,
        dimensions=LibDimensions(
            min_width=min_width,
            max_width=max_width,
            min_height=min_height,
            max_height=max_height,
            responsive=Responsive(width=True, height=True),
        ),
    )


# Generative Formats - AI-powered creative generation
# Generative formats use catalog_requirements to declare what offering data they need.
# The AI generates creative from the catalog context + a generation prompt.
# Template format accepts dimension parameters; concrete formats are for backward compatibility.
GENERATIVE_FORMATS = [
    # Template format - supports any dimensions
    CreativeFormat(
        format_id=create_format_id("display_generative"),
        name="Display Banner - AI Generated",
        type=FormatCategory.display,
        description="AI-generated display banner from brand context and prompt (supports any dimensions)",
        accepts_parameters=[FormatIdParameter.dimensions],
        supported_macros=COMMON_MACROS,
        catalog_requirements=[
            CatalogRequirements(
                catalog_type=CatalogType.offering,
                required_fields=["name"],
            ),
        ],
        assets=[
            create_asset(
                asset_id="generation_prompt",
                asset_type=AssetType.text,
                required=True,
                requirements={"description": "Text prompt describing the desired creative"},
            ),
            create_impression_tracker_asset(),
        ],
    ),
    # Concrete formats for backward compatibility
    CreativeFormat(
        format_id=create_format_id("display_300x250_generative"),
        name="Medium Rectangle - AI Generated",
        type=FormatCategory.display,
        description="AI-generated 300x250 banner from brand context and prompt",
        renders=[create_fixed_render(300, 250)],
        output_format_ids=[create_format_id("display_300x250_image")],
        supported_macros=COMMON_MACROS,
        catalog_requirements=[
            CatalogRequirements(
                catalog_type=CatalogType.offering,
                required_fields=["name"],
            ),
        ],
        assets=[
            create_asset(
                asset_id="generation_prompt",
                asset_type=AssetType.text,
                required=True,
                requirements={"description": "Text prompt describing the desired creative"},
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("display_728x90_generative"),
        name="Leaderboard - AI Generated",
        type=FormatCategory.display,
        description="AI-generated 728x90 banner from brand context and prompt",
        renders=[create_fixed_render(728, 90)],
        output_format_ids=[create_format_id("display_728x90_image")],
        supported_macros=COMMON_MACROS,
        catalog_requirements=[
            CatalogRequirements(
                catalog_type=CatalogType.offering,
                required_fields=["name"],
            ),
        ],
        assets=[
            create_asset(
                asset_id="generation_prompt",
                asset_type=AssetType.text,
                required=True,
                requirements={"description": "Text prompt describing the desired creative"},
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("display_320x50_generative"),
        name="Mobile Banner - AI Generated",
        type=FormatCategory.display,
        description="AI-generated 320x50 mobile banner from brand context and prompt",
        renders=[create_fixed_render(320, 50)],
        output_format_ids=[create_format_id("display_320x50_image")],
        supported_macros=COMMON_MACROS,
        catalog_requirements=[
            CatalogRequirements(
                catalog_type=CatalogType.offering,
                required_fields=["name"],
            ),
        ],
        assets=[
            create_asset(
                asset_id="generation_prompt",
                asset_type=AssetType.text,
                required=True,
                requirements={"description": "Text prompt describing the desired creative"},
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("display_160x600_generative"),
        name="Wide Skyscraper - AI Generated",
        type=FormatCategory.display,
        description="AI-generated 160x600 wide skyscraper from brand context and prompt",
        renders=[create_fixed_render(160, 600)],
        output_format_ids=[create_format_id("display_160x600_image")],
        supported_macros=COMMON_MACROS,
        catalog_requirements=[
            CatalogRequirements(
                catalog_type=CatalogType.offering,
                required_fields=["name"],
            ),
        ],
        assets=[
            create_asset(
                asset_id="generation_prompt",
                asset_type=AssetType.text,
                required=True,
                requirements={"description": "Text prompt describing the desired creative"},
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("display_336x280_generative"),
        name="Large Rectangle - AI Generated",
        type=FormatCategory.display,
        description="AI-generated 336x280 large rectangle from brand context and prompt",
        renders=[create_fixed_render(336, 280)],
        output_format_ids=[create_format_id("display_336x280_image")],
        supported_macros=COMMON_MACROS,
        catalog_requirements=[
            CatalogRequirements(
                catalog_type=CatalogType.offering,
                required_fields=["name"],
            ),
        ],
        assets=[
            create_asset(
                asset_id="generation_prompt",
                asset_type=AssetType.text,
                required=True,
                requirements={"description": "Text prompt describing the desired creative"},
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("display_300x600_generative"),
        name="Half Page - AI Generated",
        type=FormatCategory.display,
        description="AI-generated 300x600 half page from brand context and prompt",
        renders=[create_fixed_render(300, 600)],
        output_format_ids=[create_format_id("display_300x600_image")],
        supported_macros=COMMON_MACROS,
        catalog_requirements=[
            CatalogRequirements(
                catalog_type=CatalogType.offering,
                required_fields=["name"],
            ),
        ],
        assets=[
            create_asset(
                asset_id="generation_prompt",
                asset_type=AssetType.text,
                required=True,
                requirements={"description": "Text prompt describing the desired creative"},
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("display_970x250_generative"),
        name="Billboard - AI Generated",
        type=FormatCategory.display,
        description="AI-generated 970x250 billboard from brand context and prompt",
        renders=[create_fixed_render(970, 250)],
        output_format_ids=[create_format_id("display_970x250_image")],
        supported_macros=COMMON_MACROS,
        catalog_requirements=[
            CatalogRequirements(
                catalog_type=CatalogType.offering,
                required_fields=["name"],
            ),
        ],
        assets=[
            create_asset(
                asset_id="generation_prompt",
                asset_type=AssetType.text,
                required=True,
                requirements={"description": "Text prompt describing the desired creative"},
            ),
            create_impression_tracker_asset(),
        ],
    ),
]

# Video Formats
# Template formats (for new integrations) + concrete formats (for backward compatibility)
VIDEO_FORMATS = [
    # Template format - supports any duration
    CreativeFormat(
        format_id=create_format_id("video_standard"),
        name="Standard Video",
        type=FormatCategory.video,
        description="Video ad in standard aspect ratios (supports any duration)",
        accepts_parameters=[FormatIdParameter.duration],
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        assets=[
            create_asset(
                asset_id="video_file",
                asset_type=AssetType.video,
                required=True,
                requirements={
                    "acceptable_formats": ["mp4", "mov", "webm"],
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    # Template format - supports any dimensions
    CreativeFormat(
        format_id=create_format_id("video_dimensions"),
        name="Video with Dimensions",
        type=FormatCategory.video,
        description="Video ad with specific dimensions (supports any size)",
        accepts_parameters=[FormatIdParameter.dimensions],
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        assets=[
            create_asset(
                asset_id="video_file",
                asset_type=AssetType.video,
                required=True,
                requirements={
                    "acceptable_formats": ["mp4", "mov", "webm"],
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    # Template format - VAST tag with any duration
    CreativeFormat(
        format_id=create_format_id("video_vast"),
        name="VAST Video",
        type=FormatCategory.video,
        description="Video ad via VAST tag (supports any duration)",
        accepts_parameters=[FormatIdParameter.duration],
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        assets=[
            create_asset(
                asset_id="vast_tag",
                asset_type=AssetType.vast,
                required=True,
            ),
        ],
    ),
    # Concrete formats for backward compatibility
    CreativeFormat(
        format_id=create_format_id("video_standard_30s"),
        name="Standard Video - 30 seconds",
        type=FormatCategory.video,
        description="30-second video ad in standard aspect ratios",
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        assets=[
            create_asset(
                asset_id="video_file",
                asset_type=AssetType.video,
                required=True,
                requirements={
                    "duration_seconds": 30,
                    "acceptable_formats": ["mp4", "mov", "webm"],
                    "description": "30-second video file",
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("video_standard_15s"),
        name="Standard Video - 15 seconds",
        type=FormatCategory.video,
        description="15-second video ad in standard aspect ratios",
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        assets=[
            create_asset(
                asset_id="video_file",
                asset_type=AssetType.video,
                required=True,
                requirements={
                    "duration_seconds": 15,
                    "acceptable_formats": ["mp4", "mov", "webm"],
                    "description": "15-second video file",
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("video_vast_30s"),
        name="VAST Video - 30 seconds",
        type=FormatCategory.video,
        description="30-second video ad via VAST tag",
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        assets=[
            create_asset(
                asset_id="vast_tag",
                asset_type=AssetType.vast,
                required=True,
                requirements={
                    "description": "VAST 4.x compatible tag",
                },
            ),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("video_1920x1080"),
        name="Full HD Video - 1920x1080",
        type=FormatCategory.video,
        description="1920x1080 Full HD video (16:9)",
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        renders=[create_fixed_render(1920, 1080)],
        assets=[
            create_asset(
                asset_id="video_file",
                asset_type=AssetType.video,
                required=True,
                requirements={
                    "width": 1920,
                    "height": 1080,
                    "acceptable_formats": ["mp4", "mov", "webm"],
                    "description": "1920x1080 video file",
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("video_1280x720"),
        name="HD Video - 1280x720",
        type=FormatCategory.video,
        description="1280x720 HD video (16:9)",
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        renders=[create_fixed_render(1280, 720)],
        assets=[
            create_asset(
                asset_id="video_file",
                asset_type=AssetType.video,
                required=True,
                requirements={
                    "width": 1280,
                    "height": 720,
                    "acceptable_formats": ["mp4", "mov", "webm"],
                    "description": "1280x720 video file",
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("video_1080x1920"),
        name="Vertical Video - 1080x1920",
        type=FormatCategory.video,
        description="1080x1920 vertical video (9:16) for mobile stories",
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        renders=[create_fixed_render(1080, 1920)],
        assets=[
            create_asset(
                asset_id="video_file",
                asset_type=AssetType.video,
                required=True,
                requirements={
                    "width": 1080,
                    "height": 1920,
                    "acceptable_formats": ["mp4", "mov", "webm"],
                    "description": "1080x1920 vertical video file",
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("video_1080x1080"),
        name="Square Video - 1080x1080",
        type=FormatCategory.video,
        description="1080x1080 square video (1:1) for social feeds",
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        renders=[create_fixed_render(1080, 1080)],
        assets=[
            create_asset(
                asset_id="video_file",
                asset_type=AssetType.video,
                required=True,
                requirements={
                    "width": 1080,
                    "height": 1080,
                    "acceptable_formats": ["mp4", "mov", "webm"],
                    "description": "1080x1080 square video file",
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("video_ctv_preroll_30s"),
        name="CTV Pre-Roll - 30 seconds",
        type=FormatCategory.video,
        description="30-second pre-roll ad for Connected TV and streaming platforms",
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE", "PLAYER_SIZE"],
        assets=[
            create_asset(
                asset_id="video_file",
                asset_type=AssetType.video,
                required=True,
                requirements={
                    "duration_seconds": 30,
                    "acceptable_formats": ["mp4", "mov"],
                    "description": "30-second CTV-optimized video file (1920x1080 recommended)",
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("video_ctv_midroll_30s"),
        name="CTV Mid-Roll - 30 seconds",
        type=FormatCategory.video,
        description="30-second mid-roll ad for Connected TV and streaming platforms",
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE", "PLAYER_SIZE"],
        assets=[
            create_asset(
                asset_id="video_file",
                asset_type=AssetType.video,
                required=True,
                requirements={
                    "duration_seconds": 30,
                    "acceptable_formats": ["mp4", "mov"],
                    "description": "30-second CTV-optimized video file (1920x1080 recommended)",
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
]

# Display Formats - Image-based
# Template format (for new integrations) + concrete formats (for backward compatibility)
DISPLAY_IMAGE_FORMATS = [
    # Template format - supports any dimensions
    CreativeFormat(
        format_id=create_format_id("display_image"),
        name="Display Banner - Image",
        type=FormatCategory.display,
        description="Static image banner (supports any dimensions)",
        accepts_parameters=[FormatIdParameter.dimensions],
        supported_macros=COMMON_MACROS,
        assets=[
            create_asset(
                asset_id="banner_image",
                asset_type=AssetType.image,
                required=True,
                requirements={
                    "acceptable_formats": ["jpg", "png", "gif", "webp"],
                },
            ),
            create_click_url_asset(),
            create_impression_tracker_asset(),
        ],
    ),
    # Concrete formats for backward compatibility
    CreativeFormat(
        format_id=create_format_id("display_300x250_image"),
        name="Medium Rectangle - Image",
        type=FormatCategory.display,
        description="300x250 static image banner",
        supported_macros=COMMON_MACROS,
        renders=[create_fixed_render(300, 250)],
        assets=[
            create_asset(
                asset_id="banner_image",
                asset_type=AssetType.image,
                required=True,
                requirements={
                    "width": 300,
                    "height": 250,
                    "max_file_size_mb": 0.2,
                    "acceptable_formats": ["jpg", "png", "gif", "webp"],
                },
            ),
            create_click_url_asset(),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("display_728x90_image"),
        name="Leaderboard - Image",
        type=FormatCategory.display,
        description="728x90 static image banner",
        supported_macros=COMMON_MACROS,
        renders=[create_fixed_render(728, 90)],
        assets=[
            create_asset(
                asset_id="banner_image",
                asset_type=AssetType.image,
                required=True,
                requirements={
                    "width": 728,
                    "height": 90,
                    "max_file_size_mb": 0.15,
                    "acceptable_formats": ["jpg", "png", "gif", "webp"],
                },
            ),
            create_click_url_asset(),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("display_320x50_image"),
        name="Mobile Banner - Image",
        type=FormatCategory.display,
        description="320x50 mobile banner",
        supported_macros=COMMON_MACROS,
        renders=[create_fixed_render(320, 50)],
        assets=[
            create_asset(
                asset_id="banner_image",
                asset_type=AssetType.image,
                required=True,
                requirements={
                    "width": 320,
                    "height": 50,
                    "max_file_size_mb": 0.05,
                    "acceptable_formats": ["jpg", "png", "gif", "webp"],
                },
            ),
            create_click_url_asset(),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("display_160x600_image"),
        name="Wide Skyscraper - Image",
        type=FormatCategory.display,
        description="160x600 wide skyscraper banner",
        supported_macros=COMMON_MACROS,
        renders=[create_fixed_render(160, 600)],
        assets=[
            create_asset(
                asset_id="banner_image",
                asset_type=AssetType.image,
                required=True,
                requirements={
                    "width": 160,
                    "height": 600,
                    "max_file_size_mb": 0.15,
                    "acceptable_formats": ["jpg", "png", "gif", "webp"],
                },
            ),
            create_click_url_asset(),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("display_336x280_image"),
        name="Large Rectangle - Image",
        type=FormatCategory.display,
        description="336x280 large rectangle banner",
        supported_macros=COMMON_MACROS,
        renders=[create_fixed_render(336, 280)],
        assets=[
            create_asset(
                asset_id="banner_image",
                asset_type=AssetType.image,
                required=True,
                requirements={
                    "width": 336,
                    "height": 280,
                    "max_file_size_mb": 0.25,
                    "acceptable_formats": ["jpg", "png", "gif", "webp"],
                },
            ),
            create_click_url_asset(),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("display_300x600_image"),
        name="Half Page - Image",
        type=FormatCategory.display,
        description="300x600 half page banner",
        supported_macros=COMMON_MACROS,
        renders=[create_fixed_render(300, 600)],
        assets=[
            create_asset(
                asset_id="banner_image",
                asset_type=AssetType.image,
                required=True,
                requirements={
                    "width": 300,
                    "height": 600,
                    "max_file_size_mb": 0.3,
                    "acceptable_formats": ["jpg", "png", "gif", "webp"],
                },
            ),
            create_click_url_asset(),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("display_970x250_image"),
        name="Billboard - Image",
        type=FormatCategory.display,
        description="970x250 billboard banner",
        supported_macros=COMMON_MACROS,
        renders=[create_fixed_render(970, 250)],
        assets=[
            create_asset(
                asset_id="banner_image",
                asset_type=AssetType.image,
                required=True,
                requirements={
                    "width": 970,
                    "height": 250,
                    "max_file_size_mb": 0.4,
                    "acceptable_formats": ["jpg", "png", "gif", "webp"],
                },
            ),
            create_click_url_asset(),
            create_impression_tracker_asset(),
        ],
    ),
]

# Display Formats - HTML5
# Template format (for new integrations) + concrete formats (for backward compatibility)
DISPLAY_HTML_FORMATS = [
    # Template format - supports any dimensions
    CreativeFormat(
        format_id=create_format_id("display_html"),
        name="Display Banner - HTML5",
        type=FormatCategory.display,
        description="HTML5 creative (supports any dimensions)",
        accepts_parameters=[FormatIdParameter.dimensions],
        supported_macros=COMMON_MACROS,
        assets=[
            create_asset(
                asset_id="html_creative",
                asset_type=AssetType.html,
                required=True,
                requirements={
                    "max_file_size_mb": 0.5,
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    # Concrete formats for backward compatibility
    CreativeFormat(
        format_id=create_format_id("display_300x250_html"),
        name="Medium Rectangle - HTML5",
        type=FormatCategory.display,
        description="300x250 HTML5 creative",
        supported_macros=COMMON_MACROS,
        renders=[create_fixed_render(300, 250)],
        assets=[
            create_asset(
                asset_id="html_creative",
                asset_type=AssetType.html,
                required=True,
                requirements={
                    "width": 300,
                    "height": 250,
                    "max_file_size_mb": 0.5,
                    "description": "HTML5 creative code",
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("display_728x90_html"),
        name="Leaderboard - HTML5",
        type=FormatCategory.display,
        description="728x90 HTML5 creative",
        supported_macros=COMMON_MACROS,
        renders=[create_fixed_render(728, 90)],
        assets=[
            create_asset(
                asset_id="html_creative",
                asset_type=AssetType.html,
                required=True,
                requirements={
                    "width": 728,
                    "height": 90,
                    "max_file_size_mb": 0.5,
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("display_160x600_html"),
        name="Wide Skyscraper - HTML5",
        type=FormatCategory.display,
        description="160x600 HTML5 creative",
        supported_macros=COMMON_MACROS,
        renders=[create_fixed_render(160, 600)],
        assets=[
            create_asset(
                asset_id="html_creative",
                asset_type=AssetType.html,
                required=True,
                requirements={
                    "width": 160,
                    "height": 600,
                    "max_file_size_mb": 0.5,
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("display_336x280_html"),
        name="Large Rectangle - HTML5",
        type=FormatCategory.display,
        description="336x280 HTML5 creative",
        supported_macros=COMMON_MACROS,
        renders=[create_fixed_render(336, 280)],
        assets=[
            create_asset(
                asset_id="html_creative",
                asset_type=AssetType.html,
                required=True,
                requirements={
                    "width": 336,
                    "height": 280,
                    "max_file_size_mb": 0.5,
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("display_300x600_html"),
        name="Half Page - HTML5",
        type=FormatCategory.display,
        description="300x600 HTML5 creative",
        supported_macros=COMMON_MACROS,
        renders=[create_fixed_render(300, 600)],
        assets=[
            create_asset(
                asset_id="html_creative",
                asset_type=AssetType.html,
                required=True,
                requirements={
                    "width": 300,
                    "height": 600,
                    "max_file_size_mb": 0.5,
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("display_970x250_html"),
        name="Billboard - HTML5",
        type=FormatCategory.display,
        description="970x250 HTML5 creative",
        supported_macros=COMMON_MACROS,
        renders=[create_fixed_render(970, 250)],
        assets=[
            create_asset(
                asset_id="html_creative",
                asset_type=AssetType.html,
                required=True,
                requirements={
                    "width": 970,
                    "height": 250,
                    "max_file_size_mb": 0.5,
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
]

# Display Formats - JavaScript
# Template format for JavaScript-based display ads
DISPLAY_JS_FORMATS = [
    # Template format - supports any dimensions
    CreativeFormat(
        format_id=create_format_id("display_js"),
        name="Display Banner - JavaScript",
        type=FormatCategory.display,
        description="JavaScript-based display ad (supports any dimensions)",
        accepts_parameters=[FormatIdParameter.dimensions],
        supported_macros=COMMON_MACROS,
        assets=[
            create_asset(
                asset_id="js_creative",
                asset_type=AssetType.javascript,
                required=True,
            ),
            create_impression_tracker_asset(),
        ],
    ),
]

# Native Formats
NATIVE_FORMATS = [
    CreativeFormat(
        format_id=create_format_id("native_standard"),
        name="IAB Native Standard",
        type=FormatCategory.native,
        description="Standard native ad with title, description, image, and CTA",
        supported_macros=COMMON_MACROS,
        assets=[
            create_asset(
                asset_id="title",
                asset_type=AssetType.text,
                required=True,
                requirements={
                    "description": "Headline text (25 chars recommended)",
                },
            ),
            create_asset(
                asset_id="description",
                asset_type=AssetType.text,
                required=True,
                requirements={
                    "description": "Body copy (90 chars recommended)",
                },
            ),
            create_asset(
                asset_id="main_image",
                asset_type=AssetType.image,
                required=True,
                requirements={
                    "description": "Primary image (1200x627 recommended)",
                },
            ),
            create_asset(
                asset_id="icon",
                asset_type=AssetType.image,
                required=False,
                requirements={
                    "description": "Brand icon (square, 200x200 recommended)",
                },
            ),
            create_asset(
                asset_id="cta_text",
                asset_type=AssetType.text,
                required=True,
                requirements={
                    "description": "Call-to-action text",
                },
            ),
            create_asset(
                asset_id="sponsored_by",
                asset_type=AssetType.text,
                required=True,
                requirements={
                    "description": "Advertiser name for disclosure",
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("native_content"),
        name="Native Content Placement",
        type=FormatCategory.native,
        description="In-article native ad with editorial styling",
        supported_macros=COMMON_MACROS,
        assets=[
            create_asset(
                asset_id="headline",
                asset_type=AssetType.text,
                required=True,
                requirements={
                    "description": "Editorial-style headline (60 chars recommended)",
                },
            ),
            create_asset(
                asset_id="body",
                asset_type=AssetType.text,
                required=True,
                requirements={
                    "description": "Article-style body copy (200 chars recommended)",
                },
            ),
            create_asset(
                asset_id="thumbnail",
                asset_type=AssetType.image,
                required=True,
                requirements={
                    "description": "Thumbnail image (square, 300x300 recommended)",
                },
            ),
            create_asset(
                asset_id="author",
                asset_type=AssetType.text,
                required=False,
                requirements={
                    "description": "Author name for editorial context",
                },
            ),
            create_click_url_asset(),
            create_asset(
                asset_id="disclosure",
                asset_type=AssetType.text,
                required=True,
                requirements={
                    "description": "Sponsored content disclosure text",
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
]

# Audio Formats
AUDIO_FORMATS = [
    CreativeFormat(
        format_id=create_format_id("audio_standard_15s"),
        name="Standard Audio - 15 seconds",
        type=FormatCategory.audio,
        description="15-second audio ad",
        supported_macros=[*COMMON_MACROS, "CONTENT_GENRE"],
        assets=[
            create_asset(
                asset_id="audio_file",
                asset_type=AssetType.audio,
                required=True,
                requirements={
                    "duration_seconds": 15,
                    "acceptable_formats": ["mp3", "aac", "m4a"],
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("audio_standard_30s"),
        name="Standard Audio - 30 seconds",
        type=FormatCategory.audio,
        description="30-second audio ad",
        supported_macros=[*COMMON_MACROS, "CONTENT_GENRE"],
        assets=[
            create_asset(
                asset_id="audio_file",
                asset_type=AssetType.audio,
                required=True,
                requirements={
                    "duration_seconds": 30,
                    "acceptable_formats": ["mp3", "aac", "m4a"],
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("audio_standard_60s"),
        name="Standard Audio - 60 seconds",
        type=FormatCategory.audio,
        description="60-second audio ad",
        supported_macros=[*COMMON_MACROS, "CONTENT_GENRE"],
        assets=[
            create_asset(
                asset_id="audio_file",
                asset_type=AssetType.audio,
                required=True,
                requirements={
                    "duration_seconds": 60,
                    "acceptable_formats": ["mp3", "aac", "m4a"],
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
]

# DOOH Formats
DOOH_FORMATS = [
    CreativeFormat(
        format_id=create_format_id("dooh_billboard_1920x1080"),
        name="Digital Billboard - 1920x1080",
        type=FormatCategory.dooh,
        description="Full HD digital billboard",
        supported_macros=[*COMMON_MACROS, "SCREEN_ID", "VENUE_TYPE", "VENUE_LAT", "VENUE_LONG"],
        renders=[create_fixed_render(1920, 1080)],
        assets=[
            create_asset(
                asset_id="billboard_image",
                asset_type=AssetType.image,
                required=True,
                requirements={
                    "width": 1920,
                    "height": 1080,
                    "acceptable_formats": ["jpg", "png"],
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("dooh_billboard_landscape"),
        name="Digital Billboard - Landscape",
        type=FormatCategory.dooh,
        description="Landscape-oriented digital billboard (various sizes)",
        supported_macros=[*COMMON_MACROS, "SCREEN_ID", "VENUE_TYPE", "VENUE_LAT", "VENUE_LONG"],
        assets=[
            create_asset(
                asset_id="billboard_image",
                asset_type=AssetType.image,
                required=True,
                requirements={
                    "acceptable_formats": ["jpg", "png"],
                    "description": "Landscape image (1920x1080 or larger)",
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("dooh_billboard_portrait"),
        name="Digital Billboard - Portrait",
        type=FormatCategory.dooh,
        description="Portrait-oriented digital billboard (various sizes)",
        supported_macros=[*COMMON_MACROS, "SCREEN_ID", "VENUE_TYPE", "VENUE_LAT", "VENUE_LONG"],
        assets=[
            create_asset(
                asset_id="billboard_image",
                asset_type=AssetType.image,
                required=True,
                requirements={
                    "acceptable_formats": ["jpg", "png"],
                    "description": "Portrait image (1080x1920 or similar)",
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("dooh_transit_screen"),
        name="Transit Screen",
        type=FormatCategory.dooh,
        description="Transit and subway screen displays",
        supported_macros=[*COMMON_MACROS, "SCREEN_ID", "VENUE_TYPE", "VENUE_LAT", "VENUE_LONG", "TRANSIT_LINE"],
        renders=[create_fixed_render(1920, 1080)],
        assets=[
            create_asset(
                asset_id="screen_image",
                asset_type=AssetType.image,
                required=True,
                requirements={
                    "width": 1920,
                    "height": 1080,
                    "acceptable_formats": ["jpg", "png"],
                    "description": "Transit screen content",
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
]

# Info Card Formats - For visualizing products and formats in user interfaces
INFO_CARD_FORMATS = [
    CreativeFormat(
        format_id=create_format_id("product_card_standard"),
        name="Product Card - Standard",
        type=FormatCategory.display,
        description="Standard visual card (300x400px) for displaying ad inventory products",
        supported_macros=COMMON_MACROS,
        renders=[create_fixed_render(300, 400)],
        assets=[
            create_asset(
                asset_id="product_image",
                asset_type=AssetType.image,
                required=True,
                requirements={
                    "description": "Primary product image or placement preview",
                },
            ),
            create_asset(
                asset_id="product_name",
                asset_type=AssetType.text,
                required=True,
                requirements={
                    "description": "Display name of the product (e.g., 'Homepage Leaderboard')",
                },
            ),
            create_asset(
                asset_id="product_description",
                asset_type=AssetType.text,
                required=True,
                requirements={
                    "description": "Short description of the product (supports markdown)",
                },
            ),
            create_asset(
                asset_id="pricing_model",
                asset_type=AssetType.text,
                required=False,
                requirements={
                    "description": "Pricing model (e.g., 'CPM', 'flat_rate', 'CPC')",
                },
            ),
            create_asset(
                asset_id="pricing_amount",
                asset_type=AssetType.text,
                required=False,
                requirements={
                    "description": "Price amount (e.g., '15.00')",
                },
            ),
            create_asset(
                asset_id="pricing_currency",
                asset_type=AssetType.text,
                required=False,
                requirements={
                    "description": "Currency code (e.g., 'USD')",
                },
            ),
            create_asset(
                asset_id="delivery_type",
                asset_type=AssetType.text,
                required=False,
                requirements={
                    "description": "Delivery type: 'guaranteed' or 'bidded'",
                },
            ),
            create_asset(
                asset_id="primary_asset_type",
                asset_type=AssetType.text,
                required=False,
                requirements={
                    "description": "Primary asset type: 'display', 'video', 'audio', 'native'",
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("product_card_detailed"),
        name="Product Card - Detailed",
        type=FormatCategory.display,
        description="Detailed card with carousel and full specifications for rich product presentation",
        supported_macros=COMMON_MACROS,
        renders=[create_responsive_render()],
        assets=[
            create_asset(
                asset_id="product_image",
                asset_type=AssetType.image,
                required=True,
                requirements={
                    "description": "Primary product image or placement preview",
                },
            ),
            create_asset(
                asset_id="product_name",
                asset_type=AssetType.text,
                required=True,
                requirements={
                    "description": "Display name of the product (e.g., 'Homepage Leaderboard')",
                },
            ),
            create_asset(
                asset_id="product_description",
                asset_type=AssetType.text,
                required=True,
                requirements={
                    "description": "Detailed description of the product (supports markdown)",
                },
            ),
            create_asset(
                asset_id="pricing_model",
                asset_type=AssetType.text,
                required=False,
                requirements={
                    "description": "Pricing model (e.g., 'CPM', 'flat_rate', 'CPC')",
                },
            ),
            create_asset(
                asset_id="pricing_amount",
                asset_type=AssetType.text,
                required=False,
                requirements={
                    "description": "Price amount (e.g., '15.00')",
                },
            ),
            create_asset(
                asset_id="pricing_currency",
                asset_type=AssetType.text,
                required=False,
                requirements={
                    "description": "Currency code (e.g., 'USD')",
                },
            ),
            create_asset(
                asset_id="delivery_type",
                asset_type=AssetType.text,
                required=False,
                requirements={
                    "description": "Delivery type: 'guaranteed' or 'bidded'",
                },
            ),
            create_asset(
                asset_id="primary_asset_type",
                asset_type=AssetType.text,
                required=False,
                requirements={
                    "description": "Primary asset type: 'display', 'video', 'audio', 'native'",
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("format_card_standard"),
        name="Format Card - Standard",
        type=FormatCategory.display,
        description="Standard visual card (300x400px) for displaying creative formats in user interfaces",
        supported_macros=COMMON_MACROS,
        renders=[create_fixed_render(300, 400)],
        assets=[
            create_asset(
                asset_id="format",
                asset_type=AssetType.text,
                required=True,
                requirements={
                    "description": "Creative format specification to visualize on the card",
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
    CreativeFormat(
        format_id=create_format_id("format_card_detailed"),
        name="Format Card - Detailed",
        type=FormatCategory.display,
        description="Detailed card with carousel and full specifications for rich format documentation",
        supported_macros=COMMON_MACROS,
        renders=[create_responsive_render()],
        assets=[
            create_asset(
                asset_id="format",
                asset_type=AssetType.text,
                required=True,
                requirements={
                    "description": "Creative format specification with full details for detailed card",
                },
            ),
            create_impression_tracker_asset(),
        ],
    ),
]

# Combine all formats
STANDARD_FORMATS = (
    GENERATIVE_FORMATS
    + VIDEO_FORMATS
    + DISPLAY_IMAGE_FORMATS
    + DISPLAY_HTML_FORMATS
    + DISPLAY_JS_FORMATS
    + NATIVE_FORMATS
    + AUDIO_FORMATS
    + DOOH_FORMATS
    + INFO_CARD_FORMATS
)


def get_format_by_id(format_id: FormatId) -> CreativeFormat | None:
    """Get format by FormatId object.

    For template formats, matches on base ID (agent_url + id) regardless of parameters.
    For concrete formats, requires exact match including any dimension parameters.
    """
    for fmt in STANDARD_FORMATS:
        # Compare base ID and agent URL
        if fmt.format_id.id != format_id.id or str(fmt.format_id.agent_url) != str(format_id.agent_url):
            continue

        # If format is a template, match on base ID only
        if getattr(fmt, "accepts_parameters", None):
            return fmt

        # For concrete formats, dimensions must match exactly
        fmt_width = getattr(fmt.format_id, "width", None)
        fmt_height = getattr(fmt.format_id, "height", None)
        search_width = getattr(format_id, "width", None)
        search_height = getattr(format_id, "height", None)

        if fmt_width == search_width and fmt_height == search_height:
            return fmt

    return None


def filter_formats(
    format_ids: list[FormatId] | None = None,
    type: FormatCategory | str | None = None,
    asset_types: list[AssetType | str] | None = None,
    dimensions: str | None = None,
    max_width: int | None = None,
    max_height: int | None = None,
    min_width: int | None = None,
    min_height: int | None = None,
    is_responsive: bool | None = None,
    name_search: str | None = None,
) -> list[CreativeFormat]:
    """Filter formats based on criteria."""
    results = STANDARD_FORMATS

    if format_ids:
        # Convert to (id, agent_url, width, height) tuples for comparison
        # For template formats, match on base ID if width/height not specified in search
        search_ids = [
            (fid.id, str(fid.agent_url), getattr(fid, "width", None), getattr(fid, "height", None))
            for fid in format_ids
        ]

        def matches_format_id(fmt: CreativeFormat, search_id: tuple[str, str, int | None, int | None]) -> bool:
            base_id, agent_url, search_width, search_height = search_id
            if fmt.format_id.id != base_id or str(fmt.format_id.agent_url) != agent_url:
                return False
            # If searching with parameters, template must match exactly
            # If searching without parameters, match base template ID
            if search_width is not None or search_height is not None:
                fmt_width = getattr(fmt.format_id, "width", None)
                fmt_height = getattr(fmt.format_id, "height", None)
                return bool(fmt_width == search_width and fmt_height == search_height)
            return True

        results = [fmt for fmt in results if any(matches_format_id(fmt, sid) for sid in search_ids)]

    if type:
        # Handle both Type enum and string values
        # fmt.type is always a Type enum (adcp 2.1.0+)
        if isinstance(type, str):
            # Compare enum value to string
            results = [fmt for fmt in results if fmt.type is not None and fmt.type.value == type]
        else:
            # Compare enum to enum
            results = [fmt for fmt in results if fmt.type == type]

    if dimensions:
        # Support legacy "WIDTHxHEIGHT" string format for backward compatibility
        parts = dimensions.split("x")
        if len(parts) == 2:
            try:
                target_width, target_height = int(parts[0]), int(parts[1])

                def matches_dimensions(fmt: CreativeFormat) -> bool:
                    # Template formats accept dimensions but don't have fixed renders
                    accepts_params = getattr(fmt, "accepts_parameters", None)
                    if accepts_params is not None and FormatIdParameter.dimensions in accepts_params:
                        return True
                    # Concrete formats have fixed renders
                    if not fmt.renders or len(fmt.renders) == 0:
                        return False
                    render = fmt.renders[0]
                    # renders are always Pydantic models (adcp 2.2.0+)
                    dims = render.dimensions
                    return (
                        getattr(dims, "width", None) == target_width and getattr(dims, "height", None) == target_height
                    )

                results = [fmt for fmt in results if matches_dimensions(fmt)]
            except ValueError:
                pass  # Invalid dimension format, skip filter

    # Dimension filtering
    if any([max_width, max_height, min_width, min_height]):

        def get_dimensions(fmt: CreativeFormat) -> tuple[float | None, float | None]:
            """Extract width and height from format renders."""
            if fmt.renders and len(fmt.renders) > 0:
                render = fmt.renders[0]
                # renders are always Pydantic models (adcp 2.2.0+)
                dims = render.dimensions
                return getattr(dims, "width", None), getattr(dims, "height", None)
            return None, None

        filtered = []
        for fmt in results:
            # Template formats accept any dimensions within the constraints
            accepts_params = getattr(fmt, "accepts_parameters", None)
            if accepts_params is not None and FormatIdParameter.dimensions in accepts_params:
                # Include template formats - they can satisfy any dimension requirements
                filtered.append(fmt)
                continue

            width, height = get_dimensions(fmt)
            # Exclude formats without dimensions when dimension filtering is requested
            if width is None or height is None:
                continue

            if max_width is not None and width > max_width:
                continue
            if max_height is not None and height > max_height:
                continue
            if min_width is not None and width < min_width:
                continue
            if min_height is not None and height < min_height:
                continue

            filtered.append(fmt)
        results = filtered

    if is_responsive is not None:
        # Filter based on responsive field in ADCP 2.12.0+ schema
        def is_format_responsive(fmt: CreativeFormat) -> bool:
            if not fmt.renders or len(fmt.renders) == 0:
                return False
            render = fmt.renders[0]
            # renders are always Pydantic models (adcp 2.12.0+)
            dims = render.dimensions
            # In ADCP 2.12.0+, responsive field indicates if dimensions adapt to container
            responsive = getattr(dims, "responsive", None)
            if responsive is None:
                return False
            # Check if either width or height is responsive
            return getattr(responsive, "width", False) or getattr(responsive, "height", False)

        if is_responsive:
            results = [fmt for fmt in results if is_format_responsive(fmt)]
        else:
            results = [fmt for fmt in results if not is_format_responsive(fmt)]

    if name_search:
        search_lower = name_search.lower()
        results = [fmt for fmt in results if search_lower in fmt.name.lower()]

    if asset_types:
        # Filter to formats that include ALL specified asset types
        def has_asset_type(req: Any, target_type: AssetType | str) -> bool:
            """Check if a requirement has the target asset type."""
            # Compare string values
            target_str = target_type.value if isinstance(target_type, AssetType) else target_type

            # Individual assets have asset_type directly; repeatable groups do not
            req_asset_type = getattr(req, "asset_type", None)
            if req_asset_type is not None:
                if hasattr(req_asset_type, "value"):
                    req_asset_type = req_asset_type.value
                if req_asset_type == target_str:
                    return True
            # Repeatable groups carry inner assets — check those
            if hasattr(req, "assets"):
                for asset in req.assets:
                    asset_type: Any = getattr(asset, "asset_type", None)
                    if asset_type is not None and hasattr(asset_type, "value"):
                        asset_type = asset_type.value
                    if asset_type == target_str:
                        return True
            return False

        results = [
            fmt
            for fmt in results
            if get_required_assets(fmt)
            and all(
                any(has_asset_type(req, asset_type) for req in get_required_assets(fmt)) for asset_type in asset_types
            )
        ]

    return results
