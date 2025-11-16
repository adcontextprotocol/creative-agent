"""Test discriminator field validation for discriminated unions.

These tests verify that discriminator fields properly enforce type safety:
- Invalid discriminator values are rejected
- Fields from other variants cannot be added
- Pydantic validation catches type errors early
"""

import pytest

# adcp 2.2.0+ provides semantic aliases directly
from adcp.types import (
    BothPreviewRender,
    HtmlPreviewRender,
    InlineDaastAsset,
    InlineVastAsset,
    MediaSubAsset,
    TextSubAsset,
    UrlDaastAsset,
    UrlPreviewRender,
    UrlVastAsset,
)
from pydantic import ValidationError

# Legacy aliases used in test code
Renders = UrlPreviewRender
Renders1 = HtmlPreviewRender
Renders2 = BothPreviewRender
DaastAsset1 = UrlDaastAsset
DaastAsset2 = InlineDaastAsset
VastAsset1 = UrlVastAsset
VastAsset2 = InlineVastAsset
SubAsset1 = MediaSubAsset
SubAsset2 = TextSubAsset


class TestSubAssetDiscriminator:
    """Test SubAsset discriminated union (asset_kind: media | text)."""

    def test_media_asset_valid(self):
        """Media asset with asset_kind='media' should validate."""
        asset = SubAsset1(
            asset_kind="media",
            asset_type="thumbnail_image",
            asset_id="thumb_1",
            content_uri="https://example.com/thumb.jpg",
        )
        assert asset.asset_kind == "media"
        assert str(asset.content_uri) == "https://example.com/thumb.jpg"

    def test_text_asset_valid(self):
        """Text asset with asset_kind='text' should validate."""
        asset = SubAsset2(
            asset_kind="text",
            asset_type="headline",
            asset_id="heading_1",
            content="Buy Now!",
        )
        assert asset.asset_kind == "text"
        assert asset.content == "Buy Now!"

    def test_text_asset_with_list_content(self):
        """Text asset can have list of strings for A/B testing."""
        asset = SubAsset2(
            asset_kind="text",
            asset_type="headline",
            asset_id="heading_1",
            content=["Headline A", "Headline B", "Headline C"],
        )
        assert asset.asset_kind == "text"
        assert len(asset.content) == 3

    def test_invalid_asset_kind_rejected(self):
        """Invalid asset_kind literal should fail validation."""
        with pytest.raises(ValidationError, match="Input should be 'media'"):
            SubAsset1(
                asset_kind="video",  # Invalid literal
                asset_type="thumbnail_image",
                asset_id="test",
                content_uri="https://example.com/img.png",
            )

    def test_media_asset_cannot_have_extra_fields(self):
        """Media asset should reject extra fields (like 'content')."""
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            SubAsset1(
                asset_kind="media",
                asset_type="thumbnail_image",
                asset_id="test",
                content_uri="https://example.com/img.png",
                content="This shouldn't be allowed",  # Extra field
            )

    def test_text_asset_cannot_have_extra_fields(self):
        """Text asset should reject extra fields (like 'content_uri')."""
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            SubAsset2(
                asset_kind="text",
                asset_type="headline",
                asset_id="test",
                content="Hello World",
                content_uri="https://example.com/img.png",  # Extra field
            )

    def test_media_asset_requires_content_uri(self):
        """Media asset must have content_uri field."""
        with pytest.raises(ValidationError, match="Field required"):
            SubAsset1(
                asset_kind="media",
                asset_type="thumbnail_image",
                asset_id="test",
                # Missing content_uri
            )

    def test_text_asset_requires_content(self):
        """Text asset must have content field."""
        with pytest.raises(ValidationError, match="Field required"):
            SubAsset2(
                asset_kind="text",
                asset_type="headline",
                asset_id="test",
                # Missing content
            )

    def test_sub_asset_union_validates_from_dict(self):
        """SubAsset union can validate from dict with correct discriminator."""
        # Media variant
        media_dict = {
            "asset_kind": "media",
            "asset_type": "logo",
            "asset_id": "logo_1",
            "content_uri": "https://example.com/logo.png",
        }
        asset = MediaSubAsset.model_validate(media_dict)
        assert isinstance(asset, MediaSubAsset)
        assert asset.asset_kind == "media"

        # Text variant
        text_dict = {
            "asset_kind": "text",
            "asset_type": "cta_text",
            "asset_id": "cta_1",
            "content": "Shop Now",
        }
        asset = TextSubAsset.model_validate(text_dict)
        assert isinstance(asset, TextSubAsset)
        assert asset.asset_kind == "text"


