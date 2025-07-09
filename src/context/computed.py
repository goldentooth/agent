"""Context computed properties and transformations."""

from __future__ import annotations

from typing import Any
from weakref import WeakSet

# Type aliases for context system
ContextValue = Any
ComputedFunction = Any
TransformFunction = Any


class ComputedProperty:
    """Represents a computed property that automatically updates when its dependencies change."""

    def __init__(
        self, func: ComputedFunction, dependencies: list[str] | None = None
    ) -> None:
        """Initialize a computed property.

        Args:
            func: Function that computes the value, takes Context as parameter
            dependencies: List of context keys this property depends on. If None, will track automatically.
        """
        super().__init__()
        self.func = func
        self.dependencies = (dependencies or []).copy()
        self._cached_value: ContextValue = None
        self._is_cached = False
        self._subscribers: WeakSet[Any] = WeakSet()

    def compute(self, context: Any) -> ContextValue:
        """Compute the property value for the given context.

        Args:
            context: The context to compute the value from

        Returns:
            The computed value (cached if already computed)
        """
        if self._is_cached:
            return self._cached_value

        value = self.func(context)
        self._cached_value = value
        self._is_cached = True
        return value

    def invalidate(self) -> None:
        """Invalidate the cached value, requiring recomputation."""
        self._is_cached = False
        self._cached_value = None

    def is_cached(self) -> bool:
        """Check if the property has a cached value."""
        return self._is_cached

    def get_cached_value(self) -> ContextValue:
        """Get the cached value if available."""
        return self._cached_value if self._is_cached else None

    def subscribe(self, context: Any) -> None:
        """Subscribe a context to this computed property for dependency tracking."""
        self._subscribers.add(context)

    def notify_change(self) -> None:
        """Notify all subscribed contexts that this property may have changed."""
        for context in self._subscribers:
            try:
                if hasattr(context, "_handle_computed_property_change"):
                    context._handle_computed_property_change(self)
            except Exception:
                # Continue notifying other contexts even if one fails
                pass


class Transformation:
    """Represents a value transformation applied to context keys."""

    def __init__(self, func: TransformFunction, key: str) -> None:
        """Initialize a transformation.

        Args:
            func: Function that transforms the value
            key: The context key this transformation applies to
        """
        super().__init__()
        self.func = func
        self.key = key

    def apply(self, value: ContextValue) -> ContextValue:
        """Apply the transformation to a value."""
        return self.func(value)
