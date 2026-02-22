"""Validation tests for catalog entries in creative manifests.

Tests validate_catalog() and the catalog path in validate_manifest_assets()
per ADCP 3.5.0 Catalog model.
"""

from creative_agent.validation import validate_catalog, validate_manifest_assets


class TestValidateCatalog:
    """Unit tests for validate_catalog()."""

    def test_valid_catalog_passes(self):
        catalog = {"type": "offering", "items": [{"name": "Widget"}]}
        errors = validate_catalog(catalog)
        assert errors == []

    def test_missing_type_fails(self):
        catalog = {"items": [{"name": "Widget"}]}
        errors = validate_catalog(catalog)
        assert any("'type' field" in e for e in errors)

    def test_invalid_type_fails(self):
        catalog = {"type": "bogus"}
        errors = validate_catalog(catalog)
        assert any("Invalid catalog type" in e for e in errors)

    def test_valid_catalog_with_url(self):
        catalog = {"type": "product", "url": "https://feeds.example.com/products.json"}
        errors = validate_catalog(catalog)
        assert errors == []

    def test_invalid_catalog_url_fails(self):
        catalog = {"type": "product", "url": "not-a-url"}
        errors = validate_catalog(catalog)
        assert any("url" in e.lower() for e in errors)

    def test_items_must_be_list(self):
        catalog = {"type": "offering", "items": "not a list"}
        errors = validate_catalog(catalog)
        assert any("items must be a list" in e for e in errors)

    def test_items_must_be_dicts(self):
        catalog = {"type": "offering", "items": ["not a dict"]}
        requirements = {"required_fields": ["name"]}
        errors = validate_catalog(catalog, requirements)
        assert any("must be a dictionary" in e for e in errors)


class TestCatalogRequiredFields:
    """Tests for required_fields enforcement on catalog items."""

    def test_required_fields_present(self):
        catalog = {"type": "offering", "items": [{"name": "Widget", "price": "9.99"}]}
        requirements = {"required_fields": ["name", "price"]}
        errors = validate_catalog(catalog, requirements)
        assert errors == []

    def test_missing_required_field_fails(self):
        catalog = {"type": "offering", "items": [{"price": "9.99"}]}
        requirements = {"required_fields": ["name"]}
        errors = validate_catalog(catalog, requirements)
        assert any("missing required field 'name'" in e for e in errors)

    def test_multiple_items_validated(self):
        catalog = {
            "type": "offering",
            "items": [
                {"name": "Good"},
                {"description": "Missing name"},
            ],
        }
        requirements = {"required_fields": ["name"]}
        errors = validate_catalog(catalog, requirements)
        # Only second item should fail
        assert len(errors) == 1
        assert "item[1]" in errors[0]


class TestCatalogMinItems:
    """Tests for min_items constraint."""

    def test_min_items_satisfied(self):
        catalog = {"type": "offering", "items": [{"name": "A"}, {"name": "B"}]}
        requirements = {"min_items": 2}
        errors = validate_catalog(catalog, requirements)
        assert errors == []

    def test_min_items_violated(self):
        catalog = {"type": "offering", "items": [{"name": "A"}]}
        requirements = {"min_items": 3}
        errors = validate_catalog(catalog, requirements)
        assert any("at least 3 items" in e for e in errors)


