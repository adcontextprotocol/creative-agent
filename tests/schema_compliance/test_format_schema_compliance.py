"""
Test that our format responses actually match the AdCP schemas.

When schemas change, these tests ensure our code stays in sync.
"""

import pytest
from pydantic import ValidationError

from src.creative_agent.data.standard_formats import STANDARD_FORMATS
from src.creative_agent.schemas import CreativeFormat, ListCreativeFormatsResponse


def test_all_standard_formats_validate_against_schema():
    """Every format in STANDARD_FORMATS must validate against the Format schema."""
    errors = []

    for format_obj in STANDARD_FORMATS:
        try:
            # Convert Pydantic model to dict and validate
            format_dict = format_obj.model_dump(mode="json", by_alias=True, exclude_none=True)
            CreativeFormat.model_validate(format_dict)
        except ValidationError as e:
            errors.append(f"Format {format_obj.format_id} failed validation:\n{e}")

    if errors:
        pytest.fail("\n\n".join(errors))


def test_list_creative_formats_response_validates():
    """The response from list_creative_formats must validate against schema."""
    from src.creative_agent.data.standard_formats import AGENT_CAPABILITIES, AGENT_NAME

    # Build the response structure that list_creative_formats returns
    response_data = {
        "formats": [fmt.model_dump(mode="json", by_alias=True, exclude_none=True) for fmt in STANDARD_FORMATS],
        "creative_agents": [
            {
                "agent_url": "https://creative.adcontextprotocol.org",
                "agent_name": AGENT_NAME,
                "capabilities": AGENT_CAPABILITIES,
            }
        ],
    }

    # Validate against schema
    try:
        ListCreativeFormatsResponse.model_validate(response_data)
    except ValidationError as e:
        pytest.fail(f"list_creative_formats response failed schema validation:\n{e}")


def test_format_has_required_fields():
    """Ensure all formats have required fields per schema."""
    required_fields = {"format_id", "name", "type"}

    for format_obj in STANDARD_FORMATS:
        format_dict = format_obj.model_dump(mode="json", by_alias=True, exclude_none=True)
        missing = required_fields - set(format_dict.keys())
        if missing:
            pytest.fail(f"Format {format_obj.format_id} missing required fields: {missing}")


def test_format_ids_are_structured():
    """
    Verify that any format_id references in formats are structured objects.

    This catches regressions where we might use string IDs instead of
    structured {agent_url, id} objects.
    """
    for format_obj in STANDARD_FORMATS:
        format_dict = format_obj.model_dump(mode="json", by_alias=True, exclude_none=True)
        # Check output_format_ids if present
        if "output_format_ids" in format_dict:
            output_ids = format_dict["output_format_ids"]
            if output_ids:  # Skip if empty list
                # Each should be a dict with agent_url and id
                for output_id in output_ids:
                    if not isinstance(output_id, dict):
                        pytest.fail(
                            f"Format {format_obj.format_id} has non-structured output_format_id: {output_id}. "
                            "Should be {{agent_url: str, id: str}}"
                        )
                    if "agent_url" not in output_id or "id" not in output_id:
                        pytest.fail(
                            f"Format {format_obj.format_id} has incomplete format_id structure: {output_id}. "
                            "Must have both agent_url and id fields"
                        )


def test_asset_requirements_match_schema():
    """Verify assets_required field structure matches schema."""
    for format_obj in STANDARD_FORMATS:
        format_dict = format_obj.model_dump(mode="json", by_alias=True, exclude_none=True)
        if "assets_required" not in format_dict:
            continue

        for idx, asset_req in enumerate(format_dict["assets_required"]):
            # Check if it's a repeatable group
            if "repeatable" in asset_req:
                required_group_fields = {"asset_group_id", "repeatable", "min_count", "max_count", "assets"}
                missing = required_group_fields - set(asset_req.keys())
                if missing:
                    pytest.fail(
                        f"Format {format_obj.format_id} asset_required[{idx}] is repeatable but missing: {missing}"
                    )
            else:
                # Individual asset
                required_asset_fields = {"asset_id", "asset_type"}
                missing = required_asset_fields - set(asset_req.keys())
                if missing:
                    pytest.fail(
                        f"Format {format_obj.format_id} asset_required[{idx}] missing required fields: {missing}"
                    )


def test_enum_values_match_schema():
    """Verify enum values match what's in the schema."""
    valid_types = {"audio", "video", "display", "native", "dooh", "rich_media", "universal"}
    valid_categories = {"standard", "custom"}

    for format_obj in STANDARD_FORMATS:
        format_dict = format_obj.model_dump(mode="json", by_alias=True, exclude_none=True)
        # Check type enum
        if "type" in format_dict:
            if format_dict["type"] not in valid_types:
                pytest.fail(
                    f"Format {format_obj.format_id} has invalid type '{format_dict['type']}'. "
                    f"Valid types: {valid_types}"
                )

        # Check category enum
        if "category" in format_dict:
            if format_dict["category"] not in valid_categories:
                pytest.fail(
                    f"Format {format_obj.format_id} has invalid category '{format_dict['category']}'. "
                    f"Valid categories: {valid_categories}"
                )
