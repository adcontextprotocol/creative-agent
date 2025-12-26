"""Validation tests for template format parameters.

Tests parameter validation for template formats including:
- Dimension parameters (width, height)
- Duration parameters (duration_ms)
- Parameter extraction from format_id
- Asset requirement parameter matching
"""

import pytest
from adcp import FormatId
from adcp.types.generated_poc.enums.format_id_parameter import FormatIdParameter
from pydantic import AnyUrl, ValidationError

from creative_agent.data.standard_formats import AGENT_URL, get_format_by_id


class TestDimensionParameterValidation:
    """Test validation of dimension parameters in format_id."""

    def test_format_id_accepts_width_height_parameters(self):
        """FormatId should accept width and height parameters."""
        format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="display_image", width=468, height=60)

        assert format_id.width == 468
        assert format_id.height == 60
        assert format_id.id == "display_image"

    def test_format_id_width_must_be_positive(self):
        """FormatId width parameter should reject negative values."""
        # ADCP schema should validate this, but let's verify
        # Note: Depending on ADCP library validation, this might pass
        # If validation is loose, we need application-level validation

        # Try to create with negative width
        try:
            format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="display_image", width=-100, height=60)
            # If it doesn't raise, check our validation catches it
            assert format_id.width >= 0, "Width should be validated as positive"
        except ValidationError:
            # Good - library validates it
            pass

    def test_format_id_height_must_be_positive(self):
        """FormatId height parameter should reject negative values."""
        try:
            format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="display_image", width=468, height=-60)
            assert format_id.height >= 0, "Height should be validated as positive"
        except ValidationError:
            # Good - library validates it
            pass

    def test_format_id_width_must_be_integer(self):
        """FormatId width should be integer type."""
        format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="display_image", width=468, height=60)

        # Should be stored as int
        assert isinstance(format_id.width, int)

    def test_format_id_dimensions_are_optional(self):
        """FormatId should work without dimension parameters."""
        format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="display_image")

        # Should have no dimensions
        assert getattr(format_id, "width", None) is None
        assert getattr(format_id, "height", None) is None


class TestDurationParameterValidation:
    """Test validation of duration parameters in format_id."""

    def test_format_id_accepts_duration_ms_parameter(self):
        """FormatId should accept duration_ms parameter."""
        format_id = FormatId(
            agent_url=AnyUrl(str(AGENT_URL)),
            id="video_standard",
            duration_ms=30000,  # 30 seconds
        )

        assert format_id.duration_ms == 30000
        assert format_id.id == "video_standard"

    def test_format_id_duration_must_be_positive(self):
        """FormatId duration_ms should reject negative values."""
        try:
            format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="video_standard", duration_ms=-5000)
            assert format_id.duration_ms >= 0, "Duration should be validated as positive"
        except ValidationError:
            # Good - library validates it
            pass

    def test_format_id_duration_is_milliseconds(self):
        """FormatId duration_ms should be in milliseconds."""
        # 15 seconds = 15000ms
        format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="video_standard", duration_ms=15000)

        assert format_id.duration_ms == 15000

        # 30 seconds = 30000ms
        format_id_30s = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="video_standard", duration_ms=30000)

        assert format_id_30s.duration_ms == 30000


class TestParameterExtraction:
    """Test extraction of parameters from format_id for asset validation."""

    def test_extract_dimensions_from_format_id(self):
        """Dimensions can be extracted from format_id for template formats."""
        # Get template format with dimensions
        template_format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="display_image", width=468, height=60)
        fmt = get_format_by_id(template_format_id)

        assert fmt is not None
        assert fmt.assets_required is not None

        # Template format accepts dimensions parameter
        assert FormatIdParameter.dimensions in getattr(fmt, "accepts_parameters", [])

        # Dimensions can be extracted from format_id
        extracted_width = getattr(template_format_id, "width", None)
        extracted_height = getattr(template_format_id, "height", None)

        assert extracted_width == 468, "Should extract width from format_id"
        assert extracted_height == 60, "Should extract height from format_id"

    def test_extract_duration_from_format_id(self):
        """Duration can be extracted from format_id for template formats."""
        # Get video template with duration
        template_format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="video_standard", duration_ms=15000)
        fmt = get_format_by_id(template_format_id)

        assert fmt is not None
        assert fmt.assets_required is not None

        # Template format accepts duration parameter
        assert FormatIdParameter.duration in getattr(fmt, "accepts_parameters", [])

        # Duration can be extracted from format_id
        extracted_duration = getattr(template_format_id, "duration_ms", None)
        assert extracted_duration == 15000


