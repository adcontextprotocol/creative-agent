"""Tests for format filtering logic."""

from adcp import FormatCategory, FormatId
from adcp.types.generated_poc.enums.format_id_parameter import FormatIdParameter

from creative_agent.data.standard_formats import filter_formats


def get_render_dimensions(fmt):
    """Get dimensions from first render (handles both Pydantic model and dict)."""
    if not fmt.renders or len(fmt.renders) == 0:
        return None, None
    render = fmt.renders[0]
    if hasattr(render, "dimensions"):
        # Pydantic model (adcp 2.1.0+)
        dims = render.dimensions
        return dims.width, dims.height
    # Legacy dict format
    dims = render.get("dimensions", {})
    return dims.get("width"), dims.get("height")


class TestDimensionFiltering:
    """Test dimension-based filtering."""

    def test_exact_dimensions_match(self):
        """Filter by exact dimensions string returns template formats and matching concrete formats."""
        results = filter_formats(dimensions="300x400")
        assert len(results) > 0
        # Results should either be templates that accept dimensions OR have 300x400 dimensions
        for fmt in results:
            # Template formats accept any dimensions
            if getattr(fmt, "accepts_parameters", None) and FormatIdParameter.dimensions in fmt.accepts_parameters:
                continue
            # Concrete formats must have exact dimensions
            assert fmt.renders
            assert len(fmt.renders) > 0
            assert get_render_dimensions(fmt)[0] == 300
            assert get_render_dimensions(fmt)[1] == 400

    def test_exact_dimensions_excludes_audio(self):
        """Filter by dimensions excludes audio formats without dimensions."""
        results = filter_formats(dimensions="300x400")
        # No audio formats should be in results
        for fmt in results:
            assert fmt.type != FormatCategory.audio

    def test_max_width_excludes_larger(self):
        """Filter by max_width includes template formats and excludes concrete formats wider than limit."""
        results = filter_formats(max_width=728)
        assert len(results) > 0
        for fmt in results:
            # Template formats accept any dimensions
            if getattr(fmt, "accepts_parameters", None) and FormatIdParameter.dimensions in fmt.accepts_parameters:
                continue
            # Concrete formats must be within width limit
            assert fmt.renders
            assert get_render_dimensions(fmt)[0] is not None
            assert get_render_dimensions(fmt)[0] <= 728

    def test_max_width_excludes_formats_without_dimensions(self):
        """Filter by max_width excludes audio formats but includes templates."""
        results = filter_formats(max_width=1000)
        # Audio formats without dimensions should not be in results, but templates OK
        for fmt in results:
            if getattr(fmt, "accepts_parameters", None) and FormatIdParameter.dimensions in fmt.accepts_parameters:
                continue
            assert fmt.type != FormatCategory.audio
            assert fmt.renders
            assert len(fmt.renders) > 0
            assert get_render_dimensions(fmt)[0] is not None

    def test_max_height_excludes_larger(self):
        """Filter by max_height includes templates and excludes concrete formats taller than limit."""
        results = filter_formats(max_height=500)
        assert len(results) > 0
        for fmt in results:
            if getattr(fmt, "accepts_parameters", None) and FormatIdParameter.dimensions in fmt.accepts_parameters:
                continue
            assert fmt.renders
            assert get_render_dimensions(fmt)[1] is not None
            assert get_render_dimensions(fmt)[1] <= 500

    def test_min_width_excludes_smaller(self):
        """Filter by min_width includes templates and excludes concrete formats narrower than limit."""
        results = filter_formats(min_width=1000)
        assert len(results) > 0
        for fmt in results:
            if getattr(fmt, "accepts_parameters", None) and FormatIdParameter.dimensions in fmt.accepts_parameters:
                continue
            assert fmt.renders
            assert get_render_dimensions(fmt)[0] is not None
            assert get_render_dimensions(fmt)[0] >= 1000

    def test_min_height_excludes_smaller(self):
        """Filter by min_height includes templates and excludes concrete formats shorter than limit."""
        results = filter_formats(min_height=1000)
        assert len(results) > 0
        for fmt in results:
            if getattr(fmt, "accepts_parameters", None) and FormatIdParameter.dimensions in fmt.accepts_parameters:
                continue
            assert fmt.renders
            assert get_render_dimensions(fmt)[1] is not None
            assert get_render_dimensions(fmt)[1] >= 1000

    def test_combined_min_max_filters(self):
        """Combine min and max dimension filters."""
        results = filter_formats(min_width=300, max_width=2000, min_height=400, max_height=2000)
        assert len(results) > 0
        for fmt in results:
            if getattr(fmt, "accepts_parameters", None) and FormatIdParameter.dimensions in fmt.accepts_parameters:
                continue
            assert fmt.renders
            w, h = get_render_dimensions(fmt)
            assert 300 <= w <= 2000
            assert 400 <= h <= 2000


class TestTypeFiltering:
    """Test type-based filtering."""

    def test_filter_by_display_type(self):
        """Filter by display type returns only display formats."""
        results = filter_formats(type="display")
        assert len(results) > 0
        for fmt in results:
            assert fmt.type == FormatCategory.display

    def test_filter_by_audio_type(self):
        """Filter by audio type returns only audio formats."""
        results = filter_formats(type="audio")
        assert len(results) > 0
        for fmt in results:
            assert fmt.type == FormatCategory.audio

    def test_filter_by_video_type(self):
        """Filter by video type returns only video formats."""
        results = filter_formats(type="video")
        assert len(results) > 0
        for fmt in results:
            assert fmt.type == FormatCategory.video

    def test_filter_by_native_type(self):
        """Filter by native type returns only native formats."""
        results = filter_formats(type="native")
        assert len(results) > 0
        for fmt in results:
            assert fmt.type == FormatCategory.native

    def test_filter_by_dooh_type(self):
        """Filter by DOOH type returns only DOOH formats."""
        results = filter_formats(type="dooh")
        assert len(results) > 0
        for fmt in results:
            assert fmt.type == FormatCategory.dooh


