# Security

Security module

## Background & Motivation

### Problem Statement

The security module addresses the challenge of managing security-related operations in a complex system architecture.

### Theoretical Foundation

#### Core Concepts

The module implements domain-specific concepts tailored to its functional requirements.

#### Design Philosophy

**Simplicity and Clarity**: Emphasizes straightforward implementations that are easy to understand and maintain.

### Technical Challenges Addressed

1. **Modularity**: Designing clean interfaces that promote reusability and testability
2. **Maintainability**: Structuring code for easy modification and extension
3. **Integration**: Seamlessly connecting with other system components

### Integration & Usage

The security module integrates with the broader system through well-defined interfaces.

**Key Dependencies:**
- __future__: Provides essential functionality required by this module
- abc: Provides essential functionality required by this module
- collections: Provides essential functionality required by this module
- dataclasses: Provides essential functionality required by this module
- datetime: Provides essential functionality required by this module

**Usage Patterns:**
- **Dependency Injection**: Services are provided through the Antidote DI container
- **Type-Safe Interfaces**: All public APIs use comprehensive type annotations
- **Error Propagation**: Exceptions are handled consistently with the system's error handling patterns

---

*This background file was generated using AI analysis of the security module. Please review and customize as needed.*

## Overview

- **Complexity**: Critical
- **Files**: 4 Python files
- **Lines of Code**: ~1275
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
- `is_expired(self, max_age_days: int) -> bool` - Check if secret has exceeded maximum age
- `needs_rotation(self) -> bool` - Check if secret needs rotation based on policy
- `to_dict(self) -> dict[str, Any]` - Convert metadata to dictionary for serialization
- `from_dict(cls, data: dict[str, Any]) -> SecretMetadata` - Create metadata from dictionary

#### SecretValue
Wrapper for secret values with memory protection.

**Public Methods:**
- `value(self) -> str` - Get the secret value

#### EncryptionProvider
Abstract base class for encryption providers.

**Public Methods:**
- `encrypt(self, plaintext: str) -> str` - Encrypt plaintext and return encrypted string
- `decrypt(self, encrypted: str) -> str` - Decrypt encrypted string and return plaintext

#### FernetEncryptionProvider
Fernet symmetric encryption provider using cryptography library.

**Public Methods:**
- `generate_key() -> bytes` - Generate a new Fernet encryption key
- `encrypt(self, plaintext: str) -> str` - Encrypt plaintext using Fernet
- `decrypt(self, encrypted: str) -> str` - Decrypt encrypted string using Fernet

#### PlaintextEncryptionProvider
No-op encryption provider for testing (DO NOT USE IN PRODUCTION).

**Public Methods:**
- `encrypt(self, plaintext: str) -> str` - Return plaintext unchanged (no encryption)
- `decrypt(self, encrypted: str) -> str` - Return encrypted string unchanged (no decryption)

#### SecretStore
Abstract base class for secret storage backends.

**Public Methods:**
- `store_secret(self, name: str, data: dict[str, Any]) -> None` - Store secret data
- `get_secret(self, name: str) -> dict[str, Any]` - Retrieve secret data
- `delete_secret(self, name: str) -> None` - Delete secret
- `list_secrets(self) -> list[str]` - List all secret names

#### EnvironmentSecretStore
Store secrets in environment variables (encrypted).

**Public Methods:**
- `store_secret(self, name: str, data: dict[str, Any]) -> None` - Store secret in environment variable
- `get_secret(self, name: str) -> dict[str, Any]` - Retrieve secret from environment variable
- `delete_secret(self, name: str) -> None` - Delete secret from environment
- `list_secrets(self) -> list[str]` - List all secrets in environment

#### FileSecretStore
Store secrets in encrypted files.

**Public Methods:**
- `store_secret(self, name: str, data: dict[str, Any]) -> None` - Store secret in file
- `get_secret(self, name: str) -> dict[str, Any]` - Retrieve secret from file
- `delete_secret(self, name: str) -> None` - Delete secret file
- `list_secrets(self) -> list[str]` - List all secret files

#### InMemorySecretStore
Store secrets in memory (for testing).

