# ADCP Client Bug Analysis

## The Problem

The ADCPClient TypeScript implementation has a bug in its MCP protocol handling. When configured with `protocol: 'mcp'`, it **extracts but doesn't parse** the JSON string from MCP responses.

## Evidence

Test output:
```javascript
const client = new ADCPClient({
  agent_uri: 'https://creative.adcontextprotocol.org/mcp',
  protocol: 'mcp'
});

const result = await client.listCreativeFormats({});
console.log('Response data keys:', Object.keys(result.data));
// Output: [ 'result' ]

console.log('Type:', typeof result.data.result);
// Output: string

console.log('Preview:', result.data.result.substring(0, 100));
// Output: {"formats": [{"format_id": {"agent_url": ...
```

## Root Cause

### MCP Protocol Spec
MCP tool responses wrap JSON strings in this structure:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\"formats\": [...], \"creative_agents\": [...]}"
    }],
    "isError": false
  }
}
```

### What the Client Should Do
```typescript
// 1. Extract the text field
const textContent = mcpResponse.result.content[0].text;

// 2. Parse the JSON string  ← THIS IS MISSING
const parsedData = JSON.parse(textContent);

// 3. Return the parsed object
return { success: true, data: parsedData };
```

### What the Client Actually Does (Bug)
```typescript
// 1. Extract the text field
const textContent = mcpResponse.result.content[0].text;

// 2. ❌ SKIP PARSING - just return the string
return { success: true, data: { result: textContent } };
```

## The Fix (Client-Side)

The ADCPClient needs to add ONE line - parse the JSON:

```diff
  // In ADCPClient.ts, when handling MCP responses:
  const textContent = mcpResponse.result.content[0].text;
+ const parsedData = JSON.parse(textContent);
- return { success: true, data: { result: textContent } };
+ return { success: true, data: parsedData };
```

## Workaround (Server-Side)

While waiting for the client fix, the server CAN provide direct HTTP endpoints:

### Current Architecture
```
Client → /mcp → MCP Protocol → JSON-RPC wrapped response
```

### Alternative (Implemented but Not Deployed)
```
Client → /adcp/* → Direct HTTP → Clean ADCP JSON
```

The combined_server.py provides both:
- `/mcp` - MCP protocol (correct, client bug prevents usage)
- `/adcp/*` - Direct ADCP HTTP (workaround, no MCP wrapping)

To deploy the workaround, change Dockerfile.fly:
```dockerfile
# Current (production):
CMD ["python", "-m", "creative_agent.server"]

# With workaround:
CMD ["python", "-m", "creative_agent.combined_server"]
```

Then update client to use `/adcp` instead of `/mcp`.

## Recommendation

**Fix the client, not the server.** The server is correctly implementing MCP protocol. Adding HTTP endpoints is a workaround that shouldn't be necessary.

The fix is literally one line: `JSON.parse(textContent)`
