"""Standard AdCP creative formats."""

from ..schemas.format import AssetRequirement, CreativeFormat, FormatRequirements

# Agent configuration
AGENT_URL = "https://creative.adcontextprotocol.org"
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
GENERATIVE_FORMATS = [
    CreativeFormat(
        format_id="display_300x250_generative",
        agent_url=AGENT_URL,
        name="Medium Rectangle - AI Generated",
        type="universal",
        category="custom",
        is_standard=False,
        description="AI-generated 300x250 banner from brand context and prompt",
        dimensions="300x250",
        output_format_ids=["display_300x250_image"],
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetRequirement(
                asset_id="brand_context",
                asset_role="brand_context",
                asset_type="brand_manifest",
                required=True,
                description="Brand information and product offerings for AI generation",
            ),
            AssetRequirement(
                asset_id="generation_prompt",
                asset_role="generation_prompt",
                asset_type="text",
                required=True,
                description="Text prompt describing the desired creative",
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_728x90_generative",
        agent_url=AGENT_URL,
        name="Leaderboard - AI Generated",
        type="universal",
        category="custom",
        is_standard=False,
        description="AI-generated 728x90 banner from brand context and prompt",
        dimensions="728x90",
        output_format_ids=["display_728x90_image"],
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetRequirement(
                asset_id="brand_context",
                asset_role="brand_context",
                asset_type="brand_manifest",
                required=True,
                description="Brand information and product offerings for AI generation",
            ),
            AssetRequirement(
                asset_id="generation_prompt",
                asset_role="generation_prompt",
                asset_type="text",
                required=True,
                description="Text prompt describing the desired creative",
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_320x50_generative",
        agent_url=AGENT_URL,
        name="Mobile Banner - AI Generated",
        type="universal",
        category="custom",
        is_standard=False,
        description="AI-generated 320x50 mobile banner from brand context and prompt",
        dimensions="320x50",
        output_format_ids=["display_320x50_image"],
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetRequirement(
                asset_id="brand_context",
                asset_role="brand_context",
                asset_type="brand_manifest",
                required=True,
                description="Brand information and product offerings for AI generation",
            ),
            AssetRequirement(
                asset_id="generation_prompt",
                asset_role="generation_prompt",
                asset_type="text",
                required=True,
                description="Text prompt describing the desired creative",
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_160x600_generative",
        agent_url=AGENT_URL,
        name="Wide Skyscraper - AI Generated",
        type="universal",
        category="custom",
        is_standard=False,
        description="AI-generated 160x600 wide skyscraper from brand context and prompt",
        dimensions="160x600",
        output_format_ids=["display_160x600_image"],
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetRequirement(
                asset_id="brand_context",
                asset_role="brand_context",
                asset_type="brand_manifest",
                required=True,
                description="Brand information and product offerings for AI generation",
            ),
            AssetRequirement(
                asset_id="generation_prompt",
                asset_role="generation_prompt",
                asset_type="text",
                required=True,
                description="Text prompt describing the desired creative",
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_336x280_generative",
        agent_url=AGENT_URL,
        name="Large Rectangle - AI Generated",
        type="universal",
        category="custom",
        is_standard=False,
        description="AI-generated 336x280 large rectangle from brand context and prompt",
        dimensions="336x280",
        output_format_ids=["display_336x280_image"],
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetRequirement(
                asset_id="brand_context",
                asset_role="brand_context",
                asset_type="brand_manifest",
                required=True,
                description="Brand information and product offerings for AI generation",
            ),
            AssetRequirement(
                asset_id="generation_prompt",
                asset_role="generation_prompt",
                asset_type="text",
                required=True,
                description="Text prompt describing the desired creative",
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_300x600_generative",
        agent_url=AGENT_URL,
        name="Half Page - AI Generated",
        type="universal",
        category="custom",
        is_standard=False,
        description="AI-generated 300x600 half page from brand context and prompt",
        dimensions="300x600",
        output_format_ids=["display_300x600_image"],
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetRequirement(
                asset_id="brand_context",
                asset_role="brand_context",
                asset_type="brand_manifest",
                required=True,
                description="Brand information and product offerings for AI generation",
            ),
            AssetRequirement(
                asset_id="generation_prompt",
                asset_role="generation_prompt",
                asset_type="text",
                required=True,
                description="Text prompt describing the desired creative",
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_970x250_generative",
        agent_url=AGENT_URL,
        name="Billboard - AI Generated",
        type="universal",
        category="custom",
        is_standard=False,
        description="AI-generated 970x250 billboard from brand context and prompt",
        dimensions="970x250",
        output_format_ids=["display_970x250_image"],
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetRequirement(
                asset_id="brand_context",
                asset_role="brand_context",
                asset_type="brand_manifest",
                required=True,
                description="Brand information and product offerings for AI generation",
            ),
            AssetRequirement(
                asset_id="generation_prompt",
                asset_role="generation_prompt",
                asset_type="text",
                required=True,
                description="Text prompt describing the desired creative",
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
        type="video",
        category="standard",
        is_standard=True,
        description="30-second video ad in standard aspect ratios",
        iab_specification="https://iabtechlab.com/standards/video-ad-serving-template-vast/",
        accepts_3p_tags=True,
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        requirements=FormatRequirements(
            duration_seconds=30,
            max_file_size_mb=50,
            acceptable_formats=["mp4", "mov", "webm"],
            aspect_ratios=["16:9", "9:16", "1:1", "4:5"],
        ),
        assets_required=[
            AssetRequirement(
                asset_id="video_file",
                asset_role="video_file",
                asset_type="video",
                required=True,
                duration_seconds=30,
                acceptable_formats=["mp4", "mov", "webm"],
                description="30-second video file",
            ),
        ],
    ),
    CreativeFormat(
        format_id="video_standard_15s",
        agent_url=AGENT_URL,
        name="Standard Video - 15 seconds",
        type="video",
        category="standard",
        is_standard=True,
        description="15-second video ad in standard aspect ratios",
        iab_specification="https://iabtechlab.com/standards/video-ad-serving-template-vast/",
        accepts_3p_tags=True,
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        requirements=FormatRequirements(
            duration_seconds=15,
            max_file_size_mb=25,
            acceptable_formats=["mp4", "mov", "webm"],
            aspect_ratios=["16:9", "9:16", "1:1", "4:5"],
        ),
        assets_required=[
            AssetRequirement(
                asset_id="video_file",
                asset_role="video_file",
                asset_type="video",
                required=True,
                duration_seconds=15,
                acceptable_formats=["mp4", "mov", "webm"],
            ),
        ],
    ),
    CreativeFormat(
        format_id="video_vast_30s",
        agent_url=AGENT_URL,
        name="VAST Video - 30 seconds",
        type="video",
        category="standard",
        is_standard=True,
        description="30-second video ad via VAST tag",
        iab_specification="https://iabtechlab.com/standards/video-ad-serving-template-vast/",
        accepts_3p_tags=True,
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        requirements=FormatRequirements(
            duration_seconds=30,
        ),
        assets_required=[
            AssetRequirement(
                asset_id="vast_tag",
                asset_role="vast_tag",
                asset_type="html",  # VAST tags are XML/HTML
                required=True,
                description="VAST 4.x compatible tag",
            ),
        ],
    ),
    CreativeFormat(
        format_id="video_1920x1080",
        agent_url=AGENT_URL,
        name="Full HD Video - 1920x1080",
        type="video",
        category="standard",
        is_standard=True,
        description="1920x1080 Full HD video (16:9)",
        dimensions="1920x1080",
        iab_specification="https://iabtechlab.com/standards/video-ad-serving-template-vast/",
        accepts_3p_tags=False,
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        requirements=FormatRequirements(
            max_file_size_mb=100,
            acceptable_formats=["mp4", "mov", "webm"],
            aspect_ratios=["16:9"],
        ),
        assets_required=[
            AssetRequirement(
                asset_id="video_file",
                asset_role="video_file",
                asset_type="video",
                required=True,
                width=1920,
                height=1080,
                acceptable_formats=["mp4", "mov", "webm"],
                description="1920x1080 video file",
            ),
        ],
    ),
    CreativeFormat(
        format_id="video_1280x720",
        agent_url=AGENT_URL,
        name="HD Video - 1280x720",
        type="video",
        category="standard",
        is_standard=True,
        description="1280x720 HD video (16:9)",
        dimensions="1280x720",
        iab_specification="https://iabtechlab.com/standards/video-ad-serving-template-vast/",
        accepts_3p_tags=False,
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        requirements=FormatRequirements(
            max_file_size_mb=75,
            acceptable_formats=["mp4", "mov", "webm"],
            aspect_ratios=["16:9"],
        ),
        assets_required=[
            AssetRequirement(
                asset_id="video_file",
                asset_role="video_file",
                asset_type="video",
                required=True,
                width=1280,
                height=720,
                acceptable_formats=["mp4", "mov", "webm"],
                description="1280x720 video file",
            ),
        ],
    ),
    CreativeFormat(
        format_id="video_1080x1920",
        agent_url=AGENT_URL,
        name="Vertical Video - 1080x1920",
        type="video",
        category="standard",
        is_standard=True,
        description="1080x1920 vertical video (9:16) for mobile stories",
        dimensions="1080x1920",
        iab_specification="https://iabtechlab.com/standards/video-ad-serving-template-vast/",
        accepts_3p_tags=False,
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        requirements=FormatRequirements(
            max_file_size_mb=100,
            acceptable_formats=["mp4", "mov", "webm"],
            aspect_ratios=["9:16"],
        ),
        assets_required=[
            AssetRequirement(
                asset_id="video_file",
                asset_role="video_file",
                asset_type="video",
                required=True,
                width=1080,
                height=1920,
                acceptable_formats=["mp4", "mov", "webm"],
                description="1080x1920 vertical video file",
            ),
        ],
    ),
    CreativeFormat(
        format_id="video_1080x1080",
        agent_url=AGENT_URL,
        name="Square Video - 1080x1080",
        type="video",
        category="standard",
        is_standard=True,
        description="1080x1080 square video (1:1) for social feeds",
        dimensions="1080x1080",
        iab_specification="https://iabtechlab.com/standards/video-ad-serving-template-vast/",
        accepts_3p_tags=False,
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"],
        requirements=FormatRequirements(
            max_file_size_mb=100,
            acceptable_formats=["mp4", "mov", "webm"],
            aspect_ratios=["1:1"],
        ),
        assets_required=[
            AssetRequirement(
                asset_id="video_file",
                asset_role="video_file",
                asset_type="video",
                required=True,
                width=1080,
                height=1080,
                acceptable_formats=["mp4", "mov", "webm"],
                description="1080x1080 square video file",
            ),
        ],
    ),
    CreativeFormat(
        format_id="video_ctv_preroll_30s",
        agent_url=AGENT_URL,
        name="CTV Pre-Roll - 30 seconds",
        type="video",
        category="standard",
        is_standard=True,
        description="30-second pre-roll ad for Connected TV and streaming platforms",
        iab_specification="https://iabtechlab.com/standards/video-ad-serving-template-vast/",
        accepts_3p_tags=True,
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE", "PLAYER_SIZE"],
        requirements=FormatRequirements(
            duration_seconds=30,
            max_file_size_mb=75,
            acceptable_formats=["mp4", "mov"],
            aspect_ratios=["16:9"],
        ),
        assets_required=[
            AssetRequirement(
                asset_id="video_file",
                asset_role="video_file",
                asset_type="video",
                required=True,
                duration_seconds=30,
                acceptable_formats=["mp4", "mov"],
                description="30-second CTV-optimized video file (1920x1080 recommended)",
            ),
        ],
    ),
    CreativeFormat(
        format_id="video_ctv_midroll_30s",
        agent_url=AGENT_URL,
        name="CTV Mid-Roll - 30 seconds",
        type="video",
        category="standard",
        is_standard=True,
        description="30-second mid-roll ad for Connected TV and streaming platforms",
        iab_specification="https://iabtechlab.com/standards/video-ad-serving-template-vast/",
        accepts_3p_tags=True,
        supported_macros=[*COMMON_MACROS, "VIDEO_ID", "POD_POSITION", "CONTENT_GENRE", "PLAYER_SIZE"],
        requirements=FormatRequirements(
            duration_seconds=30,
            max_file_size_mb=75,
            acceptable_formats=["mp4", "mov"],
            aspect_ratios=["16:9"],
        ),
        assets_required=[
            AssetRequirement(
                asset_id="video_file",
                asset_role="video_file",
                asset_type="video",
                required=True,
                duration_seconds=30,
                acceptable_formats=["mp4", "mov"],
                description="30-second CTV-optimized video file (1920x1080 recommended)",
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
        type="display",
        category="standard",
        is_standard=True,
        description="300x250 static image banner",
        dimensions="300x250",
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetRequirement(
                asset_id="banner_image",
                asset_role="banner_image",
                asset_type="image",
                required=True,
                width=300,
                height=250,
                max_file_size_mb=0.2,  # 200kb
                acceptable_formats=["jpg", "png", "gif", "webp"],
            ),
            AssetRequirement(
                asset_id="click_url",
                asset_role="click_url",
                asset_type="url",
                required=True,
                description="Clickthrough destination URL",
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_728x90_image",
        agent_url=AGENT_URL,
        name="Leaderboard - Image",
        type="display",
        category="standard",
        is_standard=True,
        description="728x90 static image banner",
        dimensions="728x90",
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetRequirement(
                asset_id="banner_image",
                asset_role="banner_image",
                asset_type="image",
                required=True,
                width=728,
                height=90,
                max_file_size_mb=0.15,
                acceptable_formats=["jpg", "png", "gif", "webp"],
            ),
            AssetRequirement(
                asset_id="click_url",
                asset_role="click_url",
                asset_type="url",
                required=True,
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_320x50_image",
        agent_url=AGENT_URL,
        name="Mobile Banner - Image",
        type="display",
        category="standard",
        is_standard=True,
        description="320x50 mobile banner",
        dimensions="320x50",
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetRequirement(
                asset_id="banner_image",
                asset_role="banner_image",
                asset_type="image",
                required=True,
                width=320,
                height=50,
                max_file_size_mb=0.05,
                acceptable_formats=["jpg", "png", "gif", "webp"],
            ),
            AssetRequirement(
                asset_id="click_url",
                asset_role="click_url",
                asset_type="url",
                required=True,
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_160x600_image",
        agent_url=AGENT_URL,
        name="Wide Skyscraper - Image",
        type="display",
        category="standard",
        is_standard=True,
        description="160x600 wide skyscraper banner",
        dimensions="160x600",
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetRequirement(
                asset_id="banner_image",
                asset_role="banner_image",
                asset_type="image",
                required=True,
                width=160,
                height=600,
                max_file_size_mb=0.15,
                acceptable_formats=["jpg", "png", "gif", "webp"],
            ),
            AssetRequirement(
                asset_id="click_url",
                asset_role="click_url",
                asset_type="url",
                required=True,
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_336x280_image",
        agent_url=AGENT_URL,
        name="Large Rectangle - Image",
        type="display",
        category="standard",
        is_standard=True,
        description="336x280 large rectangle banner",
        dimensions="336x280",
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetRequirement(
                asset_id="banner_image",
                asset_role="banner_image",
                asset_type="image",
                required=True,
                width=336,
                height=280,
                max_file_size_mb=0.25,
                acceptable_formats=["jpg", "png", "gif", "webp"],
            ),
            AssetRequirement(
                asset_id="click_url",
                asset_role="click_url",
                asset_type="url",
                required=True,
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_300x600_image",
        agent_url=AGENT_URL,
        name="Half Page - Image",
        type="display",
        category="standard",
        is_standard=True,
        description="300x600 half page banner",
        dimensions="300x600",
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetRequirement(
                asset_id="banner_image",
                asset_role="banner_image",
                asset_type="image",
                required=True,
                width=300,
                height=600,
                max_file_size_mb=0.3,
                acceptable_formats=["jpg", "png", "gif", "webp"],
            ),
            AssetRequirement(
                asset_id="click_url",
                asset_role="click_url",
                asset_type="url",
                required=True,
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_970x250_image",
        agent_url=AGENT_URL,
        name="Billboard - Image",
        type="display",
        category="standard",
        is_standard=True,
        description="970x250 billboard banner",
        dimensions="970x250",
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetRequirement(
                asset_id="banner_image",
                asset_role="banner_image",
                asset_type="image",
                required=True,
                width=970,
                height=250,
                max_file_size_mb=0.4,
                acceptable_formats=["jpg", "png", "gif", "webp"],
            ),
            AssetRequirement(
                asset_id="click_url",
                asset_role="click_url",
                asset_type="url",
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
        type="display",
        category="standard",
        is_standard=True,
        description="300x250 HTML5 creative",
        dimensions="300x250",
        accepts_3p_tags=True,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetRequirement(
                asset_id="html_creative",
                asset_role="html_creative",
                asset_type="html",
                required=True,
                width=300,
                height=250,
                max_file_size_mb=0.5,
                description="HTML5 creative code",
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_728x90_html",
        agent_url=AGENT_URL,
        name="Leaderboard - HTML5",
        type="display",
        category="standard",
        is_standard=True,
        description="728x90 HTML5 creative",
        dimensions="728x90",
        accepts_3p_tags=True,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetRequirement(
                asset_id="html_creative",
                asset_role="html_creative",
                asset_type="html",
                required=True,
                width=728,
                height=90,
                max_file_size_mb=0.5,
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_160x600_html",
        agent_url=AGENT_URL,
        name="Wide Skyscraper - HTML5",
        type="display",
        category="standard",
        is_standard=True,
        description="160x600 HTML5 creative",
        dimensions="160x600",
        accepts_3p_tags=True,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetRequirement(
                asset_id="html_creative",
                asset_role="html_creative",
                asset_type="html",
                required=True,
                width=160,
                height=600,
                max_file_size_mb=0.5,
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_336x280_html",
        agent_url=AGENT_URL,
        name="Large Rectangle - HTML5",
        type="display",
        category="standard",
        is_standard=True,
        description="336x280 HTML5 creative",
        dimensions="336x280",
        accepts_3p_tags=True,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetRequirement(
                asset_id="html_creative",
                asset_role="html_creative",
                asset_type="html",
                required=True,
                width=336,
                height=280,
                max_file_size_mb=0.5,
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_300x600_html",
        agent_url=AGENT_URL,
        name="Half Page - HTML5",
        type="display",
        category="standard",
        is_standard=True,
        description="300x600 HTML5 creative",
        dimensions="300x600",
        accepts_3p_tags=True,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetRequirement(
                asset_id="html_creative",
                asset_role="html_creative",
                asset_type="html",
                required=True,
                width=300,
                height=600,
                max_file_size_mb=0.5,
            ),
        ],
    ),
    CreativeFormat(
        format_id="display_970x250_html",
        agent_url=AGENT_URL,
        name="Billboard - HTML5",
        type="display",
        category="standard",
        is_standard=True,
        description="970x250 HTML5 creative",
        dimensions="970x250",
        accepts_3p_tags=True,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetRequirement(
                asset_id="html_creative",
                asset_role="html_creative",
                asset_type="html",
                required=True,
                width=970,
                height=250,
                max_file_size_mb=0.5,
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
        type="native",
        category="standard",
        is_standard=True,
        description="Standard native ad with title, description, image, and CTA",
        iab_specification="https://iabtechlab.com/standards/openrtb-native/",
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetRequirement(
                asset_id="title",
                asset_role="title",
                asset_type="text",
                required=True,
                description="Headline text (25 chars recommended)",
            ),
            AssetRequirement(
                asset_id="description",
                asset_role="description",
                asset_type="text",
                required=True,
                description="Body copy (90 chars recommended)",
            ),
            AssetRequirement(
                asset_id="main_image",
                asset_role="main_image",
                asset_type="image",
                required=True,
                description="Primary image (1200x627 recommended)",
            ),
            AssetRequirement(
                asset_id="icon",
                asset_role="icon",
                asset_type="image",
                required=False,
                description="Brand icon (square, 200x200 recommended)",
            ),
            AssetRequirement(
                asset_id="cta_text",
                asset_role="cta_text",
                asset_type="text",
                required=True,
                description="Call-to-action text",
            ),
            AssetRequirement(
                asset_id="sponsored_by",
                asset_role="sponsored_by",
                asset_type="text",
                required=True,
                description="Advertiser name for disclosure",
            ),
        ],
    ),
    CreativeFormat(
        format_id="native_content",
        agent_url=AGENT_URL,
        name="Native Content Placement",
        type="native",
        category="standard",
        is_standard=True,
        description="In-article native ad with editorial styling",
        iab_specification="https://iabtechlab.com/standards/openrtb-native/",
        accepts_3p_tags=False,
        supported_macros=COMMON_MACROS,
        assets_required=[
            AssetRequirement(
                asset_id="headline",
                asset_role="headline",
                asset_type="text",
                required=True,
                description="Editorial-style headline (60 chars recommended)",
            ),
            AssetRequirement(
                asset_id="body",
                asset_role="body",
                asset_type="text",
                required=True,
                description="Article-style body copy (200 chars recommended)",
            ),
            AssetRequirement(
                asset_id="thumbnail",
                asset_role="thumbnail",
                asset_type="image",
                required=True,
                description="Thumbnail image (square, 300x300 recommended)",
            ),
            AssetRequirement(
                asset_id="author",
                asset_role="author",
                asset_type="text",
                required=False,
                description="Author name for editorial context",
            ),
            AssetRequirement(
                asset_id="click_url",
                asset_role="click_url",
                asset_type="url",
                required=True,
                description="Landing page URL",
            ),
            AssetRequirement(
                asset_id="disclosure",
                asset_role="disclosure",
                asset_type="text",
                required=True,
                description="Sponsored content disclosure text",
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
        type="audio",
        category="standard",
        is_standard=True,
        description="15-second audio ad",
        accepts_3p_tags=True,
        supported_macros=[*COMMON_MACROS, "CONTENT_GENRE"],
        requirements=FormatRequirements(
            duration_seconds=15,
            max_file_size_mb=0.75,
            acceptable_formats=["mp3", "aac", "m4a"],
        ),
        assets_required=[
            AssetRequirement(
                asset_id="audio_file",
                asset_role="audio_file",
                asset_type="audio",
                required=True,
                duration_seconds=15,
                acceptable_formats=["mp3", "aac", "m4a"],
            ),
        ],
    ),
    CreativeFormat(
        format_id="audio_standard_30s",
        agent_url=AGENT_URL,
        name="Standard Audio - 30 seconds",
        type="audio",
        category="standard",
        is_standard=True,
        description="30-second audio ad",
        accepts_3p_tags=True,
        supported_macros=[*COMMON_MACROS, "CONTENT_GENRE"],
        requirements=FormatRequirements(
            duration_seconds=30,
            max_file_size_mb=1.5,
            acceptable_formats=["mp3", "aac", "m4a"],
        ),
        assets_required=[
            AssetRequirement(
                asset_id="audio_file",
                asset_role="audio_file",
                asset_type="audio",
                required=True,
                duration_seconds=30,
                acceptable_formats=["mp3", "aac", "m4a"],
            ),
        ],
    ),
    CreativeFormat(
        format_id="audio_standard_60s",
        agent_url=AGENT_URL,
        name="Standard Audio - 60 seconds",
        type="audio",
        category="standard",
        is_standard=True,
        description="60-second audio ad",
        accepts_3p_tags=True,
        supported_macros=[*COMMON_MACROS, "CONTENT_GENRE"],
        requirements=FormatRequirements(
            duration_seconds=60,
            max_file_size_mb=3,
            acceptable_formats=["mp3", "aac", "m4a"],
        ),
        assets_required=[
            AssetRequirement(
                asset_id="audio_file",
                asset_role="audio_file",
                asset_type="audio",
                required=True,
                duration_seconds=60,
                acceptable_formats=["mp3", "aac", "m4a"],
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
        type="dooh",
        category="standard",
        is_standard=True,
        description="Full HD digital billboard",
        dimensions="1920x1080",
        accepts_3p_tags=False,
        supported_macros=[*COMMON_MACROS, "SCREEN_ID", "VENUE_TYPE", "VENUE_LAT", "VENUE_LONG"],
        requirements=FormatRequirements(
            duration_seconds=10,  # Typical DOOH loop duration
            max_file_size_mb=5,
        ),
        assets_required=[
            AssetRequirement(
                asset_id="billboard_image",
                asset_role="billboard_image",
                asset_type="image",
                required=True,
                width=1920,
                height=1080,
                acceptable_formats=["jpg", "png"],
            ),
        ],
    ),
    CreativeFormat(
        format_id="dooh_billboard_landscape",
        agent_url=AGENT_URL,
        name="Digital Billboard - Landscape",
        type="dooh",
        category="standard",
        is_standard=True,
        description="Landscape-oriented digital billboard (various sizes)",
        accepts_3p_tags=False,
        supported_macros=[*COMMON_MACROS, "SCREEN_ID", "VENUE_TYPE", "VENUE_LAT", "VENUE_LONG"],
        requirements=FormatRequirements(
            duration_seconds=10,
            max_file_size_mb=10,
            aspect_ratios=["16:9", "21:9"],
        ),
        assets_required=[
            AssetRequirement(
                asset_id="billboard_image",
                asset_role="billboard_image",
                asset_type="image",
                required=True,
                acceptable_formats=["jpg", "png"],
                description="Landscape image (1920x1080 or larger)",
            ),
        ],
    ),
    CreativeFormat(
        format_id="dooh_billboard_portrait",
        agent_url=AGENT_URL,
        name="Digital Billboard - Portrait",
        type="dooh",
        category="standard",
        is_standard=True,
        description="Portrait-oriented digital billboard (various sizes)",
        accepts_3p_tags=False,
        supported_macros=[*COMMON_MACROS, "SCREEN_ID", "VENUE_TYPE", "VENUE_LAT", "VENUE_LONG"],
        requirements=FormatRequirements(
            duration_seconds=10,
            max_file_size_mb=10,
            aspect_ratios=["9:16"],
        ),
        assets_required=[
            AssetRequirement(
                asset_id="billboard_image",
                asset_role="billboard_image",
                asset_type="image",
                required=True,
                acceptable_formats=["jpg", "png"],
                description="Portrait image (1080x1920 or similar)",
            ),
        ],
    ),
    CreativeFormat(
        format_id="dooh_transit_screen",
        agent_url=AGENT_URL,
        name="Transit Screen",
        type="dooh",
        category="standard",
        is_standard=True,
        description="Transit and subway screen displays",
        dimensions="1920x1080",
        accepts_3p_tags=False,
        supported_macros=[*COMMON_MACROS, "SCREEN_ID", "VENUE_TYPE", "VENUE_LAT", "VENUE_LONG", "TRANSIT_LINE"],
        requirements=FormatRequirements(
            duration_seconds=15,  # Longer dwell time in transit
            max_file_size_mb=5,
        ),
        assets_required=[
            AssetRequirement(
                asset_id="screen_image",
                asset_role="screen_image",
                asset_type="image",
                required=True,
                width=1920,
                height=1080,
                acceptable_formats=["jpg", "png"],
                description="Transit screen content",
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
    type: str | None = None,
    asset_types: list[str] | None = None,
    dimensions: str | None = None,
    name_search: str | None = None,
) -> list[CreativeFormat]:
    """Filter formats based on criteria."""
    results = STANDARD_FORMATS

    if format_ids:
        results = [fmt for fmt in results if fmt.format_id in format_ids]

    if type:
        results = [fmt for fmt in results if fmt.type == type]

    if dimensions:
        results = [fmt for fmt in results if fmt.dimensions == dimensions]

    if name_search:
        search_lower = name_search.lower()
        results = [fmt for fmt in results if search_lower in fmt.name.lower()]

    if asset_types:
        # Filter to formats that include ALL specified asset types
        results = [
            fmt
            for fmt in results
            if all(any(req.asset_type == asset_type for req in fmt.assets_required) for asset_type in asset_types)
        ]

    return results
