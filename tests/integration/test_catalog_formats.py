"""Integration tests for catalog-aware format definitions.

Generative formats declare catalog_requirements instead of a promoted_offerings
asset. This verifies the format definitions are correctly structured per ADCP 3.5.0.
"""

from adcp import CatalogType, FormatId, get_format_assets
from pydantic import AnyUrl

from creative_agent.data.standard_formats import AGENT_URL, STANDARD_FORMATS, get_format_by_id

# All generative format IDs (template + concrete)
GENERATIVE_TEMPLATE_ID = "display_generative"
GENERATIVE_CONCRETE_IDS = [
    "display_300x250_generative",
    "display_728x90_generative",
    "display_160x600_generative",
    "display_320x50_generative",
    "display_336x280_generative",
    "display_300x600_generative",
    "display_970x250_generative",
]
ALL_GENERATIVE_IDS = [GENERATIVE_TEMPLATE_ID, *GENERATIVE_CONCRETE_IDS]


class TestGenerativeFormatCatalogRequirements:
    """Generative formats must declare catalog_requirements."""

    def test_generative_formats_have_catalog_requirements(self):
        """Each generative format must have catalog_requirements."""
        for fmt_id_str in ALL_GENERATIVE_IDS:
            fmt_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id=fmt_id_str)
            fmt = get_format_by_id(fmt_id)
            assert fmt is not None, f"{fmt_id_str} not found"

            reqs = getattr(fmt, "catalog_requirements", None)
            assert reqs is not None, f"{fmt_id_str}: must have catalog_requirements"
            assert len(reqs) > 0, f"{fmt_id_str}: catalog_requirements must not be empty"

    def test_catalog_requirements_type_is_offering(self):
        """Generative formats require an offering catalog."""
        for fmt_id_str in ALL_GENERATIVE_IDS:
            fmt_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id=fmt_id_str)
            fmt = get_format_by_id(fmt_id)

            reqs = fmt.catalog_requirements
            assert reqs[0].catalog_type == CatalogType.offering, f"{fmt_id_str}: catalog_type must be 'offering'"

    def test_catalog_requirements_required_fields(self):
        """Offering catalog should require at least the 'name' field."""
        for fmt_id_str in ALL_GENERATIVE_IDS:
            fmt_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id=fmt_id_str)
            fmt = get_format_by_id(fmt_id)

            reqs = fmt.catalog_requirements
            required_fields = reqs[0].required_fields or []
            assert "name" in required_fields, f"{fmt_id_str}: catalog should require 'name' field"


class TestGenerativeFormatAssets:
    """Generative formats must still have generation_prompt and impression_tracker."""

    def test_generative_formats_have_generation_prompt(self):
        """Each generative format must have a generation_prompt asset."""
        for fmt_id_str in ALL_GENERATIVE_IDS:
            fmt_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id=fmt_id_str)
            fmt = get_format_by_id(fmt_id)

            asset_ids = {getattr(a, "asset_id", None) for a in get_format_assets(fmt)}
            assert "generation_prompt" in asset_ids, f"{fmt_id_str}: must have generation_prompt asset"

    def test_generative_formats_have_impression_tracker(self):
        """Each generative format must have an impression_tracker asset."""
        for fmt_id_str in ALL_GENERATIVE_IDS:
            fmt_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id=fmt_id_str)
            fmt = get_format_by_id(fmt_id)

            asset_ids = {getattr(a, "asset_id", None) for a in get_format_assets(fmt)}
            assert "impression_tracker" in asset_ids, f"{fmt_id_str}: must have impression_tracker asset"

    def test_generative_formats_do_not_have_promoted_offerings(self):
        """No format should have a promoted_offerings asset."""
        for fmt in STANDARD_FORMATS:
            asset_ids = {getattr(a, "asset_id", None) for a in get_format_assets(fmt)}
            assert "promoted_offerings" not in asset_ids, f"{fmt.format_id.id}: must NOT have promoted_offerings asset"


class TestCatalogRequirementsSerialization:
    """catalog_requirements must serialize correctly for ADCP wire format."""

    def test_catalog_requirements_roundtrip(self):
        """catalog_requirements should serialize and validate."""
        fmt_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id=GENERATIVE_TEMPLATE_ID)
        fmt = get_format_by_id(fmt_id)

        fmt_dict = fmt.model_dump(mode="json", exclude_none=True)

        assert "catalog_requirements" in fmt_dict
        reqs = fmt_dict["catalog_requirements"]
        assert isinstance(reqs, list)
        assert len(reqs) == 1
        assert reqs[0]["catalog_type"] == "offering"
        assert "name" in reqs[0].get("required_fields", [])
