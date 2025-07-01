"""Secure secret management system with encryption and rotation.

This module provides enterprise-grade secret management including:
- Secure encryption and decryption of sensitive data
- Multiple storage backends (environment, file, memory)
- Secret rotation and lifecycle management
- Metadata tracking for compliance and auditing
- Protection against secret exposure in logs/errors

All secret operations follow security best practices and zero-trust principles.
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

try:
    from cryptography.fernet import Fernet

    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False


class SecretError(Exception):
    """Exception raised for secret management errors."""

    pass


@dataclass
class SecretConfig:
    """Configuration for secret management system."""

    # Encryption settings
    encryption_enabled: bool = True
    encryption_key_path: str | None = None
    key_derivation_iterations: int = 100000

    # Storage settings
    store_type: str = "environment"  # environment, file, memory
    file_store_path: str | None = None

    # Security policies
    require_metadata: bool = True
    max_secret_age_days: int = 365
    key_rotation_days: int = 90

    # Validation
    max_secret_length: int = 10000
    allowed_secret_types: set[str] = field(
        default_factory=lambda: {
            "api_key",
            "password",
            "token",
            "certificate",
            "private_key",
            "database_url",
            "unknown",
        }
    )


@dataclass
class SecretMetadata:
    """Metadata for tracking secret lifecycle and compliance."""

    secret_type: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_rotated: datetime | None = field(default_factory=lambda: datetime.now(UTC))
    rotation_days: int | None = None
    owner: str = ""
    environment: str = ""

    def is_expired(self, max_age_days: int) -> bool:
        """Check if secret has exceeded maximum age."""
        age = datetime.now(UTC) - self.created_at
        return age.days > max_age_days

    def needs_rotation(self) -> bool:
        """Check if secret needs rotation based on policy."""
        if not self.rotation_days or not self.last_rotated:
            return False

        age = datetime.now(UTC) - self.last_rotated
        return age.days >= self.rotation_days

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary for serialization."""
        return {
            "secret_type": self.secret_type,
            "description": self.description,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "last_rotated": (
                self.last_rotated.isoformat() if self.last_rotated else None
            ),
            "rotation_days": self.rotation_days,
            "owner": self.owner,
            "environment": self.environment,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SecretMetadata:
        """Create metadata from dictionary."""
        metadata = cls(
            secret_type=data["secret_type"],
            description=data.get("description", ""),
            tags=data.get("tags", []),
            rotation_days=data.get("rotation_days"),
            owner=data.get("owner", ""),
            environment=data.get("environment", ""),
        )

        if "created_at" in data:
            metadata.created_at = datetime.fromisoformat(data["created_at"])

        if data.get("last_rotated"):
            metadata.last_rotated = datetime.fromisoformat(data["last_rotated"])

        return metadata


class SecretValue:
    """Wrapper for secret values with memory protection."""

    def __init__(self, value: str, metadata: SecretMetadata) -> None:
        # Store value with minimal obfuscation for memory protection
        self._obfuscated = self._obfuscate(value)
        self.metadata = metadata

    def _obfuscate(self, value: str) -> bytes:
        """Simple obfuscation to avoid plain text in memory."""
        # Simple XOR with rotating key - not cryptographically secure,
        # just prevents accidental exposure in memory dumps
        key = b"GOLDENTOOTH_SECRET_OBFUSCATION_KEY"
        value_bytes = value.encode("utf-8")
        return bytes(b ^ key[i % len(key)] for i, b in enumerate(value_bytes))

    def _deobfuscate(self, obfuscated: bytes) -> str:
        """Reverse the obfuscation."""
        key = b"GOLDENTOOTH_SECRET_OBFUSCATION_KEY"
        return bytes(b ^ key[i % len(key)] for i, b in enumerate(obfuscated)).decode(
            "utf-8"
        )

    @property
    def value(self) -> str:
        """Get the secret value."""
        return self._deobfuscate(self._obfuscated)

    def __str__(self) -> str:
        """String representation without exposing value."""
        return f"SecretValue(type={self.metadata.secret_type}, ***)"

    def __repr__(self) -> str:
        """Representation without exposing value."""
        return f"SecretValue(type='{self.metadata.secret_type}', created={self.metadata.created_at}, ***)"

    def __del__(self) -> None:
        """Secure cleanup when object is destroyed."""
        if hasattr(self, "_obfuscated") and isinstance(self._obfuscated, bytes):
            # Overwrite memory (Python string interning makes this limited)
            self._obfuscated = b"0" * len(self._obfuscated)


class EncryptionProvider(ABC):
    """Abstract base class for encryption providers."""

    @abstractmethod
    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext and return encrypted string."""
        pass

    @abstractmethod
    def decrypt(self, encrypted: str) -> str:
        """Decrypt encrypted string and return plaintext."""
        pass


class FernetEncryptionProvider(EncryptionProvider):
    """Fernet symmetric encryption provider using cryptography library."""

    def __init__(self, key: bytes | None = None) -> None:
        if not CRYPTOGRAPHY_AVAILABLE:
            raise SecretError(
                "cryptography library not available. Install with: pip install cryptography"
            )

        if key is None:
            key = self.generate_key()

        self._fernet = Fernet(key)

    @staticmethod
    def generate_key() -> bytes:
        """Generate a new Fernet encryption key."""
        if not CRYPTOGRAPHY_AVAILABLE:
            raise SecretError("cryptography library not available")
        return Fernet.generate_key()

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext using Fernet."""
        try:
            plaintext_bytes = plaintext.encode("utf-8")
            encrypted_bytes = self._fernet.encrypt(plaintext_bytes)
            return encrypted_bytes.decode("ascii")
        except Exception as e:
            raise SecretError(f"Failed to encrypt secret: {e}") from e

    def decrypt(self, encrypted: str) -> str:
        """Decrypt encrypted string using Fernet."""
        try:
            encrypted_bytes = encrypted.encode("ascii")
            decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode("utf-8")
        except Exception as e:
            raise SecretError(f"Failed to decrypt secret: {e}") from e


class PlaintextEncryptionProvider(EncryptionProvider):
    """No-op encryption provider for testing (DO NOT USE IN PRODUCTION)."""

    def encrypt(self, plaintext: str) -> str:
        """Return plaintext unchanged (no encryption)."""
        return plaintext

    def decrypt(self, encrypted: str) -> str:
        """Return encrypted string unchanged (no decryption)."""
        return encrypted


class SecretStore(ABC):
    """Abstract base class for secret storage backends."""

    @abstractmethod
    def store_secret(self, name: str, data: dict[str, Any]) -> None:
        """Store secret data."""
        pass

    @abstractmethod
    def get_secret(self, name: str) -> dict[str, Any]:
        """Retrieve secret data."""
        pass

    @abstractmethod
    def delete_secret(self, name: str) -> None:
        """Delete secret."""
        pass

    @abstractmethod
    def list_secrets(self) -> list[str]:
        """List all secret names."""
        pass


class EnvironmentSecretStore(SecretStore):
    """Store secrets in environment variables (encrypted)."""

    def store_secret(self, name: str, data: dict[str, Any]) -> None:
        """Store secret in environment variable."""
        try:
            json_data = json.dumps(data)
            os.environ[name] = json_data
        except Exception as e:
            raise SecretError(f"Failed to store secret in environment: {e}") from e

    def get_secret(self, name: str) -> dict[str, Any]:
        """Retrieve secret from environment variable."""
        if name not in os.environ:
            raise SecretError(f"Secret not found: {name}")

        try:
            json_data = os.environ[name]
            data = json.loads(json_data)
            if not isinstance(data, dict):
                raise SecretError(f"Secret data is not a dictionary: {type(data)}")
            return data
        except json.JSONDecodeError as e:
            raise SecretError(f"Failed to parse secret data: {e}") from e

    def delete_secret(self, name: str) -> None:
        """Delete secret from environment."""
        if name in os.environ:
            del os.environ[name]

    def list_secrets(self) -> list[str]:
        """List all secrets in environment."""
        secrets = []
        for name, value in os.environ.items():
            try:
                # Try to parse as JSON to identify secrets
                json.loads(value)
                secrets.append(name)
            except json.JSONDecodeError:
                # Not a JSON value, skip
                continue
        return secrets


class FileSecretStore(SecretStore):
    """Store secrets in encrypted files."""

    def __init__(self, store_path: Path) -> None:
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)

    def store_secret(self, name: str, data: dict[str, Any]) -> None:
        """Store secret in file."""
        secret_file = self.store_path / f"{name}.json"

        try:
            json_data = json.dumps(data, indent=2)
            secret_file.write_text(json_data, encoding="utf-8")

            # Set restrictive permissions on Unix systems
            if os.name == "posix":
                secret_file.chmod(0o600)  # Read/write owner only

        except Exception as e:
            raise SecretError(f"Failed to store secret to file: {e}") from e

    def get_secret(self, name: str) -> dict[str, Any]:
        """Retrieve secret from file."""
        secret_file = self.store_path / f"{name}.json"

        if not secret_file.exists():
            raise SecretError(f"Secret not found: {name}")

        try:
            json_data = secret_file.read_text(encoding="utf-8")
            data = json.loads(json_data)
            if not isinstance(data, dict):
                raise SecretError(f"Secret data is not a dictionary: {type(data)}")
            return data
        except Exception as e:
            raise SecretError(f"Failed to read secret from file: {e}") from e

    def delete_secret(self, name: str) -> None:
        """Delete secret file."""
        secret_file = self.store_path / f"{name}.json"

        if secret_file.exists():
            secret_file.unlink()
        else:
            raise SecretError(f"Secret not found: {name}")

    def list_secrets(self) -> list[str]:
        """List all secret files."""
        secrets = []
        for secret_file in self.store_path.glob("*.json"):
            secrets.append(secret_file.stem)
        return secrets


