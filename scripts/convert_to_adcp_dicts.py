#!/usr/bin/env python3
"""Convert AssetRequirement and FormatRequirements to AdCP-compliant dicts."""

import re
from pathlib import Path


def convert_asset_requirement(match: re.Match) -> str:
    """Convert AssetRequirement(...) to AdCP dict format."""
    content = match.group(1)

    # Extract fields
    asset_role = re.search(r'asset_role="([^"]+)"', content)
    asset_type = re.search(r'asset_type="([^"]+)"', content)
    required = re.search(r"required=(\w+)", content)

    # Build dict
    result = "{\n"

    # asset_id = asset_role
    if asset_role:
        result += f'                "asset_id": "{asset_role.group(1)}",\n'
        result += f'                "asset_type": "{asset_type.group(1) if asset_type else "text"}",\n'
        result += f'                "asset_role": "{asset_role.group(1)}",\n'

    if required:
        result += f'                "required": {required.group(1)},\n'

    # Collect other fields into requirements dict
    req_dict = {}
    for line in content.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Skip already handled fields
        if any(x in line for x in ["asset_role=", "asset_type=", "required="]):
            continue
        # Extract field name and value
        if "=" in line:
            field_match = re.match(r"(\w+)=(.+?)(?:,|$)", line)
            if field_match:
                field_name = field_match.group(1)
                field_value = field_match.group(2).strip(",")
                req_dict[field_name] = field_value

    if req_dict:
        result += '                "requirements": {\n'
        for name, value in req_dict.items():
            result += f'                    "{name}": {value},\n'
        result += "                },\n"

    result += "            }"
    return result


def convert_format_requirements(match: re.Match) -> str:
    """Convert FormatRequirements(...) to dict."""
    content = match.group(1)

    result = "{\n"
    for line in content.split("\n"):
        line = line.strip()
        if not line or line == ")":
            continue
        # Extract field name and value
        field_match = re.match(r"(\w+)=(.+?)(?:,|$)", line)
        if field_match:
            field_name = field_match.group(1)
            field_value = field_match.group(2).strip(",")
            result += f'            "{field_name}": {field_value},\n'
    result += "        }"
    return result


def main():
    file_path = Path(__file__).parent.parent / "src/creative_agent/data/standard_formats.py"
    content = file_path.read_text()

    # Remove imports
    content = re.sub(
        r"from \.\.schemas import AssetRequirement, CreativeFormat, FormatRequirements",
        "from ..schemas import CreativeFormat",
        content,
    )

    # Convert AssetRequirement
    content = re.sub(
        r"AssetRequirement\(((?:[^()]|\([^)]*\))*)\)",
        convert_asset_requirement,
        content,
        flags=re.MULTILINE | re.DOTALL,
    )

    # Convert FormatRequirements
    content = re.sub(
        r"FormatRequirements\(((?:[^()]|\([^)]*\))*)\)",
        convert_format_requirements,
        content,
        flags=re.MULTILINE | re.DOTALL,
    )

    # Fix dimensions field (move to requirements)
    # This is complex, so we'll do it manually after

    file_path.write_text(content)
    print(f"✓ Converted {file_path}")


if __name__ == "__main__":
    main()
