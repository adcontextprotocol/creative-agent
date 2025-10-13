# Generative Creative Formats - AdCP Compliant

## What Buyers/LLMs Need to Know

When matching creative requirements to formats, the key questions are:

1. **"I have these assets - what can I build?"**
   - Query by `asset_types` in `assets_required[]`

2. **"I need to fill a 300x250 slot"**
   - Query by `dimensions` in `requirements`

3. **"Show me all display formats"**
   - Query by `type="display"`

4. **"What inputs does this format need?"**
   - Inspect `assets_required[]` for each format

5. **"What can this generative format produce?"**
   - Check `output_format_ids` (only present on generative formats)

## Generative Format Example (100% AdCP Compliant)

```python
CreativeFormat(
    format_id="display_300x250_generative",
    type="display",  # Media type it produces
    output_format_ids=["display_300x250_image"],  # Signals: this is generative
    requirements={"dimensions": "300x250"},
    assets_required=[
        {
            "asset_id": "brand_context",
            "asset_type": "brand_manifest",
            "asset_role": "brand_context",
            "required": True,
        },
        {
            "asset_id": "generation_prompt",
            "asset_type": "text",
            "asset_role": "generation_prompt",
            "required": True,
        },
    ],
)
```

## How LLMs Match Formats

**Presence of `output_format_ids`** → Generative format
- Input: `brand_manifest` + `text` prompt
- Output: Standard IAB-compliant creative in specified format(s)

**Absence of `output_format_ids`** → Direct format
- Input: Actual assets (images, videos, HTML, etc.)
- Output: Uses provided assets directly

## Key Insight

AdCP v2.4 already supports generative formats perfectly through `output_format_ids`. No protocol changes needed.
