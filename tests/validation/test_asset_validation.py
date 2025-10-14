"""Tests for asset validation."""

import pytest

from creative_agent.validation import (
    AssetValidationError,
    validate_asset,
    validate_css_content,
    validate_data_uri,
    validate_html_content,
    validate_image_url,
    validate_javascript_content,
    validate_manifest_assets,
    validate_text_content,
    validate_url,
)


class TestHTMLValidation:
    """Test HTML content validation."""

    def test_valid_html_document(self):
        """Valid HTML document should pass."""
        html = "<!DOCTYPE html><html><body><h1>Test</h1></body></html>"
        validate_html_content(html)

    def test_valid_html_snippet(self):
        """Valid HTML snippet should pass."""
        html = "<div><p>Test content</p></div>"
        validate_html_content(html)

    def test_empty_html_fails(self):
        """Empty HTML should fail."""
        with pytest.raises(AssetValidationError, match="cannot be empty"):
            validate_html_content("")

    def test_non_html_text_fails(self):
        """Plain text without HTML tags should fail."""
        with pytest.raises(AssetValidationError, match="must contain valid HTML tags"):
            validate_html_content("This is just plain text")

    def test_html_without_body_fails(self):
        """HTML document without body tag should fail."""
        with pytest.raises(AssetValidationError, match="must contain <body> tag"):
            validate_html_content("<!DOCTYPE html><html><head></head></html>")


class TestCSSValidation:
    """Test CSS content validation."""

    def test_valid_css(self):
        """Valid CSS should pass."""
        css = "body { margin: 0; padding: 0; }"
        validate_css_content(css)

    def test_valid_css_multiple_rules(self):
        """CSS with multiple rules should pass."""
        css = """
        body { margin: 0; }
        .container { width: 100%; }
        #main { color: red; }
        """
        validate_css_content(css)

    def test_empty_css_fails(self):
        """Empty CSS should fail."""
        with pytest.raises(AssetValidationError, match="cannot be empty"):
            validate_css_content("")

    def test_invalid_css_fails(self):
        """Text without CSS rules should fail."""
        with pytest.raises(AssetValidationError, match="must contain at least one valid rule"):
            validate_css_content("This is not CSS")


class TestJavaScriptValidation:
    """Test JavaScript content validation."""

    def test_valid_javascript(self):
        """Valid JavaScript should pass."""
        js = "console.log('hello world');"
        validate_javascript_content(js)

    def test_valid_javascript_function(self):
        """JavaScript function should pass."""
        js = "function test() { return true; }"
        validate_javascript_content(js)

    def test_empty_javascript_fails(self):
        """Empty JavaScript should fail."""
        with pytest.raises(AssetValidationError, match="cannot be empty"):
            validate_javascript_content("")

    def test_too_short_javascript_fails(self):
        """Very short JavaScript should fail."""
        with pytest.raises(AssetValidationError, match="too short"):
            validate_javascript_content("x=1")


class TestTextValidation:
    """Test text content validation."""

    def test_valid_text(self):
        """Valid text should pass."""
        validate_text_content("This is valid text content")

    def test_empty_text_fails(self):
        """Empty text should fail."""
        with pytest.raises(AssetValidationError, match="cannot be empty"):
            validate_text_content("")

    def test_whitespace_only_fails(self):
        """Whitespace-only text should fail."""
        with pytest.raises(AssetValidationError, match="cannot be empty"):
            validate_text_content("   \n  \t  ")


class TestURLValidation:
    """Test URL validation."""

    def test_valid_http_url(self):
        """Valid HTTP URL should pass."""
        validate_url("http://example.com/image.png")

    def test_valid_https_url(self):
        """Valid HTTPS URL should pass."""
        validate_url("https://example.com/image.png")

    def test_javascript_url_fails(self):
        """JavaScript URL should fail."""
        with pytest.raises(AssetValidationError, match="scheme not allowed"):
            validate_url("javascript:alert('xss')")

    def test_vbscript_url_fails(self):
        """VBScript URL should fail."""
        with pytest.raises(AssetValidationError, match="scheme not allowed"):
            validate_url("vbscript:alert('xss')")

    def test_file_url_fails(self):
        """File URL should fail."""
        with pytest.raises(AssetValidationError, match="scheme not allowed"):
            validate_url("file:///etc/passwd")

    def test_invalid_url_fails(self):
        """Invalid URL format should fail."""
        with pytest.raises(AssetValidationError, match="must have scheme and host"):
            validate_url("not-a-url")

    def test_empty_url_fails(self):
        """Empty URL should fail."""
        with pytest.raises(AssetValidationError, match="cannot be empty"):
            validate_url("")


class TestDataURIValidation:
    """Test data URI validation."""

    def test_valid_png_data_uri(self):
        """Valid PNG data URI should pass."""
        uri = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        validate_data_uri(uri)

    def test_valid_jpeg_data_uri(self):
        """Valid JPEG data URI should pass."""
        uri = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBD"
        validate_data_uri(uri)

    def test_invalid_mime_type_fails(self):
        """Data URI with invalid MIME type should fail."""
        with pytest.raises(AssetValidationError, match="MIME type not allowed"):
            validate_data_uri("data:text/html;base64,PHNjcmlwdD5hbGVydCgneHNzJyk8L3NjcmlwdD4=")

    def test_missing_comma_fails(self):
        """Data URI without comma should fail."""
        with pytest.raises(AssetValidationError, match="must contain comma separator"):
            validate_data_uri("data:image/pngbase64iVBORw0KGgo")

    def test_size_limit_fails(self):
        """Data URI exceeding size limit should fail."""
        large_data = "x" * (11 * 1024 * 1024)  # 11MB
        uri = f"data:image/png;base64,{large_data}"
        with pytest.raises(AssetValidationError, match="exceeds 10MB"):
            validate_data_uri(uri)


