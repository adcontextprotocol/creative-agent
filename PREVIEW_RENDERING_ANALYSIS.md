# Creative Agent Preview Rendering System - Thorough Analysis

## Overview
The AdCP Creative Agent implements a preview rendering system that converts creative manifests into displayable HTML previews. This system supports multiple asset types including images, HTML, CSS, JavaScript, and video, and generates preview variants for different device types and contexts.

---

## 1. PREVIEW GENERATION WORKFLOW

### Request Entry Point: `preview_creative()` Tool
**File:** `/src/creative_agent/server.py` (lines 169-341)

```
User Request
    ↓
preview_creative(format_id, creative_manifest, inputs, template_id)
    ↓
Validation (format exists, manifest format_id matches)
    ↓
Asset Validation (validate_manifest_assets)
    ↓
Generate Preview Variants (one per input set)
    ↓
Upload to Tigris S3 Storage
    ↓
Return PreviewCreativeResponse with URLs
```

**Key Function Parameters:**
- `format_id`: Format identifier (string or FormatId object with agent_url and id)
- `creative_manifest`: Dict containing assets and format_id
- `inputs`: List of preview input sets (device type, macros, context)
- `template_id`: Optional custom template (not currently used)

**Default Variants Generated** (if no inputs provided):
- Desktop (macros: {"DEVICE_TYPE": "desktop"})
- Mobile (macros: {"DEVICE_TYPE": "mobile"})
- Tablet (macros: {"DEVICE_TYPE": "tablet"})

---

## 2. SUPPORTED ASSET TYPES & RENDERING

### Asset Type Hierarchy
Per ADCP spec (from `_schemas_v1_core_format_json.py`):

| Asset Type | Schema | Content Type | Current Preview Support |
|---|---|---|---|
| **image** | `ImageAsset` | URL + metadata (width, height, format) | ✅ Renders in HTML |
| **html** | `HtmlAsset` | HTML content string | ⚠️ Validated, not rendered |
| **css** | `CssAsset` | CSS content string | ⚠️ Validated, not rendered |
| **javascript** | `JavascriptAsset` | JS content + module_type (esm/commonjs/script) | ⚠️ Validated, not rendered |
| **text** | `TextAsset` | Plain text content | ⚠️ Validated, not rendered |
| **url** | `UrlAsset` | HTTP/HTTPS URL | ✅ Used for click tracking |
| **video** | `VideoAsset` | URL + metadata (width, height, format) | ✅ Dimensions extracted, not video player |
| **audio** | `AudioAsset` | URL + metadata | Validated only |
| **vast** | VastAsset | XML content or URL | Validated only |
| **daast** | DaastAsset | XML content or URL | Validated only |
| **webhook** | WebhookAsset | URL endpoint | Validated only |
| **promoted_offerings** | `PromotedOfferingsAsset` | Brand manifest + products | Used for generative formats |

### Asset Validation (validation.py)

**HTML Asset Validation** (lines 14-38):
- Must contain valid HTML tags
- If DOCTYPE present, must also have <body> tag
- Uses regex to detect HTML elements

**CSS Asset Validation** (lines 41-57):
- Must contain at least one CSS rule (selector + braces)
- Basic regex pattern: `[^{}]+\{[^{}]*\}`

**JavaScript Asset Validation** (lines 60-75):
- Must be at least 5 characters long
- No strict syntax validation (avoids issues with minified code)

**Text Asset Validation** (lines 78-91):
- Must not be empty or whitespace-only

---

## 3. CURRENT PREVIEW GENERATION LOGIC

### `generate_preview_html()` Function
**File:** `/src/creative_agent/storage.py` (lines 106-235)

#### Current Implementation (Basic Display)

```python
def generate_preview_html(format_obj, manifest, input_set) -> str:
    # Extract dimensions from format
    width, height = extract_from_format_renders()

    # Build asset_id -> asset_type map from format specification
    asset_type_map = {}
    for required_asset in format_obj.assets_required:
        asset_type_map[asset_id] = asset_type.value

    # Find first image asset and click URL
    image_url = None
    for asset_id, asset_data in manifest_assets.items():
        if asset_type_map.get(asset_id) == "image":
            image_url = asset_data.get("url")
            break

    # Generate HTML preview
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{format.name} - {input_set.name}</title>
        <style>
            body {{ width: {width}px; height: {height}px; }}
            .creative-container {{ width: 100%; height: 100%; position: relative; }}
            .creative-container img {{ width: 100%; height: 100%; object-fit: cover; }}
            .preview-label {{ position: absolute; top: 5px; left: 5px; ... }}
        </style>
    </head>
    <body>
        <div class="creative-container" onclick="handleClick()">
            <img src="{image_url}" alt="{format.name}">
            <div class="preview-label">{input_set.name}</div>
        </div>
        <script>
            function handleClick() {{
                window.open("{click_url}", "_blank");
            }}
        </script>
    </body>
    </html>
    """
    return html
```

