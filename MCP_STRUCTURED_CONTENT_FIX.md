# The Real Fix: MCP structuredContent

## The Actual Problem

You were 100% correct - this was a **server bug**, not a client bug!

The MCP specification provides TWO ways to return data:
1. **`content`** - Human-readable message (e.g., "Found 38 formats")
2. **`structuredContent`** - Machine-readable structured data (the actual ADCP JSON object)

Our server was only returning JSON as a string in `content.text`, forcing clients to:
1. Extract the text field
2. Parse the JSON string
3. Use the parsed object

This is the wrong pattern! MCP clients should access `structuredContent` directly as an object.

## The MCP Spec Says

From https://modelcontextprotocol.io/specification/2025-06-18/server/tools:

```json
{
  "result": {
    "content": [{
      "type": "text",
      "text": "Found 38 creative formats"  ← Human message
    }],
    "structuredContent": {
      "formats": [...],                    ← Actual data object
      "creative_agents": [...]
    }
  }
}
```

The client should use `result.structuredContent` directly - no JSON parsing needed!

## The Fix

### Before (Wrong)
```python
@mcp.tool()
def list_creative_formats(...) -> str:
    response = ListCreativeFormatsResponse(...)
    return response.model_dump_json()  # ❌ Returns JSON string
```

MCP wraps this as:
```json
{
  "content": [{"type": "text", "text": "{\"formats\": [...]}"}],
  "structuredContent": null  ← Missing!
}
```

Client must: `JSON.parse(result.content[0].text)`

### After (Correct)
```python
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent

@mcp.tool()
def list_creative_formats(...) -> ToolResult:
    response = ListCreativeFormatsResponse(...)

    return ToolResult(
        content=[TextContent(
            type="text",
            text=f"Found {len(response.formats)} creative formats"
        )],
        structured_content=response.model_dump(mode="json")
    )
```

MCP returns:
```json
{
  "content": [{"type": "text", "text": "Found 38 creative formats"}],
  "structuredContent": {
    "formats": [...],           ← Direct object access!
    "creative_agents": [...]
  }
}
```

Client uses: `result.structuredContent.formats` (no parsing!)

## Benefits

1. **No JSON parsing** - Clients get objects directly
2. **Type safety** - Clients can validate with schemas
3. **Human-readable messages** - content describes what happened
4. **Backwards compatible** - Old clients can still parse content.text
5. **Follows MCP spec** - This is the intended pattern

## Status

✅ **list_creative_formats** - Fixed, tests passing
⏳ **preview_creative** - TODO
⏳ **build_creative** - TODO

## Migration for Other Tools

Same pattern for all tools:

```python
@mcp.tool()
def some_tool(...) -> ToolResult:
    # Do work
    result_data = {...}

    return ToolResult(
        content=[TextContent(
            type="text",
            text="Human-readable summary of what happened"
        )],
        structured_content=result_data  # Direct object
    )
```

## Client Usage

TypeScript/JavaScript MCP clients:
```typescript
const response = await client.callTool('list_creative_formats', {});

// Use structured content directly (no JSON.parse needed!)
const formats = response.structuredContent.formats;

// Human message for logging/UI
console.log(response.content[0].text); // "Found 38 creative formats"
```

Python MCP clients:
```python
response = await client.call_tool('list_creative_formats', {})

# Direct object access
formats = response.structured_content['formats']

# Human message
print(response.content[0].text)  # "Found 38 creative formats"
```

## Conclusion

The fix is to use `ToolResult` with `structured_content`. This is the proper MCP pattern and eliminates the need for JSON parsing on the client side.

The ADCPClient should be updated to use `structuredContent` instead of parsing `content[0].text`.
