"""Integration tests for ADCP 2.12.0 template format functionality.

Tests template formats that accept parameters (dimensions, duration) and can be
instantiated with specific values, avoiding the need for hundreds of concrete formats.
"""

import json

from adcp import FormatId, ListCreativeFormatsResponse
from adcp.types.generated_poc.enums.format_id_parameter import FormatIdParameter
from pydantic import AnyUrl

from creative_agent import server
from creative_agent.data.standard_formats import (
    AGENT_URL,
    STANDARD_FORMATS,
    filter_formats,
    get_format_by_id,
)

# Get actual function from FastMCP wrapper
list_creative_formats = server.list_creative_formats.fn


class TestTemplateFormatDiscovery:
    """Test discovery and listing of template formats."""

    def test_standard_formats_include_templates(self):
        """STANDARD_FORMATS should include template formats with accepts_parameters."""
        template_formats = [f for f in STANDARD_FORMATS if getattr(f, "accepts_parameters", None)]

        assert len(template_formats) == 7, f"Expected 7 template formats, found {len(template_formats)}"

        # Verify template format IDs
        template_ids = {f.format_id.id for f in template_formats}
        expected_ids = {
            "display_generative",
            "display_image",
            "display_html",
            "display_js",
            "video_standard",
            "video_dimensions",
            "video_vast",
        }
        assert template_ids == expected_ids, f"Template IDs mismatch: {template_ids} != {expected_ids}"

    def test_template_formats_have_valid_accepts_parameters(self):
        """Template formats must have valid accepts_parameters field per ADCP 2.12.0."""
        template_formats = [f for f in STANDARD_FORMATS if getattr(f, "accepts_parameters", None)]

        for fmt in template_formats:
            # Must be a list of FormatIdParameter enums
            assert isinstance(fmt.accepts_parameters, list), f"{fmt.format_id.id}: accepts_parameters must be list"
            assert len(fmt.accepts_parameters) > 0, f"{fmt.format_id.id}: accepts_parameters cannot be empty"
            assert all(isinstance(p, FormatIdParameter) for p in fmt.accepts_parameters), (
                f"{fmt.format_id.id}: accepts_parameters must contain FormatIdParameter enums"
            )

            # Must be valid parameter types
            valid_params = {FormatIdParameter.dimensions, FormatIdParameter.duration}
            for param in fmt.accepts_parameters:
                assert param in valid_params, (
                    f"{fmt.format_id.id}: unknown parameter '{param}', expected one of {valid_params}"
                )

    def test_template_formats_no_renders_field(self):
        """Template formats should not have renders field - they accept arbitrary dimensions."""
        template_formats = [f for f in STANDARD_FORMATS if getattr(f, "accepts_parameters", None)]

        for fmt in template_formats:
            # Template formats should have None or empty renders
            renders = getattr(fmt, "renders", None)
            assert renders is None or len(renders) == 0, f"{fmt.format_id.id}: template format should not have renders"

    def test_list_creative_formats_returns_templates(self):
        """list_creative_formats tool should return template formats."""
        # Call the tool function directly
        result = list_creative_formats()

        # Parse response
        assert hasattr(result, "content"), "Result should have content attribute"
        assert hasattr(result, "structured_content"), "Result should have structured_content attribute"
        assert result.structured_content, "Structured content should not be empty"

        # Validate against ADCP schema
        response = ListCreativeFormatsResponse.model_validate(result.structured_content)

        # Check for template formats
        template_formats = [f for f in response.formats if getattr(f, "accepts_parameters", None)]
        assert len(template_formats) == 7, f"Expected 7 template formats in response, found {len(template_formats)}"


