"""Tests for validate_manifest_assets with repeatable group assets.

The universal format uses repeatable groups (Assets5) for pools like headlines,
descriptions, and images. These are submitted as lists in the manifest and require
different validation logic from individual (scalar) assets.
"""

from adcp import FormatId
from pydantic import AnyUrl

from creative_agent.data.standard_formats import AGENT_URL, get_format_by_id
from creative_agent.validation import validate_manifest_assets


def _universal_fmt():
    fmt_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="universal")
    fmt = get_format_by_id(fmt_id)
    assert fmt is not None
    return fmt


def _valid_manifest() -> dict:
    return {
        "format_id": {"agent_url": str(AGENT_URL), "id": "universal"},
        "assets": {
            "brand_name": {"content": "Acme Corp"},
            "headlines": [{"text": {"content": "Shop Now"}}, {"text": {"content": "Save Big"}}],
            "descriptions": [{"text": {"content": "Best deals on widgets"}}],
            "images_landscape": [{"image": {"url": "https://example.com/img.jpg"}}],
            "images_square": [{"image": {"url": "https://example.com/sq.jpg"}}],
            "click_url": {"url": "https://example.com"},
        },
    }


class TestRequiredGroupsEnforced:
    """Required repeatable groups must be present in the manifest."""

    def test_valid_manifest_has_no_errors(self):
        errors = validate_manifest_assets(_valid_manifest(), format_obj=_universal_fmt())
        assert errors == [], f"Unexpected errors: {errors}"

    def test_missing_headlines_is_an_error(self):
        manifest = _valid_manifest()
        del manifest["assets"]["headlines"]
        errors = validate_manifest_assets(manifest, format_obj=_universal_fmt())
        assert any("headlines" in e for e in errors), f"Expected headlines error, got: {errors}"

    def test_missing_descriptions_is_an_error(self):
        manifest = _valid_manifest()
        del manifest["assets"]["descriptions"]
        errors = validate_manifest_assets(manifest, format_obj=_universal_fmt())
        assert any("descriptions" in e for e in errors), f"Expected descriptions error, got: {errors}"

    def test_missing_images_landscape_is_an_error(self):
        manifest = _valid_manifest()
        del manifest["assets"]["images_landscape"]
        errors = validate_manifest_assets(manifest, format_obj=_universal_fmt())
        assert any("images_landscape" in e for e in errors), f"Expected images_landscape error, got: {errors}"

    def test_missing_images_square_is_an_error(self):
        manifest = _valid_manifest()
        del manifest["assets"]["images_square"]
        errors = validate_manifest_assets(manifest, format_obj=_universal_fmt())
        assert any("images_square" in e for e in errors), f"Expected images_square error, got: {errors}"

    def test_missing_brand_name_is_an_error(self):
        manifest = _valid_manifest()
        del manifest["assets"]["brand_name"]
        errors = validate_manifest_assets(manifest, format_obj=_universal_fmt())
        assert any("brand_name" in e for e in errors), f"Expected brand_name error, got: {errors}"

    def test_missing_click_url_is_an_error(self):
        manifest = _valid_manifest()
        del manifest["assets"]["click_url"]
        errors = validate_manifest_assets(manifest, format_obj=_universal_fmt())
        assert any("click_url" in e for e in errors), f"Expected click_url error, got: {errors}"


class TestOptionalGroupsNotRequired:
    """Optional repeatable groups may be omitted without error."""

    def test_absent_long_headlines_is_fine(self):
        errors = validate_manifest_assets(_valid_manifest(), format_obj=_universal_fmt())
        assert not any("long_headlines" in e for e in errors)

    def test_absent_videos_is_fine(self):
        errors = validate_manifest_assets(_valid_manifest(), format_obj=_universal_fmt())
        assert not any("video" in e for e in errors)

    def test_absent_logos_is_fine(self):
        errors = validate_manifest_assets(_valid_manifest(), format_obj=_universal_fmt())
        assert not any("logo" in e for e in errors)


class TestGroupCountConstraints:
    """min_count and max_count for repeatable groups must be enforced."""

    def test_empty_required_group_fails_min_count(self):
        manifest = _valid_manifest()
        manifest["assets"]["headlines"] = []
        errors = validate_manifest_assets(manifest, format_obj=_universal_fmt())
        assert any("headlines" in e and "at least" in e for e in errors), f"Expected min_count error: {errors}"

    def test_single_item_satisfies_min_count(self):
        manifest = _valid_manifest()
        manifest["assets"]["headlines"] = [{"text": {"content": "One headline"}}]
        errors = validate_manifest_assets(manifest, format_obj=_universal_fmt())
        assert not any("headlines" in e and "at least" in e for e in errors)

    def test_exceeding_max_count_fails(self):
        manifest = _valid_manifest()
        manifest["assets"]["headlines"] = [{"text": {"content": f"Headline {i}"}} for i in range(16)]
        errors = validate_manifest_assets(manifest, format_obj=_universal_fmt())
        assert any("headlines" in e and "at most" in e for e in errors), f"Expected max_count error: {errors}"

    def test_at_max_count_is_valid(self):
        manifest = _valid_manifest()
        manifest["assets"]["headlines"] = [{"text": {"content": f"Headline {i}"}} for i in range(15)]
        errors = validate_manifest_assets(manifest, format_obj=_universal_fmt())
        assert not any("headlines" in e and "at most" in e for e in errors)


class TestGroupItemValidation:
    """Each item within a repeatable group must be validated."""

    def test_invalid_text_content_in_group_is_caught(self):
        manifest = _valid_manifest()
        manifest["assets"]["headlines"] = [{"text": {"content": ""}}]
        errors = validate_manifest_assets(manifest, format_obj=_universal_fmt())
        assert any("headlines[0]" in e for e in errors), f"Expected item error: {errors}"

    def test_invalid_image_url_in_group_is_caught(self):
        manifest = _valid_manifest()
        manifest["assets"]["images_landscape"] = [{"image": {"url": "not-a-url"}}]
        errors = validate_manifest_assets(manifest, format_obj=_universal_fmt())
        assert any("images_landscape[0]" in e for e in errors), f"Expected item error: {errors}"

    def test_malformed_item_structure_is_caught(self):
        manifest = _valid_manifest()
        manifest["assets"]["headlines"] = ["just a string"]
        errors = validate_manifest_assets(manifest, format_obj=_universal_fmt())
        assert any("headlines[0]" in e for e in errors), f"Expected malformed item error: {errors}"

    def test_second_item_error_is_reported(self):
        manifest = _valid_manifest()
        manifest["assets"]["headlines"] = [
            {"text": {"content": "Valid headline"}},
            {"text": {"content": ""}},
        ]
        errors = validate_manifest_assets(manifest, format_obj=_universal_fmt())
        assert any("headlines[1]" in e for e in errors), f"Expected error on second item: {errors}"