#### Key Characteristics:

1. **Dimension Extraction** (lines 118-126)
   - Reads width/height from first render in `format_obj.renders[0]`
   - Default fallback: 300x250
   - Converts to pixels

2. **Asset Mapping** (lines 142-152)
   - Creates asset_id -> asset_type dictionary from format specification
   - Handles both enum and string asset types
   - Supports format validation even without format object

3. **Image Discovery** (lines 154-158)
   - Finds first image asset using asset_type_map
   - Extracts URL field
   - Falls back to placeholder if no image found

4. **Click URL Discovery** (lines 161-165)
   - Finds first URL asset
   - Used for click tracking in embedded onclick handler

5. **Security: URL Sanitization** (lines 98-103)
   - Function: `sanitize_url(url)`
   - Blocks: `javascript:`, `data:`, `vbscript:` protocols
   - Replaces dangerous URLs with "#"
   - HTML escapes remaining URLs

6. **HTML Output** (lines 168-233)
   - Wraps in DOCTYPE HTML5
   - Sets explicit dimensions as px units
   - Includes viewport meta tag
   - Applies CSS to fit image in container
   - Adds preview label (device type name)
   - Includes minimal click handler

#### Current Limitations:

- ❌ **HTML assets not rendered** - Only image-based previews
- ❌ **CSS assets not applied** - No style injection
- ❌ **JavaScript assets not executed** - No JS inclusion
- ❌ **Video not previewed** - Only dimensions extracted
- ❌ **Native format text not rendered** - No text layout
- ⚠️ **Macro substitution not implemented** - Macros in input_set not applied to content
- ⚠️ **Template system not implemented** - template_id parameter unused

---

## 4. FORMAT DEFINITIONS & ASSET REQUIREMENTS

### Display Formats (Image-based)
**File:** `/src/creative_agent/data/standard_formats.py` (lines 418-605)

Example: `display_300x250_image`
```python
assets_required=[
    AssetsRequired(
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
    AssetsRequired(
        asset_id="click_url",
        asset_type=AssetType.url,
        required=True,
        requirements={"description": "Clickthrough destination URL"},
    ),
]
```

### Display Formats (HTML5)
**File:** `/src/creative_agent/data/standard_formats.py` (lines 607-730)

Example: `display_300x250_html`
```python
assets_required=[
    AssetsRequired(
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
]
```

#### HTML Formats Available:
- display_300x250_html (Medium Rectangle)
- display_728x90_html (Leaderboard)
- display_160x600_html (Wide Skyscraper)
- display_336x280_html (Large Rectangle)
- display_300x600_html (Half Page)
- display_970x250_html (Billboard)

### Native Formats
**File:** `/src/creative_agent/data/standard_formats.py` (lines 732-848)

Example: `native_standard`
```python
assets_required=[
    AssetsRequired(asset_id="title", asset_type=AssetType.text),
    AssetsRequired(asset_id="description", asset_type=AssetType.text),
    AssetsRequired(asset_id="main_image", asset_type=AssetType.image),
    AssetsRequired(asset_id="icon", asset_type=AssetType.image, required=False),
    AssetsRequired(asset_id="cta_text", asset_type=AssetType.text),
    AssetsRequired(asset_id="sponsored_by", asset_type=AssetType.text),
]
```

### Video Formats
Support for various video dimensions with video file assets:
- video_standard_30s, 15s
- video_1920x1080 (Full HD)
- video_1280x720 (HD)
- video_1080x1920 (Vertical)
- video_1080x1080 (Square)
- video_ctv_preroll_30s, video_ctv_midroll_30s (Connected TV)

### Generative Formats
**File:** `/src/creative_agent/data/standard_formats.py` (lines 71-235)

