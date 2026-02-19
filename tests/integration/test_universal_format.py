"""Integration tests for the universal creative format.

The universal format is a multi-channel asset pool — similar to Google's Performance Max
asset groups — where publishers pick the best combination for each placement.
"""

from adcp import FormatCategory, FormatId, ListCreativeFormatsResponse, get_required_assets
from pydantic import AnyUrl

from creative_agent import server
from creative_agent.data.standard_formats import (
    AGENT_URL,
    STANDARD_FORMATS,
    get_format_by_id,
)
from creative_agent.schemas import CreativeFormat

# Get actual function from FastMCP wrapper
list_creative_formats = server.list_creative_formats.fn
build_creative = server.build_creative.fn


def _asset_identifier(asset) -> str:
    """Return the identifier for an asset, handling both individual and repeatable group types."""
    return getattr(asset, "asset_id", None) or getattr(asset, "asset_group_id", None) or ""


class TestUniversalFormatDiscovery:
    """Test that the universal format is discoverable and schema-compliant."""

    def test_universal_format_in_standard_formats(self):
        """STANDARD_FORMATS should include the universal format."""
        ids = {f.format_id.id for f in STANDARD_FORMATS}
        assert "universal" in ids

    def test_universal_format_schema_compliance(self):
        """Universal format must validate against the CreativeFormat schema."""
        fmt_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="universal")
        fmt = get_format_by_id(fmt_id)

        assert fmt is not None, "universal format not found"

        fmt_dict = fmt.model_dump(mode="json", exclude_none=True)
        # Raises ValidationError if schema is violated
        CreativeFormat.model_validate(fmt_dict)

    def test_universal_format_in_list_response(self):
        """list_creative_formats() must return the universal format with a valid response."""
        result = list_creative_formats()

        assert result.structured_content, "structured_content should not be empty"
        response = ListCreativeFormatsResponse.model_validate(result.structured_content)

        fmt_ids = {f.format_id.id for f in response.formats}
        assert "universal" in fmt_ids, f"universal not found in {fmt_ids}"

    def test_universal_format_type_filter(self):
        """Filtering by type=universal returns exactly the universal format."""
        result = list_creative_formats(type="universal")

        response = ListCreativeFormatsResponse.model_validate(result.structured_content)
        assert len(response.formats) == 1, f"Expected 1 universal format, got {len(response.formats)}"
        assert response.formats[0].format_id.id == "universal"

    def test_universal_format_type_is_universal(self):
        """Universal format must have type=universal."""
        fmt_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="universal")
        fmt = get_format_by_id(fmt_id)

        assert fmt is not None
        assert fmt.type == FormatCategory.universal


