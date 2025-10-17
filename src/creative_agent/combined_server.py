"""Combined server that provides both MCP and ADCP HTTP endpoints.

Routes:
- /mcp - MCP protocol endpoint (FastMCP streamable-http)
- /adcp/* - ADCP-native HTTP endpoints (unwrapped responses)
- / - Root redirects to /adcp/
"""

import os

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from . import server as mcp_server
from .adcp_http import app as adcp_app

# Create main FastAPI app
app = FastAPI(
    title="AdCP Creative Agent - Combined Server",
    description="Provides both MCP and ADCP HTTP endpoints",
    version="1.0.0",
)


@app.get("/")
async def root() -> RedirectResponse:
    """Redirect root to ADCP API documentation."""
    return RedirectResponse(url="/adcp/")


# Mount ADCP HTTP app at /adcp
app.mount("/adcp", adcp_app)

# Get FastMCP's streamable HTTP app and mount it at /mcp
mcp_app = mcp_server.mcp.streamable_http_app
app.mount("/mcp", mcp_app)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
