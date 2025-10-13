"""Standard AdCP creative formats."""

from pydantic import AnyUrl

from ..schemas import CreativeFormat
from ..schemas_generated._schemas_v1_core_format_json import AssetsRequired, AssetType, Category, Type

# Agent configuration
AGENT_URL = AnyUrl("https://creative.adcontextprotocol.org")
AGENT_NAME = "AdCP Standard Creative Agent"
AGENT_CAPABILITIES = ["validation", "assembly", "generation", "preview"]

# Common macros supported across all formats
COMMON_MACROS = [
    "MEDIA_BUY_ID",
    "CREATIVE_ID",
    "CACHEBUSTER",
    "CLICK_URL",
    "IMPRESSION_URL",
    "DEVICE_TYPE",
    "GDPR",
    "GDPR_CONSENT",
    "US_PRIVACY",
    "GPP_STRING",
]

# Generative Formats - AI-powered creative generation
# These use type='display' (what they generate) and output_format_ids
# to specify what standard formats they can produce
GENERATIVE_FORMATS = [
    CreativeFormat(
        format_id="display_300x250_generative",
        agent_url=AGENT_URL,
        name="Medium Rectangle - AI Generated",
        type=Type.display,
        category=Category.standard,
        is_standard=True,
        description="AI-generated 300x250 banner from brand context and prompt",
        requirements={"dimensions": "300x250"},
        output_format_ids=["display_300x250_image"],
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetsRequired(
                asset_id="brand_context",
                asset_type=AssetType.brand_manifest,
                asset_role="brand_context",
                required=True,
                requirements={"description": "Brand information and product offerings for AI generation"},
            ),
            AssetsRequired(
                asset_id="generation_prompt",
                asset_type=AssetType.text,
                asset_role="generation_prompt",
                required=True,
                requirements={"description": "Text prompt describing the desired creative"},
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_728x90_generative",
        agent_url=AGENT_URL,
        name="Leaderboard - AI Generated",
        type=Type.display,
        category=Category.standard,
        is_standard=True,
        description="AI-generated 728x90 banner from brand context and prompt",
        requirements={"dimensions": "728x90"},
        output_format_ids=["display_728x90_image"],
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetsRequired(
                asset_id="brand_context",
                asset_type=AssetType.brand_manifest,
                asset_role="brand_context",
                required=True,
                requirements={"description": "Brand information and product offerings for AI generation"},
            ),
            AssetsRequired(
                asset_id="generation_prompt",
                asset_type=AssetType.text,
                asset_role="generation_prompt",
                required=True,
                requirements={"description": "Text prompt describing the desired creative"},
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_320x50_generative",
        agent_url=AGENT_URL,
        name="Mobile Banner - AI Generated",
        type=Type.display,
        category=Category.standard,
        is_standard=True,
        description="AI-generated 320x50 mobile banner from brand context and prompt",
        requirements={"dimensions": "320x50"},
        output_format_ids=["display_320x50_image"],
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetsRequired(
                asset_id="brand_context",
                asset_type=AssetType.brand_manifest,
                asset_role="brand_context",
                required=True,
                requirements={"description": "Brand information and product offerings for AI generation"},
            ),
            AssetsRequired(
                asset_id="generation_prompt",
                asset_type=AssetType.text,
                asset_role="generation_prompt",
                required=True,
                requirements={"description": "Text prompt describing the desired creative"},
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_160x600_generative",
        agent_url=AGENT_URL,
        name="Wide Skyscraper - AI Generated",
        type=Type.display,
        category=Category.standard,
        is_standard=True,
        description="AI-generated 160x600 wide skyscraper from brand context and prompt",
        requirements={"dimensions": "160x600"},
        output_format_ids=["display_160x600_image"],
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetsRequired(
                asset_id="brand_context",
                asset_type=AssetType.brand_manifest,
                asset_role="brand_context",
                required=True,
                requirements={"description": "Brand information and product offerings for AI generation"},
            ),
            AssetsRequired(
                asset_id="generation_prompt",
                asset_type=AssetType.text,
                asset_role="generation_prompt",
                required=True,
                requirements={"description": "Text prompt describing the desired creative"},
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_336x280_generative",
        agent_url=AGENT_URL,
        name="Large Rectangle - AI Generated",
        type=Type.display,
        category=Category.standard,
        is_standard=True,
        description="AI-generated 336x280 large rectangle from brand context and prompt",
        requirements={"dimensions": "336x280"},
        output_format_ids=["display_336x280_image"],
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetsRequired(
                asset_id="brand_context",
                asset_type=AssetType.brand_manifest,
                asset_role="brand_context",
                required=True,
                requirements={"description": "Brand information and product offerings for AI generation"},
            ),
            AssetsRequired(
                asset_id="generation_prompt",
                asset_type=AssetType.text,
                asset_role="generation_prompt",
                required=True,
                requirements={"description": "Text prompt describing the desired creative"},
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_300x600_generative",
        agent_url=AGENT_URL,
        name="Half Page - AI Generated",
        type=Type.display,
        category=Category.standard,
        is_standard=True,
        description="AI-generated 300x600 half page from brand context and prompt",
        requirements={"dimensions": "300x600"},
        output_format_ids=["display_300x600_image"],
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetsRequired(
                asset_id="brand_context",
                asset_type=AssetType.brand_manifest,
                asset_role="brand_context",
                required=True,
                requirements={"description": "Brand information and product offerings for AI generation"},
            ),
            AssetsRequired(
                asset_id="generation_prompt",
                asset_type=AssetType.text,
                asset_role="generation_prompt",
                required=True,
                requirements={"description": "Text prompt describing the desired creative"},
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_970x250_generative",
        agent_url=AGENT_URL,
        name="Billboard - AI Generated",
        type=Type.display,
        category=Category.standard,
        is_standard=True,
        description="AI-generated 970x250 billboard from brand context and prompt",
        requirements={"dimensions": "970x250"},
        output_format_ids=["display_970x250_image"],
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetsRequired(
                asset_id="brand_context",
                asset_type=AssetType.brand_manifest,
                asset_role="brand_context",
                required=True,
                requirements={"description": "Brand information and product offerings for AI generation"},
            ),
            AssetsRequired(
                asset_id="generation_prompt",
                asset_type=AssetType.text,
                asset_role="generation_prompt",
                required=True,
                requirements={"description": "Text prompt describing the desired creative"},
            ),
        ],
    ),
]

# Video Formats
VIDEO_FORMATS = [
    CreativeFormat(
        format_id="video_standard_30s",
        agent_url=AGENT_URL,
        name="Standard Video - 30 seconds",
        type=Type.video,
        category=Category.standard,
        is_standard=True,
        description="30-second video ad in standard aspect ratios",
        accepts_3p_tags=True,
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        requirements={
            "duration_seconds": 30,
            "max_file_size_mb": 50,
            "acceptable_formats": ["mp4", "mov", "webm"],
            "aspect_ratios": ["16:9", "9:16", "1:1", "4:5"],
        },
        assets_required=[
            AssetsRequired(
                asset_id="video_file",
                asset_type=AssetType.video,
                asset_role="video_file",
                required=True,
                requirements={
                    "duration_seconds": 30,
                    "acceptable_formats": ["mp4", "mov", "webm"],
                    "description": "30-second video file",
                },
            ),
        ],
    ),
    CreativeFormat(
        format_id="video_standard_15s",
        agent_url=AGENT_URL,
        name="Standard Video - 15 seconds",
        type=Type.video,
        category=Category.standard,
        is_standard=True,
        description="15-second video ad in standard aspect ratios",
        accepts_3p_tags=True,
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        requirements={
            "duration_seconds": 15,
            "max_file_size_mb": 25,
            "acceptable_formats": ["mp4", "mov", "webm"],
            "aspect_ratios": ["16:9", "9:16", "1:1", "4:5"],
        },
        assets_required=[
            AssetsRequired(
                asset_id="video_file",
                asset_type=AssetType.video,
                asset_role="video_file",
                required=True,
                requirements={
                    "duration_seconds": 15,
                    "acceptable_formats": ["mp4", "mov", "webm"],
                    "description": "15-second video file",
                },
            ),
        ],
    ),
    CreativeFormat(
        format_id="video_vast_30s",
        agent_url=AGENT_URL,
        name="VAST Video - 30 seconds",
        type=Type.video,
        category=Category.standard,
        is_standard=True,
        description="30-second video ad via VAST tag",
        accepts_3p_tags=True,
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        requirements={
            "duration_seconds": 30,
        },
        assets_required=[
            AssetsRequired(
                asset_id="vast_tag",
                asset_type=AssetType.text,
                asset_role="vast_tag",
                required=True,
                requirements={
                    "description": "VAST 4.x compatible tag",
                },
            ),
        ],
    ),
    CreativeFormat(
        format_id="video_1920x1080",
        agent_url=AGENT_URL,
        name="Full HD Video - 1920x1080",
        type=Type.video,
        category=Category.standard,
        is_standard=True,
        description="1920x1080 Full HD video (16:9)",
        accepts_3p_tags=False,
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        requirements={
            "dimensions": "1920x1080",
            "max_file_size_mb": 100,
            "acceptable_formats": ["mp4", "mov", "webm"],
            "aspect_ratios": ["16:9"],
        },
        assets_required=[
            AssetsRequired(
                asset_id="video_file",
                asset_type=AssetType.video,
                asset_role="video_file",
                required=True,
                requirements={
                    "width": 1920,
                    "height": 1080,
                    "acceptable_formats": ["mp4", "mov", "webm"],
                    "description": "1920x1080 video file",
                },
            ),
        ],
    ),
    CreativeFormat(
        format_id="video_1280x720",
        agent_url=AGENT_URL,
        name="HD Video - 1280x720",
        type=Type.video,
        category=Category.standard,
        is_standard=True,
        description="1280x720 HD video (16:9)",
        accepts_3p_tags=False,
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        requirements={
            "dimensions": "1280x720",
            "max_file_size_mb": 75,
            "acceptable_formats": ["mp4", "mov", "webm"],
            "aspect_ratios": ["16:9"],
        },
        assets_required=[
            AssetsRequired(
                asset_id="video_file",
                asset_type=AssetType.video,
                asset_role="video_file",
                required=True,
                requirements={
                    "width": 1280,
                    "height": 720,
                    "acceptable_formats": ["mp4", "mov", "webm"],
                    "description": "1280x720 video file",
                },
            ),
        ],
    ),
    CreativeFormat(
        format_id="video_1080x1920",
        agent_url=AGENT_URL,
        name="Vertical Video - 1080x1920",
        type=Type.video,
        category=Category.standard,
        is_standard=True,
        description="1080x1920 vertical video (9:16) for mobile stories",
        accepts_3p_tags=False,
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        requirements={
            "dimensions": "1080x1920",
            "max_file_size_mb": 100,
            "acceptable_formats": ["mp4", "mov", "webm"],
            "aspect_ratios": ["9:16"],
        },
        assets_required=[
            AssetsRequired(
                asset_id="video_file",
                asset_type=AssetType.video,
                asset_role="video_file",
                required=True,
                requirements={
                    "width": 1080,
                    "height": 1920,
                    "acceptable_formats": ["mp4", "mov", "webm"],
                    "description": "1080x1920 vertical video file",
                },
            ),
        ],
    ),
    CreativeFormat(
        format_id="video_1080x1080",
        agent_url=AGENT_URL,
        name="Square Video - 1080x1080",
        type=Type.video,
        category=Category.standard,
        is_standard=True,
        description="1080x1080 square video (1:1) for social feeds",
        accepts_3p_tags=False,
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        requirements={
            "dimensions": "1080x1080",
            "max_file_size_mb": 100,
            "acceptable_formats": ["mp4", "mov", "webm"],
            "aspect_ratios": ["1:1"],
        },
        assets_required=[
            AssetsRequired(
                asset_id="video_file",
                asset_type=AssetType.video,
                asset_role="video_file",
                required=True,
                requirements={
                    "width": 1080,
                    "height": 1080,
                    "acceptable_formats": ["mp4", "mov", "webm"],
                    "description": "1080x1080 square video file",
                },
            ),
        ],
    ),
    CreativeFormat(
        format_id="video_ctv_preroll_30s",
        agent_url=AGENT_URL,
        name="CTV Pre-Roll - 30 seconds",
        type=Type.video,
        category=Category.standard,
        is_standard=True,
        description="30-second pre-roll ad for Connected TV and streaming platforms",
        accepts_3p_tags=True,
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE", "PLAYER_SIZE"],
        requirements={
            "duration_seconds": 30,
            "max_file_size_mb": 75,
            "acceptable_formats": ["mp4", "mov"],
            "aspect_ratios": ["16:9"],
        },
        assets_required=[
            AssetsRequired(
                asset_id="video_file",
                asset_type=AssetType.video,
                asset_role="video_file",
                required=True,
                requirements={
                    "duration_seconds": 30,
                    "acceptable_formats": ["mp4", "mov"],
                    "description": "30-second CTV-optimized video file (1920x1080 recommended)",
                },
            ),
        ],
    ),
    CreativeFormat(
        format_id="video_ctv_midroll_30s",
        agent_url=AGENT_URL,
        name="CTV Mid-Roll - 30 seconds",
        type=Type.video,
        category=Category.standard,
        is_standard=True,
        description="30-second mid-roll ad for Connected TV and streaming platforms",
        accepts_3p_tags=True,
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE", "PLAYER_SIZE"],
        requirements={
            "duration_seconds": 30,
            "max_file_size_mb": 75,
            "acceptable_formats": ["mp4", "mov"],
            "aspect_ratios": ["16:9"],
        },
        assets_required=[
            AssetsRequired(
                asset_id="video_file",
                asset_type=AssetType.video,
                asset_role="video_file",
                required=True,
                requirements={
                    "duration_seconds": 30,
                    "acceptable_formats": ["mp4", "mov"],
                    "description": "30-second CTV-optimized video file (1920x1080 recommended)",
                },
            ),
        ],
    ),
]

# Display Formats - Image-based
DISPLAY_IMAGE_FORMATS = [
    CreativeFormat(
        format_id="display_300x250_image",
        agent_url=AGENT_URL,
        name="Medium Rectangle - Image",
        type=Type.display,
        category=Category.standard,
        is_standard=True,
        description="300x250 static image banner",
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        requirements={
            "dimensions": "300x250",
        },
        assets_required=[
            AssetsRequired(
                asset_id="banner_image",
                asset_type=AssetType.image,
                asset_role="banner_image",
                required=True,
                requirements={
                    "width": 300,
                    "height": 250,
                    "max_file_size_mb": 0.2,
                    "acceptable_formats": ["jpg", "png", "gif", "webp"],
                },
            ),
            AssetsRequired(
                asset_id="click_url",
                asset_type=AssetType.url,
                asset_role="click_url",
                required=True,
                requirements={
                    "description": "Clickthrough destination URL",
                },
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_728x90_image",
        agent_url=AGENT_URL,
        name="Leaderboard - Image",
        type=Type.display,
        category=Category.standard,
        is_standard=True,
        description="728x90 static image banner",
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        requirements={
            "dimensions": "728x90",
        },
        assets_required=[
            AssetsRequired(
                asset_id="banner_image",
                asset_type=AssetType.image,
                asset_role="banner_image",
                required=True,
                requirements={
                    "width": 728,
                    "height": 90,
                    "max_file_size_mb": 0.15,
                    "acceptable_formats": ["jpg", "png", "gif", "webp"],
                },
            ),
            AssetsRequired(
                asset_id="click_url",
                asset_type=AssetType.url,
                asset_role="click_url",
                required=True,
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_320x50_image",
        agent_url=AGENT_URL,
        name="Mobile Banner - Image",
        type=Type.display,
        category=Category.standard,
        is_standard=True,
        description="320x50 mobile banner",
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        requirements={
            "dimensions": "320x50",
        },
        assets_required=[
            AssetsRequired(
                asset_id="banner_image",
                asset_type=AssetType.image,
                asset_role="banner_image",
                required=True,
                requirements={
                    "width": 320,
                    "height": 50,
                    "max_file_size_mb": 0.05,
                    "acceptable_formats": ["jpg", "png", "gif", "webp"],
                },
            ),
            AssetsRequired(
                asset_id="click_url",
                asset_type=AssetType.url,
                asset_role="click_url",
                required=True,
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_160x600_image",
        agent_url=AGENT_URL,
        name="Wide Skyscraper - Image",
        type=Type.display,
        category=Category.standard,
        is_standard=True,
        description="160x600 wide skyscraper banner",
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        requirements={
            "dimensions": "160x600",
        },
        assets_required=[
            AssetsRequired(
                asset_id="banner_image",
                asset_type=AssetType.image,
                asset_role="banner_image",
                required=True,
                requirements={
                    "width": 160,
                    "height": 600,
                    "max_file_size_mb": 0.15,
                    "acceptable_formats": ["jpg", "png", "gif", "webp"],
                },
            ),
            AssetsRequired(
                asset_id="click_url",
                asset_type=AssetType.url,
                asset_role="click_url",
                required=True,
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_336x280_image",
        agent_url=AGENT_URL,
        name="Large Rectangle - Image",
        type=Type.display,
        category=Category.standard,
        is_standard=True,
        description="336x280 large rectangle banner",
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        requirements={
            "dimensions": "336x280",
        },
        assets_required=[
            AssetsRequired(
                asset_id="banner_image",
                asset_type=AssetType.image,
                asset_role="banner_image",
                required=True,
                requirements={
                    "width": 336,
                    "height": 280,
                    "max_file_size_mb": 0.25,
                    "acceptable_formats": ["jpg", "png", "gif", "webp"],
                },
            ),
            AssetsRequired(
                asset_id="click_url",
                asset_type=AssetType.url,
                asset_role="click_url",
                required=True,
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_300x600_image",
        agent_url=AGENT_URL,
        name="Half Page - Image",
        type=Type.display,
        category=Category.standard,
        is_standard=True,
        description="300x600 half page banner",
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        requirements={
            "dimensions": "300x600",
        },
        assets_required=[
            AssetsRequired(
                asset_id="banner_image",
                asset_type=AssetType.image,
                asset_role="banner_image",
                required=True,
                requirements={
                    "width": 300,
                    "height": 600,
                    "max_file_size_mb": 0.3,
                    "acceptable_formats": ["jpg", "png", "gif", "webp"],
                },
            ),
            AssetsRequired(
                asset_id="click_url",
                asset_type=AssetType.url,
                asset_role="click_url",
                required=True,
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_970x250_image",
        agent_url=AGENT_URL,
        name="Billboard - Image",
        type=Type.display,
        category=Category.standard,
        is_standard=True,
        description="970x250 billboard banner",
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        requirements={
            "dimensions": "970x250",
        },
        assets_required=[
            AssetsRequired(
                asset_id="banner_image",
                asset_type=AssetType.image,
                asset_role="banner_image",
                required=True,
                requirements={
                    "width": 970,
                    "height": 250,
                    "max_file_size_mb": 0.4,
                    "acceptable_formats": ["jpg", "png", "gif", "webp"],
                },
            ),
            AssetsRequired(
                asset_id="click_url",
                asset_type=AssetType.url,
                asset_role="click_url",
                required=True,
            ),
        ],
    ),
]

# Display Formats - HTML5
DISPLAY_HTML_FORMATS = [
    CreativeFormat(
        format_id="display_300x250_html",
        agent_url=AGENT_URL,
        name="Medium Rectangle - HTML5",
        type=Type.display,
        category=Category.standard,
        is_standard=True,
        description="300x250 HTML5 creative",
        accepts_3p_tags=True,
        supported_macros=COMMON_MACROS,
        requirements={
            "dimensions": "300x250",
        },
        assets_required=[
            AssetsRequired(
                asset_id="html_creative",
                asset_type=AssetType.html,
                asset_role="html_creative",
                required=True,
                requirements={
                    "width": 300,
                    "height": 250,
                    "max_file_size_mb": 0.5,
                    "description": "HTML5 creative code",
                },
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_728x90_html",
        agent_url=AGENT_URL,
        name="Leaderboard - HTML5",
        type=Type.display,
        category=Category.standard,
        is_standard=True,
        description="728x90 HTML5 creative",
        accepts_3p_tags=True,
        supported_macros=COMMON_MACROS,
        requirements={
            "dimensions": "728x90",
        },
        assets_required=[
            AssetsRequired(
                asset_id="html_creative",
                asset_type=AssetType.html,
                asset_role="html_creative",
                required=True,
                requirements={
                    "width": 728,
                    "height": 90,
                    "max_file_size_mb": 0.5,
                },
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_160x600_html",
        agent_url=AGENT_URL,
        name="Wide Skyscraper - HTML5",
        type=Type.display,
        category=Category.standard,
        is_standard=True,
        description="160x600 HTML5 creative",
        accepts_3p_tags=True,
        supported_macros=COMMON_MACROS,
        requirements={
            "dimensions": "160x600",
        },
        assets_required=[
            AssetsRequired(
                asset_id="html_creative",
                asset_type=AssetType.html,
                asset_role="html_creative",
                required=True,
                requirements={
                    "width": 160,
                    "height": 600,
                    "max_file_size_mb": 0.5,
                },
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_336x280_html",
        agent_url=AGENT_URL,
        name="Large Rectangle - HTML5",
        type=Type.display,
        category=Category.standard,
        is_standard=True,
        description="336x280 HTML5 creative",
        accepts_3p_tags=True,
        supported_macros=COMMON_MACROS,
        requirements={
            "dimensions": "336x280",
        },
        assets_required=[
            AssetsRequired(
                asset_id="html_creative",
                asset_type=AssetType.html,
                asset_role="html_creative",
                required=True,
                requirements={
                    "width": 336,
                    "height": 280,
                    "max_file_size_mb": 0.5,
                },
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_300x600_html",
        agent_url=AGENT_URL,
        name="Half Page - HTML5",
        type=Type.display,
        category=Category.standard,
        is_standard=True,
        description="300x600 HTML5 creative",
        accepts_3p_tags=True,
        supported_macros=COMMON_MACROS,
        requirements={
            "dimensions": "300x600",
        },
        assets_required=[
            AssetsRequired(
                asset_id="html_creative",
                asset_type=AssetType.html,
                asset_role="html_creative",
                required=True,
                requirements={
                    "width": 300,
                    "height": 600,
                    "max_file_size_mb": 0.5,
                },
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_970x250_html",
        agent_url=AGENT_URL,
        name="Billboard - HTML5",
        type=Type.display,
        category=Category.standard,
        is_standard=True,
        description="970x250 HTML5 creative",
        accepts_3p_tags=True,
        supported_macros=COMMON_MACROS,
        requirements={
            "dimensions": "970x250",
        },
        assets_required=[
            AssetsRequired(
                asset_id="html_creative",
                asset_type=AssetType.html,
                asset_role="html_creative",
                required=True,
                requirements={
                    "width": 970,
                    "height": 250,
                    "max_file_size_mb": 0.5,
                },
            ),
        ],
    ),
]

# Native Formats
NATIVE_FORMATS = [
    CreativeFormat(
        format_id="native_standard",
        agent_url=AGENT_URL,
        name="IAB Native Standard",
        type=Type.native,
        category=Category.standard,
        is_standard=True,
        description="Standard native ad with title, description, image, and CTA",
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetsRequired(
                asset_id="title",
                asset_type=AssetType.text,
                asset_role="title",
                required=True,
                requirements={
                    "description": "Headline text (25 chars recommended)",
                },
            ),
            AssetsRequired(
                asset_id="description",
                asset_type=AssetType.text,
                asset_role="description",
                required=True,
                requirements={
                    "description": "Body copy (90 chars recommended)",
                },
            ),
            AssetsRequired(
                asset_id="main_image",
                asset_type=AssetType.image,
                asset_role="main_image",
                required=True,
                requirements={
                    "description": "Primary image (1200x627 recommended)",
                },
            ),
            AssetsRequired(
                asset_id="icon",
                asset_type=AssetType.image,
                asset_role="icon",
                required=False,
                requirements={
                    "description": "Brand icon (square, 200x200 recommended)",
                },
            ),
            AssetsRequired(
                asset_id="cta_text",
                asset_type=AssetType.text,
                asset_role="cta_text",
                required=True,
                requirements={
                    "description": "Call-to-action text",
                },
            ),
            AssetsRequired(
                asset_id="sponsored_by",
                asset_type=AssetType.text,
                asset_role="sponsored_by",
                required=True,
                requirements={
                    "description": "Advertiser name for disclosure",
                },
            ),
        ],
    ),
    CreativeFormat(
        format_id="native_content",
        agent_url=AGENT_URL,
        name="Native Content Placement",
        type=Type.native,
        category=Category.standard,
        is_standard=True,
        description="In-article native ad with editorial styling",
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetsRequired(
                asset_id="headline",
                asset_type=AssetType.text,
                asset_role="headline",
                required=True,
                requirements={
                    "description": "Editorial-style headline (60 chars recommended)",
                },
            ),
            AssetsRequired(
                asset_id="body",
                asset_type=AssetType.text,
                asset_role="body",
                required=True,
                requirements={
                    "description": "Article-style body copy (200 chars recommended)",
                },
            ),
            AssetsRequired(
                asset_id="thumbnail",
                asset_type=AssetType.image,
                asset_role="thumbnail",
                required=True,
                requirements={
                    "description": "Thumbnail image (square, 300x300 recommended)",
                },
            ),
            AssetsRequired(
                asset_id="author",
                asset_type=AssetType.text,
                asset_role="author",
                required=False,
                requirements={
                    "description": "Author name for editorial context",
                },
            ),
            AssetsRequired(
                asset_id="click_url",
                asset_type=AssetType.url,
                asset_role="click_url",
                required=True,
                requirements={
                    "description": "Landing page URL",
                },
            ),
            AssetsRequired(
                asset_id="disclosure",
                asset_type=AssetType.text,
                asset_role="disclosure",
                required=True,
                requirements={
                    "description": "Sponsored content disclosure text",
                },
            ),
        ],
    ),
]

# Audio Formats
AUDIO_FORMATS = [
    CreativeFormat(
        format_id="audio_standard_15s",
        agent_url=AGENT_URL,
        name="Standard Audio - 15 seconds",
        type=Type.audio,
        category=Category.standard,
        is_standard=True,
        description="15-second audio ad",
        accepts_3p_tags=True,
        supported_macros=[*COMMON_MACROS, "CONTENT_GENRE"],
        requirements={
            "duration_seconds": 15,
            "max_file_size_mb": 0.75,
            "acceptable_formats": ["mp3", "aac", "m4a"],
        },
        assets_required=[
            AssetsRequired(
                asset_id="audio_file",
                asset_type=AssetType.audio,
                asset_role="audio_file",
                required=True,
                requirements={
                    "duration_seconds": 15,
                    "acceptable_formats": ["mp3", "aac", "m4a"],
                },
            ),
        ],
    ),
    CreativeFormat(
        format_id="audio_standard_30s",
        agent_url=AGENT_URL,
        name="Standard Audio - 30 seconds",
        type=Type.audio,
        category=Category.standard,
        is_standard=True,
        description="30-second audio ad",
        accepts_3p_tags=True,
        supported_macros=[*COMMON_MACROS, "CONTENT_GENRE"],
        requirements={
            "duration_seconds": 30,
            "max_file_size_mb": 1.5,
            "acceptable_formats": ["mp3", "aac", "m4a"],
        },
        assets_required=[
            AssetsRequired(
                asset_id="audio_file",
                asset_type=AssetType.audio,
                asset_role="audio_file",
                required=True,
                requirements={
                    "duration_seconds": 30,
                    "acceptable_formats": ["mp3", "aac", "m4a"],
                },
            ),
        ],
    ),
    CreativeFormat(
        format_id="audio_standard_60s",
        agent_url=AGENT_URL,
        name="Standard Audio - 60 seconds",
        type=Type.audio,
        category=Category.standard,
        is_standard=True,
        description="60-second audio ad",
        accepts_3p_tags=True,
        supported_macros=[*COMMON_MACROS, "CONTENT_GENRE"],
        requirements={
            "duration_seconds": 60,
            "max_file_size_mb": 3,
            "acceptable_formats": ["mp3", "aac", "m4a"],
        },
        assets_required=[
            AssetsRequired(
                asset_id="audio_file",
                asset_type=AssetType.audio,
                asset_role="audio_file",
                required=True,
                requirements={
                    "duration_seconds": 60,
                    "acceptable_formats": ["mp3", "aac", "m4a"],
                },
            ),
        ],
    ),
]

# DOOH Formats
DOOH_FORMATS = [
    CreativeFormat(
        format_id="dooh_billboard_1920x1080",
        agent_url=AGENT_URL,
        name="Digital Billboard - 1920x1080",
        type=Type.dooh,
        category=Category.standard,
        is_standard=True,
        description="Full HD digital billboard",
        accepts_3p_tags=False,
        supported_macros=[*COMMON_MACROS, "SCREEN_ID", "VENUE_TYPE", "VENUE_LAT", "VENUE_LONG"],
        requirements={
            "dimensions": "1920x1080",
            "duration_seconds": 10,
            "max_file_size_mb": 5,
        },
        assets_required=[
            AssetsRequired(
                asset_id="billboard_image",
                asset_type=AssetType.image,
                asset_role="billboard_image",
                required=True,
                requirements={
                    "width": 1920,
                    "height": 1080,
                    "acceptable_formats": ["jpg", "png"],
                },
            ),
        ],
    ),
    CreativeFormat(
        format_id="dooh_billboard_landscape",
        agent_url=AGENT_URL,
        name="Digital Billboard - Landscape",
        type=Type.dooh,
        category=Category.standard,
        is_standard=True,
        description="Landscape-oriented digital billboard (various sizes)",
        accepts_3p_tags=False,
        supported_macros=[*COMMON_MACROS, "SCREEN_ID", "VENUE_TYPE", "VENUE_LAT", "VENUE_LONG"],
        requirements={
            "duration_seconds": 10,
            "max_file_size_mb": 10,
            "aspect_ratios": ["16:9", "21:9"],
        },
        assets_required=[
            AssetsRequired(
                asset_id="billboard_image",
                asset_type=AssetType.image,
                asset_role="billboard_image",
                required=True,
                requirements={
                    "acceptable_formats": ["jpg", "png"],
                    "description": "Landscape image (1920x1080 or larger)",
                },
            ),
        ],
    ),
    CreativeFormat(
        format_id="dooh_billboard_portrait",
        agent_url=AGENT_URL,
        name="Digital Billboard - Portrait",
        type=Type.dooh,
        category=Category.standard,
        is_standard=True,
        description="Portrait-oriented digital billboard (various sizes)",
        accepts_3p_tags=False,
        supported_macros=[*COMMON_MACROS, "SCREEN_ID", "VENUE_TYPE", "VENUE_LAT", "VENUE_LONG"],
        requirements={
            "duration_seconds": 10,
            "max_file_size_mb": 10,
            "aspect_ratios": ["9:16"],
        },
        assets_required=[
            AssetsRequired(
                asset_id="billboard_image",
                asset_type=AssetType.image,
                asset_role="billboard_image",
                required=True,
                requirements={
                    "acceptable_formats": ["jpg", "png"],
                    "description": "Portrait image (1080x1920 or similar)",
                },
            ),
        ],
    ),
    CreativeFormat(
        format_id="dooh_transit_screen",
        agent_url=AGENT_URL,
        name="Transit Screen",
        type=Type.dooh,
        category=Category.standard,
        is_standard=True,
        description="Transit and subway screen displays",
        accepts_3p_tags=False,
        supported_macros=[*COMMON_MACROS, "SCREEN_ID", "VENUE_TYPE", "VENUE_LAT", "VENUE_LONG", "TRANSIT_LINE"],
        requirements={
            "dimensions": "1920x1080",
            "duration_seconds": 15,
            "max_file_size_mb": 5,
        },
        assets_required=[
            AssetsRequired(
                asset_id="screen_image",
                asset_type=AssetType.image,
                asset_role="screen_image",
                required=True,
                requirements={
                    "width": 1920,
                    "height": 1080,
                    "acceptable_formats": ["jpg", "png"],
                    "description": "Transit screen content",
                },
            ),
        ],
    ),
]

# Combine all formats
STANDARD_FORMATS = (
    GENERATIVE_FORMATS
    + VIDEO_FORMATS
    + DISPLAY_IMAGE_FORMATS
    + DISPLAY_HTML_FORMATS
    + NATIVE_FORMATS
    + AUDIO_FORMATS
    + DOOH_FORMATS
)


def get_format_by_id(format_id: str) -> CreativeFormat | None:
    """Get format by ID."""
    for fmt in STANDARD_FORMATS:
        if fmt.format_id == format_id:
            return fmt
    return None


def filter_formats(
    format_ids: list[str] | None = None,
    type: Type | str | None = None,
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
        results = [fmt for fmt in results if fmt.format_id in format_ids]

    if type:
        # Handle both Type enum and string values
        if isinstance(type, str):
            results = [fmt for fmt in results if fmt.type.value == type]
        else:
            results = [fmt for fmt in results if fmt.type == type]

    if dimensions:
        results = [fmt for fmt in results if fmt.requirements and fmt.requirements.get("dimensions") == dimensions]

    # Dimension filtering - parse width and height from "WIDTHxHEIGHT" format
    if any([max_width, max_height, min_width, min_height]):

        def get_dimensions(fmt: CreativeFormat) -> tuple[int | None, int | None]:
            """Extract width and height from format."""
            if fmt.requirements and "dimensions" in fmt.requirements:
                dims = fmt.requirements["dimensions"]
                if isinstance(dims, str) and "x" in dims:
                    parts = dims.split("x")
                    if len(parts) == 2:
                        try:
                            return int(parts[0]), int(parts[1])
                        except ValueError:
                            pass
            return None, None

        filtered = []
        for fmt in results:
            width, height = get_dimensions(fmt)
            if width is None or height is None:
                continue  # Skip formats without dimensions

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
        # Filter for responsive formats (those without fixed dimensions)
        if is_responsive:
            results = [
                fmt
                for fmt in results
                if not (fmt.requirements and "dimensions" in fmt.requirements and fmt.requirements["dimensions"])
            ]
        else:
            # Filter for non-responsive (fixed dimension) formats
            results = [
                fmt
                for fmt in results
                if fmt.requirements and "dimensions" in fmt.requirements and fmt.requirements["dimensions"]
            ]

    if name_search:
        search_lower = name_search.lower()
        results = [fmt for fmt in results if search_lower in fmt.name.lower()]

    if asset_types:
        # Filter to formats that include ALL specified asset types
        def has_asset_type(req: AssetsRequired | object, target_type: AssetType | str) -> bool:
            """Check if a requirement has the target asset type."""
            if isinstance(req, AssetsRequired):
                if isinstance(target_type, AssetType):
                    return req.asset_type == target_type
                return req.asset_type.value == target_type
            # AssetsRequired1 - check assets within the group
            if hasattr(req, "assets"):
                for asset in req.assets:
                    if isinstance(target_type, AssetType):
                        if asset.asset_type == target_type:
                            return True
                    elif asset.asset_type.value == target_type:
                        return True
            return False

        results = [
            fmt
            for fmt in results
            if fmt.assets_required
            and all(any(has_asset_type(req, asset_type) for req in fmt.assets_required) for asset_type in asset_types)
        ]

    return results