class TestVastAssetDiscriminator:
    """Test VastAsset discriminated union (delivery_type: url | inline)."""

    def test_vast_url_delivery_valid(self):
        """VAST asset with delivery_type='url' should validate."""
        asset = VastAsset1(
            delivery_type="url",
            url="https://adserver.com/vast.xml",
        )
        assert asset.delivery_type == "url"
        assert str(asset.url) == "https://adserver.com/vast.xml"

    def test_vast_inline_delivery_valid(self):
        """VAST asset with delivery_type='inline' should validate."""
        asset = VastAsset2(
            delivery_type="inline",
            content="<VAST version='3.0'>...</VAST>",
        )
        assert asset.delivery_type == "inline"
        assert asset.content == "<VAST version='3.0'>...</VAST>"

    def test_invalid_delivery_type_rejected(self):
        """Invalid delivery_type literal should fail validation."""
        with pytest.raises(ValidationError, match="Input should be 'url'"):
            VastAsset1(
                delivery_type="xml",  # Invalid literal
                url="https://adserver.com/vast.xml",
            )

    def test_url_delivery_cannot_have_content(self):
        """URL delivery should reject 'content' field."""
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            VastAsset1(
                delivery_type="url",
                url="https://adserver.com/vast.xml",
                content="<VAST>...</VAST>",  # Extra field
            )

    def test_inline_delivery_cannot_have_url(self):
        """Inline delivery should reject 'url' field."""
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            VastAsset2(
                delivery_type="inline",
                content="<VAST>...</VAST>",
                url="https://adserver.com/vast.xml",  # Extra field
            )

    def test_vast_union_validates_from_dict(self):
        """VastAsset union can validate from dict with correct discriminator."""
        # URL variant
        url_dict = {
            "delivery_type": "url",
            "url": "https://adserver.com/vast.xml",
            "vast_version": "4.2",
        }
        asset = UrlVastAsset.model_validate(url_dict)
        assert isinstance(asset, UrlVastAsset)
        assert asset.delivery_type == "url"

        # Inline variant
        inline_dict = {
            "delivery_type": "inline",
            "content": "<VAST version='3.0'>...</VAST>",
        }
        asset = InlineVastAsset.model_validate(inline_dict)
        assert isinstance(asset, InlineVastAsset)
        assert asset.delivery_type == "inline"


class TestDaastAssetDiscriminator:
    """Test DaastAsset discriminated union (delivery_type: url | inline)."""

    def test_daast_url_delivery_valid(self):
        """DAAST asset with delivery_type='url' should validate."""
        asset = DaastAsset1(
            delivery_type="url",
            url="https://audioserver.com/daast.xml",
        )
        assert asset.delivery_type == "url"
        assert str(asset.url) == "https://audioserver.com/daast.xml"

    def test_daast_inline_delivery_valid(self):
        """DAAST asset with delivery_type='inline' should validate."""
        asset = DaastAsset2(
            delivery_type="inline",
            content="<DAAST version='1.0'>...</DAAST>",
        )
        assert asset.delivery_type == "inline"
        assert asset.content == "<DAAST version='1.0'>...</DAAST>"

    def test_url_delivery_cannot_have_content(self):
        """URL delivery should reject 'content' field."""
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            DaastAsset1(
                delivery_type="url",
                url="https://audioserver.com/daast.xml",
                content="<DAAST>...</DAAST>",  # Extra field
            )

    def test_inline_delivery_cannot_have_url(self):
        """Inline delivery should reject 'url' field."""
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            DaastAsset2(
                delivery_type="inline",
                content="<DAAST>...</DAAST>",
                url="https://audioserver.com/daast.xml",  # Extra field
            )


