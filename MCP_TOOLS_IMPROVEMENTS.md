# MCP Tools Improvements

## Summary

Improved the `list_creative_formats` and `preview_creative` MCP tools based on user feedback about tool contract clarity and error precision.

## Changes Made

### 1. Enhanced `list_creative_formats` Tool

**Before:**
- Returned raw format objects without usage examples
- No clear indication of expected manifest structure
- Users had to guess field names and structure

**After:**
- Added `manifest_example` field to each format showing complete working example
- Enhanced docstring explaining the structure of returned data
- Provides concrete examples for each asset type (image, video, text, url, etc.)
- Clear documentation of required vs. optional fields

**Example output:**
```json
{
  "format_id": "display_300x250_image",
  "name": "Medium Rectangle - Image",
  "assets_required": [...],
  "manifest_example": {
    "format_id": "display_300x250_image",
    "assets": {
      "banner_image": {
        "url": "https://example.com/image.jpg"
      },
      "click_url": {
        "url": "https://example.com/landing"
      }
    }
  }
}
```

### 2. Improved `preview_creative` Tool

**Before:**
- Generic error messages like "format_id is required"
- Single-string error responses
- No JSON Pointer paths for error locations
- No examples of correct values

**After:**
- Structured error responses with JSON Pointer paths
- Actionable error messages with hints
- Type differentiation (missing_required_field, invalid_type, server_internal, etc.)
- Examples of correct values in error responses
- Pre-validation before attempting preview generation

**Example error response:**
```json
{
  "errors": [
    {
      "path": "/assets/banner_image/url",
      "message": "Asset of type 'image' requires a 'url' field",
      "type": "missing_required_field",
      "example": {"url": "https://example.com/asset.jpg"}
    }
  ]
}
```

### 3. Updated Docstrings

**Before:**
- Vague example with incorrect field names
- No explanation of asset structure

**After:**
- Concrete working example matching actual format requirements
- Clear notes about:
  - Assets must be a dictionary (not a list)
  - Media assets use "url" field
  - Text/HTML assets use "value" field
  - Reference to `list_creative_formats` for format-specific examples

### 4. Fixed Import Paths

- Corrected `creative_agent.data.formats` → `creative_agent.data.standard_formats`
- Fixed in both `mcp_server.py` and `api_server.py`

## Impact

These improvements address all major pain points from the feedback:

1. ✅ **Self-describing contracts** - Manifest examples show exact expected structure
2. ✅ **Consistent naming** - Examples use correct field names (url vs. value)
3. ✅ **Exposed constraints** - Asset requirements shown in examples
4. ✅ **Actionable errors** - JSON Pointer paths + examples of correct values
5. ✅ **Validation paths** - Errors caught before expensive operations

## Files Modified

- `mcp_server.py` - Enhanced both MCP tool implementations
- `src/creative_agent/api_server.py` - Fixed import path
- `test_mcp_tools.py` - Created validation test script (new file)

## Testing

Syntax validation completed successfully. Full integration testing requires dependency resolution (poetry environment setup issue with Python 4.0 compatibility).

## Next Steps (Future)

Per feedback, additional high-leverage improvements could include:

1. Add JSON Schema output option to `list_creative_formats`
2. Create a `validate_creative` tool for pre-flight validation without preview generation
3. Add file size validation and URL format checking
4. Provide compression/optimization helpers for assets