class InMemorySecretStore(SecretStore):
    """Store secrets in memory (for testing)."""

    def __init__(self) -> None:
        self._secrets: dict[str, dict[str, Any]] = {}

    def store_secret(self, name: str, data: dict[str, Any]) -> None:
        """Store secret in memory."""
        self._secrets[name] = data.copy()

    def get_secret(self, name: str) -> dict[str, Any]:
        """Retrieve secret from memory."""
        if name not in self._secrets:
            raise SecretError(f"Secret not found: {name}")
        return self._secrets[name].copy()

    def delete_secret(self, name: str) -> None:
        """Delete secret from memory."""
        if name not in self._secrets:
            raise SecretError(f"Secret not found: {name}")
        del self._secrets[name]

    def list_secrets(self) -> list[str]:
        """List all secrets in memory."""
        return list(self._secrets.keys())


class SecretManager:
    """Main secret management class."""

    def __init__(self, config: SecretConfig) -> None:
        self.config = config

        # Initialize encryption provider
        if config.encryption_enabled:
            if config.encryption_key_path:
                key_path = Path(config.encryption_key_path)
                if key_path.exists():
                    key = key_path.read_bytes()
                else:
                    # Generate new key and save it
                    key = FernetEncryptionProvider.generate_key()
                    key_path.parent.mkdir(parents=True, exist_ok=True)
                    key_path.write_bytes(key)
                    if os.name == "posix":
                        key_path.chmod(0o600)
                self.encryption: EncryptionProvider = FernetEncryptionProvider(key)
            else:
                self.encryption = FernetEncryptionProvider()
        else:
            self.encryption = PlaintextEncryptionProvider()

        # Initialize secret store
        if config.store_type == "environment":
            self.store: SecretStore = EnvironmentSecretStore()
        elif config.store_type == "file":
            store_path = Path(config.file_store_path or "./secrets")
            self.store = FileSecretStore(store_path)
        elif config.store_type == "memory":
            self.store = InMemorySecretStore()
        else:
            raise SecretError(f"Unknown store type: {config.store_type}")

    def store_secret(
        self, name: str, value: str, metadata: SecretMetadata | None = None
    ) -> None:
        """Store a secret with encryption and metadata."""
        # Validate inputs
        if not name or not isinstance(name, str):
            raise SecretError("Secret name must be a non-empty string")

        if not value or not isinstance(value, str):
            raise SecretError("Secret value must be a non-empty string")

        if len(value) > self.config.max_secret_length:
            raise SecretError(
                f"Secret value exceeds maximum length ({self.config.max_secret_length})"
            )

        # Require metadata if configured
        if self.config.require_metadata and metadata is None:
            raise SecretError("Metadata is required but not provided")

        # Create default metadata if none provided
        if metadata is None:
            metadata = SecretMetadata(secret_type="unknown")

        # Validate secret type
        if (
            self.config.allowed_secret_types
            and metadata.secret_type not in self.config.allowed_secret_types
        ):
            raise SecretError(f"Secret type '{metadata.secret_type}' not allowed")

        # Encrypt the value
        encrypted_value = self.encryption.encrypt(value)

        # Prepare storage data
        storage_data = {"value": encrypted_value, "metadata": metadata.to_dict()}

        # Store the secret
        self.store.store_secret(name, storage_data)

    def get_secret(self, name: str) -> SecretValue:
        """Retrieve and decrypt a secret."""
        if not name or not isinstance(name, str):
            raise SecretError("Secret name must be a non-empty string")

        # Get encrypted data from store
        storage_data = self.store.get_secret(name)

        # Extract components
        encrypted_value = storage_data["value"]
        metadata_dict = storage_data["metadata"]

        # Decrypt the value
        decrypted_value = self.encryption.decrypt(encrypted_value)

        # Reconstruct metadata
        metadata = SecretMetadata.from_dict(metadata_dict)

        return SecretValue(decrypted_value, metadata)

    def delete_secret(self, name: str) -> None:
        """Delete a secret."""
        if not name or not isinstance(name, str):
            raise SecretError("Secret name must be a non-empty string")

        self.store.delete_secret(name)

    def list_secrets(self) -> list[str]:
        """List all secret names."""
        return self.store.list_secrets()

    def secret_exists(self, name: str) -> bool:
        """Check if a secret exists."""
        try:
            self.store.get_secret(name)
            return True
        except SecretError:
            return False

    def get_secret_metadata(self, name: str) -> SecretMetadata:
        """Get only the metadata for a secret (without decrypting value)."""
        storage_data = self.store.get_secret(name)
        metadata_dict = storage_data["metadata"]
        return SecretMetadata.from_dict(metadata_dict)

    def update_secret_metadata(self, name: str, metadata: SecretMetadata) -> None:
        """Update metadata for an existing secret."""
        # Get current secret data
        secret = self.get_secret(name)

        # Store with new metadata but same value
        self.store_secret(name, secret.value, metadata)

    def rotate_secret(self, name: str, new_value: str) -> None:
        """Rotate a secret to a new value."""
        # Get current metadata
        metadata = self.get_secret_metadata(name)

        # Update rotation timestamp
        metadata.last_rotated = datetime.now(UTC)

        # Store with new value and updated metadata
        self.store_secret(name, new_value, metadata)

    def find_secrets_needing_rotation(self) -> list[str]:
        """Find secrets that need rotation based on policy."""
        needing_rotation = []

        for secret_name in self.list_secrets():
            try:
                metadata = self.get_secret_metadata(secret_name)
                if metadata.needs_rotation():
                    needing_rotation.append(secret_name)
            except SecretError:
                # Skip secrets we can't read
                continue

        return needing_rotation

    def find_expired_secrets(self) -> list[str]:
        """Find secrets that have exceeded maximum age."""
        expired = []

        for secret_name in self.list_secrets():
            try:
                metadata = self.get_secret_metadata(secret_name)
                if metadata.is_expired(self.config.max_secret_age_days):
                    expired.append(secret_name)
            except SecretError:
                # Skip secrets we can't read
                continue

        return expired


