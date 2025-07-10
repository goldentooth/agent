"""Transformations management for Context objects."""

from __future__ import annotations

from typing import Any, Callable

from .computed import Transformation

# Type aliases
ContextValue = Any
TransformFunction = Callable[[ContextValue], ContextValue]


class TransformationsManager:
    """Manages value transformations for Context keys."""

    def __init__(self) -> None:
        """Initialize the transformations manager."""
        super().__init__()
        self._transformations: dict[str, list[Transformation]] = {}

    def add_transformation(self, key: str, func: TransformFunction) -> None:
        """Add a value transformation for a specific key.

        Args:
            key: The context key to apply transformation to
            func: Function that transforms the value
        """
        if key not in self._transformations:
            self._transformations[key] = []

        transformation = Transformation(func, key)
        self._transformations[key].append(transformation)

    def remove_transformations(self, key: str) -> None:
        """Remove all transformations for a specific key.

        Args:
            key: The context key to remove transformations from
        """
        if key in self._transformations:
            del self._transformations[key]

    def apply_transformations(self, key: str, value: ContextValue) -> ContextValue:
        """Apply all transformations for a given key to the value.

        Args:
            key: The key whose transformations should be applied
            value: The value to transform

        Returns:
            The transformed value, or original value if no transformations exist
            or if all transformations fail
        """
        if key not in self._transformations:
            return value

        transformed_value = value
        for transformation in self._transformations[key]:
            try:
                transformed_value = transformation.apply(transformed_value)
            except Exception:
                # If transformation fails, use the current value and continue
                pass

        return transformed_value

    def get_transformations(self, key: str) -> list[Transformation]:
        """Get all transformations for a specific key.

        Args:
            key: The context key to get transformations for

        Returns:
            List of transformations for the key (copy)
        """
        if key not in self._transformations:
            return []
        return self._transformations[key].copy()

    def get_all_transformations(self) -> dict[str, list[Transformation]]:
        """Get all transformations in this manager.

        Returns:
            Dictionary mapping context keys to lists of transformations (copy)
        """
        return {k: v.copy() for k, v in self._transformations.items()}

    def has_transformations(self, key: str) -> bool:
        """Check if a key has any transformations.

        Args:
            key: The context key to check

        Returns:
            True if the key has transformations, False otherwise
        """
        return key in self._transformations and len(self._transformations[key]) > 0

    def get_keys(self) -> list[str]:
        """Get all keys that have transformations.

        Returns:
            List of all keys with transformations
        """
        return list(self._transformations.keys())

    def copy_to_manager(self, other_manager: "TransformationsManager") -> None:
        """Copy all transformations to another manager.

        Args:
            other_manager: The target manager to copy transformations to
        """
        for key, transformations in self._transformations.items():
            other_manager._transformations[key] = []
            for transformation in transformations:
                other_manager._transformations[key].append(
                    Transformation(transformation.func, transformation.key)
                )

    def clear(self) -> None:
        """Clear all transformations."""
        self._transformations.clear()

    def __len__(self) -> int:
        """Get the total number of transformation keys."""
        return len(self._transformations)

    def __contains__(self, key: str) -> bool:
        """Check if a key exists in the transformations."""
        return key in self._transformations
