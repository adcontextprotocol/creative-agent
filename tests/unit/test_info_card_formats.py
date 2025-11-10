"""Tests for info card format definitions."""

from adcp.types.generated import FormatId

from creative_agent.data.format_types import AssetType
from creative_agent.data.standard_formats import AGENT_URL, INFO_CARD_FORMATS, filter_formats


class TestInfoCardFormatsExist:
    """Test that all info card formats are properly defined."""

    def test_product_card_standard_exists(self):
        """Product card standard format is defined."""
        format_id = FormatId(agent_url=AGENT_URL, id="product_card_standard")
        results = filter_formats(format_ids=[format_id])
        assert len(results) == 1
        fmt = results[0]
        assert fmt.format_id.id == "product_card_standard"
        assert fmt.name == "Product Card - Standard"
        assert fmt.type == "display"

    def test_product_card_detailed_exists(self):
        """Product card detailed format is defined."""
        format_id = FormatId(agent_url=AGENT_URL, id="product_card_detailed")
        results = filter_formats(format_ids=[format_id])
        assert len(results) == 1
        fmt = results[0]
        assert fmt.format_id.id == "product_card_detailed"
        assert fmt.name == "Product Card - Detailed"
        assert fmt.type == "display"

    def test_format_card_standard_exists(self):
        """Format card standard format is defined."""
        format_id = FormatId(agent_url=AGENT_URL, id="format_card_standard")
        results = filter_formats(format_ids=[format_id])
        assert len(results) == 1
        fmt = results[0]
        assert fmt.format_id.id == "format_card_standard"
        assert fmt.name == "Format Card - Standard"
        assert fmt.type == "display"

    def test_format_card_detailed_exists(self):
        """Format card detailed format is defined."""
        format_id = FormatId(agent_url=AGENT_URL, id="format_card_detailed")
        results = filter_formats(format_ids=[format_id])
        assert len(results) == 1
        fmt = results[0]
        assert fmt.format_id.id == "format_card_detailed"
        assert fmt.name == "Format Card - Detailed"
        assert fmt.type == "display"


class TestProductCardStandard:
    """Test product_card_standard format details."""

    def test_has_fixed_dimensions(self):
        """Product card standard has fixed 300x400 dimensions."""
        format_id = FormatId(agent_url=AGENT_URL, id="product_card_standard")
        results = filter_formats(format_ids=[format_id])
        fmt = results[0]
        assert fmt.renders
        assert len(fmt.renders) == 1
        assert fmt.renders[0]["dimensions"]["width"] == 300
        assert fmt.renders[0]["dimensions"]["height"] == 400
        assert fmt.renders[0]["dimensions"]["responsive"]["width"] is False
        assert fmt.renders[0]["dimensions"]["responsive"]["height"] is False

    def test_requires_product_assets(self):
        """Product card standard requires individual product assets."""
        format_id = FormatId(agent_url=AGENT_URL, id="product_card_standard")
        results = filter_formats(format_ids=[format_id])
        fmt = results[0]
        assert fmt.assets_required
        assert len(fmt.assets_required) == 8

        # Check required assets
        asset_ids = {asset["asset_id"] for asset in fmt.assets_required}
        assert "product_image" in asset_ids
        assert "product_name" in asset_ids
        assert "product_description" in asset_ids

        # Check asset types
        asset_type_map = {asset["asset_id"]: asset["asset_type"] for asset in fmt.assets_required}
        assert asset_type_map["product_image"] == "image"
        assert asset_type_map["product_name"] == "text"
        assert asset_type_map["product_description"] == "text"

        # Check required fields
        required_asset_ids = {asset["asset_id"] for asset in fmt.assets_required if asset["required"]}
        assert "product_image" in required_asset_ids
        assert "product_name" in required_asset_ids
        assert "product_description" in required_asset_ids


class TestProductCardDetailed:
    """Test product_card_detailed format details."""

    def test_has_responsive_dimensions(self):
        """Product card detailed has responsive dimensions."""
        format_id = FormatId(agent_url=AGENT_URL, id="product_card_detailed")
        results = filter_formats(format_ids=[format_id])
        fmt = results[0]
        assert fmt.renders
        assert len(fmt.renders) == 1
        assert fmt.renders[0]["dimensions"]["width"] is None
        assert fmt.renders[0]["dimensions"]["height"] is None
        assert fmt.renders[0]["dimensions"]["responsive"]["width"] is True
        assert fmt.renders[0]["dimensions"]["responsive"]["height"] is True

    def test_requires_product_assets(self):
        """Product card detailed requires individual product assets."""
        format_id = FormatId(agent_url=AGENT_URL, id="product_card_detailed")
        results = filter_formats(format_ids=[format_id])
        fmt = results[0]
        assert fmt.assets_required
        assert len(fmt.assets_required) == 8

        # Check required assets
        asset_ids = {asset["asset_id"] for asset in fmt.assets_required}
        assert "product_image" in asset_ids
        assert "product_name" in asset_ids
        assert "product_description" in asset_ids

        # Check asset types
        asset_type_map = {asset["asset_id"]: asset["asset_type"] for asset in fmt.assets_required}
        assert asset_type_map["product_image"] == "image"
        assert asset_type_map["product_name"] == "text"
        assert asset_type_map["product_description"] == "text"

        # Check required fields
        required_asset_ids = {asset["asset_id"] for asset in fmt.assets_required if asset["required"]}
        assert "product_image" in required_asset_ids
        assert "product_name" in required_asset_ids
        assert "product_description" in required_asset_ids


