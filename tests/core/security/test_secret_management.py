"""Tests for secure secret management system."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from goldentooth_agent.core.security.secret_management import (
    EnvironmentSecretStore,
    FernetEncryptionProvider,
    FileSecretStore,
    InMemorySecretStore,
    PlaintextEncryptionProvider,
    SecretConfig,
    SecretError,
    SecretManager,
    SecretMetadata,
    SecretValue,
    create_secret_manager,
    delete_secret,
    get_secret,
    set_secret,
)


class TestSecretConfig:
    """Test secret management configuration."""

    def test_secret_config_defaults(self):
        config = SecretConfig()

        assert config.encryption_enabled is True
        assert config.key_rotation_days == 90
        assert config.max_secret_age_days == 365
        assert config.require_metadata is True
        assert config.store_type == "environment"
        assert config.key_derivation_iterations == 100000

    def test_secret_config_custom_values(self):
        config = SecretConfig(
            encryption_enabled=False,
            store_type="file",
            encryption_key_path="/secure/path/key.bin",
        )

        assert config.encryption_enabled is False
        assert config.store_type == "file"
        assert config.encryption_key_path == "/secure/path/key.bin"


class TestEncryptionProviders:
    """Test encryption provider implementations."""

    def test_fernet_encryption_provider(self):
        provider = FernetEncryptionProvider()

        # Test encryption/decryption round trip
        plaintext = "super secret password"
        encrypted = provider.encrypt(plaintext)
        decrypted = provider.decrypt(encrypted)

        assert decrypted == plaintext
        assert encrypted != plaintext
        assert len(encrypted) > len(plaintext)

    def test_fernet_encryption_with_custom_key(self):
        # Generate a key
        key = FernetEncryptionProvider.generate_key()
        provider = FernetEncryptionProvider(key)

        plaintext = "test secret"
        encrypted = provider.encrypt(plaintext)
        decrypted = provider.decrypt(encrypted)

        assert decrypted == plaintext

    def test_fernet_encryption_different_keys_fail(self):
        provider1 = FernetEncryptionProvider()
        provider2 = FernetEncryptionProvider()

        plaintext = "test secret"
        encrypted = provider1.encrypt(plaintext)

        # Different provider with different key should fail to decrypt
        with pytest.raises(SecretError, match="Failed to decrypt"):
            provider2.decrypt(encrypted)

    def test_plaintext_provider_for_testing(self):
        provider = PlaintextEncryptionProvider()

        plaintext = "test secret"
        encrypted = provider.encrypt(plaintext)
        decrypted = provider.decrypt(encrypted)

        # In plaintext mode, encrypted should equal plaintext
        assert encrypted == plaintext
        assert decrypted == plaintext

    def test_key_generation(self):
        key1 = FernetEncryptionProvider.generate_key()
        key2 = FernetEncryptionProvider.generate_key()

        assert key1 != key2
        assert isinstance(key1, bytes)
        assert isinstance(key2, bytes)
        assert len(key1) == 44  # Fernet key length
        assert len(key2) == 44


class TestSecretStores:
    """Test secret store implementations."""

    def test_environment_secret_store(self):
        store = EnvironmentSecretStore()

        # Test storing and retrieving from environment
        secret_name = "TEST_SECRET_123"
        secret_data = {
            "value": "encrypted_value",
            "metadata": {"created_at": "2023-01-01", "type": "api_key"},
        }

        with patch.dict(os.environ, {}, clear=True):
            store.store_secret(secret_name, secret_data)

            # Should be stored in environment
            assert secret_name in os.environ

            # Should be retrievable
            retrieved = store.get_secret(secret_name)
            assert retrieved == secret_data

    def test_environment_store_nonexistent_secret(self):
        store = EnvironmentSecretStore()

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(SecretError, match="Secret not found"):
                store.get_secret("NONEXISTENT_SECRET")

    def test_environment_store_list_secrets(self):
        store = EnvironmentSecretStore()

        secrets = {
            "SECRET_1": '{"value": "val1", "metadata": {}}',
            "SECRET_2": '{"value": "val2", "metadata": {}}',
            "NOT_A_SECRET": "regular_env_var",
        }

        with patch.dict(os.environ, secrets, clear=True):
            secret_names = store.list_secrets()

            # Should only return actual secrets (JSON format)
            assert "SECRET_1" in secret_names
            assert "SECRET_2" in secret_names
            assert "NOT_A_SECRET" not in secret_names

    def test_environment_store_delete_secret(self):
        store = EnvironmentSecretStore()
        secret_name = "DELETE_TEST_SECRET"

        with patch.dict(os.environ, {secret_name: '{"value": "test"}'}, clear=False):
            assert secret_name in os.environ

            store.delete_secret(secret_name)

            assert secret_name not in os.environ

    def test_file_secret_store(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = FileSecretStore(Path(temp_dir))

            secret_name = "test_file_secret"
            secret_data = {
                "value": "encrypted_file_secret",
                "metadata": {"type": "database_password"},
            }

            # Store secret
            store.store_secret(secret_name, secret_data)

            # Verify file was created
            secret_file = Path(temp_dir) / f"{secret_name}.json"
            assert secret_file.exists()

            # Retrieve secret
            retrieved = store.get_secret(secret_name)
            assert retrieved == secret_data

    def test_file_store_list_secrets(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = FileSecretStore(Path(temp_dir))

            # Create some secret files
            secrets = ["secret1", "secret2", "secret3"]
            for secret in secrets:
                store.store_secret(secret, {"value": f"value_{secret}"})

            # Create a non-secret file
            (Path(temp_dir) / "not_secret.txt").write_text("not a secret")

            # List secrets
            found_secrets = store.list_secrets()

            for secret in secrets:
                assert secret in found_secrets

            assert "not_secret" not in found_secrets

    def test_file_store_delete_secret(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = FileSecretStore(Path(temp_dir))

            secret_name = "delete_test"
            store.store_secret(secret_name, {"value": "test"})

            secret_file = Path(temp_dir) / f"{secret_name}.json"
            assert secret_file.exists()

            store.delete_secret(secret_name)

            assert not secret_file.exists()

            with pytest.raises(SecretError, match="Secret not found"):
                store.get_secret(secret_name)

    def test_in_memory_secret_store(self):
        store = InMemorySecretStore()

        secret_name = "memory_secret"
        secret_data = {"value": "memory_value", "metadata": {}}

        # Store and retrieve
        store.store_secret(secret_name, secret_data)
        retrieved = store.get_secret(secret_name)

        assert retrieved == secret_data

        # List secrets
        secrets = store.list_secrets()
        assert secret_name in secrets

        # Delete secret
        store.delete_secret(secret_name)
        secrets = store.list_secrets()
        assert secret_name not in secrets

        with pytest.raises(SecretError, match="Secret not found"):
            store.get_secret(secret_name)


class TestSecretMetadata:
    """Test secret metadata functionality."""

    def test_secret_metadata_creation(self):
        metadata = SecretMetadata(
            secret_type="api_key",
            description="Test API key for external service",
            tags=["api", "external", "test"],
            rotation_days=30,
        )

        assert metadata.secret_type == "api_key"
        assert metadata.description == "Test API key for external service"
        assert "api" in metadata.tags
        assert metadata.rotation_days == 30
        assert metadata.created_at is not None

    def test_secret_metadata_is_expired(self):
        from datetime import datetime, timedelta

        # Recent metadata should not be expired
        recent_metadata = SecretMetadata(secret_type="test")
        assert not recent_metadata.is_expired(max_age_days=30)

        # Old metadata should be expired
        old_metadata = SecretMetadata(secret_type="test")
        old_metadata.created_at = datetime.utcnow() - timedelta(days=40)
        assert old_metadata.is_expired(max_age_days=30)

    def test_secret_metadata_needs_rotation(self):
        from datetime import datetime, timedelta

        # New secret should not need rotation
        new_metadata = SecretMetadata(secret_type="test", rotation_days=30)
        assert not new_metadata.needs_rotation()

        # Old secret should need rotation
        old_metadata = SecretMetadata(secret_type="test", rotation_days=30)
        old_metadata.last_rotated = datetime.utcnow() - timedelta(days=35)
        assert old_metadata.needs_rotation()

    def test_secret_metadata_to_dict(self):
        metadata = SecretMetadata(
            secret_type="test", description="Test secret", tags=["test"]
        )

        dict_repr = metadata.to_dict()

        assert dict_repr["secret_type"] == "test"
        assert dict_repr["description"] == "Test secret"
        assert dict_repr["tags"] == ["test"]
        assert "created_at" in dict_repr
        assert "last_rotated" in dict_repr


class TestSecretValue:
    """Test secret value wrapper."""

    def test_secret_value_creation(self):
        metadata = SecretMetadata(secret_type="test")
        secret = SecretValue("secret_data", metadata)

        assert secret.value == "secret_data"
        assert secret.metadata == metadata

    def test_secret_value_repr_protection(self):
        secret = SecretValue("sensitive_data", SecretMetadata(secret_type="test"))

        # repr should not expose the actual value
        repr_str = repr(secret)
        assert "sensitive_data" not in repr_str
        assert "SecretValue" in repr_str
        assert "***" in repr_str

    def test_secret_value_str_protection(self):
        secret = SecretValue("sensitive_data", SecretMetadata(secret_type="test"))

        # str should not expose the actual value
        str_repr = str(secret)
        assert "sensitive_data" not in str_repr
        assert "***" in str_repr


class TestSecretManager:
    """Test the main SecretManager class."""

    def test_secret_manager_initialization(self):
        config = SecretConfig(store_type="memory", encryption_enabled=False)
        manager = SecretManager(config)

        assert isinstance(manager.store, InMemorySecretStore)
        assert isinstance(manager.encryption, PlaintextEncryptionProvider)

    def test_secret_manager_with_encryption(self):
        config = SecretConfig(store_type="memory", encryption_enabled=True)
        manager = SecretManager(config)

        assert isinstance(manager.encryption, FernetEncryptionProvider)

    def test_store_and_retrieve_secret(self):
        config = SecretConfig(store_type="memory", encryption_enabled=True)
        manager = SecretManager(config)

        metadata = SecretMetadata(secret_type="api_key", description="Test API key")
        secret_name = "test_api_key"
        secret_value = "sk-1234567890abcdef"

        # Store secret
        manager.store_secret(secret_name, secret_value, metadata)

        # Retrieve secret
        retrieved = manager.get_secret(secret_name)

        assert isinstance(retrieved, SecretValue)
        assert retrieved.value == secret_value
        assert retrieved.metadata.secret_type == "api_key"
        assert retrieved.metadata.description == "Test API key"

    def test_store_secret_without_metadata_when_required(self):
        config = SecretConfig(store_type="memory", require_metadata=True)
        manager = SecretManager(config)

        with pytest.raises(SecretError, match="Metadata is required"):
            manager.store_secret("test_secret", "value")

    def test_store_secret_without_metadata_when_optional(self):
        config = SecretConfig(store_type="memory", require_metadata=False)
        manager = SecretManager(config)

        # Should work without metadata
        manager.store_secret("test_secret", "value")
        retrieved = manager.get_secret("test_secret")

        assert retrieved.value == "value"
        assert retrieved.metadata is not None  # Should create default metadata

    def test_list_secrets(self):
        config = SecretConfig(store_type="memory")
        manager = SecretManager(config)

        secrets = ["secret1", "secret2", "secret3"]
        for secret in secrets:
            manager.store_secret(secret, f"value_{secret}")

        listed_secrets = manager.list_secrets()

        for secret in secrets:
            assert secret in listed_secrets

    def test_delete_secret(self):
        config = SecretConfig(store_type="memory")
        manager = SecretManager(config)

        secret_name = "delete_test"
        manager.store_secret(secret_name, "test_value")

        # Verify it exists
        assert secret_name in manager.list_secrets()

        # Delete it
        manager.delete_secret(secret_name)

        # Verify it's gone
        assert secret_name not in manager.list_secrets()

        with pytest.raises(SecretError, match="Secret not found"):
            manager.get_secret(secret_name)

    def test_secret_exists(self):
        config = SecretConfig(store_type="memory")
        manager = SecretManager(config)

        secret_name = "exists_test"

        # Should not exist initially
        assert not manager.secret_exists(secret_name)

        # Store it
        manager.store_secret(secret_name, "test_value")

        # Should exist now
        assert manager.secret_exists(secret_name)

    def test_get_secret_metadata(self):
        config = SecretConfig(store_type="memory")
        manager = SecretManager(config)

        metadata = SecretMetadata(
            secret_type="database_password",
            description="Main database password",
            tags=["database", "production"],
        )

        manager.store_secret("db_password", "super_secret", metadata)

        retrieved_metadata = manager.get_secret_metadata("db_password")

        assert retrieved_metadata.secret_type == "database_password"
        assert retrieved_metadata.description == "Main database password"
        assert "database" in retrieved_metadata.tags

    def test_update_secret_metadata(self):
        config = SecretConfig(store_type="memory")
        manager = SecretManager(config)

        original_metadata = SecretMetadata(
            secret_type="api_key", description="Original"
        )
        manager.store_secret("test_key", "value", original_metadata)

        # Update metadata
        new_metadata = SecretMetadata(
            secret_type="api_key", description="Updated description"
        )
        manager.update_secret_metadata("test_key", new_metadata)

        # Verify update
        retrieved_metadata = manager.get_secret_metadata("test_key")
        assert retrieved_metadata.description == "Updated description"

        # Verify value unchanged
        retrieved_secret = manager.get_secret("test_key")
        assert retrieved_secret.value == "value"


class TestSecretRotation:
    """Test secret rotation functionality."""

    def test_rotate_secret(self):
        config = SecretConfig(store_type="memory")
        manager = SecretManager(config)

        original_value = "original_secret"
        new_value = "rotated_secret"

        metadata = SecretMetadata(secret_type="api_key", rotation_days=30)
        manager.store_secret("rotate_test", original_value, metadata)

        # Rotate the secret
        manager.rotate_secret("rotate_test", new_value)

        # Verify new value
        retrieved = manager.get_secret("rotate_test")
        assert retrieved.value == new_value

        # Verify metadata updated
        assert retrieved.metadata.last_rotated is not None

    def test_find_secrets_needing_rotation(self):
        from datetime import datetime, timedelta

        config = SecretConfig(store_type="memory")
        manager = SecretManager(config)

        # Create secrets with different rotation needs
        old_metadata = SecretMetadata(secret_type="api_key", rotation_days=30)
        old_metadata.last_rotated = datetime.utcnow() - timedelta(days=35)

        new_metadata = SecretMetadata(secret_type="api_key", rotation_days=30)

        manager.store_secret("old_secret", "value1", old_metadata)
        manager.store_secret("new_secret", "value2", new_metadata)

        # Find secrets needing rotation
        needing_rotation = manager.find_secrets_needing_rotation()

        assert "old_secret" in needing_rotation
        assert "new_secret" not in needing_rotation


class TestSecretManagerFactory:
    """Test secret manager factory functions."""

    def test_create_secret_manager_with_config(self):
        config = SecretConfig(store_type="memory", encryption_enabled=False)
        manager = create_secret_manager(config)

        assert isinstance(manager, SecretManager)
        assert isinstance(manager.store, InMemorySecretStore)

    def test_create_secret_manager_with_environment_detection(self):
        # Test environment-based configuration
        with patch.dict(
            os.environ,
            {
                "GOLDENTOOTH_SECRET_STORE": "memory",
                "GOLDENTOOTH_ENCRYPTION_ENABLED": "false",
            },
            clear=False,
        ):
            manager = create_secret_manager()

            assert isinstance(manager.store, InMemorySecretStore)
            assert isinstance(manager.encryption, PlaintextEncryptionProvider)


class TestConvenienceFunctions:
    """Test convenience functions for secret operations."""

    def test_convenience_functions(self):
        # These functions should work with a global secret manager
        with patch(
            "goldentooth_agent.core.security.secret_management._global_manager"
        ) as mock_manager:
            mock_manager.store_secret.return_value = None
            mock_manager.get_secret.return_value = SecretValue(
                "test_value", SecretMetadata(secret_type="test")
            )
            mock_manager.secret_exists.return_value = True
            mock_manager.delete_secret.return_value = None

            # Test set_secret
            set_secret("test_key", "test_value")
            mock_manager.store_secret.assert_called_once()

            # Test get_secret
            result = get_secret("test_key")
            assert result.value == "test_value"
            mock_manager.get_secret.assert_called_once()

            # Test delete_secret
            delete_secret("test_key")
            mock_manager.delete_secret.assert_called_once()


class TestSecurityFeatures:
    """Test security-specific features."""

    def test_secret_value_memory_protection(self):
        # Test that secret values are not accidentally leaked
        secret = SecretValue(
            "super_secret_password", SecretMetadata(secret_type="password")
        )

        # Should not appear in string representations
        assert "super_secret_password" not in str(secret)
        assert "super_secret_password" not in repr(secret)

        # Should not appear in dict conversion if implemented
        if hasattr(secret, "__dict__"):
            dict_repr = str(secret.__dict__)
            assert "super_secret_password" not in dict_repr

    def test_encryption_key_security(self):
        # Test that encryption keys are handled securely
        provider = FernetEncryptionProvider()

        # Key should not be exposed in string representations
        key_repr = repr(provider)
        assert len(key_repr) < 100  # Should not contain the full key

        # Multiple instances should have different keys
        provider2 = FernetEncryptionProvider()

        # They should encrypt to different values
        plaintext = "test"
        encrypted1 = provider.encrypt(plaintext)
        encrypted2 = provider2.encrypt(plaintext)

        assert encrypted1 != encrypted2

    def test_file_store_permissions(self):
        # Test that file store creates files with appropriate permissions
        with tempfile.TemporaryDirectory() as temp_dir:
            store = FileSecretStore(Path(temp_dir))

            secret_name = "permission_test"
            store.store_secret(secret_name, {"value": "secret"})

            secret_file = Path(temp_dir) / f"{secret_name}.json"

            # File should exist
            assert secret_file.exists()

            # On Unix systems, check permissions are restrictive
            if os.name == "posix":
                stat_info = secret_file.stat()
                # Should be readable/writable by owner only (600)
                permissions = stat_info.st_mode & 0o777
                assert permissions & 0o077 == 0  # No permissions for group/other


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_encryption_error_handling(self):
        provider = FernetEncryptionProvider()

        # Test invalid encrypted data
        with pytest.raises(SecretError, match="Failed to decrypt"):
            provider.decrypt("invalid_encrypted_data")

    def test_secret_manager_error_propagation(self):
        config = SecretConfig(store_type="memory")
        manager = SecretManager(config)

        # Test getting non-existent secret
        with pytest.raises(SecretError, match="Secret not found"):
            manager.get_secret("nonexistent")

        # Test deleting non-existent secret
        with pytest.raises(SecretError, match="Secret not found"):
            manager.delete_secret("nonexistent")

    def test_invalid_store_type(self):
        config = SecretConfig(store_type="invalid_store_type")

        with pytest.raises(SecretError, match="Unknown store type"):
            SecretManager(config)
