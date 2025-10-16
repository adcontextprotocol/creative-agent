"""Tests for format filtering logic."""

from creative_agent.data.standard_formats import filter_formats
from creative_agent.schemas_generated._schemas_v1_core_format_json import FormatId, Type


class TestDimensionFiltering:
    """Test dimension-based filtering."""

    def test_exact_dimensions_match(self):
        """Filter by exact dimensions string returns only matching formats."""
        results = filter_formats(dimensions="970x250")
        assert len(results) > 0
        # All results should have 970x250 dimensions
        for fmt in results:
            assert fmt.renders
            assert len(fmt.renders) > 0
            assert fmt.renders[0].dimensions.width == 970
            assert fmt.renders[0].dimensions.height == 250

    def test_exact_dimensions_excludes_audio(self):
        """Filter by dimensions excludes audio formats without dimensions."""
        results = filter_formats(dimensions="970x250")
        # No audio formats should be in results
        for fmt in results:
            assert fmt.type != Type.audio

    def test_max_width_excludes_larger(self):
        """Filter by max_width excludes formats wider than limit."""
        results = filter_formats(max_width=728)
        assert len(results) > 0
        for fmt in results:
            assert fmt.renders
            assert fmt.renders[0].dimensions.width is not None
            assert fmt.renders[0].dimensions.width <= 728

    def test_max_width_excludes_formats_without_dimensions(self):
        """Filter by max_width excludes formats without dimensions (audio)."""
        results = filter_formats(max_width=1000)
        # No audio formats should be in results
        for fmt in results:
            assert fmt.type != Type.audio
            assert fmt.renders
            assert len(fmt.renders) > 0
            assert fmt.renders[0].dimensions.width is not None

    def test_max_height_excludes_larger(self):
        """Filter by max_height excludes formats taller than limit."""
        results = filter_formats(max_height=250)
        assert len(results) > 0
        for fmt in results:
            assert fmt.renders
            assert fmt.renders[0].dimensions.height is not None
            assert fmt.renders[0].dimensions.height <= 250

    def test_min_width_excludes_smaller(self):
        """Filter by min_width excludes formats narrower than limit."""
        results = filter_formats(min_width=728)
        assert len(results) > 0
        for fmt in results:
            assert fmt.renders
            assert fmt.renders[0].dimensions.width is not None
            assert fmt.renders[0].dimensions.width >= 728

    def test_min_height_excludes_smaller(self):
        """Filter by min_height excludes formats shorter than limit."""
        results = filter_formats(min_height=600)
        assert len(results) > 0
        for fmt in results:
            assert fmt.renders
            assert fmt.renders[0].dimensions.height is not None
            assert fmt.renders[0].dimensions.height >= 600

    def test_combined_min_max_filters(self):
        """Combine min and max dimension filters."""
        results = filter_formats(min_width=300, max_width=970, min_height=250, max_height=600)
        assert len(results) > 0
        for fmt in results:
            assert fmt.renders
            w = fmt.renders[0].dimensions.width
            h = fmt.renders[0].dimensions.height
            assert 300 <= w <= 970
            assert 250 <= h <= 600


class TestTypeFiltering:
    """Test type-based filtering."""

    def test_filter_by_display_type(self):
        """Filter by display type returns only display formats."""
        results = filter_formats(type="display")
        assert len(results) > 0
        for fmt in results:
            assert fmt.type == Type.display

    def test_filter_by_audio_type(self):
        """Filter by audio type returns only audio formats."""
        results = filter_formats(type="audio")
        assert len(results) > 0
        for fmt in results:
            assert fmt.type == Type.audio

    def test_filter_by_video_type(self):
        """Filter by video type returns only video formats."""
        results = filter_formats(type="video")
        assert len(results) > 0
        for fmt in results:
            assert fmt.type == Type.video

    def test_filter_by_native_type(self):
        """Filter by native type returns only native formats."""
        results = filter_formats(type="native")
        assert len(results) > 0
        for fmt in results:
            assert fmt.type == Type.native

    def test_filter_by_dooh_type(self):
        """Filter by DOOH type returns only DOOH formats."""
        results = filter_formats(type="dooh")
        assert len(results) > 0
        for fmt in results:
            assert fmt.type == Type.dooh


class TestCombinedFiltering:
    """Test combining multiple filters."""

    def test_type_and_dimensions(self):
        """Combine type and dimension filters."""
        results = filter_formats(type="display", dimensions="970x250")
        assert len(results) > 0
        for fmt in results:
            assert fmt.type == Type.display
            assert fmt.renders[0].dimensions.width == 970
            assert fmt.renders[0].dimensions.height == 250

    def test_type_and_max_width(self):
        """Combine type and max_width filters."""
        results = filter_formats(type="display", max_width=728)
        assert len(results) > 0
        for fmt in results:
            assert fmt.type == Type.display
            assert fmt.renders[0].dimensions.width <= 728

    def test_dimensions_excludes_audio_even_with_no_type_filter(self):
        """Dimension filtering should exclude audio formats."""
        # This is the bug we fixed - audio formats should not appear
        # when dimension filters are applied
        results = filter_formats(max_width=1920, max_height=1080)
        for fmt in results:
            # All results must have dimensions
            assert fmt.renders
            assert len(fmt.renders) > 0
            assert fmt.renders[0].dimensions.width is not None
            assert fmt.renders[0].dimensions.height is not None
            # No audio formats should appear
            assert fmt.type != Type.audio


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
        # Should return all formats including audio, video, display, native, dooh
        assert len(results) > 30  # We have 38+ formats defined
        # Verify we have multiple types
        types = {fmt.type for fmt in results}
        assert Type.audio in types
        assert Type.video in types
        assert Type.display in types
        assert Type.native in types
        assert Type.dooh in types


class TestBugReproduction:
    """Test that reproduces the original bug report."""

    def test_no_filter_returns_audio_formats(self):
        """When no filters are applied, audio formats should be returned."""
        results = filter_formats()
        audio_formats = [fmt for fmt in results if fmt.type == Type.audio]
        assert len(audio_formats) > 0

    def test_dimension_filter_excludes_audio_formats(self):
        """When dimension filters are applied, audio formats should be excluded.

        This was the bug: audio formats (which have no dimensions) were appearing
        in buy-side UI when filtering for display formats with specific dimensions.
        """
        # Simulate what buy-side does: filter for 970x250 display formats
        results = filter_formats(dimensions="970x250")

        # Audio formats should NOT appear in results
        audio_formats = [fmt for fmt in results if fmt.type == Type.audio]
        assert len(audio_formats) == 0, "Audio formats should not appear when filtering by dimensions"

        # Only display formats with 970x250 should appear
        for fmt in results:
            assert fmt.renders
            assert len(fmt.renders) > 0
            assert fmt.renders[0].dimensions.width == 970
            assert fmt.renders[0].dimensions.height == 250