class TestFormatCardStandard:
    """Test format_card_standard format details."""

    def test_has_fixed_dimensions(self):
        """Format card standard has fixed 300x400 dimensions."""
        format_id = FormatId(agent_url=AGENT_URL, id="format_card_standard")
        results = filter_formats(format_ids=[format_id])
        fmt = results[0]
        assert fmt.renders
        assert len(fmt.renders) == 1
        assert fmt.renders[0]["dimensions"]["width"] == 300
        assert fmt.renders[0]["dimensions"]["height"] == 400
        assert fmt.renders[0]["dimensions"]["responsive"]["width"] is False
        assert fmt.renders[0]["dimensions"]["responsive"]["height"] is False

    def test_requires_format_asset(self):
        """Format card standard requires text asset for format specification."""
        format_id = FormatId(agent_url=AGENT_URL, id="format_card_standard")
        results = filter_formats(format_ids=[format_id])
        fmt = results[0]
        assert fmt.assets_required
        assert len(fmt.assets_required) == 1
        asset = fmt.assets_required[0]
        assert asset["asset_id"] == "format"
        assert asset["asset_type"] == "text"
        assert asset["required"] is True


class TestFormatCardDetailed:
    """Test format_card_detailed format details."""

    def test_has_responsive_dimensions(self):
        """Format card detailed has responsive dimensions."""
        format_id = FormatId(agent_url=AGENT_URL, id="format_card_detailed")
        results = filter_formats(format_ids=[format_id])
        fmt = results[0]
        assert fmt.renders
        assert len(fmt.renders) == 1
        assert fmt.renders[0]["dimensions"]["width"] is None
        assert fmt.renders[0]["dimensions"]["height"] is None
        assert fmt.renders[0]["dimensions"]["responsive"]["width"] is True
        assert fmt.renders[0]["dimensions"]["responsive"]["height"] is True

    def test_requires_format_asset(self):
        """Format card detailed requires text asset for format specification."""
        format_id = FormatId(agent_url=AGENT_URL, id="format_card_detailed")
        results = filter_formats(format_ids=[format_id])
        fmt = results[0]
        assert fmt.assets_required
        assert len(fmt.assets_required) == 1
        asset = fmt.assets_required[0]
        assert asset["asset_id"] == "format"
        assert asset["asset_type"] == "text"
        assert asset["required"] is True


class TestInfoCardFormatsFiltering:
    """Test filtering behavior with info card formats."""

    def test_filter_by_300x400_dimensions(self):
        """Filter by 300x400 returns both standard card formats."""
        results = filter_formats(dimensions="300x400")
        assert len(results) == 2
        result_ids = {fmt.format_id.id for fmt in results}
        assert "product_card_standard" in result_ids
        assert "format_card_standard" in result_ids

    def test_filter_by_name_card(self):
        """Name search for 'card' returns all info card formats."""
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

    def test_filter_by_image_asset(self):
        """Filter by image asset type returns product cards."""
        results = filter_formats(asset_types=[AssetType.image])
        product_cards = [fmt for fmt in results if "product_card" in fmt.format_id.id]
        assert len(product_cards) == 2
        result_ids = {fmt.format_id.id for fmt in product_cards}
        assert "product_card_standard" in result_ids
        assert "product_card_detailed" in result_ids


class TestInfoCardFormatsCount:
    """Test that info card formats are included in total count."""

    def test_info_card_formats_list_has_four_items(self):
        """INFO_CARD_FORMATS constant has exactly 4 formats."""
        assert len(INFO_CARD_FORMATS) == 4

    def test_all_formats_includes_info_cards(self):
        """All formats includes info card formats."""
        all_formats = filter_formats()
        meta_formats = [fmt for fmt in all_formats if "card" in fmt.format_id.id]
        assert len(meta_formats) >= 4
        # Verify all four are present
        meta_ids = {fmt.format_id.id for fmt in meta_formats}
        assert "product_card_standard" in meta_ids
        assert "product_card_detailed" in meta_ids
        assert "format_card_standard" in meta_ids
        assert "format_card_detailed" in meta_ids
