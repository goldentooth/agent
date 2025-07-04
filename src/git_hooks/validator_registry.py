"""Validator registry for extensible validation system."""

from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, overload

from .core import Validator

T = TypeVar("T", bound=Validator)


class ValidatorNotFoundError(Exception):
    """Raised when attempting to create an unknown validator type."""

    pass


class ValidatorRegistry:
    """Registry for validator classes enabling extensible validation system."""

    _validators: Dict[str, Type[Validator]] = {}

    @classmethod
    @overload
    def register(cls, name: str) -> Callable[[Type[T]], Type[T]]:
        """Register a validator class as decorator."""
        ...

    @classmethod
    @overload
    def register(cls, name: str, validator_class: Type[T]) -> Type[T]:
        """Register a validator class directly."""
        ...

    @classmethod
    def register(
        cls, name: str, validator_class: Optional[Type[T]] = None
    ) -> Union[Type[T], Callable[[Type[T]], Type[T]]]:
        """Register a validator class."""
        if validator_class is None:
            return cls._create_decorator(name)
        else:
            return cls._register_directly(name, validator_class)

    @classmethod
    def _create_decorator(cls, name: str) -> Callable[[Type[T]], Type[T]]:
        """Create decorator for validator registration."""

        def decorator(validator_cls: Type[T]) -> Type[T]:
            cls._validators[name] = validator_cls
            return validator_cls

        return decorator

    @classmethod
    def _register_directly(cls, name: str, validator_class: Type[T]) -> Type[T]:
        """Register validator class directly."""
        cls._validators[name] = validator_class
        return validator_class

    @classmethod
    def create(cls, name: str, config: Dict[str, Any]) -> Validator:
        """Create a validator instance from configuration."""
        cls._validate_name_exists(name)
        validator_class = cls._validators[name]
        return validator_class(**config)

    @classmethod
    def _validate_name_exists(cls, name: str) -> None:
        """Validate that validator name exists."""
        if name not in cls._validators:
            raise ValidatorNotFoundError(f"Unknown validator type: {name}")

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Check if a validator is registered.

        Args:
            name: Name of the validator to check

        Returns:
            True if validator is registered, False otherwise
        """
        return name in cls._validators

    @classmethod
    def get_registered_validators(cls) -> List[str]:
        """Get list of all registered validator names.

        Returns:
            List of registered validator names
        """
        return list(cls._validators.keys())

    @classmethod
    def clear(cls) -> None:
        """Clear all registered validators.

        Mainly used for testing purposes.
        """
        cls._validators.clear()

    @classmethod
    def unregister(cls, name: str) -> bool:
        """Remove a specific validator from the registry.

        Args:
            name: Name of the validator to remove

        Returns:
            True if validator was removed, False if it wasn't registered
        """
        if name in cls._validators:
            del cls._validators[name]
            return True
        return False

    @classmethod
    def get_validators_dict(cls) -> Dict[str, Type[Validator]]:
        """Get a copy of the validators dictionary.

        Used for test isolation and state management.

        Returns:
            Copy of the internal validators dictionary
        """
        return cls._validators.copy()

    @classmethod
    def restore_validators(cls, validators_dict: Dict[str, Type[Validator]]) -> None:
        """Restore the validators dictionary from a saved state.

        Used for test isolation and state management.

        Args:
            validators_dict: Dictionary of validators to restore
        """
        cls._validators.clear()
        cls._validators.update(validators_dict)