class TestPreviewRenderDiscriminator:
    """Test preview render discriminated union (output_format: url | html | both)."""

    def test_url_output_format_valid(self):
        """Render with output_format='url' should validate."""
        render = Renders(
            render_id="render_1",
            output_format="url",
            preview_url="https://preview.example.com/creative.html",
            role="primary",
        )
        assert render.output_format == "url"
        assert str(render.preview_url) == "https://preview.example.com/creative.html"

    def test_html_output_format_valid(self):
        """Render with output_format='html' should validate."""
        render = Renders1(
            render_id="render_1",
            output_format="html",
            preview_html="<div>Creative content</div>",
            role="primary",
        )
        assert render.output_format == "html"
        assert render.preview_html == "<div>Creative content</div>"

    def test_both_output_format_valid(self):
        """Render with output_format='both' should validate."""
        render = Renders2(
            render_id="render_1",
            output_format="both",
            preview_url="https://preview.example.com/creative.html",
            preview_html="<div>Creative content</div>",
            role="primary",
        )
        assert render.output_format == "both"
        assert str(render.preview_url) == "https://preview.example.com/creative.html"
        assert render.preview_html == "<div>Creative content</div>"

    def test_url_format_cannot_have_preview_html(self):
        """URL format should reject 'preview_html' field."""
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            Renders(
                render_id="render_1",
                output_format="url",
                preview_url="https://preview.example.com/creative.html",
                preview_html="<div>Not allowed</div>",  # Extra field
                role="primary",
            )

    def test_html_format_cannot_have_preview_url(self):
        """HTML format should reject 'preview_url' field."""
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            Renders1(
                render_id="render_1",
                output_format="html",
                preview_html="<div>Creative content</div>",
                preview_url="https://preview.example.com/creative.html",  # Extra field
                role="primary",
            )

    def test_invalid_output_format_rejected(self):
        """Invalid output_format literal should fail validation."""
        with pytest.raises(ValidationError, match="Input should be 'url'"):
            Renders(
                render_id="render_1",
                output_format="json",  # Invalid literal
                preview_url="https://preview.example.com/creative.html",
                role="primary",
            )


class TestDiscriminatorSerializationRoundtrip:
    """Test that discriminated unions serialize/deserialize correctly."""

    def test_sub_asset_json_roundtrip(self):
        """SubAsset should serialize and deserialize preserving variant type."""
        # Create media asset
        media_asset = MediaSubAsset(
            asset_kind="media",
            asset_type="logo",
            asset_id="logo_1",
            content_uri="https://example.com/logo.png",
        )

        # Serialize to JSON
        json_str = media_asset.model_dump_json()

        # Deserialize back
        parsed = MediaSubAsset.model_validate_json(json_str)

        # Verify it's still the correct variant
        assert isinstance(parsed, MediaSubAsset)
        assert parsed.asset_kind == "media"
        assert str(parsed.content_uri) == "https://example.com/logo.png"

    def test_vast_asset_json_roundtrip(self):
        """VastAsset should serialize and deserialize preserving variant type."""
        # Create inline VAST asset
        inline_asset = InlineVastAsset(
            delivery_type="inline",
            content="<VAST version='4.0'>...</VAST>",
        )

        # Serialize to JSON
        json_str = inline_asset.model_dump_json()

        # Deserialize back
        parsed = InlineVastAsset.model_validate_json(json_str)

        # Verify it's still the correct variant
        assert isinstance(parsed, InlineVastAsset)
        assert parsed.delivery_type == "inline"
        assert parsed.content == "<VAST version='4.0'>...</VAST>"

    def test_preview_render_json_roundtrip(self):
        """Preview render should serialize and deserialize preserving variant type."""
        # Create 'both' format render
        both_render = Renders2(
            render_id="render_1",
            output_format="both",
            preview_url="https://preview.example.com/creative.html",
            preview_html="<div>Content</div>",
            role="primary",
        )

        # Serialize to JSON
        json_str = both_render.model_dump_json()

        # Deserialize back
        parsed = Renders2.model_validate_json(json_str)

        # Verify it's still the correct variant
        assert parsed.output_format == "both"
        assert str(parsed.preview_url) == "https://preview.example.com/creative.html"
        assert parsed.preview_html == "<div>Content</div>"
