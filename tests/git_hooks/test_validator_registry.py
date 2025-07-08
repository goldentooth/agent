"""Tests for validator registry pattern."""

from pathlib import Path
from typing import Any, Dict, Optional, Type

import pytest

from git_hooks.core import ValidationResult, Validator
from git_hooks.validator_registry import ValidatorNotFoundError, ValidatorRegistry


class MockValidator(Validator):
    """Mock validator for testing."""

    def __init__(self, limit: int, **kwargs: Any):
        super().__init__(limit)
        self.kwargs: Dict[str, Any] = kwargs

    def validate(self, path: Path) -> Optional[ValidationResult]:
        return None


class TestValidatorRegistry:
    """Test validator registry functionality."""

    _saved_validators: Dict[str, Type[Validator]] = {}

    def setup_method(self) -> None:
        """Reset registry before each test."""
        # Save existing validators to restore later
        self._saved_validators = ValidatorRegistry.get_validators_dict()
        ValidatorRegistry.clear()

    def teardown_method(self) -> None:
        """Restore registry after each test."""
        # Clear test validators and restore original state
        ValidatorRegistry.restore_validators(self._saved_validators)

    def test_register_validator(self) -> None:
        """Should register validator successfully."""
        ValidatorRegistry.register("mock", MockValidator)

        assert ValidatorRegistry.is_registered("mock")
        assert not ValidatorRegistry.is_registered("nonexistent")

    def test_create_validator_with_basic_config(self) -> None:
        """Should create validator with basic configuration."""
        ValidatorRegistry.register("mock", MockValidator)

        config = {"limit": 100}
        validator = ValidatorRegistry.create("mock", config)

        assert isinstance(validator, MockValidator)
        assert validator.limit == 100

    def test_create_validator_with_extended_config(self) -> None:
        """Should create validator with extended configuration."""
        ValidatorRegistry.register("mock", MockValidator)

        config = {
            "limit": 100,
            "warn_threshold": 80,
            "urgent_threshold": 90,
            "exclude_patterns": ["*.pyc"],
        }
        validator = ValidatorRegistry.create("mock", config)

        assert isinstance(validator, MockValidator)
        assert validator.limit == 100
        assert validator.kwargs["warn_threshold"] == 80
        assert validator.kwargs["urgent_threshold"] == 90
        assert validator.kwargs["exclude_patterns"] == ["*.pyc"]

    def test_create_unknown_validator_raises_error(self) -> None:
        """Should raise error for unknown validator type."""
        with pytest.raises(
            ValidatorNotFoundError, match="Unknown validator type: unknown"
        ):
            ValidatorRegistry.create("unknown", {"limit": 100})

    def test_decorator_registration(self) -> None:
        """Should register validator using decorator."""

        @ValidatorRegistry.register("decorated")
        class DecoratedValidator(Validator):
            def validate(self, path: Path) -> Optional[ValidationResult]:
                return None

        assert ValidatorRegistry.is_registered("decorated")
        validator = ValidatorRegistry.create("decorated", {"limit": 50})
        assert isinstance(validator, DecoratedValidator)

    def test_get_registered_validators(self) -> None:
        """Should return list of registered validator names."""
        ValidatorRegistry.register("validator1", MockValidator)
        ValidatorRegistry.register("validator2", MockValidator)

        validators = ValidatorRegistry.get_registered_validators()
        assert "validator1" in validators
        assert "validator2" in validators
        assert len(validators) == 2

    def test_clear_registry(self) -> None:
        """Should clear all registered validators."""
        ValidatorRegistry.register("temp", MockValidator)
        assert ValidatorRegistry.is_registered("temp")

        ValidatorRegistry.clear()
        assert not ValidatorRegistry.is_registered("temp")
        assert len(ValidatorRegistry.get_registered_validators()) == 0

    def test_register_duplicate_name_overwrites(self) -> None:
        """Should allow overwriting existing validator registration."""

        class FirstValidator(Validator):
            def validate(self, path: Path) -> Optional[ValidationResult]:
                return None

        class SecondValidator(Validator):
            def validate(self, path: Path) -> Optional[ValidationResult]:
                return None

        ValidatorRegistry.register("duplicate", FirstValidator)
        ValidatorRegistry.register("duplicate", SecondValidator)

        validator = ValidatorRegistry.create("duplicate", {"limit": 100})
        assert isinstance(validator, SecondValidator)

    def test_unregister_validator(self) -> None:
        """Should remove validator from registry."""
        ValidatorRegistry.register("temp", MockValidator)
        assert ValidatorRegistry.is_registered("temp")

        result = ValidatorRegistry.unregister("temp")
        assert result is True
        assert not ValidatorRegistry.is_registered("temp")

    def test_unregister_nonexistent_validator(self) -> None:
        """Should return False when trying to unregister nonexistent validator."""
        result = ValidatorRegistry.unregister("nonexistent")
        assert result is False
