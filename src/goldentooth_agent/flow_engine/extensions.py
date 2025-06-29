"""Plugin registry system for Flow Engine extensions."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")
ExtensionFunction = Callable[..., Any]


class FlowExtensionRegistry:
    """Registry for Flow extensions that can be added without circular imports."""

    def __init__(self) -> None:
        self._extensions: dict[str, ExtensionFunction] = {}
        self._method_extensions: dict[str, ExtensionFunction] = {}
        self._initialization_hooks: list[Callable[[Any], None]] = []

    def register_extension(self, name: str, func: ExtensionFunction) -> None:
        """Register a function extension."""
        self._extensions[name] = func

    def register_method_extension(
        self, method_name: str, func: ExtensionFunction
    ) -> None:
        """Register a method extension for Flow classes."""
        self._method_extensions[method_name] = func

    def register_initialization_hook(self, hook: Callable[[Any], None]) -> None:
        """Register a hook that runs when Flow classes are extended."""
        self._initialization_hooks.append(hook)

    def get_extension(self, name: str) -> ExtensionFunction | None:
        """Get a registered extension."""
        return self._extensions.get(name)

    def get_method_extension(self, method_name: str) -> ExtensionFunction | None:
        """Get a registered method extension."""
        return self._method_extensions.get(method_name)

    def extend_flow_class(self, flow_class: type) -> None:
        """Apply all registered extensions to a Flow class."""
        # Add method extensions
        for method_name, method_func in self._method_extensions.items():
            if not hasattr(flow_class, method_name):
                setattr(flow_class, method_name, method_func)

        # Run initialization hooks
        for hook in self._initialization_hooks:
            hook(flow_class)


# Global registry instance
flow_registry = FlowExtensionRegistry()


def register_flow_extension(
    name: str,
) -> Callable[[ExtensionFunction], ExtensionFunction]:
    """Decorator to register flow extensions."""

    def decorator(func: ExtensionFunction) -> ExtensionFunction:
        flow_registry.register_extension(name, func)
        return func

    return decorator


def register_flow_method(
    method_name: str,
) -> Callable[[ExtensionFunction], ExtensionFunction]:
    """Decorator to register flow method extensions."""

    def decorator(func: ExtensionFunction) -> ExtensionFunction:
        flow_registry.register_method_extension(method_name, func)
        return func

    return decorator