class TestAssetParameterMatching:
    """Test that asset properties match format_id parameters."""

    def test_asset_dimensions_should_match_format_id_dimensions(self):
        """Template formats accept dimensions from format_id."""
        format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="display_image", width=728, height=90)

        # Get format - template should accept dimensions
        fmt = get_format_by_id(format_id)
        assert FormatIdParameter.dimensions in getattr(fmt, "accepts_parameters", [])

        # Format_id carries the dimensions
        assert format_id.width == 728
        assert format_id.height == 90

    def test_concrete_format_has_explicit_dimensions(self):
        """Concrete formats should have explicit dimension requirements."""
        format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="display_300x250_image")

        fmt = get_format_by_id(format_id)
        image_asset = next(a for a in fmt.assets_required if a.asset_id == "banner_image")

        requirements = getattr(image_asset, "requirements", {})

        # Concrete format has explicit values in requirements
        assert requirements.get("width") == 300
        assert requirements.get("height") == 250


class TestParameterValidationEdgeCases:
    """Test edge cases and boundary conditions for parameter validation."""

    def test_format_id_with_only_width_parameter(self):
        """FormatId can have width without height (partial parameters)."""
        format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="display_image", width=468)

        assert format_id.width == 468
        assert getattr(format_id, "height", None) is None

    def test_format_id_with_only_height_parameter(self):
        """FormatId can have height without width (partial parameters)."""
        format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="display_image", height=60)

        assert getattr(format_id, "width", None) is None
        assert format_id.height == 60

    def test_format_id_with_zero_dimensions(self):
        """FormatId with zero dimensions should be rejected by ADCP schema."""
        # ADCP 2.12.0 validates dimensions must be >= 1
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="display_image", width=0, height=0)

        # Should raise validation error
        assert "greater_than_equal" in str(exc_info.value)

    def test_format_id_with_large_dimensions(self):
        """FormatId should accept large dimension values."""
        # DOOH screens can be very large
        format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="display_image", width=3840, height=2160)

        assert format_id.width == 3840
        assert format_id.height == 2160

    def test_format_id_with_very_long_duration(self):
        """FormatId should accept long duration values."""
        # 60 second video = 60000ms
        format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="video_standard", duration_ms=60000)

        assert format_id.duration_ms == 60000

    def test_format_id_with_short_duration(self):
        """FormatId should accept short duration values."""
        # 5 second video = 5000ms
        format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="video_standard", duration_ms=5000)

        assert format_id.duration_ms == 5000


class TestMultipleParameterTypes:
    """Test formats that might accept multiple parameter types."""

    def test_video_format_with_dimensions_and_duration(self):
        """Video format could potentially accept both dimensions and duration."""
        # While our current video_dimensions template only accepts dimensions,
        # theoretically a video could have both

        format_id = FormatId(
            agent_url=AnyUrl(str(AGENT_URL)), id="video_dimensions", width=1920, height=1080, duration_ms=30000
        )

        # FormatId should accept multiple parameters
        assert format_id.width == 1920
        assert format_id.height == 1080
        assert format_id.duration_ms == 30000

    def test_template_lookup_with_extra_parameters(self):
        """Template lookup should work even with extra parameters."""
        from adcp.types.generated_poc.enums.format_id_parameter import FormatIdParameter

        # Look up display_image with duration parameter (which it doesn't use)
        format_id = FormatId(
            agent_url=AnyUrl(str(AGENT_URL)),
            id="display_image",
            width=468,
            height=60,
            duration_ms=15000,  # Extra parameter
        )

        # Should still find the template
        fmt = get_format_by_id(format_id)
        assert fmt is not None
        assert fmt.format_id.id == "display_image"
        assert FormatIdParameter.dimensions in getattr(fmt, "accepts_parameters", [])


class TestParameterSerialization:
    """Test that format_id parameters serialize correctly."""

    def test_format_id_with_dimensions_serializes_correctly(self):
        """FormatId with dimensions should serialize to JSON correctly."""
        import json

        format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="display_image", width=300, height=250)

        # Serialize with mode='json' to handle AnyUrl
        format_id_dict = format_id.model_dump(mode="json", exclude_none=True)
        format_id_json = json.dumps(format_id_dict)

        # Deserialize
        format_id_restored = FormatId.model_validate_json(format_id_json)

        # Should preserve parameters
        assert format_id_restored.width == 300
        assert format_id_restored.height == 250
        assert format_id_restored.id == "display_image"

    def test_format_id_without_parameters_serializes_correctly(self):
        """FormatId without parameters should serialize cleanly (no null fields)."""
        import json

        format_id = FormatId(agent_url=AnyUrl(str(AGENT_URL)), id="display_image")

        # Serialize with exclude_none and mode='json' to handle AnyUrl
        format_id_dict = format_id.model_dump(mode="json", exclude_none=True)

        # Should not have width, height, duration_ms keys
        assert "width" not in format_id_dict
        assert "height" not in format_id_dict
        assert "duration_ms" not in format_id_dict

        # Should be valid JSON
        format_id_json = json.dumps(format_id_dict)
        format_id_restored = FormatId.model_validate_json(format_id_json)

        assert format_id_restored.id == "display_image"
