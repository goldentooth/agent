"""Tests for input validation and sanitization system."""

from typing import Any

import pytest

from goldentooth_agent.core.flow_agent import FlowIOSchema
from goldentooth_agent.core.security.input_validation import (
    InputSanitizer,
    InputValidator,
    SecurityConfig,
    ValidationError,
    sanitize_string,
    validate_file_path,
    validate_flow_input,
    validate_json_payload,
    validate_url,
)


class TestSecurityConfig:
    """Test security configuration."""

    def test_security_config_defaults(self):
        config = SecurityConfig()

        assert config.max_string_length == 10000
        assert config.max_list_length == 1000
        assert config.max_dict_depth == 10
        assert config.allowed_file_extensions == {
            ".txt",
            ".json",
            ".yaml",
            ".yml",
            ".md",
        }
        assert config.blocked_domains == {"localhost", "127.0.0.1", "::1"}
        assert config.enable_xss_protection is True
        assert config.enable_sql_injection_protection is True
        assert config.enable_path_traversal_protection is True

    def test_security_config_custom_values(self):
        config = SecurityConfig(
            max_string_length=5000,
            max_list_length=500,
            blocked_domains={"evil.com", "malware.net"},
        )

        assert config.max_string_length == 5000
        assert config.max_list_length == 500
        assert "evil.com" in config.blocked_domains
        assert "malware.net" in config.blocked_domains


class TestInputValidator:
    """Test input validation functionality."""

    @pytest.fixture
    def validator(self):
        return InputValidator()

    @pytest.fixture
    def strict_validator(self):
        config = SecurityConfig(
            max_string_length=100, max_list_length=10, max_dict_depth=3
        )
        return InputValidator(config)

    def test_validate_string_success(self, validator):
        # Valid strings should pass
        assert validator.validate_string("Hello, world!") == "Hello, world!"
        assert validator.validate_string("") == ""
        assert (
            validator.validate_string("Normal text with spaces and numbers 123")
            is not None
        )

    def test_validate_string_length_limit(self, strict_validator):
        # String within limit should pass
        short_string = "a" * 50
        assert strict_validator.validate_string(short_string) == short_string

        # String exceeding limit should fail
        long_string = "a" * 200
        with pytest.raises(ValidationError, match="String length exceeds maximum"):
            strict_validator.validate_string(long_string)

    def test_validate_string_xss_protection(self, validator):
        # XSS attempts should be blocked
        malicious_strings = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "onclick='alert(\"xss\")'",
            "<iframe src='javascript:alert(\"xss\")'></iframe>",
        ]

        for malicious in malicious_strings:
            with pytest.raises(ValidationError, match="Potential XSS"):
                validator.validate_string(malicious)

    def test_validate_string_sql_injection_protection(self, validator):
        # SQL injection attempts should be blocked
        malicious_strings = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "UNION SELECT * FROM passwords",
            "' OR 1=1 --",
            "; DELETE FROM users WHERE 1=1 --",
        ]

        for malicious in malicious_strings:
            with pytest.raises(ValidationError, match="Potential SQL injection"):
                validator.validate_string(malicious)

    def test_validate_list_success(self, validator):
        # Valid lists should pass
        assert validator.validate_list([1, 2, 3]) == [1, 2, 3]
        assert validator.validate_list([]) == []
        assert validator.validate_list(["a", "b", "c"]) == ["a", "b", "c"]

    def test_validate_list_length_limit(self, strict_validator):
        # List within limit should pass
        short_list = list(range(5))
        assert strict_validator.validate_list(short_list) == short_list

        # List exceeding limit should fail
        long_list = list(range(20))
        with pytest.raises(ValidationError, match="List length exceeds maximum"):
            strict_validator.validate_list(long_list)

    def test_validate_dict_success(self, validator):
        # Valid dictionaries should pass
        simple_dict = {"key": "value"}
        assert validator.validate_dict(simple_dict) == simple_dict

        nested_dict = {"level1": {"level2": {"level3": "value"}}}
        result = validator.validate_dict(nested_dict)
        assert result == nested_dict

    def test_validate_dict_depth_limit(self, strict_validator):
        # Dict within depth limit should pass
        shallow_dict = {"level1": {"level2": "value"}}
        assert strict_validator.validate_dict(shallow_dict) == shallow_dict

        # Dict exceeding depth limit should fail
        deep_dict = {"l1": {"l2": {"l3": {"l4": "value"}}}}
        with pytest.raises(
            ValidationError, match="Dictionary nesting exceeds maximum depth"
        ):
            strict_validator.validate_dict(deep_dict)

    def test_validate_any_recursive(self, validator):
        # Complex nested structure should be validated recursively
        complex_data = {
            "strings": ["safe string", "another safe string"],
            "numbers": [1, 2, 3],
            "nested": {"inner_list": ["a", "b"], "inner_dict": {"key": "value"}},
        }

        result = validator.validate_any(complex_data)
        assert result == complex_data

    def test_validate_any_with_malicious_content(self, validator):
        # Nested malicious content should be caught
        malicious_data = {
            "safe_key": "safe_value",
            "malicious_key": "<script>alert('xss')</script>",
            "nested": {"deep_malicious": "'; DROP TABLE users; --"},
        }

        with pytest.raises(ValidationError):
            validator.validate_any(malicious_data)