class TestCombinedFiltering:
    """Test combining multiple filters."""

    def test_type_and_dimensions(self):
        """Combine type and dimension filters."""
        results = filter_formats(type="display", dimensions="970x250")
        assert len(results) > 0
        for fmt in results:
            # Template formats accept any dimensions
            if getattr(fmt, "accepts_parameters", None) and FormatIdParameter.dimensions in fmt.accepts_parameters:
                continue
            assert fmt.type == FormatCategory.display
            assert get_render_dimensions(fmt)[0] == 970
            assert get_render_dimensions(fmt)[1] == 250

    def test_type_and_max_width(self):
        """Combine type and max_width filters."""
        results = filter_formats(type="display", max_width=728)
        assert len(results) > 0
        for fmt in results:
            # Template formats accept any dimensions
            if getattr(fmt, "accepts_parameters", None) and FormatIdParameter.dimensions in fmt.accepts_parameters:
                continue
            assert fmt.type == FormatCategory.display
            assert get_render_dimensions(fmt)[0] <= 728

    def test_dimensions_excludes_audio_even_with_no_type_filter(self):
        """Dimension filtering should exclude audio formats."""
        # This is the bug we fixed - audio formats should not appear
        # when dimension filters are applied
        results = filter_formats(max_width=1920, max_height=1080)
        for fmt in results:
            # Template formats accept any dimensions
            if getattr(fmt, "accepts_parameters", None) and FormatIdParameter.dimensions in fmt.accepts_parameters:
                continue
            # All results must have dimensions
            assert fmt.renders
            assert len(fmt.renders) > 0
            assert get_render_dimensions(fmt)[0] is not None
            assert get_render_dimensions(fmt)[1] is not None
            # No audio formats should appear
            assert fmt.type != FormatCategory.audio


class TestNameSearch:
    """Test name-based search filtering."""

    def test_name_search_case_insensitive(self):
        """Name search is case-insensitive."""
        results = filter_formats(name_search="billboard")
        assert len(results) > 0
        for fmt in results:
            assert "billboard" in fmt.name.lower()

    def test_name_search_partial_match(self):
        """Name search matches partial strings."""
        results = filter_formats(name_search="Audio")
        assert len(results) > 0
        for fmt in results:
            assert "audio" in fmt.name.lower()


class TestFormatIdFiltering:
    """Test filtering by specific format IDs."""

    def test_filter_by_single_format_id(self):
        """Filter by a specific format ID."""
        from creative_agent.data.standard_formats import AGENT_URL

        format_id = FormatId(agent_url=AGENT_URL, id="display_300x250_image")
        results = filter_formats(format_ids=[format_id])
        assert len(results) == 1
        assert results[0].format_id.id == "display_300x250_image"

    def test_filter_by_multiple_format_ids(self):
        """Filter by multiple format IDs."""
        from creative_agent.data.standard_formats import AGENT_URL

        format_ids = [
            FormatId(agent_url=AGENT_URL, id="display_300x250_image"),
            FormatId(agent_url=AGENT_URL, id="display_728x90_image"),
        ]
        results = filter_formats(format_ids=format_ids)
        assert len(results) == 2
        result_ids = {r.format_id.id for r in results}
        assert result_ids == {"display_300x250_image", "display_728x90_image"}


class TestNoFilters:
    """Test behavior with no filters applied."""

    def test_no_filters_returns_all_formats(self):
        """No filters returns all standard formats."""
        results = filter_formats()
        # Should return all formats including audio, video, display, native, dooh, info card
        # 8 generative (1 template + 7 concrete) + 12 video (3 templates + 9 concrete) + 8 display_image (1 template + 7 concrete) + 7 display_html (1 template + 6 concrete) + 1 display_js template + 2 native + 3 audio + 4 dooh + 4 info card = 49
        assert len(results) == 49
        # Verify we have multiple types
        types = {fmt.type for fmt in results}
        assert FormatCategory.audio in types
        assert FormatCategory.video in types
        assert FormatCategory.display in types
        assert FormatCategory.native in types
        assert FormatCategory.dooh in types


class TestBugReproduction:
    """Test that reproduces the original bug report."""

    def test_no_filter_returns_audio_formats(self):
        """When no filters are applied, audio formats should be returned."""
        results = filter_formats()
        audio_formats = [fmt for fmt in results if fmt.type == FormatCategory.audio]
        assert len(audio_formats) > 0

    def test_dimension_filter_excludes_audio_formats(self):
        """When dimension filters are applied, audio formats should be excluded.

        This was the bug: audio formats (which have no dimensions) were appearing
        in buy-side UI when filtering for display formats with specific dimensions.
        """
        # Simulate what buy-side does: filter for 970x250 display formats
        results = filter_formats(dimensions="970x250")

        # Audio formats should NOT appear in results
        audio_formats = [fmt for fmt in results if fmt.type == FormatCategory.audio]
        assert len(audio_formats) == 0, "Audio formats should not appear when filtering by dimensions"

        # Only display formats with 970x250 should appear
        for fmt in results:
            # Template formats accept any dimensions
            if getattr(fmt, "accepts_parameters", None) and FormatIdParameter.dimensions in fmt.accepts_parameters:
                continue
            assert fmt.renders
            assert len(fmt.renders) > 0
            assert get_render_dimensions(fmt)[0] == 970
            assert get_render_dimensions(fmt)[1] == 250
