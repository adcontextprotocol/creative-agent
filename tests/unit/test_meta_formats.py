"""Tests for meta format definitions."""

from creative_agent.data.standard_formats import AGENT_URL, META_FORMATS, filter_formats
from creative_agent.schemas_generated._schemas_v1_core_format_json import AssetType, FormatId, Type


class TestMetaFormatsExist:
    """Test that all meta formats are properly defined."""

    def test_product_card_standard_exists(self):
        """Product card standard format is defined."""
        format_id = FormatId(agent_url=AGENT_URL, id="product_card_standard")
        results = filter_formats(format_ids=[format_id])
        assert len(results) == 1
        fmt = results[0]
        assert fmt.format_id.id == "product_card_standard"
        assert fmt.name == "Product Card - Standard"
        assert fmt.type == Type.display

    def test_product_card_detailed_exists(self):
        """Product card detailed format is defined."""
        format_id = FormatId(agent_url=AGENT_URL, id="product_card_detailed")
        results = filter_formats(format_ids=[format_id])
        assert len(results) == 1
        fmt = results[0]
        assert fmt.format_id.id == "product_card_detailed"
        assert fmt.name == "Product Card - Detailed"
        assert fmt.type == Type.display

    def test_format_card_standard_exists(self):
        """Format card standard format is defined."""
        format_id = FormatId(agent_url=AGENT_URL, id="format_card_standard")
        results = filter_formats(format_ids=[format_id])
        assert len(results) == 1
        fmt = results[0]
        assert fmt.format_id.id == "format_card_standard"
        assert fmt.name == "Format Card - Standard"
        assert fmt.type == Type.display

    def test_format_card_detailed_exists(self):
        """Format card detailed format is defined."""
        format_id = FormatId(agent_url=AGENT_URL, id="format_card_detailed")
        results = filter_formats(format_ids=[format_id])
        assert len(results) == 1
        fmt = results[0]
        assert fmt.format_id.id == "format_card_detailed"
        assert fmt.name == "Format Card - Detailed"
        assert fmt.type == Type.display


class TestProductCardStandard:
    """Test product_card_standard format details."""

    def test_has_fixed_dimensions(self):
        """Product card standard has fixed 300x400 dimensions."""
        format_id = FormatId(agent_url=AGENT_URL, id="product_card_standard")
        results = filter_formats(format_ids=[format_id])
        fmt = results[0]
        assert fmt.renders
        assert len(fmt.renders) == 1
        assert fmt.renders[0].dimensions.width == 300
        assert fmt.renders[0].dimensions.height == 400
        assert fmt.renders[0].dimensions.responsive.width is False
        assert fmt.renders[0].dimensions.responsive.height is False

    def test_requires_product_asset(self):
        """Product card standard requires promoted_offerings asset."""
        format_id = FormatId(agent_url=AGENT_URL, id="product_card_standard")
        results = filter_formats(format_ids=[format_id])
        fmt = results[0]
        assert fmt.assets_required
        assert len(fmt.assets_required) == 1
        asset = fmt.assets_required[0]
        assert asset.asset_id == "product"
        assert asset.asset_type == AssetType.promoted_offerings
        assert asset.required is True


class TestProductCardDetailed:
    """Test product_card_detailed format details."""

    def test_has_responsive_dimensions(self):
        """Product card detailed has responsive dimensions."""
        format_id = FormatId(agent_url=AGENT_URL, id="product_card_detailed")
        results = filter_formats(format_ids=[format_id])
        fmt = results[0]
        assert fmt.renders
        assert len(fmt.renders) == 1
        assert fmt.renders[0].dimensions.width is None
        assert fmt.renders[0].dimensions.height is None
        assert fmt.renders[0].dimensions.responsive.width is True
        assert fmt.renders[0].dimensions.responsive.height is True

    def test_requires_product_asset(self):
        """Product card detailed requires promoted_offerings asset."""
        format_id = FormatId(agent_url=AGENT_URL, id="product_card_detailed")
        results = filter_formats(format_ids=[format_id])
        fmt = results[0]
        assert fmt.assets_required
        assert len(fmt.assets_required) == 1
        asset = fmt.assets_required[0]
        assert asset.asset_id == "product"
        assert asset.asset_type == AssetType.promoted_offerings
        assert asset.required is True