class TestInputSanitizer:
    """Test input sanitization functionality."""

    @pytest.fixture
    def sanitizer(self):
        return InputSanitizer()

    def test_sanitize_string_html(self, sanitizer):
        # HTML should be escaped
        html_input = "<script>alert('test')</script>"
        sanitized = sanitizer.sanitize_string(html_input)
        assert "<script>" not in sanitized
        assert "&lt;script&gt;" in sanitized

    def test_sanitize_string_unicode_normalization(self, sanitizer):
        # Unicode should be normalized
        unicode_input = "café"  # Contains combining characters
        sanitized = sanitizer.sanitize_string(unicode_input)
        assert sanitized is not None
        assert len(sanitized) > 0

    def test_sanitize_string_whitespace(self, sanitizer):
        # Whitespace should be cleaned
        whitespace_input = "  \t\n  hello world  \r\n  "
        sanitized = sanitizer.sanitize_string(whitespace_input)
        assert sanitized == "hello world"

    def test_sanitize_dict_recursive(self, sanitizer):
        # Dictionaries should be sanitized recursively
        dirty_dict = {
            "clean_key": "clean_value",
            "dirty_key": "<script>alert('xss')</script>",
            "nested": {"inner_dirty": "  dirty value  "},
        }

        clean_dict = sanitizer.sanitize_dict(dirty_dict)

        assert clean_dict["clean_key"] == "clean_value"
        assert "<script>" not in clean_dict["dirty_key"]
        assert clean_dict["nested"]["inner_dirty"] == "dirty value"

    def test_sanitize_list_recursive(self, sanitizer):
        # Lists should be sanitized recursively
        dirty_list = [
            "clean item",
            "<script>alert('xss')</script>",
            {"nested_dirty": "  dirty  "},
        ]

        clean_list = sanitizer.sanitize_list(dirty_list)

        assert clean_list[0] == "clean item"
        assert "<script>" not in clean_list[1]
        assert clean_list[2]["nested_dirty"] == "dirty"


class TestFilePathValidation:
    """Test file path validation."""

    def test_validate_file_path_success(self):
        # Valid file paths should pass
        valid_paths = [
            "/safe/path/file.txt",
            "relative/path/file.json",
            "/home/user/documents/file.md",
        ]

        for path in valid_paths:
            result = validate_file_path(path)
            assert result == path

    def test_validate_file_path_traversal_protection(self):
        # Path traversal attempts should be blocked
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "/safe/path/../../../etc/passwd",
            "file.txt/../../../sensitive.txt",
            "../../.env",
        ]

        for path in malicious_paths:
            with pytest.raises(ValidationError, match="Path traversal"):
                validate_file_path(path)

    def test_validate_file_path_extension_validation(self):
        # Only allowed extensions should pass
        config = SecurityConfig(allowed_file_extensions={".txt", ".json"})

        # Allowed extensions should pass
        assert validate_file_path("file.txt", config) == "file.txt"
        assert validate_file_path("data.json", config) == "data.json"

        # Disallowed extensions should fail
        with pytest.raises(ValidationError, match="File extension not allowed"):
            validate_file_path("script.exe", config)

        with pytest.raises(ValidationError, match="File extension not allowed"):
            validate_file_path("config.php", config)

    def test_validate_file_path_absolute_vs_relative(self):
        # Both absolute and relative paths should be validated
        config = SecurityConfig()

        # Absolute path with traversal should fail
        with pytest.raises(ValidationError):
            validate_file_path("/home/user/../../../etc/passwd", config)

        # Relative path with traversal should fail
        with pytest.raises(ValidationError):
            validate_file_path("../../../etc/passwd", config)