class TestTemplateFormatFiltering:
    """Test filtering template formats vs concrete formats."""

    def test_filter_by_type_includes_templates(self):
        """Filtering by type should include both template and concrete formats."""
        from adcp import FormatCategory

        # Filter for display formats
        display_formats = filter_formats(type=FormatCategory.display)

        # Should include template formats
        template_displays = [f for f in display_formats if getattr(f, "accepts_parameters", None)]
        assert len(template_displays) == 4, f"Expected 4 display templates, found {len(template_displays)}"

        # Verify IDs
        template_ids = {f.format_id.id for f in template_displays}
        expected_ids = {"display_generative", "display_image", "display_html", "display_js"}
        assert template_ids == expected_ids

    def test_filter_by_type_video_includes_templates(self):
        """Filtering for video should include video template formats."""
        from adcp import FormatCategory

        video_formats = filter_formats(type=FormatCategory.video)

        # Should include 3 video templates + 9 concrete
        template_videos = [f for f in video_formats if getattr(f, "accepts_parameters", None)]
        assert len(template_videos) == 3, f"Expected 3 video templates, found {len(template_videos)}"

        # Verify IDs
        template_ids = {f.format_id.id for f in template_videos}
        expected_ids = {"video_standard", "video_dimensions", "video_vast"}
        assert template_ids == expected_ids

    def test_dimension_filter_includes_templates(self):
        """Dimension filtering should include template formats that accept dimensions."""
        # Filter for specific dimensions
        results = filter_formats(dimensions="468x60")

        # Should include dimension-accepting templates
        template_results = [f for f in results if getattr(f, "accepts_parameters", None)]
        dimension_templates = [
            f for f in template_results if FormatIdParameter.dimensions in getattr(f, "accepts_parameters", [])
        ]

        # Should have display_generative, display_image, display_html, display_js, video_dimensions
        assert len(dimension_templates) >= 4, (
            f"Expected at least 4 dimension templates for 468x60, found {len(dimension_templates)}"
        )

        # All should accept dimensions parameter
        for fmt in dimension_templates:
            assert FormatIdParameter.dimensions in fmt.accepts_parameters

    def test_max_width_filter_includes_templates(self):
        """Max width filtering should include dimension templates."""
        results = filter_formats(max_width=500)

        # Should include templates that accept dimensions
        template_results = [f for f in results if getattr(f, "accepts_parameters", None)]
        dimension_templates = [
            f for f in template_results if FormatIdParameter.dimensions in getattr(f, "accepts_parameters", [])
        ]

        # Template formats can satisfy any dimension requirement
        assert len(dimension_templates) >= 4, "Should include dimension-accepting templates"


class TestTemplateFormatLookup:
    """Test looking up template formats by ID."""

    def test_get_template_format_by_base_id(self):
        """get_format_by_id should match template on base ID only."""
        # Look up template without parameters
        format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="display_image")

        result = get_format_by_id(format_id)

        assert result is not None, "Should find template format"
        assert result.format_id.id == "display_image"
        assert FormatIdParameter.dimensions in getattr(result, "accepts_parameters", [])

    def test_get_template_format_ignores_dimension_params(self):
        """Template format lookup should ignore dimension parameters in format_id."""
        # Look up template WITH dimension parameters
        format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="display_image", width=468, height=60)

        result = get_format_by_id(format_id)

        # Should still match the template (not look for concrete format)
        assert result is not None, "Should find template format"
        assert result.format_id.id == "display_image"
        assert FormatIdParameter.dimensions in getattr(result, "accepts_parameters", [])
        # Template format_id should NOT have dimensions
        assert getattr(result.format_id, "width", None) is None
        assert getattr(result.format_id, "height", None) is None

    def test_get_concrete_format_requires_exact_match(self):
        """Concrete format lookup should require exact dimension match."""
        # Look up concrete format
        format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="display_300x250_image")

        result = get_format_by_id(format_id)

        assert result is not None, "Should find concrete format"
        assert result.format_id.id == "display_300x250_image"
        assert getattr(result, "accepts_parameters", None) is None, "Should not be a template"
        # Should have renders with fixed dimensions
        assert result.renders is not None
        assert len(result.renders) > 0

    def test_get_video_template_by_base_id(self):
        """get_format_by_id should match video template on base ID."""
        format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="video_standard")

        result = get_format_by_id(format_id)

        assert result is not None, "Should find video template"
        assert result.format_id.id == "video_standard"
        assert FormatIdParameter.duration in getattr(result, "accepts_parameters", [])


class TestTemplateAssetRequirements:
    """Test asset requirements for template vs concrete formats."""

    def test_template_formats_have_assets_required(self):
        """Template formats should have assets_required defined."""
        # Get display_image template
        format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="display_image")
        fmt = get_format_by_id(format_id)

        assert fmt is not None
        assert fmt.assets_required is not None
        assert len(fmt.assets_required) > 0

        # Find the image asset
        image_asset = None
        for asset in fmt.assets_required:
            if asset.asset_id == "banner_image":
                image_asset = asset
                break

        assert image_asset is not None, "Should have banner_image asset"

    def test_concrete_formats_have_explicit_requirements(self):
        """Concrete formats should have explicit dimension requirements."""
        # Get concrete format
        format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="display_300x250_image")
        fmt = get_format_by_id(format_id)

        assert fmt is not None
        assert fmt.assets_required is not None
        assert len(fmt.assets_required) > 0

        # Find the image asset
        image_asset = None
        for asset in fmt.assets_required:
            if asset.asset_id == "banner_image":
                image_asset = asset
                break

        assert image_asset is not None

        # Should have explicit width/height requirements
        requirements = getattr(image_asset, "requirements", None)
        assert requirements is not None
        assert "width" in requirements, "Concrete format should have explicit width"
        assert "height" in requirements, "Concrete format should have explicit height"
        assert requirements["width"] == 300
        assert requirements["height"] == 250


