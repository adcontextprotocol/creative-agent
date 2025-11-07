# ADCP Creative Embedding Examples

This directory contains examples of how to embed ADCP creative previews in your application.

## Web Component Approach (Recommended)

The `<rendered-creative>` web component provides the easiest way to embed creative previews in a grid or list.

### Features

- **Shadow DOM** - Complete CSS isolation, no style conflicts
- **Lazy Loading** - Components load only when visible (IntersectionObserver)
- **Framework Agnostic** - Works with React, Vue, Angular, or vanilla JS
- **Easy Grid Layouts** - No need for iframes, just drop components in a grid

### Basic Usage

```html
<!-- 1. Include the script -->
<script src="https://creative.adcontextprotocol.org/static/rendered-creative.js"></script>

<!-- 2. Use the component -->
<rendered-creative
    src="https://preview-url.com/uuid/desktop.html"
    width="300"
    height="400">
</rendered-creative>
```

### Grid Layout Example

```html
<div class="product-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 24px;">
    <rendered-creative
        src="https://preview-url.com/product1/desktop.html"
        width="300"
        height="400">
    </rendered-creative>
    <rendered-creative
        src="https://preview-url.com/product2/desktop.html"
        width="300"
        height="400">
    </rendered-creative>
    <rendered-creative
        src="https://preview-url.com/product3/desktop.html"
        width="300"
        height="400">
    </rendered-creative>
</div>
```

### React Example (with Batch Preview)

```jsx
import { useEffect, useState } from 'react';

function FormatShowcaseGrid() {
  const [previews, setPreviews] = useState([]);

  useEffect(() => {
    async function loadPreviews() {
      // 1. List all formats
      const formats = await creativeAgent.list_creative_formats();

      // 2. Batch preview all formats with HTML output (no S3 uploads!)
      const response = await creativeAgent.preview_creative({
        output_format: "html",  // Get HTML directly
        requests: formats.formats.map(format => ({
          format_id: format.format_id,
          creative_manifest: format.format_card.manifest,
          inputs: [{ name: "Desktop", macros: { DEVICE_TYPE: "desktop" } }]
        }))
      });

      // 3. Extract successful previews
      const successful = response.results
        .filter(r => r.success)
        .map(r => r.response.previews[0]);

      setPreviews(successful);
    }

    loadPreviews();
  }, []);

  return (
    <div className="grid">
      {previews.map(preview => (
        <div
          key={preview.preview_id}
          dangerouslySetInnerHTML={{ __html: preview.renders[0].preview_html }}
        />
      ))}
    </div>
  );
}
```

**Why batch mode?**
- **5-10x faster**: One API call instead of N calls
- **No storage**: HTML output bypasses S3 entirely
- **Simpler**: No need to track/cleanup uploaded files

### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `src` | string | required | URL to the creative HTML |
| `width` | number | auto | Width in pixels |
| `height` | number | auto | Height in pixels |
| `lazy` | boolean | `true` | Enable lazy loading |

### Local Development

To test the web component locally:

```bash
# 1. Generate test HTML files
uv run python scripts/test_card_rendering.py

# 2. Start a local web server (required for fetch to work)
cd /path/to/creative-agent
python -m http.server 8000

# 3. Open the demo in your browser
open http://localhost:8000/examples/web-component-grid.html
```

**Note**: Opening `web-component-grid.html` directly (file://) won't work because browsers block fetch requests from file:// URLs for security reasons. You must use a web server.

The demo shows:
- Product cards in a grid layout
- Format cards alongside product cards
- No iframe overhead
- Proper CSS isolation via Shadow DOM

## iframe Approach (Alternative)

If you need maximum isolation or can't use web components, you can still use iframes:

```html
<div class="grid">
    <iframe
        src="https://preview-url.com/uuid/desktop.html"
        width="300"
        height="400"
        frameborder="0"
        sandbox="allow-same-origin">
    </iframe>
</div>
```

**Note**: iframes are heavier and harder to style as a cohesive grid, but provide the strongest isolation.

## Batch Mode & HTML Output (New!)

### When to Use Batch Mode

Use batch mode when you need to preview multiple creatives at once:
- **Format showcases** (previewing all available formats)
- **Campaign reviews** (previewing all creatives in a campaign)
- **A/B testing grids** (comparing multiple creative variants)

### When to Use HTML Output

Use HTML output (`output_format="html"`) when:
- Embedding previews directly in your page (no iframe needed)
- Building preview grids with 50+ items
- You don't need shareable URLs
- You want to avoid S3 storage costs

### Batch + HTML Example

```javascript
// Preview 10 different creatives in one API call with HTML output
const response = await creativeAgent.preview_creative({
  output_format: "html",  // Default for all requests
  requests: [
    {
      format_id: "display_300x250_image",
      creative_manifest: manifest1
    },
    {
      format_id: "display_728x90_image",
      creative_manifest: manifest2
    },
    // ... up to 50 requests
  ]
});

// Handle results (some may fail)
response.results.forEach((result, idx) => {
  if (result.success) {
    const html = result.response.previews[0].renders[0].preview_html;
    document.getElementById(`preview-${idx}`).innerHTML = html;
  } else {
    console.error(`Preview ${idx} failed:`, result.error.message);
  }
});
```

### Per-Request Output Override

You can mix output formats in a batch:

```javascript
const response = await creativeAgent.preview_creative({
  output_format: "html",  // Default
  requests: [
    {
      format_id: "format1",
      creative_manifest: manifest1,
      output_format: "url"  // Override: this one returns a URL
    },
    {
      format_id: "format2",
      creative_manifest: manifest2
      // Uses default "html"
    }
  ]
});
```

## API Response Structure

### Single Mode Response

When you call `preview_creative` in single mode, you get:

```json
{
  "previews": [
    {
      "preview_id": "uuid-123",
      "renders": [
        {
          "render_id": "primary",
          "preview_url": "https://creative.adcontextprotocol.org/preview/uuid-123/desktop.html",
          "role": "primary",
          "dimensions": {
            "width": 300,
            "height": 400
          }
        }
      ],
      "input": {
        "name": "Desktop"
      }
    }
  ],
  "interactive_url": "https://creative.adcontextprotocol.org/preview/uuid-123/interactive",
  "expires_at": "2025-11-07T10:00:00Z"
}
```

Just pass `preview_url` to the web component's `src` attribute!

### Batch Mode Response

When you call `preview_creative` in batch mode, you get:

```json
{
  "results": [
    {
      "success": true,
      "response": {
        "previews": [...],
        "interactive_url": "...",
        "expires_at": "..."
      }
    },
    {
      "success": false,
      "error": {
        "code": "preview_failed",
        "message": "Format not found"
      }
    }
  ]
}
```

Each result has a `success` field. Check this before accessing `response` or `error`.

### HTML Output Response

When using `output_format="html"`, the response includes `preview_html` instead of (or in addition to) `preview_url`:

```json
{
  "previews": [{
    "renders": [{
      "preview_html": "<div class='creative'>...</div>",
      "role": "primary",
      "dimensions": { "width": 300, "height": 250 }
    }]
  }]
}
```

Use `dangerouslySetInnerHTML` in React or `innerHTML` in vanilla JS to render it.
