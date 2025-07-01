"""Comprehensive input validation and sanitization system.

This module provides enterprise-grade input validation and sanitization to protect against:
- XSS (Cross-Site Scripting) attacks
- SQL injection attempts
- Path traversal attacks
- Data injection and manipulation
- DoS through oversized inputs

All validation follows OWASP security guidelines and defensive programming principles.
"""

from __future__ import annotations

import html
import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeVar
from urllib.parse import urlparse

from pydantic import ValidationError as PydanticValidationError

from ..flow_agent import FlowIOSchema

T = TypeVar("T", bound=FlowIOSchema)


class ValidationError(Exception):
    """Custom validation error with detailed context."""

    def __init__(
        self,
        message: str,
        validation_type: str = "unknown",
        input_value: Any = None,
        field_name: str | None = None,
    ):
        super().__init__(message)
        self.validation_type = validation_type
        self.input_value = input_value
        self.field_name = field_name


@dataclass
class SecurityConfig:
    """Security configuration for input validation."""

    # String validation limits
    max_string_length: int = 10000
    max_json_payload_size: int = 1024 * 1024  # 1MB

    # Collection validation limits
    max_list_length: int = 1000
    max_dict_depth: int = 10
    max_dict_size: int = 1000

    # File validation
    allowed_file_extensions: set[str] = field(
        default_factory=lambda: {".txt", ".json", ".yaml", ".yml", ".md"}
    )
    max_file_size_mb: int = 10

    # URL validation
    allowed_url_schemes: set[str] = field(default_factory=lambda: {"http", "https"})
    blocked_domains: set[str] = field(
        default_factory=lambda: {"localhost", "127.0.0.1", "::1"}
    )

    # Security features
    enable_xss_protection: bool = True
    enable_sql_injection_protection: bool = True
    enable_path_traversal_protection: bool = True
    enable_unicode_validation: bool = True

    # Rate limiting (used by other modules)
    max_requests_per_minute: int = 100
    max_concurrent_requests: int = 10


@dataclass
class SanitizationConfig:
    """Configuration for input sanitization."""

    # HTML/XSS sanitization
    escape_html: bool = True
    remove_control_chars: bool = True
    normalize_unicode: bool = True

    # Whitespace handling
    trim_whitespace: bool = True
    normalize_whitespace: bool = True
    max_consecutive_spaces: int = 3

    # String transformation
    max_sanitized_length: int = 5000
    preserve_newlines: bool = True