class TestCatalogOfferingAssetConstraints:
    """Tests for offering_asset_constraints validation on catalog items."""

    def test_valid_offering_assets(self):
        catalog = {
            "type": "offering",
            "items": [
                {
                    "name": "Widget",
                    "assets": {
                        "product_images": [
                            {"url": "https://cdn.example.com/img1.jpg"},
                        ],
                    },
                },
            ],
        }
        requirements = {
            "offering_asset_constraints": [
                {
                    "asset_group_id": "product_images",
                    "asset_type": "image",
                    "required": True,
                    "min_count": 1,
                    "max_count": 5,
                },
            ],
        }
        errors = validate_catalog(catalog, requirements)
        assert errors == []

    def test_missing_required_asset_group_fails(self):
        catalog = {
            "type": "offering",
            "items": [{"name": "Widget", "assets": {}}],
        }
        requirements = {
            "offering_asset_constraints": [
                {
                    "asset_group_id": "product_images",
                    "asset_type": "image",
                    "required": True,
                },
            ],
        }
        errors = validate_catalog(catalog, requirements)
        assert any("missing required asset group 'product_images'" in e for e in errors)

    def test_optional_asset_group_not_required(self):
        catalog = {
            "type": "offering",
            "items": [{"name": "Widget", "assets": {}}],
        }
        requirements = {
            "offering_asset_constraints": [
                {
                    "asset_group_id": "product_images",
                    "asset_type": "image",
                    "required": False,
                },
            ],
        }
        errors = validate_catalog(catalog, requirements)
        assert errors == []

    def test_max_count_exceeded_fails(self):
        catalog = {
            "type": "offering",
            "items": [
                {
                    "name": "Widget",
                    "assets": {
                        "product_images": [
                            {"url": "https://cdn.example.com/1.jpg"},
                            {"url": "https://cdn.example.com/2.jpg"},
                            {"url": "https://cdn.example.com/3.jpg"},
                        ],
                    },
                },
            ],
        }
        requirements = {
            "offering_asset_constraints": [
                {
                    "asset_group_id": "product_images",
                    "asset_type": "image",
                    "required": True,
                    "max_count": 2,
                },
            ],
        }
        errors = validate_catalog(catalog, requirements)
        assert any("at most 2 items" in e for e in errors)

    def test_invalid_asset_content_fails(self):
        catalog = {
            "type": "offering",
            "items": [
                {
                    "name": "Widget",
                    "assets": {
                        "descriptions": [
                            {"content": ""},
                        ],
                    },
                },
            ],
        }
        requirements = {
            "offering_asset_constraints": [
                {
                    "asset_group_id": "descriptions",
                    "asset_type": "text",
                    "required": True,
                },
            ],
        }
        errors = validate_catalog(catalog, requirements)
        assert any("cannot be empty" in e.lower() for e in errors)


class TestCatalogEnumFields:
    """Tests for enum field validation on catalogs."""

    def test_valid_feed_format(self):
        catalog = {"type": "product", "feed_format": "google_merchant_center"}
        errors = validate_catalog(catalog)
        assert errors == []

    def test_invalid_feed_format(self):
        catalog = {"type": "product", "feed_format": "amazon_feed"}
        errors = validate_catalog(catalog)
        assert any("Invalid feed_format" in e for e in errors)

    def test_valid_content_id_type(self):
        catalog = {"type": "product", "content_id_type": "sku"}
        errors = validate_catalog(catalog)
        assert errors == []

    def test_invalid_content_id_type(self):
        catalog = {"type": "product", "content_id_type": "barcode"}
        errors = validate_catalog(catalog)
        assert any("Invalid content_id_type" in e for e in errors)

    def test_valid_update_frequency(self):
        catalog = {"type": "product", "update_frequency": "daily"}
        errors = validate_catalog(catalog)
        assert errors == []

    def test_invalid_update_frequency(self):
        catalog = {"type": "product", "update_frequency": "every_5_minutes"}
        errors = validate_catalog(catalog)
        assert any("Invalid update_frequency" in e for e in errors)

    def test_valid_conversion_events(self):
        catalog = {"type": "offering", "conversion_events": ["purchase", "add_to_cart"]}
        errors = validate_catalog(catalog)
        assert errors == []

    def test_invalid_conversion_event(self):
        catalog = {"type": "offering", "conversion_events": ["purchase", "bogus_event"]}
        errors = validate_catalog(catalog)
        assert any("Invalid conversion_event[1]" in e for e in errors)

    def test_conversion_events_must_be_list(self):
        catalog = {"type": "offering", "conversion_events": "purchase"}
        errors = validate_catalog(catalog)
        assert any("conversion_events must be a list" in e for e in errors)

    def test_all_enum_fields_valid_together(self):
        catalog = {
            "type": "product",
            "feed_format": "shopify",
            "content_id_type": "sku",
            "update_frequency": "hourly",
            "conversion_events": ["purchase", "view_content"],
        }
        errors = validate_catalog(catalog)
        assert errors == []


