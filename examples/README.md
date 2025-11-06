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

### React Example

```jsx
function ProductGrid({ previews }) {
  return (
    <div className="grid">
      {previews.map(preview => (
        <rendered-creative
          key={preview.preview_id}
          src={preview.renders[0].preview_url}
          width={preview.renders[0].dimensions?.width}
          height={preview.renders[0].dimensions?.height}
        />
      ))}
    </div>
  );
}
```

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

## API Response Structure

When you call `preview_creative`, you get:

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
