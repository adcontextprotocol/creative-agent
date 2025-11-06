"""Utility functions for the creative agent."""

import html as html_module


def sanitize_url(url: str) -> str:
    """Sanitize URL for safe inclusion in HTML.

    Blocks dangerous protocols and escapes the URL.

    Args:
        url: URL string to sanitize

    Returns:
        Sanitized URL or "#" if dangerous
    """
    if not url:
        return "#"

    url_lower = url.lower().strip()

    # Block dangerous protocols
    dangerous_protocols = ["javascript:", "data:", "vbscript:", "file:"]
    for protocol in dangerous_protocols:
        if url_lower.startswith(protocol):
            return "#"

    return html_module.escape(url)