class TestUrlValidation:
    """Test URL validation."""

    def test_validate_url_success(self):
        # Valid URLs should pass
        valid_urls = [
            "https://api.example.com/data",
            "http://public-api.com/endpoint",
            "https://secure-api.net/v1/users",
        ]

        for url in valid_urls:
            result = validate_url(url)
            assert result == url

    def test_validate_url_blocked_domains(self):
        # Blocked domains should be rejected
        config = SecurityConfig(
            blocked_domains={"localhost", "127.0.0.1", "internal.com"}
        )

        blocked_urls = [
            "http://localhost:8080/api",
            "https://127.0.0.1:443/data",
            "http://internal.com/secret",
            "https://internal.com:8443/api",
        ]

        for url in blocked_urls:
            with pytest.raises(ValidationError, match="Domain is blocked"):
                validate_url(url, config)

    def test_validate_url_scheme_validation(self):
        # Only HTTP/HTTPS should be allowed
        invalid_schemes = [
            "ftp://files.example.com/data",
            "file:///etc/passwd",
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
        ]

        for url in invalid_schemes:
            with pytest.raises(ValidationError, match="Invalid URL scheme"):
                validate_url(url)

    def test_validate_url_malformed(self):
        # Malformed URLs should be rejected
        malformed_urls = [
            "not-a-url",
            "http://",
            "https://",
            "://example.com",
            "http:///path",
        ]

        for url in malformed_urls:
            with pytest.raises(ValidationError, match="Invalid URL format"):
                validate_url(url)


class TestJsonPayloadValidation:
    """Test JSON payload validation."""

    def test_validate_json_payload_success(self):
        # Valid JSON payloads should pass
        valid_payloads = [
            '{"key": "value"}',
            '{"number": 123, "boolean": true}',
            '{"nested": {"array": [1, 2, 3]}}',
        ]

        for payload in valid_payloads:
            result = validate_json_payload(payload)
            assert isinstance(result, dict)

    def test_validate_json_payload_size_limit(self):
        # Large payloads should be rejected
        config = SecurityConfig(max_json_payload_size=100)

        # Small payload should pass
        small_payload = '{"key": "value"}'
        result = validate_json_payload(small_payload, config)
        assert result == {"key": "value"}

        # Large payload should fail
        large_payload = '{"data": "' + "x" * 200 + '"}'
        with pytest.raises(ValidationError, match="JSON payload exceeds maximum size"):
            validate_json_payload(large_payload, config)

    def test_validate_json_payload_malformed(self):
        # Malformed JSON should be rejected
        malformed_payloads = [
            '{"key": value}',  # Missing quotes
            '{"key": "value",}',  # Trailing comma
            '{key: "value"}',  # Unquoted key
            '{"unclosed": "value"',  # Missing closing brace
            "not json at all",
        ]

        for payload in malformed_payloads:
            with pytest.raises(ValidationError, match="Invalid JSON"):
                validate_json_payload(payload)