class InputValidator:
    """Comprehensive input validator with security-focused validation rules."""

    def __init__(self, config: SecurityConfig | None = None):
        self.config = config or SecurityConfig()

        # Compile regex patterns for performance
        self._xss_patterns = [
            re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
            re.compile(r"javascript:", re.IGNORECASE),
            re.compile(r"on\w+\s*=", re.IGNORECASE),
            re.compile(r"<iframe[^>]*>.*?</iframe>", re.IGNORECASE | re.DOTALL),
            re.compile(r"<object[^>]*>.*?</object>", re.IGNORECASE | re.DOTALL),
            re.compile(r"<embed[^>]*>", re.IGNORECASE),
            re.compile(r"<link[^>]*>", re.IGNORECASE),
            re.compile(r"<meta[^>]*>", re.IGNORECASE),
        ]

        self._sql_patterns = [
            re.compile(r"';.*--", re.IGNORECASE),
            re.compile(r"'.*OR.*'1'.*=.*'1", re.IGNORECASE),
            re.compile(r"'\s*OR\s*'?\d+'?\s*=\s*'?\d+'?", re.IGNORECASE),
            re.compile(r"'\s*OR\s+\d+\s*=\s*\d+", re.IGNORECASE),
            re.compile(r"union.*select", re.IGNORECASE),
            re.compile(r"insert.*into", re.IGNORECASE),
            re.compile(r"delete.*from", re.IGNORECASE),
            re.compile(r"update.*set", re.IGNORECASE),
            re.compile(r"drop.*table", re.IGNORECASE),
            re.compile(r"create.*table", re.IGNORECASE),
            re.compile(r"alter.*table", re.IGNORECASE),
            re.compile(r"exec(ute)?", re.IGNORECASE),
            re.compile(r";\s*drop\s+table", re.IGNORECASE),
            re.compile(r";\s*delete\s+from", re.IGNORECASE),
        ]

        self._path_traversal_patterns = [
            re.compile(r"\.\.[\\/]"),
            re.compile(r"[\\/]\.\."),
            re.compile(r"\.\."),
        ]

    def validate_string(self, value: Any) -> Any:
        """Validate string input with security checks."""
        if value is None or not isinstance(value, str):
            return value

        # Length validation
        if len(value) > self.config.max_string_length:
            raise ValidationError(
                f"String length exceeds maximum allowed ({self.config.max_string_length})",
                validation_type="length_limit",
                input_value=value[:100] + "..." if len(value) > 100 else value,
            )

        if self.config.enable_xss_protection:
            self._check_xss_patterns(value)

        if self.config.enable_sql_injection_protection:
            self._check_sql_injection_patterns(value)

        if self.config.enable_unicode_validation:
            self._validate_unicode_safety(value)

        return value

    def validate_list(self, value: Any) -> Any:
        """Validate list input with size limits and recursive validation."""
        if value is None or not isinstance(value, list):
            return value

        # Length validation
        if len(value) > self.config.max_list_length:
            raise ValidationError(
                f"List length exceeds maximum allowed ({self.config.max_list_length})",
                validation_type="length_limit",
                input_value=f"[{len(value)} items]",
            )

        # Recursively validate list items
        validated_items = []
        for i, item in enumerate(value):
            try:
                validated_item = self.validate_any(item)
                validated_items.append(validated_item)
            except ValidationError as e:
                # Add context about list position
                raise ValidationError(
                    f"Validation error in list item {i}: {e}",
                    validation_type=e.validation_type,
                    input_value=e.input_value,
                    field_name=f"[{i}]",
                ) from e

        return validated_items

    def validate_dict(self, value: Any, current_depth: int = 0) -> Any:
        """Validate dictionary input with depth limits and recursive validation."""
        if value is None or not isinstance(value, dict):
            return value

        # Depth validation
        if current_depth >= self.config.max_dict_depth:
            raise ValidationError(
                f"Dictionary nesting exceeds maximum depth ({self.config.max_dict_depth})",
                validation_type="depth_limit",
                input_value="[deeply nested dict]",
            )

        # Size validation
        if len(value) > self.config.max_dict_size:
            raise ValidationError(
                f"Dictionary size exceeds maximum allowed ({self.config.max_dict_size})",
                validation_type="size_limit",
                input_value=f"[{len(value)} keys]",
            )

        # Recursively validate keys and values
        validated_dict = {}
        for key, val in value.items():
            try:
                # Validate key (should be string)
                validated_key = self.validate_string(key)
                # Validate value recursively
                validated_value = self.validate_any(val, current_depth + 1)
                validated_dict[validated_key] = validated_value
            except ValidationError as e:
                # Add context about dict key
                raise ValidationError(
                    f"Validation error in dict key '{key}': {e}",
                    validation_type=e.validation_type,
                    input_value=e.input_value,
                    field_name=str(key),
                ) from e

        return validated_dict

    def validate_any(self, value: Any, current_depth: int = 0) -> Any:
        """Validate any input type with appropriate method."""
        if value is None:
            return value
        elif isinstance(value, str):
            return self.validate_string(value)
        elif isinstance(value, list):
            return self.validate_list(value)
        elif isinstance(value, dict):
            return self.validate_dict(value, current_depth)
        else:
            # For other types (int, float, bool, etc.), return as-is
            return value

    def _check_xss_patterns(self, value: str) -> None:
        """Check for XSS attack patterns."""
        for pattern in self._xss_patterns:
            if pattern.search(value):
                raise ValidationError(
                    "Potential XSS attack detected",
                    validation_type="xss_protection",
                    input_value=value[:100] + "..." if len(value) > 100 else value,
                )

    def _check_sql_injection_patterns(self, value: str) -> None:
        """Check for SQL injection attack patterns."""
        for pattern in self._sql_patterns:
            if pattern.search(value):
                raise ValidationError(
                    "Potential SQL injection attack detected",
                    validation_type="sql_injection_protection",
                    input_value=value[:100] + "..." if len(value) > 100 else value,
                )

    def _validate_unicode_safety(self, value: str) -> None:
        """Validate Unicode characters for safety."""
        try:
            # Check for dangerous Unicode categories
            for char in value:
                category = unicodedata.category(char)
                # Block control characters except common whitespace
                if category.startswith("C") and char not in "\t\n\r ":
                    raise ValidationError(
                        f"Dangerous Unicode control character detected: {repr(char)}",
                        validation_type="unicode_safety",
                        input_value=value[:100] + "..." if len(value) > 100 else value,
                    )
        except UnicodeError as e:
            raise ValidationError(
                f"Invalid Unicode sequence: {e}",
                validation_type="unicode_safety",
                input_value=value[:100] + "..." if len(value) > 100 else value,
            ) from e


