# ADCP Client Migration Guide

## Issue
The creative agent server was using MCP protocol, which wraps responses in JSON-RPC format. This caused double-encoding issues for HTTP clients expecting direct ADCP JSON.

## Solution
The server now provides two endpoints:
- `/mcp` - MCP protocol (for MCP clients like Claude Desktop)
- `/adcp/*` - Direct ADCP HTTP endpoints (for standard HTTP clients)

## Migration for TypeScript ADCP Client

### Current (Broken) Configuration
```typescript
const client = new ADCPClient({
  id: 'test',
  name: 'Creative Agent',
  agent_uri: 'https://creative.adcontextprotocol.org/mcp',
  protocol: 'mcp'
}, {});
```

This returns:
```json
{
  "result": "{\"formats\": [...]}"  // ❌ Double-encoded JSON string
}
```

### New (Fixed) Configuration
```typescript
const client = new ADCPClient({
  id: 'test',
  name: 'Creative Agent',
  agent_uri: 'https://creative.adcontextprotocol.org/adcp',
  protocol: 'http'  // or remove protocol field
}, {});
```

This returns:
```json
{
  "formats": [...],  // ✅ Clean ADCP JSON
  "creative_agents": [...]
}
```

## Available ADCP HTTP Endpoints

### List Creative Formats
```bash
# GET with query parameters
GET /adcp/list-creative-formats?type=display&max_width=300

# POST with JSON body
POST /adcp/list-creative-formats
Content-Type: application/json
{
  "type": "display",
  "max_width": 300
}
```

### Preview Creative
```bash
POST /adcp/preview-creative
Content-Type: application/json
{
  "format_id": "display_300x250_image",
  "creative_manifest": {
    "format_id": {"agent_url": "...", "id": "..."},
    "assets": {...}
  }
}
```

### Build Creative (AI-powered)
```bash
POST /adcp/build-creative
Content-Type: application/json
{
  "message": "Create a banner ad for coffee",
  "format_id": "display_300x250_generative",
  "gemini_api_key": "your-api-key"
}
```

## Response Format

All ADCP endpoints return clean JSON matching the ADCP schema:
- No MCP `result` wrapper
- No JSON-RPC `content` array
- Direct ADCP response objects

Example:
```json
{
  "formats": [
    {
      "format_id": {
        "agent_url": "https://creative.adcontextprotocol.org/",
        "id": "display_300x250_image"
      },
      "name": "Medium Rectangle - Image",
      "type": "display",
      ...
    }
  ],
  "creative_agents": [...],
  "errors": []
}
```

## Testing

Test the endpoints locally:
```bash
# Start server
PORT=8080 python -m creative_agent.combined_server

# Test ADCP endpoint
curl http://localhost:8080/adcp/list-creative-formats

# Should return clean JSON with top-level "formats" key
```

## Deployment

The fix is deployed when:
1. Changes are merged to main
2. Fly.io deployment is triggered (uses `Dockerfile.fly`)
3. Production URL: `https://creative.adcontextprotocol.org/adcp/*`

Both `/mcp` and `/adcp` endpoints will be available in production.
