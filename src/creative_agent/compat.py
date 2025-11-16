"""DEPRECATED: Compatibility layer for adcp library types.

## Deprecation Notice

As of adcp 2.2.0, semantic type aliases are provided directly by the library.
This module is no longer needed and will be removed in a future version.

**Instead of:**
```python
from creative_agent.compat import UrlPreviewRender
```

**Use:**
```python
from adcp.types import UrlPreviewRender
```

## Migration

All imports from this module should be updated to import directly from `adcp.types`:
- `UrlPreviewRender`, `HtmlPreviewRender`, `BothPreviewRender`
- `UrlVastAsset`, `InlineVastAsset`
- `UrlDaastAsset`, `InlineDaastAsset`
- `MediaSubAsset`, `TextSubAsset`

This module now re-exports from the library for backward compatibility.
"""

import warnings

# Re-export from library for backward compatibility
from adcp.types import (
    BothPreviewRender,
    HtmlPreviewRender,
    InlineDaastAsset,
    InlineVastAsset,
    MediaSubAsset,
    TextSubAsset,
    UrlDaastAsset,
    UrlPreviewRender,
    UrlVastAsset,
)

# Emit deprecation warning on import
warnings.warn(
    "creative_agent.compat is deprecated. Import type aliases directly from adcp.types instead. "
    "This module will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    # DAAST assets
    "BothPreviewRender",
    "HtmlPreviewRender",
    "InlineDaastAsset",
    "InlineVastAsset",
    # SubAssets
    "MediaSubAsset",
    "TextSubAsset",
    # VAST assets
    "UrlDaastAsset",
    "UrlPreviewRender",
    "UrlVastAsset",
]