class InputSanitizer:
    """Input sanitizer for cleaning potentially malicious or dirty input."""

    def __init__(self, config: SanitizationConfig | None = None):
        self.config = config or SanitizationConfig()

    def sanitize_string(self, value: Any) -> Any:
        """Sanitize string input by escaping and normalizing."""
        if value is None or not isinstance(value, str):
            return value

        result = value

        # Unicode normalization
        if self.config.normalize_unicode:
            result = unicodedata.normalize("NFKC", result)

        # Remove control characters
        if self.config.remove_control_chars:
            result = "".join(
                char
                for char in result
                if unicodedata.category(char)[0] != "C" or char in "\t\n\r "
            )

        # HTML escaping
        if self.config.escape_html:
            result = html.escape(result, quote=True)

        # Whitespace handling
        if self.config.trim_whitespace:
            result = result.strip()

        if self.config.normalize_whitespace:
            # Replace multiple spaces with single spaces
            result = re.sub(r"\s+", " ", result)
            # Limit consecutive spaces
            if self.config.max_consecutive_spaces > 0:
                pattern = r" {" + str(self.config.max_consecutive_spaces + 1) + ",}"
                result = re.sub(
                    pattern, " " * self.config.max_consecutive_spaces, result
                )

        # Length limiting
        if len(result) > self.config.max_sanitized_length:
            result = result[: self.config.max_sanitized_length]

        return result

    def sanitize_list(self, value: Any) -> Any:
        """Sanitize list input recursively."""
        if value is None or not isinstance(value, list):
            return value

        return [self.sanitize_any(item) for item in value]

    def sanitize_dict(self, value: Any) -> Any:
        """Sanitize dictionary input recursively."""
        if value is None or not isinstance(value, dict):
            return value

        return {
            self.sanitize_string(key): self.sanitize_any(val)
            for key, val in value.items()
        }

    def sanitize_any(self, value: Any) -> Any:
        """Sanitize any input type with appropriate method."""
        if value is None:
            return value
        elif isinstance(value, str):
            return self.sanitize_string(value)
        elif isinstance(value, list):
            return self.sanitize_list(value)
        elif isinstance(value, dict):
            return self.sanitize_dict(value)
        else:
            return value


