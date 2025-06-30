# Security

Security module

## Overview

- **Complexity**: Critical
- **Files**: 4 Python files
- **Lines of Code**: ~1261
- **Classes**: 26
- **Functions**: 96

## API Reference

### Classes

#### SecretError
Exception raised for secret management errors.

#### SecretConfig
Configuration for secret management system.

#### SecretMetadata
Metadata for tracking secret lifecycle and compliance.

**Public Methods:**
- `is_expired()`
- `needs_rotation()`
- `to_dict()`
- `from_dict()`

#### SecretValue
Wrapper for secret values with memory protection.

**Public Methods:**
- `value()`

#### EncryptionProvider
Abstract base class for encryption providers.

**Public Methods:**
- `encrypt()`
- `decrypt()`

#### FernetEncryptionProvider
Fernet symmetric encryption provider using cryptography library.

**Public Methods:**
- `generate_key()`
- `encrypt()`
- `decrypt()`

#### PlaintextEncryptionProvider
No-op encryption provider for testing (DO NOT USE IN PRODUCTION).

**Public Methods:**
- `encrypt()`
- `decrypt()`

#### SecretStore
Abstract base class for secret storage backends.

**Public Methods:**
- `store_secret()`
- `get_secret()`
- `delete_secret()`
- `list_secrets()`

#### EnvironmentSecretStore
Store secrets in environment variables (encrypted).

**Public Methods:**
- `store_secret()`
- `get_secret()`
- `delete_secret()`
- `list_secrets()`

#### FileSecretStore
Store secrets in encrypted files.

**Public Methods:**
- `store_secret()`
- `get_secret()`
- `delete_secret()`
- `list_secrets()`

#### InMemorySecretStore
Store secrets in memory (for testing).

**Public Methods:**
- `store_secret()`
- `get_secret()`
- `delete_secret()`
- `list_secrets()`

#### SecretManager
Main secret management class.

**Public Methods:**
- `store_secret()`
- `get_secret()`
- `delete_secret()`
- `list_secrets()`
- `secret_exists()`
- `get_secret_metadata()`
- `update_secret_metadata()`
- `rotate_secret()`
- `find_secrets_needing_rotation()`
- `find_expired_secrets()`

#### RateLimitError
Exception raised when rate limit is exceeded.

#### RateLimitConfig
Configuration for rate limiting system.

#### RateLimitResult
Result of a rate limit check.

#### RateLimitStore
Abstract base class for rate limit storage backends.

**Public Methods:**
- `get()`
- `set()`
- `increment()`
- `delete()`

#### MemoryRateLimitStore
In-memory rate limit store with TTL support.

**Public Methods:**
- `force_cleanup()`
- `get()`
- `set()`
- `increment()`
- `delete()`

#### RateLimiter
Abstract base class for rate limiting algorithms.

**Public Methods:**
- `check_rate_limit()`

#### TokenBucketLimiter
Token bucket rate limiting algorithm.

**Public Methods:**
- `check_rate_limit()`

#### SlidingWindowLimiter
Sliding window rate limiting algorithm.

**Public Methods:**
- `check_rate_limit()`

#### FixedWindowLimiter
Fixed window rate limiting algorithm.

**Public Methods:**
- `check_rate_limit()`

#### ValidationError
Custom validation error with detailed context.

#### SecurityConfig
Security configuration for input validation.

#### SanitizationConfig
Configuration for input sanitization.

#### InputValidator
Comprehensive input validator with security-focused validation rules.

**Public Methods:**
- `validate_string()`
- `validate_list()`
- `validate_dict()`
- `validate_any()`

#### InputSanitizer
Input sanitizer for cleaning potentially malicious or dirty input.

**Public Methods:**
- `sanitize_string()`
- `sanitize_list()`
- `sanitize_dict()`
- `sanitize_any()`

### Functions

#### `def create_secret_manager(config: SecretConfig | None) -> SecretManager`
Create a secret manager instance with optional config.

#### `def get_global_manager() -> SecretManager`
Get or create the global secret manager.

#### `def set_secret(name: str, value: str, secret_type: str, description: str, tags: list[str] | None) -> None`
Store a secret using the global manager.

#### `def get_secret(name: str) -> SecretValue`
Retrieve a secret using the global manager.

#### `def delete_secret(name: str) -> None`
Delete a secret using the global manager.

#### `def secret_exists(name: str) -> bool`
Check if a secret exists using the global manager.

#### `def rotate_secret(name: str, new_value: str) -> None`
Rotate a secret using the global manager.

#### `def create_rate_limiter(config: RateLimitConfig, store: RateLimitStore | None) -> RateLimiter`
Create a rate limiter based on configuration.

#### `def get_global_limiter() -> RateLimiter`
Get or create the global rate limiter.

#### `async def check_rate_limit(key: str) -> RateLimitResult`
Check rate limit using the global limiter.

#### `def rate_limit_decorator(config: RateLimitConfig, key_func: Callable[..., str] | None) -> Callable[[Callable[..., Any]], Callable[..., Any]]`
Decorator to apply rate limiting to async functions.

#### `def validate_file_path(path: str, config: SecurityConfig | None) -> str`
Validate file path for security issues.

#### `def validate_url(url: str, config: SecurityConfig | None) -> str`
Validate URL for security issues.

#### `def validate_json_payload(payload: str, config: SecurityConfig | None) -> dict[str, Any]`
Validate JSON payload for security and format issues.

#### `def validate_flow_input(data: dict[str, Any], schema_class: type[T], sanitize: bool, config: SecurityConfig | None) -> T`
Validate Flow input data against schema with security checks.

#### `def sanitize_string(value: str, config: SanitizationConfig | None) -> str`
Standalone string sanitization function.

### Constants

#### `T`

## Dependencies

### External Dependencies
- `__future__`
- `abc`
- `collections`
- `dataclasses`
- `datetime`
- `flow_agent`
- `functools`
- `html`
- `input_validation`
- `json`
- `os`
- `pathlib`
- `pydantic`
- `re`
- `time`
- `typing`
- `unicodedata`
- `urllib`

## Exports

This module exports the following symbols:

- `InputSanitizer`
- `InputValidator`
- `SanitizationConfig`
- `SecurityConfig`
- `ValidationError`
- `sanitize_string`
- `validate_file_path`
- `validate_flow_input`
- `validate_json_payload`
- `validate_url`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
