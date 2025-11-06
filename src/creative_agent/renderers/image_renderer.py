"""Renderer for simple image-based display formats."""

import html as html_module
from typing import Any

from ..utils import sanitize_url
from .base import BaseRenderer


class ImageRenderer(BaseRenderer):
    """Renderer for display formats using static images."""

    def render(self, format_obj: Any, manifest: Any, input_set: Any, fragment: bool = True) -> str:
        """Generate HTML preview for image-based display formats.

        Args:
            format_obj: Format definition
            manifest: Creative manifest with assets
            input_set: Preview input configuration
            fragment: If True (default), return HTML fragment. If False, return full document.

        Returns:
            HTML string with image display
        """
        width, height = self.get_dimensions(format_obj)
        manifest_assets = self.get_manifest_assets(manifest)
        asset_type_map = self.build_asset_type_map(format_obj)

        # Find image and click URL
        image_asset = self.find_asset_by_type(manifest_assets, asset_type_map, "image")
        image_url = None
        if image_asset and isinstance(image_asset, dict):
            image_url = image_asset.get("url")

        click_asset = self.find_asset_by_type(manifest_assets, asset_type_map, "url")
        click_url = None
        if click_asset and isinstance(click_asset, dict):
            click_url = click_asset.get("url")

        # Generate HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html_module.escape(format_obj.name)} - {html_module.escape(input_set.name)}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            width: {width}px;
            height: {height}px;
            overflow: hidden;
            font-family: Arial, sans-serif;
        }}
        .creative-container {{
            width: 100%;
            height: 100%;
            position: relative;
            cursor: pointer;
        }}
        .creative-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .preview-label {{
            position: absolute;
            top: 5px;
            left: 5px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 2px 6px;
            font-size: 10px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="creative-container" onclick="handleClick()">
"""

        if image_url:
            safe_image_url = sanitize_url(image_url)
            safe_format_name = html_module.escape(format_obj.name)
            html += f'        <img src="{safe_image_url}" alt="{safe_format_name}">\n'
        else:
            safe_format_name = html_module.escape(format_obj.name)
            html += f'        <div style="background: #f0f0f0; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #666;">{safe_format_name}</div>\n'

        safe_input_name = html_module.escape(input_set.name)
        html += f"""        <div class="preview-label">{safe_input_name}</div>
    </div>
    <script>
        function handleClick() {{
"""

        if click_url:
            safe_click_url = sanitize_url(click_url)
            html += f'            window.open("{safe_click_url}", "_blank");\n'
        else:
            html += '            console.log("Click registered - no URL configured");\n'

        html += """        }
    </script>
</body>
</html>"""

        return html