class TestTemplateFormatSerialization:
    """Test that template formats serialize correctly for ADCP."""

    def test_template_format_serializes_with_accepts_parameters(self):
        """Template format should serialize with accepts_parameters field."""
        format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="display_image")
        fmt = get_format_by_id(format_id)

        # Serialize to dict with mode='json' to get enum string values
        fmt_dict = fmt.model_dump(mode="json", exclude_none=True)

        assert "accepts_parameters" in fmt_dict, "Serialized format should include accepts_parameters"
        assert fmt_dict["accepts_parameters"] == ["dimensions"]

        # Should NOT have renders
        assert "renders" not in fmt_dict or fmt_dict.get("renders") is None

    def test_template_format_roundtrip(self):
        """Template format should deserialize correctly."""
        from creative_agent.schemas import CreativeFormat

        format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="video_standard")
        fmt = get_format_by_id(format_id)

        # Serialize with mode='json' to get enum string values
        fmt_dict = fmt.model_dump(mode="json", exclude_none=True)
        fmt_json = json.dumps(fmt_dict)
        fmt_restored = CreativeFormat.model_validate_json(fmt_json)

        # Should preserve template properties (as enum objects after deserialization)
        assert fmt_restored.format_id.id == "video_standard"
        assert FormatIdParameter.duration in getattr(fmt_restored, "accepts_parameters", [])


class TestTemplateFormatValidation:
    """Test validation rules for template formats."""

    def test_template_cannot_have_both_renders_and_accepts_parameters(self):
        """A format should not have both renders and accepts_parameters (logical constraint)."""
        # This is more of a schema validation - template formats by definition
        # accept arbitrary dimensions, so they shouldn't specify fixed renders

        for fmt in STANDARD_FORMATS:
            accepts_params = getattr(fmt, "accepts_parameters", None)
            renders = getattr(fmt, "renders", None)

            if accepts_params and FormatIdParameter.dimensions in accepts_params:
                # Template format - should not have fixed renders
                assert renders is None or len(renders) == 0, (
                    f"{fmt.format_id.id}: template format should not specify renders"
                )

    def test_template_with_dimensions_has_no_output_format_ids(self):
        """Template formats accepting dimensions should not specify output_format_ids."""
        # Templates are flexible - they don't transform to a specific concrete format

        for fmt in STANDARD_FORMATS:
            accepts_params = getattr(fmt, "accepts_parameters", None)
            if accepts_params and FormatIdParameter.dimensions in accepts_params:
                output_formats = getattr(fmt, "output_format_ids", None)

                # Generative template might have output formats, but dimension templates shouldn't
                if fmt.format_id.id not in ["display_generative"]:
                    assert output_formats is None or len(output_formats) == 0, (
                        f"{fmt.format_id.id}: dimension template should not have output_format_ids"
                    )


class TestTemplateFormatCoverage:
    """Test that we have appropriate template format coverage."""

    def test_have_display_dimension_templates(self):
        """Should have template formats for common display types."""
        display_templates = [
            f
            for f in STANDARD_FORMATS
            if getattr(f, "accepts_parameters", None)
            and FormatIdParameter.dimensions in f.accepts_parameters
            and f.type.value == "display"
        ]

        template_ids = {f.format_id.id for f in display_templates}

        # Should have templates for: generative, image, html, js
        assert "display_generative" in template_ids
        assert "display_image" in template_ids
        assert "display_html" in template_ids
        assert "display_js" in template_ids

    def test_have_video_templates(self):
        """Should have template formats for video with both duration and dimensions."""
        video_templates = [
            f for f in STANDARD_FORMATS if getattr(f, "accepts_parameters", None) and f.type.value == "video"
        ]

        # Should have both duration and dimension templates
        duration_templates = [f for f in video_templates if FormatIdParameter.duration in f.accepts_parameters]
        dimension_templates = [f for f in video_templates if FormatIdParameter.dimensions in f.accepts_parameters]

        # video_standard and video_vast accept duration, video_dimensions accepts dimensions
        assert len(duration_templates) >= 2, "Should have video duration templates (video_standard, video_vast)"
        assert len(dimension_templates) >= 1, "Should have video dimension template"

    def test_template_to_concrete_ratio(self):
        """Should have reasonable ratio of templates to concrete formats."""
        templates = [f for f in STANDARD_FORMATS if getattr(f, "accepts_parameters", None)]
        concrete = [f for f in STANDARD_FORMATS if not getattr(f, "accepts_parameters", None)]

        # With templates, we should have far fewer total formats than without
        # Expected: 7 templates + 42 concrete = 49 total
        assert len(templates) == 7, f"Expected 7 templates, found {len(templates)}"
        assert len(concrete) == 42, f"Expected 42 concrete formats, found {len(concrete)}"
        assert len(STANDARD_FORMATS) == 49

        # Ratio should be roughly 1:6 (7 templates replace ~42 potential concrete formats)
        ratio = len(concrete) / len(templates)
        assert ratio > 5, f"Should have healthy template-to-concrete ratio, got {ratio}"
