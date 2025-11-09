"""Base renderer class for creative previews."""

from abc import ABC, abstractmethod
from typing import Any


class BaseRenderer(ABC):
    """Base class for format-specific preview renderers."""

    @abstractmethod
    def render(self, format_obj: Any, manifest: Any, input_set: Any, fragment: bool = True) -> str:
        """Generate HTML preview content for a creative manifest.

        Args:
            format_obj: Format definition containing renders, assets_required, etc.
            manifest: Creative manifest with assets
            input_set: Preview input configuration (device type, macros, etc.)
            fragment: If True (default), return HTML fragment for embedding.
                     If False, return complete HTML document with DOCTYPE.

        Returns:
            HTML string - fragment for direct embedding or full document for iframe
        """

    def get_dimensions(self, format_obj: Any) -> tuple[int, int]:
        """Extract width and height from format renders.

        Args:
            format_obj: Format definition

        Returns:
            Tuple of (width, height) in pixels, defaults to (300, 250)
        """
        width = 300
        height = 250
        if format_obj.renders and len(format_obj.renders) > 0:
            first_render = format_obj.renders[0]
            # Handle both dict and object access
            dimensions = (
                first_render.get("dimensions")
                if isinstance(first_render, dict)
                else getattr(first_render, "dimensions", None)
            )
            if dimensions:
                dim_width = (
                    dimensions.get("width") if isinstance(dimensions, dict) else getattr(dimensions, "width", None)
                )
                dim_height = (
                    dimensions.get("height") if isinstance(dimensions, dict) else getattr(dimensions, "height", None)
                )
                if dim_width is not None:
                    width = int(dim_width)
                if dim_height is not None:
                    height = int(dim_height)
        return width, height

    def get_manifest_assets(self, manifest: Any) -> dict[str, Any]:
        """Extract assets dictionary from manifest.

        Args:
            manifest: Creative manifest (dict, Pydantic object, or None)

        Returns:
            Dictionary of asset_id -> asset_data
        """
        if manifest is None:
            return {}
        if isinstance(manifest, dict):
            assets: dict[str, Any] = manifest.get("assets", {})
            return assets
        if hasattr(manifest, "assets"):
            assets_obj: dict[str, Any] = manifest.assets
            return assets_obj
        raise TypeError(f"Invalid manifest type: {type(manifest)}")

    def build_asset_type_map(self, format_obj: Any) -> dict[str, str]:
        """Build asset_id -> asset_type mapping from format specification.

        This allows us to determine asset types without storing them in the manifest.

        Args:
            format_obj: Format definition

        Returns:
            Dictionary mapping asset_id to asset_type string
        """
        asset_type_map = {}
        if hasattr(format_obj, "assets_required") and format_obj.assets_required:
            for required_asset in format_obj.assets_required:
                # Handle both dict and object access
                if isinstance(required_asset, dict):
                    asset_id = required_asset.get("asset_id")
                    asset_type = required_asset.get("asset_type")
                else:
                    asset_id = getattr(required_asset, "asset_id", None)
                    asset_type = getattr(required_asset, "asset_type", None)

                if asset_id and asset_type:
                    # Handle enum or string asset_type
                    if hasattr(asset_type, "value"):
                        asset_type_map[asset_id] = asset_type.value
                    else:
                        asset_type_map[asset_id] = str(asset_type)
        return asset_type_map

    def find_asset_by_type(
        self, manifest_assets: dict[str, Any], asset_type_map: dict[str, str], target_type: str
    ) -> Any | None:
        """Find first asset matching the target type.

        Args:
            manifest_assets: Assets from manifest
            asset_type_map: Mapping of asset_id -> asset_type
            target_type: Type to search for (e.g., "image", "url")

        Returns:
            Asset data or None if not found
        """
        for asset_id, asset_data in manifest_assets.items():
            if asset_type_map.get(asset_id) == target_type:
                return asset_data
        return None

    def wrap_with_document(self, title: str, body_html: str, body_style: str = "") -> str:
        """Wrap HTML content in a full HTML document.

        Args:
            title: Page title
            body_html: HTML content for body
            body_style: Optional inline CSS for body tag

        Returns:
            Complete HTML document
        """
        style_attr = f' style="{body_style}"' if body_style else ""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body{style_attr}>
{body_html}
</body>
</html>"""