class TestFormatCardStandard:
    """Test format_card_standard format details."""

    def test_has_fixed_dimensions(self):
        """Format card standard has fixed 300x400 dimensions."""
        format_id = FormatId(agent_url=AGENT_URL, id="format_card_standard")
        results = filter_formats(format_ids=[format_id])
        fmt = results[0]
        assert fmt.renders
        assert len(fmt.renders) == 1
        assert fmt.renders[0].dimensions.width == 300
        assert fmt.renders[0].dimensions.height == 400
        assert fmt.renders[0].dimensions.responsive.width is False
        assert fmt.renders[0].dimensions.responsive.height is False

    def test_requires_format_asset(self):
        """Format card standard requires text asset for format specification."""
        format_id = FormatId(agent_url=AGENT_URL, id="format_card_standard")
        results = filter_formats(format_ids=[format_id])
        fmt = results[0]
        assert fmt.assets_required
        assert len(fmt.assets_required) == 1
        asset = fmt.assets_required[0]
        assert asset.asset_id == "format"
        assert asset.asset_type == AssetType.text
        assert asset.required is True


class TestFormatCardDetailed:
    """Test format_card_detailed format details."""

    def test_has_responsive_dimensions(self):
        """Format card detailed has responsive dimensions."""
        format_id = FormatId(agent_url=AGENT_URL, id="format_card_detailed")
        results = filter_formats(format_ids=[format_id])
        fmt = results[0]
        assert fmt.renders
        assert len(fmt.renders) == 1
        assert fmt.renders[0].dimensions.width is None
        assert fmt.renders[0].dimensions.height is None
        assert fmt.renders[0].dimensions.responsive.width is True
        assert fmt.renders[0].dimensions.responsive.height is True

    def test_requires_format_asset(self):
        """Format card detailed requires text asset for format specification."""
        format_id = FormatId(agent_url=AGENT_URL, id="format_card_detailed")
        results = filter_formats(format_ids=[format_id])
        fmt = results[0]
        assert fmt.assets_required
        assert len(fmt.assets_required) == 1
        asset = fmt.assets_required[0]
        assert asset.asset_id == "format"
        assert asset.asset_type == AssetType.text
        assert asset.required is True


class TestMetaFormatsFiltering:
    """Test filtering behavior with meta formats."""

    def test_filter_by_300x400_dimensions(self):
        """Filter by 300x400 returns both standard card formats."""
        results = filter_formats(dimensions="300x400")
        assert len(results) == 2
        result_ids = {fmt.format_id.id for fmt in results}
        assert "product_card_standard" in result_ids
        assert "format_card_standard" in result_ids

    def test_filter_by_name_card(self):
        """Name search for 'card' returns all meta formats."""
        results = filter_formats(name_search="card")
        meta_format_ids = {fmt.format_id.id for fmt in results if "card" in fmt.format_id.id}
        assert "product_card_standard" in meta_format_ids
        assert "product_card_detailed" in meta_format_ids
        assert "format_card_standard" in meta_format_ids
        assert "format_card_detailed" in meta_format_ids

    def test_filter_by_responsive(self):
        """Filter by responsive=True returns detailed card formats."""
        results = filter_formats(is_responsive=True)
        meta_responsive = [fmt for fmt in results if "card" in fmt.format_id.id and "detailed" in fmt.format_id.id]
        assert len(meta_responsive) == 2
        result_ids = {fmt.format_id.id for fmt in meta_responsive}
        assert "product_card_detailed" in result_ids
        assert "format_card_detailed" in result_ids

    def test_filter_by_promoted_offerings_asset(self):
        """Filter by promoted_offerings asset type returns product cards."""
        results = filter_formats(asset_types=[AssetType.promoted_offerings])
        product_cards = [fmt for fmt in results if "product_card" in fmt.format_id.id]
        assert len(product_cards) == 2
        result_ids = {fmt.format_id.id for fmt in product_cards}
        assert "product_card_standard" in result_ids
        assert "product_card_detailed" in result_ids


class TestMetaFormatsCount:
    """Test that meta formats are included in total count."""

    def test_meta_formats_list_has_four_items(self):
        """META_FORMATS constant has exactly 4 formats."""
        assert len(META_FORMATS) == 4

    def test_all_formats_includes_meta(self):
        """All formats includes meta formats."""
        all_formats = filter_formats()
        meta_formats = [fmt for fmt in all_formats if "card" in fmt.format_id.id]
        assert len(meta_formats) >= 4
        # Verify all four are present
        meta_ids = {fmt.format_id.id for fmt in meta_formats}
        assert "product_card_standard" in meta_ids
        assert "product_card_detailed" in meta_ids
        assert "format_card_standard" in meta_ids
        assert "format_card_detailed" in meta_ids
