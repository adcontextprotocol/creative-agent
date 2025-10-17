"""Unit tests for storage.py error handling paths.

These tests cover error scenarios like missing S3 credentials,
S3 upload failures, None manifests, and environment validation.
"""

from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError, NoCredentialsError

from creative_agent.data.standard_formats import AGENT_URL, get_format_by_id
from creative_agent.schemas_generated._schemas_v1_core_format_json import FormatId
from creative_agent.storage import (
    _validate_s3_config,
    generate_preview_html,
    upload_preview_html,
)


class TestS3ConfigValidation:
    """Test environment variable validation for S3."""

    def test_validation_skipped_in_non_production(self, monkeypatch):
        """Validation should be skipped when ENVIRONMENT is not production."""
        monkeypatch.setenv("ENVIRONMENT", "development")
        monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
        monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)

        # Should not raise even with missing credentials
        _validate_s3_config()

    def test_validation_passes_with_all_credentials(self, monkeypatch):
        """Validation should pass when all required env vars are set."""
        # Mock the module-level variables that were loaded at import time
        import creative_agent.storage as storage_module

        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setattr(storage_module, "AWS_ACCESS_KEY_ID", "test-key")
        monkeypatch.setattr(storage_module, "AWS_SECRET_ACCESS_KEY", "test-secret")
        monkeypatch.setattr(storage_module, "AWS_ENDPOINT_URL", "https://test.s3.example.com")

        _validate_s3_config()

    def test_validation_fails_missing_access_key(self, monkeypatch):
        """Validation should fail when AWS_ACCESS_KEY_ID is missing."""
        import creative_agent.storage as storage_module

        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setattr(storage_module, "AWS_ACCESS_KEY_ID", None)
        monkeypatch.setattr(storage_module, "AWS_SECRET_ACCESS_KEY", "test-secret")
        monkeypatch.setattr(storage_module, "AWS_ENDPOINT_URL", "https://test.s3.example.com")

        with pytest.raises(RuntimeError, match=r"Missing required S3 configuration.*AWS_ACCESS_KEY_ID"):
            _validate_s3_config()

    def test_validation_fails_missing_secret_key(self, monkeypatch):
        """Validation should fail when AWS_SECRET_ACCESS_KEY is missing."""
        import creative_agent.storage as storage_module

        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setattr(storage_module, "AWS_ACCESS_KEY_ID", "test-key")
        monkeypatch.setattr(storage_module, "AWS_SECRET_ACCESS_KEY", None)
        monkeypatch.setattr(storage_module, "AWS_ENDPOINT_URL", "https://test.s3.example.com")

        with pytest.raises(RuntimeError, match=r"Missing required S3 configuration.*AWS_SECRET_ACCESS_KEY"):
            _validate_s3_config()

    def test_validation_fails_missing_endpoint(self, monkeypatch):
        """Validation should fail when AWS_ENDPOINT_URL_S3 is missing."""
        import creative_agent.storage as storage_module

        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setattr(storage_module, "AWS_ACCESS_KEY_ID", "test-key")
        monkeypatch.setattr(storage_module, "AWS_SECRET_ACCESS_KEY", "test-secret")
        monkeypatch.setattr(storage_module, "AWS_ENDPOINT_URL", None)

        with pytest.raises(RuntimeError, match=r"Missing required S3 configuration.*AWS_ENDPOINT_URL_S3"):
            _validate_s3_config()

    def test_validation_fails_missing_multiple(self, monkeypatch):
        """Validation should report all missing credentials."""
        import creative_agent.storage as storage_module

        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setattr(storage_module, "AWS_ACCESS_KEY_ID", None)
        monkeypatch.setattr(storage_module, "AWS_SECRET_ACCESS_KEY", None)
        monkeypatch.setattr(storage_module, "AWS_ENDPOINT_URL", "https://test.s3.example.com")

        with pytest.raises(RuntimeError, match=r"AWS_ACCESS_KEY_ID.*AWS_SECRET_ACCESS_KEY"):
            _validate_s3_config()