class TestUniversalFormatStructure:
    """Test universal format asset and render structure."""

    def _get_format(self):
        fmt_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="universal")
        fmt = get_format_by_id(fmt_id)
        assert fmt is not None, "universal format not found"
        return fmt

    def test_no_renders(self):
        """Universal format must not have fixed renders (it's a template)."""
        fmt = self._get_format()

        renders = getattr(fmt, "renders", None)
        assert renders is None or len(renders) == 0, "universal template should not have renders"

    def test_no_output_format_ids(self):
        """Universal is a submission container, not a generative format — no output_format_ids."""
        fmt = self._get_format()

        output_ids = getattr(fmt, "output_format_ids", None)
        assert output_ids is None or len(output_ids) == 0, (
            "universal should not have output_format_ids (it is not a generative format)"
        )

    def test_required_text_assets_present(self):
        """Required text assets: brand_name (individual), headlines and descriptions (groups)."""
        fmt = self._get_format()

        required_ids = {_asset_identifier(a) for a in get_required_assets(fmt)}
        for expected in ("brand_name", "headlines", "descriptions"):
            assert expected in required_ids, f"'{expected}' must be required"

    def test_required_image_assets_present(self):
        """Required image groups: images_landscape, images_square."""
        fmt = self._get_format()

        required_ids = {_asset_identifier(a) for a in get_required_assets(fmt)}
        for expected in ("images_landscape", "images_square"):
            assert expected in required_ids, f"'{expected}' must be required"

    def test_click_url_is_required(self):
        """click_url must be a required individual asset."""
        fmt = self._get_format()

        required_ids = {_asset_identifier(a) for a in get_required_assets(fmt)}
        assert "click_url" in required_ids, "click_url must be required"

    def test_optional_groups_present(self):
        """Optional repeatable groups (logos, videos, etc.) must be defined."""
        fmt = self._get_format()

        all_ids = {_asset_identifier(a) for a in (fmt.assets or [])}

        for optional in (
            "long_headlines",
            "images_portrait",
            "logos_square",
            "logos_landscape",
            "videos_landscape",
            "videos_portrait",
            "videos_square",
        ):
            assert optional in all_ids, f"'{optional}' should be defined as an optional group"

    def test_optional_individual_assets_present(self):
        """Optional individual assets (cta, promoted_offerings, impression_tracker) must be defined."""
        fmt = self._get_format()

        all_ids = {_asset_identifier(a) for a in (fmt.assets or [])}
        for optional in ("cta", "promoted_offerings", "impression_tracker"):
            assert optional in all_ids, f"'{optional}' should be defined as an optional asset"

    def test_promoted_offerings_is_optional(self):
        """promoted_offerings must be optional (not all advertisers have a product catalog)."""
        fmt = self._get_format()

        po_asset = next(
            (a for a in (fmt.assets or []) if getattr(a, "asset_id", None) == "promoted_offerings"),
            None,
        )
        assert po_asset is not None, "promoted_offerings asset must be defined"
        assert po_asset.required is False, "promoted_offerings must be optional"

    def test_video_orientations_are_separate_groups(self):
        """Video landscape and portrait must be separate repeatable groups."""
        fmt = self._get_format()

        all_ids = {_asset_identifier(a) for a in (fmt.assets or [])}
        assert "videos_landscape" in all_ids, "videos_landscape group must exist"
        assert "videos_portrait" in all_ids, "videos_portrait group must exist"
        # No singular old-style video slot
        assert "video" not in all_ids, "generic 'video' slot should not exist"
        assert "video_landscape" not in all_ids, "old-style 'video_landscape' should not exist"

    def test_repeatable_groups_have_correct_counts(self):
        """Repeatable groups must have correct min/max counts."""
        fmt = self._get_format()

        groups = {
            _asset_identifier(a): a for a in (fmt.assets or []) if getattr(a, "item_type", None) == "repeatable_group"
        }

        assert groups["headlines"].min_count == 1
        assert groups["headlines"].max_count == 15
        assert groups["headlines"].required is True

        assert groups["descriptions"].min_count == 1
        assert groups["descriptions"].max_count == 5
        assert groups["descriptions"].required is True

        assert groups["images_landscape"].min_count == 1
        assert groups["images_landscape"].max_count == 20
        assert groups["images_landscape"].required is True

        assert groups["images_square"].min_count == 1
        assert groups["images_square"].max_count == 20

        assert groups["long_headlines"].min_count == 0
        assert groups["long_headlines"].max_count == 5
        assert groups["long_headlines"].required is False

        assert groups["videos_portrait"].min_count == 0
        assert groups["videos_portrait"].max_count == 15


class TestBuildCreativeUniversal:
    """Test build_creative behavior for universal format (no Gemini calls needed)."""

    def test_build_creative_universal_returns_manifest_as_is(self):
        """Universal is not a generative format, so build_creative returns the manifest unchanged."""
        manifest = {
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

        result = build_creative(
            target_format_id="universal",
            creative_manifest=manifest,
        )

        # No error — universal is not generative, so it just returns the manifest
        assert result.structured_content is not None
        assert "error" not in result.structured_content
        assert "creative_manifest" in result.structured_content