# Global secret manager instance
_global_manager: SecretManager | None = None


def create_secret_manager(config: SecretConfig | None = None) -> SecretManager:
    """Create a secret manager instance with optional config."""
    if config is None:
        # Create config from environment variables
        config = SecretConfig(
            store_type=os.getenv("GOLDENTOOTH_SECRET_STORE", "environment"),
            encryption_enabled=os.getenv(
                "GOLDENTOOTH_ENCRYPTION_ENABLED", "true"
            ).lower()
            == "true",
            file_store_path=os.getenv("GOLDENTOOTH_SECRET_STORE_PATH"),
            encryption_key_path=os.getenv("GOLDENTOOTH_ENCRYPTION_KEY_PATH"),
        )

    return SecretManager(config)


def get_global_manager() -> SecretManager:
    """Get or create the global secret manager."""
    global _global_manager
    if _global_manager is None:
        _global_manager = create_secret_manager()
    return _global_manager


# Convenience functions for common operations
def set_secret(
    name: str,
    value: str,
    secret_type: str = "unknown",
    description: str = "",
    tags: list[str] | None = None,
) -> None:
    """Store a secret using the global manager."""
    metadata = SecretMetadata(
        secret_type=secret_type, description=description, tags=tags or []
    )
    get_global_manager().store_secret(name, value, metadata)


def get_secret(name: str) -> SecretValue:
    """Retrieve a secret using the global manager."""
    return get_global_manager().get_secret(name)


def delete_secret(name: str) -> None:
    """Delete a secret using the global manager."""
    get_global_manager().delete_secret(name)


def secret_exists(name: str) -> bool:
    """Check if a secret exists using the global manager."""
    return get_global_manager().secret_exists(name)


def rotate_secret(name: str, new_value: str) -> None:
    """Rotate a secret using the global manager."""
    get_global_manager().rotate_secret(name, new_value)
