# AdCP Creative Agent

A production-grade MCP server providing AdCP creative format specifications and preview generation capabilities. This agent serves as the authoritative source for standard IAB creative formats with built-in preview generation using Tigris storage.

## Overview

The AdCP Creative Agent is a stateless service that:
- Provides complete specifications for standard IAB creative formats (video, display, audio, native, DOOH)
- Generates live previews from creative manifests using AI (Gemini)
- Stores preview HTML in Tigris (Fly.io's S3-compatible global storage)
- Supports both local development (stdio) and production deployment (HTTP)

## Architecture

```
┌─────────────────────────────────────────────────┐
│  MCP Client (Claude, Agent, etc.)               │
└───────────────┬─────────────────────────────────┘
                │
                │ MCP Protocol (stdio or HTTP)
                │
┌───────────────▼─────────────────────────────────┐
│  AdCP Creative Agent                            │
│  ┌───────────────────────────────────────────┐  │
│  │ list_creative_formats                     │  │
│  │ - Returns all standard format specs       │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │ build_creative (AI-powered)               │  │
│  │ - Generates creative using Gemini API     │  │
│  │ - Uses brand assets + user message        │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │ preview_creative                          │  │
│  │ - Renders creative to HTML                │  │
│  │ - Uploads to Tigris storage               │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                │
                │ S3 API
                │
┌───────────────▼─────────────────────────────────┐
│  Tigris Global Object Storage                   │
│  - Public bucket: adcp-previews                 │
│  - Preview HTML files cached for 1 hour         │
│  - Public URLs: https://[bucket].fly.storage... │
└─────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- Fly.io account (for production deployment)

### Local Development

```bash
# Install dependencies
uv sync

# Run server locally (stdio mode for MCP)
uv run adcp-creative-agent

# Run smoke tests
uv run pytest tests/smoke/ -v -m smoke
```

### Testing with MCP Inspector

For interactive testing and development:

```bash
# Start FastMCP development server
uv run fastmcp dev src/creative_agent/server.py

# Opens web UI at http://localhost:8000
# - Test list_creative_formats
# - Test preview_creative with sample manifests
# - See real-time request/response JSON
```

### Connect to Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "adcp-creative-agent": {
      "command": "uv",
      "args": ["run", "adcp-creative-agent"],
      "cwd": "/absolute/path/to/creative-agent/.conductor/jackson-v1"
    }
  }
}
```

Restart Claude Desktop to load the server.

## Environment Variables

### Required for Production

```bash
# Tigris S3 Storage (automatically set by Fly.io)
AWS_ACCESS_KEY_ID=tid_xxxxx
AWS_SECRET_ACCESS_KEY=tsec_xxxxx
AWS_ENDPOINT_URL_S3=https://fly.storage.tigris.dev
BUCKET_NAME=adcp-previews
AWS_REGION=auto

# Production flag
PRODUCTION=true
PORT=8080
```

### Setting Secrets on Fly.io

```bash
# Tigris credentials (from fly storage create)
fly secrets set AWS_ACCESS_KEY_ID=tid_xxxxx
fly secrets set AWS_SECRET_ACCESS_KEY=tsec_xxxxx
fly secrets set AWS_ENDPOINT_URL_S3=https://fly.storage.tigris.dev
fly secrets set BUCKET_NAME=adcp-previews
```

## MCP Tools

### `list_creative_formats`

Returns all available AdCP creative format specifications.

**Response:** JSON array of AdCP `CreativeFormat` objects.

See the [AdCP Creative Formats specification](https://github.com/anthropics/adcp) for complete schema and field definitions.

### `build_creative`

Generate a creative using AI (Gemini) based on brand assets and a user message.

**Input:**
- `message` (string, required) - User's advertising message/goal
- `format_id` (string, required) - Target format ID from `list_creative_formats`
- `gemini_api_key` (string, required) - User's Gemini API key (we don't store or pay for API calls)
- `brand_card` (object, optional) - Brand information including colors, assets, guidelines

**Output:**
- `status` - "success" or "error"
- `creative_output` - Generated creative manifest ready for preview
- `context_id` - Unique identifier for this generation session

**Example Request:**
```json
{
  "message": "I want to advertise to tired dads with cats",
  "format_id": "display_300x250_image",
  "gemini_api_key": "AIzaSy...",
  "brand_card": {
    "name": "Kraft Mac & Cheese",
    "colors": ["#FFD700", "#FF6600"],
    "assets": [
      {"type": "logo", "url": "https://example.com/logo.png"}
    ]
  }
}
```

### `preview_creative`

Generate HTML previews from a creative manifest and upload to Tigris.

**Input:**
- `format_id` (string, required) - Format identifier
- `creative_manifest` (object, required) - Creative manifest with assets
- `inputs` (array, optional) - Preview variations with macro substitutions

**Output:**
- `preview_id` - Unique preview session ID
- `previews` - Array of preview objects with URLs
- `expires_at` - ISO timestamp when previews expire (24 hours)

**Example Request:**
```json
{
  "format_id": "display_300x250_image",
  "creative_manifest": {
    "format_id": "display_300x250_image",
    "assets": {
      "image": {
        "asset_type": "image",
        "url": "https://example.com/banner.jpg"
      },
      "click_url": {
        "asset_type": "url",
        "url": "https://example.com/landing"
      }
    }
  },
  "inputs": [
    {"name": "Desktop", "macros": {"DEVICE_TYPE": "desktop"}},
    {"name": "Mobile", "macros": {"DEVICE_TYPE": "mobile"}}
  ]
}
```

**Example Response:**
```json
{
  "preview_id": "550e8400-e29b-41d4-a716-446655440000",
  "previews": [
    {
      "input": {"name": "Desktop", "macros": {"DEVICE_TYPE": "desktop"}},
      "preview_url": "https://adcp-previews.fly.storage.tigris.dev/previews/550e8400.../Desktop.html",
      "hints": {
        "estimated_dimensions": {"width": 300, "height": 250},
        "primary_media_type": "image",
        "contains_audio": false,
        "contains_video": false
      }
    }
  ],
  "expires_at": "2025-10-12T13:00:00Z"
}
```

## Supported AdCP Formats

Use the `list_creative_formats` MCP tool to see all available formats with complete specifications.

The agent supports 38 AdCP-compliant formats across video, display, audio, native, DOOH, and generative categories. All formats include standard IAB macro support for privacy compliance (GDPR, CCPA, GPP), device info, and tracking.

## How to Add New Creative Format Templates

Creative formats are defined in `/src/creative_agent/data/standard_formats.py`. To add a new format:

### 1. Define the Format

Add a new `CreativeFormat` object to the appropriate format list (VIDEO_FORMATS, DISPLAY_FORMATS, etc.):

```python
CreativeFormat(
    format_id="display_300x600_image",  # Unique ID (use descriptive naming)
    agent_url=AGENT_URL,                 # Keep this as AGENT_URL
    name="Half Page - Image",            # Human-readable name
    type="display",                      # video|display|audio|native|dooh|interactive
    category="standard",                 # standard|custom
    is_standard=True,                    # True for IAB standard formats
    description="300x600 half-page display ad with static image",
    dimensions="300x600",                # Width x Height (if applicable)
    accepts_3p_tags=False,               # True if format accepts third-party tags
    supported_macros=COMMON_MACROS,      # Macro support (privacy, device, tracking)
    requirements=FormatRequirements(     # Optional technical requirements
        max_file_size_mb=1.0,
        acceptable_formats=["jpg", "png", "gif"],
    ),
    assets_required=[                    # List of required/optional assets
        AssetRequirement(
            asset_role="image",          # Unique identifier for this asset
            asset_type="image",          # image|video|audio|text|html|url|vast_tag
            required=True,               # Is this asset required?
            width=300,                   # Asset width (optional)
            height=600,                  # Asset height (optional)
            max_file_size_mb=1.0,       # Max file size (optional)
            acceptable_formats=["jpg", "png", "gif"],  # Acceptable formats
            description="Main display image for 300x600 half-page ad",
        ),
        AssetRequirement(
            asset_role="click_url",
            asset_type="url",
            required=True,
            description="Landing page URL for click-through",
        ),
    ],
)
```

### 2. Add to Format List

Ensure your format is added to the appropriate list:

```python
# At the bottom of standard_formats.py
STANDARD_FORMATS = (
    VIDEO_FORMATS
    + DISPLAY_FORMATS  # Your format should be in one of these
    + NATIVE_FORMATS
    + AUDIO_FORMATS
    + DOOH_FORMATS
)
```

### 3. Test Your Format

```bash
# Test that the format appears in list_creative_formats
uv run fastmcp dev src/creative_agent/server.py

# In the web UI, call list_creative_formats and search for your format_id
```

### 4. Asset Types Reference

- `image` - Static image (JPG, PNG, GIF, WebP)
- `video` - Video file (MP4, MOV, WebM)
- `audio` - Audio file (MP3, AAC, WAV)
- `text` - Text content (headline, body, CTA)
- `html` - HTML5 creative code
- `url` - URL string (click-through, landing page)
- `vast_tag` - VAST XML tag URL

### 5. Macro Support

Standard macros (included in `COMMON_MACROS`):
- Privacy: `GDPR`, `GDPR_CONSENT`, `US_PRIVACY`, `GPP_STRING`
- Tracking: `MEDIA_BUY_ID`, `CREATIVE_ID`, `IMPRESSION_URL`, `CLICK_URL`
- Device: `DEVICE_TYPE`, `OS`, `OS_VERSION`, `USER_AGENT`
- Context: `CACHEBUSTER`

Add custom macros for specific format needs:
```python
supported_macros=COMMON_MACROS + ["VIDEO_ID", "POD_POSITION", "CONTENT_GENRE"]
```

### 6. IAB Specification Links

For standard IAB formats, include specification URLs:
- Video: `https://iabtechlab.com/standards/video-ad-serving-template-vast/`
- Native: `https://iabtechlab.com/standards/openrtb-native/`
- Display: `https://iabtechlab.com/ad-experiences/display-ad-formats/`

## Deployment

### Initial Setup

```bash
# 1. Create Fly.io app
fly launch

# 2. Create public Tigris bucket
fly storage create --name adcp-previews --org personal --public -y

# 3. Set environment variables
fly secrets set AWS_ACCESS_KEY_ID=tid_xxxxx
fly secrets set AWS_SECRET_ACCESS_KEY=tsec_xxxxx
fly secrets set AWS_ENDPOINT_URL_S3=https://fly.storage.tigris.dev
fly secrets set BUCKET_NAME=adcp-previews
fly secrets set AWS_REGION=auto
```

### Deploy Updates

```bash
# Deploy to production
fly deploy

# Check logs
fly logs

# Check app status
fly status
```

### Health Checks

The server includes automatic health checks configured in `fly.toml`:
- TCP health checks every 30s
- 60s grace period for startup
- Auto-start/stop for cost optimization

## Development

### Project Structure

```
.
├── src/creative_agent/
│   ├── server.py              # Main MCP server (basic tools)
│   ├── server_v2.py           # Extended server with AI generation
│   ├── storage.py             # Tigris storage integration
│   ├── data/
│   │   ├── formats.py         # Format utilities
│   │   └── standard_formats.py # All format definitions
│   └── schemas/
│       ├── format.py          # Format data models
│       ├── manifest.py        # Creative manifest models
│       ├── assets.py          # Asset models
│       ├── preview.py         # Preview request/response models
│       └── build.py           # AI generation models
├── tests/
│   └── smoke/
│       └── test_server_startup.py
├── pyproject.toml             # Project dependencies
├── fly.toml                   # Fly.io deployment config
└── Dockerfile.fly             # Production container image
```

### Code Quality

```bash
# Run linter
uv run ruff check src/

# Run type checker
uv run mypy src/

# Run tests with coverage
uv run pytest --cov=src/creative_agent tests/
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run hooks manually
uv run pre-commit run --all-files
```

## Security

### Secrets Management

NEVER commit these to version control:
- AWS/Tigris credentials
- Gemini API keys
- Any user-provided API keys

Use environment variables and `.env` files (gitignored):
```bash
# .env (local development)
AWS_ACCESS_KEY_ID=tid_xxxxx
AWS_SECRET_ACCESS_KEY=tsec_xxxxx
AWS_ENDPOINT_URL_S3=https://fly.storage.tigris.dev
BUCKET_NAME=adcp-previews
```

### Production Checklist

- [ ] All secrets set via `fly secrets set`
- [ ] Tigris bucket created with `--public` flag
- [ ] Preview URLs tested and accessible
- [ ] Health checks passing
- [ ] Logs monitoring configured
- [ ] Error tracking enabled (Sentry/similar)

## Troubleshooting

### Preview URLs Return 403 Access Denied

**Problem:** Presigned URLs returning access denied errors.

**Solution:** The bucket was created with `--public` flag, so we use direct virtual-hosted-style URLs instead of presigned URLs:
```
https://[bucket-name].fly.storage.tigris.dev/[object-key]
```

This is already implemented in `storage.py` (v2).

### Server Won't Start on Fly.io

Check logs:
```bash
fly logs
```

Common issues:
- Missing environment variables
- Port mismatch (should be 8080)
- Dockerfile build errors

### Tests Fail Locally

Ensure dependencies are installed:
```bash
uv sync
```

For Tigris-dependent tests, set environment variables in `.env`.

## Contributing

1. Create feature branch from `main`
2. Add tests for new functionality
3. Run linter and tests
4. Create pull request with description
5. Ensure CI passes

## License

MIT License - see LICENSE file

## Spec Reference

Format specifications from [AdCP Media Buy Protocol](https://adcontextprotocol.org/docs/media-buy/capability-discovery/creative-formats)