class TestFlowInputValidation:
    """Test Flow input validation integration."""

    class SampleInput(FlowIOSchema):
        name: str
        description: str
        count: int
        tags: list[str]
        metadata: dict[str, Any]

    def test_validate_flow_input_success(self):
        # Valid Flow input should pass
        valid_data = {
            "name": "test_flow",
            "description": "A test flow for validation",
            "count": 42,
            "tags": ["test", "validation"],
            "metadata": {"version": "1.0", "author": "tester"},
        }

        result = validate_flow_input(valid_data, self.SampleInput)
        assert isinstance(result, self.SampleInput)
        assert result.name == "test_flow"
        assert result.count == 42

    def test_validate_flow_input_with_malicious_content(self):
        # Malicious content should be caught
        malicious_data = {
            "name": "<script>alert('xss')</script>",
            "description": "'; DROP TABLE flows; --",
            "count": 42,
            "tags": ["safe", "<img src=x onerror=alert('xss')>"],
            "metadata": {"safe": "value", "malicious": "javascript:alert('xss')"},
        }

        with pytest.raises(ValidationError):
            validate_flow_input(malicious_data, self.SampleInput)

    def test_validate_flow_input_sanitization_mode(self):
        # Test sanitization instead of rejection
        dirty_data = {
            "name": "  test_flow  ",
            "description": "<b>Bold description</b>",
            "count": 42,
            "tags": ["  tag1  ", "tag2"],
            "metadata": {"key": "  value  "},
        }

        result = validate_flow_input(dirty_data, self.SampleInput, sanitize=True)

        assert result.name == "test_flow"  # Whitespace trimmed
        assert "&lt;b&gt;" in result.description  # HTML escaped
        assert "tag1" in result.tags  # List items sanitized


class TestSanitizationHelpers:
    """Test standalone sanitization helper functions."""

    def test_sanitize_string_function(self):
        # Test the standalone sanitize_string function
        assert sanitize_string("  hello  ") == "hello"
        assert sanitize_string("<script>test</script>") != "<script>test</script>"
        assert "&lt;script&gt;" in sanitize_string("<script>test</script>")

    def test_sanitize_string_preserves_safe_content(self):
        # Safe content should be preserved
        safe_strings = [
            "Hello, World!",
            "123 Main Street",
            "user@example.com",
            "Normal text with punctuation: comma, period.",
            "Unicode: café, naïve, résumé",
        ]

        for safe_string in safe_strings:
            sanitized = sanitize_string(safe_string)
            # Should be mostly unchanged (except whitespace normalization)
            assert len(sanitized) > 0
            assert not any(char in sanitized for char in ["<", ">", "&", "script"])


class TestValidationPerformance:
    """Test validation performance with large inputs."""

    @pytest.mark.performance
    def test_large_input_validation_performance(self):
        # Test that validation doesn't timeout on large inputs
        validator = InputValidator()

        # Create a large but valid data structure
        large_data = {
            "large_list": list(range(1000)),
            "large_string": "a" * 5000,
            "nested_data": {f"key_{i}": f"value_{i}" for i in range(100)},
        }

        import time

        start_time = time.time()
        result = validator.validate_any(large_data)
        execution_time = time.time() - start_time

        assert result == large_data
        assert execution_time < 1.0  # Should complete within 1 second

    @pytest.mark.performance
    def test_sanitization_performance(self):
        # Test sanitization performance
        sanitizer = InputSanitizer()

        # Create data with lots of content to sanitize
        dirty_data = {
            "html_content": "<div><p>Test</p></div>" * 100,
            "whitespace_content": "  spaced  " * 100,
            "nested": {
                f"dirty_key_{i}": f"  <span>content {i}</span>  " for i in range(50)
            },
        }

        import time

        start_time = time.time()
        result = sanitizer.sanitize_any(dirty_data)
        execution_time = time.time() - start_time

        assert isinstance(result, dict)
        assert execution_time < 2.0  # Should complete within 2 seconds


class TestValidationErrorHandling:
    """Test error handling and edge cases."""

    def test_validation_error_details(self):
        validator = InputValidator()

        try:
            validator.validate_string("<script>alert('xss')</script>")
            raise AssertionError("Should have raised ValidationError")
        except ValidationError as e:
            assert "Potential XSS" in str(e)
            assert hasattr(e, "validation_type")
            assert hasattr(e, "input_value")

    def test_none_input_handling(self):
        validator = InputValidator()

        # None values should be handled gracefully
        assert validator.validate_any(None) is None
        assert validator.validate_string(None) is None
        assert validator.validate_list(None) is None
        assert validator.validate_dict(None) is None

    def test_non_string_type_validation(self):
        validator = InputValidator()

        # Non-string types should pass through validate_string
        assert validator.validate_string(123) == 123
        assert validator.validate_string(True) is True
        assert validator.validate_string([1, 2, 3]) == [1, 2, 3]