class TestCatalogFeedFormatCompatibility:
    """Tests for feed_format compatibility between catalog and requirements."""

    def _generative_format(self):
        from adcp import FormatId
        from pydantic import AnyUrl

        from creative_agent.data.standard_formats import AGENT_URL, get_format_by_id

        fmt_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="display_generative")
        return get_format_by_id(fmt_id)

    def test_feed_format_compatible(self):
        """Catalog feed_format matches one of the requirement's feed_formats."""
        from adcp import CatalogRequirements, CatalogType, FeedFormat, Format, FormatId
        from pydantic import AnyUrl

        fmt = Format(
            format_id=FormatId(agent_url=AnyUrl("https://test.example.com"), id="test_fmt"),
            name="Test Format",
            catalog_requirements=[
                CatalogRequirements(
                    catalog_type=CatalogType.product,
                    feed_formats=[FeedFormat.google_merchant_center, FeedFormat.shopify],
                ),
            ],
        )
        manifest = {
            "assets": {"banner": {"url": "https://cdn.example.com/img.jpg", "width": 300, "height": 250}},
            "catalogs": [{"type": "product", "feed_format": "google_merchant_center"}],
        }
        errors = validate_manifest_assets(manifest, format_obj=fmt)
        assert not any("feed_format" in e for e in errors)

    def test_feed_format_incompatible(self):
        """Catalog feed_format does not match any of the requirement's feed_formats."""
        from adcp import CatalogRequirements, CatalogType, FeedFormat, Format, FormatId
        from pydantic import AnyUrl

        fmt = Format(
            format_id=FormatId(agent_url=AnyUrl("https://test.example.com"), id="test_fmt"),
            name="Test Format",
            catalog_requirements=[
                CatalogRequirements(
                    catalog_type=CatalogType.product,
                    feed_formats=[FeedFormat.google_merchant_center],
                ),
            ],
        )
        manifest = {
            "assets": {"banner": {"url": "https://cdn.example.com/img.jpg", "width": 300, "height": 250}},
            "catalogs": [{"type": "product", "feed_format": "shopify"}],
        }
        errors = validate_manifest_assets(manifest, format_obj=fmt)
        assert any("feed_format" in e and "shopify" in e for e in errors)


class TestManifestCatalogValidation:
    """Tests for catalog validation within validate_manifest_assets()."""

    def _generative_format(self):
        """Get a generative format with catalog_requirements."""
        from adcp import FormatId
        from pydantic import AnyUrl

        from creative_agent.data.standard_formats import AGENT_URL, get_format_by_id

        fmt_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="display_generative")
        return get_format_by_id(fmt_id)

    def test_manifest_with_catalog_passes(self):
        fmt = self._generative_format()
        manifest = {
            "format_id": {"agent_url": "https://creative.example.com", "id": "display_generative"},
            "assets": {
                "generation_prompt": {"content": "Create a banner ad"},
                "impression_tracker": {"url": "https://track.example.com/imp"},
            },
            "catalogs": [
                {"type": "offering", "items": [{"name": "Widget"}]},
            ],
        }
        errors = validate_manifest_assets(manifest, format_obj=fmt)
        assert errors == [], f"Unexpected errors: {errors}"

    def test_manifest_missing_required_catalog_fails(self):
        fmt = self._generative_format()
        manifest = {
            "format_id": {"agent_url": "https://creative.example.com", "id": "display_generative"},
            "assets": {
                "generation_prompt": {"content": "Create a banner ad"},
                "impression_tracker": {"url": "https://track.example.com/imp"},
            },
        }
        errors = validate_manifest_assets(manifest, format_obj=fmt)
        assert any("Required catalog missing" in e for e in errors)

    def test_manifest_catalog_wrong_type_fails(self):
        fmt = self._generative_format()
        manifest = {
            "format_id": {"agent_url": "https://creative.example.com", "id": "display_generative"},
            "assets": {
                "generation_prompt": {"content": "Create a banner ad"},
                "impression_tracker": {"url": "https://track.example.com/imp"},
            },
            "catalogs": [
                {"type": "job", "items": [{"title": "Engineer"}]},
            ],
        }
        errors = validate_manifest_assets(manifest, format_obj=fmt)
        assert any("Required catalog missing for type: offering" in e for e in errors)
