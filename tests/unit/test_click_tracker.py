"""Unit tests for click_tracker asset functionality."""

from creative_agent.data.standard_formats import (
    STANDARD_FORMATS,
    create_click_tracker_asset,
)


class TestClickTrackerAsset:
    """Tests for the click_tracker asset helper function."""

    def test_click_tracker_asset_id(self):
        """Test click_tracker has correct asset_id."""
        tracker = create_click_tracker_asset()
        assert tracker.asset_id == "click_tracker"

    def test_click_tracker_asset_type(self):
        """Test click_tracker is a URL type asset."""
        tracker = create_click_tracker_asset()
        assert tracker.asset_type.value == "url"

    def test_click_tracker_is_optional(self):
        """Test click_tracker is not required."""
        tracker = create_click_tracker_asset()
        assert tracker.required is False

    def test_click_tracker_url_type(self):
        """Test click_tracker uses tracker_redirect url_type."""
        tracker = create_click_tracker_asset()
        assert tracker.requirements["url_type"] == "tracker_redirect"

    def test_click_tracker_has_description(self):
        """Test click_tracker has a description in requirements."""
        tracker = create_click_tracker_asset()
        assert "description" in tracker.requirements
        assert "click" in tracker.requirements["description"].lower()


class TestClickTrackerFormatCoverage:
    """Tests for click_tracker coverage across formats."""

    EXPECTED_FORMATS_WITH_CLICK_TRACKER = [
        # Image formats
        "display_image",
        "display_300x250_image",
        "display_728x90_image",
        "display_320x50_image",
        "display_160x600_image",
        "display_336x280_image",
        "display_300x600_image",
        "display_970x250_image",
        # HTML formats
        "display_html",
        "display_300x250_html",
        "display_728x90_html",
        "display_160x600_html",
        "display_336x280_html",
        "display_300x600_html",
        "display_970x250_html",
        # JS format
        "display_js",
        # VAST formats
        "video_vast",
        "video_vast_30s",
        # Native
        "native_content",
    ]

    def test_click_tracker_format_count(self):
        """Verify exactly 19 formats have click_tracker."""
        count = sum(
            1
            for fmt in STANDARD_FORMATS
            if "click_tracker" in [a.asset_id for a in (fmt.assets or [])]
        )
        assert count == 19

    def test_click_tracker_on_expected_formats(self):
        """Verify click_tracker is on all expected formats."""
        for fmt in STANDARD_FORMATS:
            asset_ids = [a.asset_id for a in (fmt.assets or [])]
            if fmt.format_id.id in self.EXPECTED_FORMATS_WITH_CLICK_TRACKER:
                assert "click_tracker" in asset_ids, (
                    f"{fmt.format_id.id} should have click_tracker"
                )

    def test_click_tracker_only_on_expected_formats(self):
        """Verify click_tracker is only on formats in the expected list."""
        for fmt in STANDARD_FORMATS:
            asset_ids = [a.asset_id for a in (fmt.assets or [])]
            if "click_tracker" in asset_ids:
                assert fmt.format_id.id in self.EXPECTED_FORMATS_WITH_CLICK_TRACKER, (
                    f"{fmt.format_id.id} has click_tracker but is not in expected list"
                )

    def test_click_tracker_not_on_non_clickable_formats(self):
        """Verify click_tracker is NOT on formats without click functionality."""
        # Audio and DOOH don't support click tracking
        # VAST video formats DO support click tracking (external to VAST tag)
        non_clickable_types = ["audio", "dooh"]
        for fmt in STANDARD_FORMATS:
            fmt_type = str(fmt.type).lower() if fmt.type else ""
            asset_ids = [a.asset_id for a in (fmt.assets or [])]

            # Skip if not a non-clickable type
            if not any(t in fmt_type for t in non_clickable_types):
                continue

            assert "click_tracker" not in asset_ids, (
                f"{fmt.format_id.id} ({fmt_type}) should not have click_tracker"
            )