# Validation helper functions
def validate_file_path(path: str, config: SecurityConfig | None = None) -> str:
    """Validate file path for security issues."""
    config = config or SecurityConfig()

    if config.enable_path_traversal_protection:
        # Check for path traversal patterns
        validator = InputValidator(config)
        for pattern in validator._path_traversal_patterns:
            if pattern.search(path):
                raise ValidationError(
                    "Path traversal attempt detected",
                    validation_type="path_traversal",
                    input_value=path,
                )

    # Validate file extension
    if config.allowed_file_extensions:
        path_obj = Path(path)
        if path_obj.suffix.lower() not in config.allowed_file_extensions:
            raise ValidationError(
                f"File extension not allowed: {path_obj.suffix}",
                validation_type="file_extension",
                input_value=path,
            )

    return path


def validate_url(url: str, config: SecurityConfig | None = None) -> str:
    """Validate URL for security issues."""
    config = config or SecurityConfig()

    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValidationError(
            "Invalid URL format", validation_type="url_format", input_value=url
        ) from e

    # Check for missing scheme
    if not parsed.scheme:
        raise ValidationError(
            "Invalid URL format", validation_type="url_format", input_value=url
        )

    # Validate scheme first
    if parsed.scheme.lower() not in config.allowed_url_schemes:
        raise ValidationError(
            f"Invalid URL scheme: {parsed.scheme}",
            validation_type="url_scheme",
            input_value=url,
        )

    # Check for missing netloc (only for schemes that require it)
    if not parsed.netloc and parsed.scheme.lower() in ["http", "https", "ftp"]:
        raise ValidationError(
            "Invalid URL format", validation_type="url_format", input_value=url
        )

    # Check blocked domains
    hostname = parsed.hostname
    if hostname and any(
        blocked in hostname.lower() for blocked in config.blocked_domains
    ):
        raise ValidationError(
            f"Domain is blocked: {hostname}",
            validation_type="blocked_domain",
            input_value=url,
        )

    return url


def validate_json_payload(
    payload: str, config: SecurityConfig | None = None
) -> dict[str, Any]:
    """Validate JSON payload for security and format issues."""
    config = config or SecurityConfig()

    # Size validation
    if len(payload) > config.max_json_payload_size:
        raise ValidationError(
            f"JSON payload exceeds maximum size ({config.max_json_payload_size} bytes)",
            validation_type="payload_size",
            input_value=f"[{len(payload)} bytes]",
        )

    # Parse JSON
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as e:
        raise ValidationError(
            f"Invalid JSON format: {e}",
            validation_type="json_format",
            input_value=payload[:200] + "..." if len(payload) > 200 else payload,
        ) from e

    # Validate parsed data
    validator = InputValidator(config)
    validated_data = validator.validate_any(data)

    # Type validation - should be a dict since we parsed JSON
    if not isinstance(validated_data, dict):
        raise ValidationError(
            "Invalid data structure: expected object after validation",
            validation_type="structure",
            input_value=str(validated_data)[:200],
        )
    
    return validated_data


def validate_flow_input(
    data: dict[str, Any],
    schema_class: type[T],
    sanitize: bool = False,
    config: SecurityConfig | None = None,
) -> T:
    """Validate Flow input data against schema with security checks."""
    config = config or SecurityConfig()

    # Apply sanitization if requested
    if sanitize:
        sanitizer = InputSanitizer()
        data = sanitizer.sanitize_any(data)
    else:
        # Apply validation
        validator = InputValidator(config)
        data = validator.validate_any(data)

    # Validate against Pydantic schema
    try:
        return schema_class.model_validate(data)
    except PydanticValidationError as e:
        raise ValidationError(
            f"Schema validation failed: {e}",
            validation_type="schema_validation",
            input_value=str(data)[:200] + "..." if len(str(data)) > 200 else str(data),
        ) from e


def sanitize_string(value: str, config: SanitizationConfig | None = None) -> str:
    """Standalone string sanitization function."""
    sanitizer = InputSanitizer(config)
    result = sanitizer.sanitize_string(value)
    # Type assertion - should be str since input is str
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    return result
