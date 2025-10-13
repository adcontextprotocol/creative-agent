"""HTTP server for AdCP Creative Agent (for Fly.io deployment)."""

import os

from .server import mcp

# Get port from environment (Fly.io sets this)
PORT = int(os.getenv("PORT", "8080"))

if __name__ == "__main__":
    # Run in HTTP mode for production deployment
    mcp.run(transport="sse", port=PORT, host="0.0.0.0")