class TestS3UploadErrorHandling:
    """Test S3 upload error scenarios."""

    @patch("creative_agent.storage.get_s3_client")
    def test_upload_no_credentials_error(self, mock_get_client):
        """Should raise ValueError with clear message when S3 credentials missing."""
        mock_s3 = MagicMock()
        mock_s3.put_object.side_effect = NoCredentialsError()
        mock_get_client.return_value = mock_s3

        with pytest.raises(
            ValueError, match=r"S3 credentials not configured.*AWS_ACCESS_KEY_ID.*AWS_SECRET_ACCESS_KEY"
        ):
            upload_preview_html("test-preview-id", "mobile", "<html>test</html>")

    @patch("creative_agent.storage.get_s3_client")
    def test_upload_client_error_403(self, mock_get_client):
        """Should raise ValueError with error code when S3 returns 403."""
        mock_s3 = MagicMock()
        error_response: dict[str, dict[str, str]] = {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}}
        mock_s3.put_object.side_effect = ClientError(error_response, "PutObject")  # type: ignore[arg-type]
        mock_get_client.return_value = mock_s3

        with pytest.raises(ValueError, match="S3 upload failed \\(AccessDenied\\)"):
            upload_preview_html("test-preview-id", "mobile", "<html>test</html>")

    @patch("creative_agent.storage.get_s3_client")
    def test_upload_client_error_unknown(self, mock_get_client):
        """Should raise ValueError with 'Unknown' when error code missing."""
        mock_s3 = MagicMock()
        error_response: dict[str, dict[str, str]] = {"Error": {}}  # No Code field
        mock_s3.put_object.side_effect = ClientError(error_response, "PutObject")  # type: ignore[arg-type]
        mock_get_client.return_value = mock_s3

        with pytest.raises(ValueError, match="S3 upload failed \\(Unknown\\)"):
            upload_preview_html("test-preview-id", "mobile", "<html>test</html>")

    @patch("creative_agent.storage.get_s3_client")
    def test_upload_unexpected_error(self, mock_get_client):
        """Should raise ValueError for unexpected errors."""
        mock_s3 = MagicMock()
        mock_s3.put_object.side_effect = RuntimeError("Network timeout")
        mock_get_client.return_value = mock_s3

        with pytest.raises(ValueError, match=r"Unexpected error during S3 upload.*Network timeout"):
            upload_preview_html("test-preview-id", "mobile", "<html>test</html>")


class TestGeneratePreviewHTMLNoneManifest:
    """Test generate_preview_html with None manifest."""

    def test_none_manifest_generates_html(self):
        """Should handle None manifest by showing format name without image."""
        format_obj = get_format_by_id(FormatId(agent_url=AGENT_URL, id="display_300x250_image"))

        # Create input set mock
        input_set = MagicMock()
        input_set.name = "Test Input"

        html = generate_preview_html(format_obj, None, input_set)

        # Should contain format name
        assert format_obj.name in html
        # Should contain input name
        assert "Test Input" in html
        # Should not have an <img> tag (no assets)
        assert "<img" not in html
        # Should have placeholder div
        assert "display: flex" in html


class TestGeneratePreviewHTMLInvalidManifest:
    """Test generate_preview_html with invalid manifest types."""

    def test_invalid_manifest_type_raises_error(self):
        """Should raise TypeError for invalid manifest types."""
        format_obj = get_format_by_id(FormatId(agent_url=AGENT_URL, id="display_300x250_image"))

        input_set = MagicMock()
        input_set.name = "Test Input"

        # Pass invalid type (list instead of dict/Pydantic/None)
        with pytest.raises(TypeError, match="Invalid manifest type: <class 'list'>"):
            generate_preview_html(format_obj, [], input_set)

    def test_invalid_manifest_type_string_raises_error(self):
        """Should raise TypeError when manifest is string."""
        format_obj = get_format_by_id(FormatId(agent_url=AGENT_URL, id="display_300x250_image"))

        input_set = MagicMock()
        input_set.name = "Test Input"

        with pytest.raises(TypeError, match="Invalid manifest type: <class 'str'>"):
            generate_preview_html(format_obj, "invalid", input_set)