Example: `display_300x250_generative`
```python
assets_required=[
    AssetsRequired(
        asset_id="promoted_offerings",
        asset_type=AssetType.promoted_offerings,
        required=True,
        requirements={"description": "Brand manifest and product offerings"},
    ),
    AssetsRequired(
        asset_id="generation_prompt",
        asset_type=AssetType.text,
        required=True,
        requirements={"description": "Text prompt describing the desired creative"},
    ),
]
output_format_ids=[create_format_id("display_300x250_image")]
```

---

## 5. HTML STRUCTURE & CSS STYLING

### Generated HTML Template
**File:** `/src/creative_agent/storage.py` (lines 168-233)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{format_name} - {input_name}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            width: {width}px;
            height: {height}px;
            overflow: hidden;
            font-family: Arial, sans-serif;
        }
        .creative-container {
            width: 100%;
            height: 100%;
            position: relative;
            cursor: pointer;
        }
        .creative-container img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .preview-label {
            position: absolute;
            top: 5px;
            left: 5px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 2px 6px;
            font-size: 10px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="creative-container" onclick="handleClick()">
        <img src="{image_url}" alt="{format_name}">
        <div class="preview-label">{input_name}</div>
    </div>
    <script>
        function handleClick() {
            window.open("{click_url}", "_blank");
        }
    </script>
</body>
</html>
```

### CSS Features:
- **Border Box Sizing**: Standard box model
- **Fixed Dimensions**: width/height in pixels
- **Image Fitting**: `object-fit: cover` for responsive image scaling
- **No Overflow**: Crop content to exact dimensions
- **Preview Label**: Overlay showing device type
- **Click Handling**: onclick handler for tracking

### Limitations:
- ❌ No support for CSS from CssAsset
- ❌ No media queries for responsive behavior
- ❌ No animation or transitions
- ❌ No font customization from assets
- ❌ No flexbox/grid layouts for complex creatives

---

## 6. STORAGE & DELIVERY SYSTEM

### S3 Upload (`upload_preview_html`)
**File:** `/src/creative_agent/storage.py` (lines 53-95)

**Flow:**
```
HTML Content
    ↓
encode to UTF-8
    ↓
S3.put_object(
    Bucket=BUCKET_NAME ("adcp-previews"),
    Key=f"previews/{preview_id}/{variant_name}.html",
    Body=encoded_content,
    ContentType="text/html",
    CacheControl="public, max-age=3600"  # 1 hour cache
)
    ↓
Generate Public URL:
https://{BUCKET_NAME}.fly.storage.tigris.dev/{key}
```

**S3 Configuration** (lines 10-15):
- Uses environment variables from Fly.io
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- `AWS_ENDPOINT_URL_S3` (Tigris endpoint)
- `AWS_REGION` (defaults to "auto")
- `BUCKET_NAME` (defaults to "adcp-previews")

**URL Construction** (lines 84-86):
```
https://{BUCKET_NAME}.fly.storage.tigris.dev/previews/{preview_id}/{variant_name}.html
```

### Response Structure
**File:** `/src/creative_agent/server.py` (lines 343-412)

```python
PreviewCreativeResponse(
    previews=[
        Preview(
            preview_id=preview_id,
            renders=[
                Render(
                    render_id=f"{preview_id}-primary",
                    preview_url=preview_url,  # S3 URL
                    role="primary",
                    dimensions=Dimensions(width=300, height=250),
                    embedding=Embedding(
                        recommended_sandbox="allow-scripts allow-same-origin",
                        requires_https=False,
                        supports_fullscreen=is_video_or_rich_media,
                    ),
                ),
            ],
            input=Input(
                name=input_set.name,
                macros=input_set.macros,
                context_description=input_set.context_description,
            ),
        ),
        # ... more previews for each input
    ],
    interactive_url=f"{AGENT_URL}/preview/{preview_id}/interactive",
    expires_at=datetime.now(UTC) + timedelta(hours=24),
)
```

---

## 7. MACRO SYSTEM & SUBSTITUTION

### Defined Macros
**File:** `/src/creative_agent/data/standard_formats.py` (lines 26-37)

```python
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
```

### Input Set with Macros
```python
PreviewInput(
    name="Desktop",
    macros={"DEVICE_TYPE": "desktop"},
    context_description="Desktop viewing context"
)
```

### Current Status:
- ✅ Macros stored in response via `input.macros`
- ✅ DEVICE_TYPE macro passed to preview
- ⚠️ **Macro substitution not yet implemented in preview generation**
- ⚠️ No replacement of {{MACRO}} or ${MACRO} in content

---

## 8. TEST COVERAGE & VALIDATION

### Unit Tests: Preview Generation
**File:** `/tests/unit/test_preview_generation.py`

Tests cover:
- ✅ Spec-compliant manifest handling
- ✅ Image URL extraction
- ✅ Click URL extraction
- ✅ Dimension inclusion
- ✅ JavaScript URL sanitization
- ✅ Format name HTML escaping
- ✅ Multiple input names
- ✅ Video format support
- ✅ Optional assets beyond format requirements
- ✅ Pydantic validation of dimensions and URLs

### Integration Tests: Preview Creative Tool
**File:** `/tests/integration/test_preview_creative.py`

Tests cover:
- ✅ Spec-compliant manifest submission
- ✅ Custom input variants
- ✅ Format ID mismatch validation
- ✅ FormatId as dict parameter
- ✅ Malicious URL validation
- ✅ Interactive URL generation
- ✅ Expiration timestamp (24 hours)
- ✅ Unknown format rejection
- ✅ Full ADCP spec compliance validation
- ✅ ISO 8601 timestamp format
- ✅ Missing required asset detection
- ✅ Clear error messages

### Validation Tests: Asset Types
**File:** `/tests/validation/test_asset_validation.py`

Tests cover:
- ✅ HTML validation (tags, body requirement)
- ✅ CSS validation (rules syntax)
- ✅ JavaScript validation (length check)
- ✅ Text validation (non-empty)
- ✅ URL validation (scheme, safety)
- ✅ Data URI validation (MIME types, size limits)
- ✅ Image URL validation
- ✅ VAST/DAAST validation
- ✅ Promoted offerings validation

---

## 9. MANIFEST STRUCTURE FOR PREVIEW REQUESTS

### Creative Manifest (dict-based)
```python
{
    "format_id": {
        "agent_url": "https://creative.adcontextprotocol.org",
        "id": "display_300x250_image"
    },
    "assets": {
        "banner_image": {
            "url": "https://example.com/image.png",
            "width": 300,
            "height": 250,
            "format": "png"
        },
        "click_url": {
            "url": "https://example.com/landing"
        }
    }
}
```

### For HTML Format:
```python
{
    "format_id": {
        "agent_url": "https://creative.adcontextprotocol.org",
        "id": "display_300x250_html"
    },
    "assets": {
        "html_creative": {
            "content": "<!DOCTYPE html>..."
        }
    }
}
```

### For Native Format:
```python
{
    "format_id": {
        "agent_url": "https://creative.adcontextprotocol.org",
        "id": "native_standard"
    },
    "assets": {
        "title": {"content": "Headline"},
        "description": {"content": "Body copy..."},
        "main_image": {
            "url": "https://example.com/image.jpg",
            "width": 1200,
            "height": 627
        },
        "icon": {
            "url": "https://example.com/icon.png",
            "width": 200,
            "height": 200
        },
        "cta_text": {"content": "Learn More"},
        "sponsored_by": {"content": "Brand Name"}
    }
}
```

---

## 10. RELATIONSHIP BETWEEN FORMAT DEFINITIONS & PREVIEW GENERATION

### Format Definition Flow

1. **Format Specification Defines Assets**
   ```
   Format (display_300x250_html)
   ├── assets_required
   │   └── [AssetsRequired]
   │       ├── asset_id: "html_creative"
   │       ├── asset_type: AssetType.html
   │       └── requirements: {width: 300, height: 250, ...}
   └── renders
       └── [Render]
           ├── role: "primary"
           └── dimensions: {width: 300, height: 250}
   ```

2. **Manifest Provides Asset Content**
   ```
   CreativeManifest
   ├── format_id: (matches format)
   └── assets:
       └── {asset_id: asset_data}
           └── html_creative: {content: "..."}
   ```

3. **Preview Generation Uses Both**
   ```python
   # Extract from format
   asset_type_map = {asset_id: asset_type for each in format.assets_required}
   dimensions = format.renders[0].dimensions

   # Extract from manifest
   asset_data = manifest.assets[asset_id]

   # Generate preview based on asset_type
   if asset_type_map[asset_id] == "image":
       render_image(asset_data["url"])
   elif asset_type_map[asset_id] == "html":
       inject_html(asset_data["content"])  # NOT YET IMPLEMENTED
   ```

---

## 11. MARKDOWN RENDERING SUPPORT

### Current Status: ❌ NOT SUPPORTED

**Findings:**
- No markdown parser imports in codebase
- No markdown asset type in ADCP spec
- `TextAsset` is plain text only
- `HtmlAsset` is raw HTML only
- No markdown-to-HTML conversion in storage.py

**Related Patterns:**
- Text content validated to be non-empty strings
- HTML content must contain actual HTML tags
- No preprocessing or transpilation layer

---

## 12. KEY FINDINGS & GAPS

### What Works Today:
1. ✅ **Image-based display format previews** - Renders banner images in fixed containers
2. ✅ **Click URL handling** - Tracks click destinations
3. ✅ **Device type variants** - Generates desktop/mobile/tablet previews
4. ✅ **S3 storage integration** - Uploads previews to Tigris with caching
5. ✅ **Security** - Sanitizes dangerous URLs and HTML-escapes content
6. ✅ **Asset validation** - Comprehensive validation for all asset types
7. ✅ **Format specification system** - Clear asset type mapping

### Major Gaps:
1. ❌ **HTML asset rendering** - HTML5 formats defined but not rendered
2. ❌ **CSS asset rendering** - CSS assets validated but not applied
3. ❌ **JavaScript execution** - JS assets validated but not injected
4. ❌ **Native format rendering** - Text/image layout not generated
5. ❌ **Video preview** - No video player, dimensions only
6. ❌ **Macro substitution** - Macros stored but not applied to content
7. ❌ **Template system** - template_id parameter is unused
8. ❌ **Markdown support** - No markdown asset type or conversion
9. ❌ **Rich media rendering** - No support for complex interactive layouts
10. ❌ **Dynamic content** - No support for variable substitution or templating

### Architecture Insights:
- **Clean separation**: Format definitions, validation, and rendering are modular
- **Asset type map**: Smart use of format specification to determine asset types without embedded type info
- **Security-first**: URL sanitization applied before HTML generation
- **S3 integration**: Seamless preview distribution via Tigris
- **Spec compliance**: Full validation against ADCP schemas
- **Extensible**: Clear patterns for adding new asset type support

---

## 13. COMPONENT INTERACTION DIAGRAM

```
┌─────────────────────────────────────────────────────────────┐
│ Client (LLM, Automation Agent)                              │
└──────────────────┬──────────────────────────────────────────┘
                   │ preview_creative(format_id, manifest, inputs)
                   ▼
        ┌──────────────────────────────────┐
        │ server.py::preview_creative()     │
        │ - Normalize format_id             │
        │ - Parse inputs or use defaults    │
        └──────────────┬───────────────────┘
                       │
        ┌──────────────▼───────────────────┐
        │ Get format by ID                  │
        │ (data/standard_formats.py)        │
        └──────────────┬───────────────────┘
                       │
        ┌──────────────▼───────────────────┐
        │ Validate manifest assets          │
        │ (validation.py::validate_...)     │
        │ - Uses format asset type map      │
        └──────────────┬───────────────────┘
                       │
        ┌──────────────▼───────────────────────────┐
        │ For each input_set:                      │
        │   generate_preview_html()                │
        │   (storage.py)                           │
        │   - Extract dimensions from format      │
        │   - Build asset_type_map                │
        │   - Find image/url assets               │
        │   - Inject into HTML template           │
        │   - Sanitize URLs                       │
        └──────────────┬───────────────────────────┘
                       │
        ┌──────────────▼─────────────────┐
        │ Upload to S3/Tigris             │
        │ (storage.py::upload_preview_html)
        │ Key: previews/{id}/{variant}    │
        └──────────────┬─────────────────┘
                       │
        ┌──────────────▼──────────────────────┐
        │ Build Response                       │
        │ (server.py::_generate_preview_...)   │
        │ - Create Preview objects             │
        │ - Set render_id, preview_url         │
        │ - Add Embedding metadata             │
        │ - Set expiration (24h)              │
        └──────────────┬──────────────────────┘
                       │
        ┌──────────────▼──────────────────────┐
        │ Return PreviewCreativeResponse       │
        │ - JSON with preview URLs            │
        │ - S3 URLs for HTML pages            │
        │ - Metadata (dimensions, macros)     │
        └──────────────┬──────────────────────┘
                       │
        ┌──────────────▼──────────────────────┐
        │ Client renders HTML in iframe/modal  │
        │ Preview user can:                    │
        │ - View rendered creative             │
        │ - Click to navigate                  │
        │ - Test different variants            │
        └──────────────────────────────────────┘
```

---

## 14. CODE ENTRY POINTS

### Main Files:

1. **`/src/creative_agent/server.py`**
   - `preview_creative()` - Main tool (lines 169-341)
   - `_generate_preview_variant()` - Response builder (lines 343-412)
   - Imports: validation, storage, format helpers

2. **`/src/creative_agent/storage.py`**
   - `generate_preview_html()` - HTML generation (lines 106-235)
   - `upload_preview_html()` - S3 upload (lines 53-95)
   - `sanitize_url()` - Security (lines 98-103)
   - Imports: boto3, html module

3. **`/src/creative_agent/validation.py`**
   - `validate_manifest_assets()` - Full validation (lines 349-422)
   - `validate_asset()` - Individual asset (lines 191-346)
   - `validate_html_content()` - HTML check (lines 14-38)
   - `validate_css_content()` - CSS check (lines 41-57)
   - `validate_javascript_content()` - JS check (lines 60-75)
   - Imports: re, httpx, urllib

4. **`/src/creative_agent/data/standard_formats.py`**
   - Format definitions (lines 71-1070+)
   - Asset requirements per format
   - Render specifications (dimensions)

5. **`/src/creative_agent/schemas/manifest.py`**
   - `PreviewInput` - Input set for preview (lines 13-18)
   - `PreviewCreativeRequest` - Request schema (lines 21-27)
   - Not directly used (manifest is dict in current code)

---

## 15. API RESPONSE EXAMPLES

### Success Response:
```json
{
  "previews": [
    {
      "preview_id": "550e8400-e29b-41d4-a716-446655440000",
      "renders": [
        {
          "render_id": "550e8400-e29b-41d4-a716-446655440000-primary",
          "preview_url": "https://adcp-previews.fly.storage.tigris.dev/previews/550e8400-e29b-41d4-a716-446655440000/desktop.html",
          "role": "primary",
          "dimensions": {
            "width": 300.0,
            "height": 250.0,
            "unit": "px"
          },
          "embedding": {
            "recommended_sandbox": "allow-scripts allow-same-origin",
            "requires_https": false,
            "supports_fullscreen": false
          }
        }
      ],
      "input": {
        "name": "Desktop",
        "macros": {"DEVICE_TYPE": "desktop"},
        "context_description": null
      }
    },
    // ... mobile and tablet variants
  ],
  "interactive_url": "https://creative.adcontextprotocol.org/preview/550e8400-e29b-41d4-a716-446655440000/interactive",
  "expires_at": "2025-11-07T14:30:45.123456Z"
}
```

### Error Response:
```json
{
  "error": "Asset validation failed",
  "validation_errors": [
    "Asset 'banner_image': Image width must be a positive integer",
    "Required asset missing: click_url"
  ]
}
```

---

## 16. LIMITATIONS & FUTURE ENHANCEMENT AREAS

### Technical Debt:
1. HTML/CSS/JS assets exist in spec but rendering not implemented
2. Macro substitution framework missing (macros stored but not applied)
3. Template system architecture incomplete (template_id unused)
4. Native format text rendering missing (would need layout logic)
5. Video preview generation missing (would need video player or screenshots)

### Architectural Improvements:
1. Implement asset rendering system (visitor pattern?)
2. Add template engine (Jinja2? Handlebars?)
3. Add macro substitution pipeline
4. Separate rendering strategies by format type
5. Add batch preview generation
6. Add preview caching strategy beyond S3

### Feature Gaps:
1. Markdown support (requires parser + converter)
2. Custom CSS injection per format
3. Dynamic content preview (forms, submissions)
4. Screenshot generation for non-HTML content
5. A/B variant preview comparison
6. Historical preview archive

---

**Report Generated:** 2025-11-06
**Codebase:** AdCP Creative Agent (brisbane-v1 branch)
**Status:** Very thorough analysis of preview system architecture and asset rendering