**Public Methods:**
- `store_secret(self, name: str, data: dict[str, Any]) -> None` - Store secret in memory
- `get_secret(self, name: str) -> dict[str, Any]` - Retrieve secret from memory
- `delete_secret(self, name: str) -> None` - Delete secret from memory
- `list_secrets(self) -> list[str]` - List all secrets in memory

#### SecretManager
Main secret management class.

**Public Methods:**
- `store_secret(self, name: str, value: str, metadata: SecretMetadata | None) -> None` - Store a secret with encryption and metadata
- `get_secret(self, name: str) -> SecretValue` - Retrieve and decrypt a secret
- `delete_secret(self, name: str) -> None` - Delete a secret
- `list_secrets(self) -> list[str]` - List all secret names
- `secret_exists(self, name: str) -> bool` - Check if a secret exists
- `get_secret_metadata(self, name: str) -> SecretMetadata` - Get only the metadata for a secret (without decrypting value)
- `update_secret_metadata(self, name: str, metadata: SecretMetadata) -> None` - Update metadata for an existing secret
- `rotate_secret(self, name: str, new_value: str) -> None` - Rotate a secret to a new value
- `find_secrets_needing_rotation(self) -> list[str]` - Find secrets that need rotation based on policy
- `find_expired_secrets(self) -> list[str]` - Find secrets that have exceeded maximum age

#### RateLimitError
Exception raised when rate limit is exceeded.

#### RateLimitConfig
Configuration for rate limiting system.

#### RateLimitResult
Result of a rate limit check.

#### RateLimitStore
Abstract base class for rate limit storage backends.

**Public Methods:**
- `async get(self, key: str) -> dict[str, Any] | None` - Get data for a key
- `async set(self, key: str, data: dict[str, Any], ttl: float | None) -> None` - Set data for a key with optional TTL
- `async increment(self, key: str, ttl: float | None) -> int` - Increment a counter and return new value
- `async delete(self, key: str) -> None` - Delete a key

#### MemoryRateLimitStore
In-memory rate limit store with TTL support.

**Public Methods:**
- `async force_cleanup(self) -> None` - Force cleanup of expired entries
- `async get(self, key: str) -> dict[str, Any] | None` - Get data for a key
- `async set(self, key: str, data: dict[str, Any], ttl: float | None) -> None` - Set data for a key with optional TTL
- `async increment(self, key: str, ttl: float | None) -> int` - Increment a counter and return new value
- `async delete(self, key: str) -> None` - Delete a key

#### RateLimiter
Abstract base class for rate limiting algorithms.

**Public Methods:**
- `async check_rate_limit(self, key: str) -> RateLimitResult` - Check if request is allowed under rate limit

#### TokenBucketLimiter
Token bucket rate limiting algorithm.

**Public Methods:**
- `async check_rate_limit(self, key: str) -> RateLimitResult` - Check rate limit using token bucket algorithm

#### SlidingWindowLimiter
Sliding window rate limiting algorithm.

**Public Methods:**
- `async check_rate_limit(self, key: str) -> RateLimitResult` - Check rate limit using sliding window algorithm

#### FixedWindowLimiter
Fixed window rate limiting algorithm.

**Public Methods:**
- `async check_rate_limit(self, key: str) -> RateLimitResult` - Check rate limit using fixed window algorithm

#### ValidationError
Custom validation error with detailed context.

#### SecurityConfig
Security configuration for input validation.

#### SanitizationConfig
Configuration for input sanitization.

#### InputValidator
Comprehensive input validator with security-focused validation rules.

**Public Methods:**
- `validate_string(self, value: Any) -> Any` - Validate string input with security checks
- `validate_list(self, value: Any) -> Any` - Validate list input with size limits and recursive validation
- `validate_dict(self, value: Any, current_depth: int) -> Any` - Validate dictionary input with depth limits and recursive validation
- `validate_any(self, value: Any, current_depth: int) -> Any` - Validate any input type with appropriate method

#### InputSanitizer
Input sanitizer for cleaning potentially malicious or dirty input.

**Public Methods:**
- `sanitize_string(self, value: Any) -> Any` - Sanitize string input by escaping and normalizing
- `sanitize_list(self, value: Any) -> Any` - Sanitize list input recursively
- `sanitize_dict(self, value: Any) -> Any` - Sanitize dictionary input recursively
- `sanitize_any(self, value: Any) -> Any` - Sanitize any input type with appropriate method

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
