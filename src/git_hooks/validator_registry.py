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
        """Register a validator class.

        Can be used as a decorator or called directly.

        Args:
            name: Unique name for the validator
            validator_class: Validator class to register

        Returns:
            The validator class (for decorator usage)
        """
        if validator_class is None:
            # Used as decorator
            def decorator(validator_cls: Type[T]) -> Type[T]:
                cls._validators[name] = validator_cls
                return validator_cls

            return decorator
        else:
            # Used directly
            cls._validators[name] = validator_class
            return validator_class

    @classmethod
    def create(cls, name: str, config: Dict[str, Any]) -> Validator:
        """Create a validator instance from configuration.

        Args:
            name: Name of the validator to create
            config: Configuration dictionary for the validator

        Returns:
            Configured validator instance

        Raises:
            ValidatorNotFoundError: If validator name is not registered
        """
        if name not in cls._validators:
            raise ValidatorNotFoundError(f"Unknown validator type: {name}")

        validator_class = cls._validators[name]
        return validator_class(**config)

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