class TestImageURLValidation:
    """Test image URL validation."""

    def test_valid_image_url(self):
        """Valid image URL should pass."""
        validate_image_url("https://example.com/image.png", check_mime=False)

    def test_valid_data_uri_image(self):
        """Valid data URI image should pass."""
        uri = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        validate_image_url(uri, check_mime=False)

    def test_javascript_image_url_fails(self):
        """JavaScript URL should fail even for images."""
        with pytest.raises(AssetValidationError, match="scheme not allowed"):
            validate_image_url("javascript:alert('xss')", check_mime=False)


class TestAssetValidation:
    """Test full asset validation."""

    def test_valid_html_asset(self):
        """Valid HTML asset should pass."""
        asset = {
            "asset_type": "html",
            "content": "<div><h1>Test</h1></div>",
        }
        validate_asset(asset)

    def test_valid_css_asset(self):
        """Valid CSS asset should pass."""
        asset = {
            "asset_type": "css",
            "content": "body { margin: 0; }",
        }
        validate_asset(asset)

    def test_valid_javascript_asset(self):
        """Valid JavaScript asset should pass."""
        asset = {
            "asset_type": "javascript",
            "content": "console.log('test');",
        }
        validate_asset(asset)

    def test_valid_text_asset(self):
        """Valid text asset should pass."""
        asset = {
            "asset_type": "text",
            "content": "This is a headline",
        }
        validate_asset(asset)

    def test_valid_url_asset(self):
        """Valid URL asset should pass."""
        asset = {
            "asset_type": "url",
            "url": "https://example.com/landing",
        }
        validate_asset(asset)

    def test_valid_image_asset(self):
        """Valid image asset should pass."""
        asset = {
            "asset_type": "image",
            "url": "https://example.com/image.png",
            "width": 300,
            "height": 250,
            "format": "png",
        }
        validate_asset(asset)

    def test_invalid_html_asset_fails(self):
        """Invalid HTML asset should fail."""
        asset = {
            "asset_type": "html",
            "content": "Not HTML content",
        }
        with pytest.raises(AssetValidationError, match="must contain valid HTML tags"):
            validate_asset(asset)

    def test_invalid_image_dimensions_fail(self):
        """Image with invalid dimensions should fail."""
        asset = {
            "asset_type": "image",
            "url": "https://example.com/image.png",
            "width": 0,
        }
        with pytest.raises(AssetValidationError, match="must be a positive integer"):
            validate_asset(asset)

    def test_invalid_image_format_fails(self):
        """Image with invalid format should fail."""
        asset = {
            "asset_type": "image",
            "url": "https://example.com/image.png",
            "format": "exe",
        }
        with pytest.raises(AssetValidationError, match="format not allowed"):
            validate_asset(asset)

    def test_missing_asset_type_fails(self):
        """Asset without asset_type should fail."""
        asset = {
            "content": "test",
        }
        with pytest.raises(AssetValidationError, match="must have asset_type"):
            validate_asset(asset)

    def test_unknown_asset_type_fails(self):
        """Asset with unknown type should fail."""
        asset = {
            "asset_type": "unknown",
        }
        with pytest.raises(AssetValidationError, match="Unknown asset_type"):
            validate_asset(asset)


class TestManifestValidation:
    """Test full manifest validation."""

    def test_valid_manifest(self):
        """Valid manifest should pass."""
        manifest = {
            "format_id": "display_300x250",
            "assets": {
                "headline": {
                    "asset_type": "text",
                    "content": "Buy Now!",
                },
                "background": {
                    "asset_type": "image",
                    "url": "https://example.com/bg.png",
                    "width": 300,
                    "height": 250,
                },
                "clickthrough": {
                    "asset_type": "url",
                    "url": "https://example.com/landing",
                },
            },
        }
        errors = validate_manifest_assets(manifest)
        assert errors == []

    def test_manifest_with_invalid_asset(self):
        """Manifest with invalid asset should return errors."""
        manifest = {
            "format_id": "display_300x250",
            "assets": {
                "headline": {
                    "asset_type": "text",
                    "content": "",  # Invalid empty text
                },
            },
        }
        errors = validate_manifest_assets(manifest)
        assert len(errors) == 1
        assert "headline" in errors[0]
        assert "cannot be empty" in errors[0]

    def test_manifest_multiple_errors(self):
        """Manifest with multiple invalid assets should return all errors."""
        manifest = {
            "format_id": "display_300x250",
            "assets": {
                "headline": {
                    "asset_type": "text",
                    "content": "",  # Invalid
                },
                "background": {
                    "asset_type": "image",
                    "url": "javascript:alert('xss')",  # Invalid
                },
            },
        }
        errors = validate_manifest_assets(manifest)
        assert len(errors) == 2
        assert any("headline" in err for err in errors)
        assert any("background" in err for err in errors)

    def test_manifest_without_assets_fails(self):
        """Manifest without assets field should fail."""
        manifest = {
            "format_id": "display_300x250",
        }
        errors = validate_manifest_assets(manifest)
        assert len(errors) == 1
        assert "must contain assets" in errors[0]

    def test_invalid_manifest_type_fails(self):
        """Non-dict manifest should fail."""
        errors = validate_manifest_assets("not a dict")
        assert len(errors) == 1
        assert "must be a dictionary" in errors[0]
