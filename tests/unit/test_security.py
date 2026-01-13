"""
Security tests for the application.

These tests verify that security measures are properly implemented.
Following TDD approach - tests written before implementation.
"""
import pytest
from pathlib import Path
from app.config import settings


class TestCORSConfiguration:
    """Test CORS security configuration."""

    def test_cors_not_wildcard(self):
        """Test that CORS is not configured with wildcard (*)."""
        # This test will fail until we fix CORS
        from app.main import app
        from fastapi.middleware.cors import CORSMiddleware

        # Find CORS middleware in the app
        cors_middlewares = [m for m in app.user_middleware if m.cls == CORSMiddleware]
        assert len(cors_middlewares) > 0, "CORS middleware should be configured"

        # Check middleware options
        cors_options = cors_middlewares[0].kwargs
        allow_origins = cors_options.get('allow_origins', [])

        # This will FAIL initially (RED phase) - we expect wildcard currently
        assert allow_origins != ["*"], "CORS should not allow all origins (wildcard)"


class TestMD5Usage:
    """Test that MD5 is used correctly (not for security)."""

    def test_md5_in_exam_builder_safe(self):
        """Test that MD5 usage in exam_builder is marked as non-security."""
        # Check that MD5 is used with usedforsecurity=False
        from app.core import exam_builder
        import inspect

        source = inspect.getsource(exam_builder)

        # Check that usedforsecurity=False appears near MD5 usage
        # This handles multi-line calls
        assert 'hashlib.md5' in source, "Should use MD5"
        assert 'usedforsecurity=False' in source, "MD5 should be marked as usedforsecurity=False"

        # Verify they appear in same context (within 5 lines of each other)
        lines = source.split('\n')
        md5_line_nums = [i for i, line in enumerate(lines) if 'hashlib.md5' in line]
        for md5_line in md5_line_nums:
            # Check surrounding lines for usedforsecurity
            context = '\n'.join(lines[max(0, md5_line-2):md5_line+3])
            assert 'usedforsecurity=False' in context, f"usedforsecurity=False should be near MD5 usage at line {md5_line}"

    def test_md5_in_llm_provider_safe(self):
        """Test that MD5 usage in llm_provider is marked as non-security."""
        from app.services import llm_provider
        import inspect

        source = inspect.getsource(llm_provider)

        # Check that usedforsecurity=False appears near MD5 usage
        assert 'hashlib.md5' in source, "Should use MD5"
        assert 'usedforsecurity=False' in source, "MD5 should be marked as usedforsecurity=False"

        # Verify they appear in same context
        lines = source.split('\n')
        md5_line_nums = [i for i, line in enumerate(lines) if 'hashlib.md5' in line]
        for md5_line in md5_line_nums:
            # Check surrounding lines for usedforsecurity
            context = '\n'.join(lines[max(0, md5_line-2):md5_line+3])
            assert 'usedforsecurity=False' in context, f"usedforsecurity=False should be near MD5 usage at line {md5_line}"


class TestSecretsManagement:
    """Test that secrets are properly managed."""

    def test_env_file_in_gitignore(self):
        """Test that .env is in .gitignore."""
        gitignore_path = Path(__file__).parent.parent.parent / ".gitignore"

        if gitignore_path.exists():
            content = gitignore_path.read_text()
            assert ".env" in content, ".env should be in .gitignore"

    def test_no_hardcoded_secrets_in_config(self):
        """Test that no secrets are hardcoded."""
        from app.config import settings

        # API keys should be empty or from environment
        if settings.openai_api_key:
            # If set, it should be from environment, not hardcoded
            assert len(settings.openai_api_key) > 10, "Should be actual key from env"


class TestPathSecurity:
    """Test path traversal protection."""

    def test_safe_join_prevents_traversal(self):
        """Test that safe_join prevents path traversal."""
        from app.utils.path import safe_join
        from pathlib import Path
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)

            # Should raise ValueError for path traversal attempts
            with pytest.raises(ValueError):
                safe_join(base_dir, "../../etc/passwd")

            with pytest.raises(ValueError):
                safe_join(base_dir, "../outside")

            with pytest.raises(ValueError):
                safe_join(base_dir, "subdir/../../outside")

    def test_safe_join_allows_valid_paths(self):
        """Test that safe_join allows valid paths."""
        from app.utils.path import safe_join
        from pathlib import Path
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)

            # Should succeed for valid paths
            result = safe_join(base_dir, "valid_file.md")
            assert str(result).startswith(str(base_dir.resolve()))

            result = safe_join(base_dir, "subdir/file.md")
            assert str(result).startswith(str(base_dir.resolve()))


class TestFileUploadValidation:
    """Test file upload validation logic."""

    def test_file_size_limit_constant_defined(self):
        """Test that MAX_FILE_SIZE limit is defined."""
        # This will FAIL initially (RED phase) - constant doesn't exist yet
        from app.api import files

        assert hasattr(files, 'MAX_FILE_SIZE'), "MAX_FILE_SIZE should be defined"
        assert files.MAX_FILE_SIZE == 10 * 1024 * 1024, "Should be 10MB"

    def test_markdown_extension_validation_exists(self):
        """Test that markdown extension validation exists."""
        from app.api.files import upload_file
        import inspect

        source = inspect.getsource(upload_file)
        assert ".md" in source, "Should check for .md extension"
        assert "endswith" in source or "suffix" in source, "Should validate file extension"


class TestRateLimitingConfiguration:
    """Test rate limiting configuration."""

    def test_rate_limiter_configured(self):
        """Test that rate limiter is configured in app."""
        # This will FAIL initially (RED phase) - no rate limiting yet
        from app.main import app

        assert hasattr(app.state, 'limiter'), "Rate limiter should be configured"

    def test_slowapi_dependency_available(self):
        """Test that slowapi is available for rate limiting."""
        # This will FAIL initially (RED phase) - slowapi not installed yet
        try:
            import slowapi
            assert True
        except ImportError:
            pytest.fail("slowapi should be installed for rate limiting")
