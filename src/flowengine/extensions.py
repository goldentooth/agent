"""Flow extension system for dynamic functionality."""

from abc import ABC, abstractmethod
from typing import Any, Callable

# Type aliases for legacy support
ExtensionFunction = Callable[..., Any]
InitializationHook = Callable[[type], None]


class FlowExtension(ABC):
    """Base class for all flow extensions."""

    def __init__(self) -> None:
        """Initialize extension."""
        super().__init__()
        self._enabled = True
        self._config: dict[str, Any] = {}

    @property
    @abstractmethod
    def name(self) -> str:
        """Extension name."""
        pass

    @property
    def description(self) -> str:
        """Extension description."""
        return ""

    @property
    def enabled(self) -> bool:
        """Whether extension is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Set enabled state."""
        self._enabled = value

    @abstractmethod
    def on_flow_init(self, flow_class: type) -> None:
        """Called when extending a flow class."""
        del flow_class  # unused
        raise NotImplementedError

    def get_methods(self) -> dict[str, Callable[..., Any]]:
        """Return methods to add to flow class."""
        return {}

    def get_config(self) -> dict[str, Any]:
        """Return extension configuration."""
        return self._config.copy()

    def set_config(self, config: dict[str, Any]) -> None:
        """Set extension configuration."""
        self._config = config.copy()


class ExtensionRegistry:
    """Registry for managing flow extensions."""

    def __init__(self) -> None:
        """Initialize extension registry."""
        super().__init__()
        self.extensions: dict[str, FlowExtension] = {}
        self.enabled_extensions: set[str] = set()
        # Legacy support
        self._function_extensions: dict[str, ExtensionFunction] = {}
        self._method_extensions: dict[str, ExtensionFunction] = {}
        self._initialization_hooks: list[InitializationHook] = []

    def register_extension(self, extension: FlowExtension) -> None:
        """Register a new extension."""
        name = extension.name
        if name in self.extensions:
            raise ValueError(f"Extension '{name}' already registered")

        self.extensions[name] = extension
        if extension.enabled:
            self.enabled_extensions.add(name)

    def unregister_extension(self, name: str) -> None:
        """Unregister an extension."""
        if name not in self.extensions:
            raise ValueError(f"Extension '{name}' not found")

        del self.extensions[name]
        self.enabled_extensions.discard(name)

    def enable(self, name: str) -> None:
        """Enable an extension."""
        if name not in self.extensions:
            raise ValueError(f"Extension '{name}' not found")

        self.extensions[name].enabled = True
        self.enabled_extensions.add(name)

    def disable(self, name: str) -> None:
        """Disable an extension."""
        if name not in self.extensions:
            raise ValueError(f"Extension '{name}' not found")

        self.extensions[name].enabled = False
        self.enabled_extensions.discard(name)

    def list_extensions(self) -> list[dict[str, Any]]:
        """List all extensions with their status."""
        return [
            {
                "name": name,
                "enabled": extension.enabled,
                "description": extension.description,
            }
            for name, extension in self.extensions.items()
        ]

    # Legacy support methods
    def register_function_extension(self, name: str, func: ExtensionFunction) -> None:
        """Register a function-based extension (legacy support)."""
        if name in self._function_extensions:
            raise ValueError(f"Function extension '{name}' already registered")
        self._function_extensions[name] = func

    def register_method_extension(
        self, method_name: str, func: ExtensionFunction
    ) -> None:
        """Register a method extension (legacy support)."""
        if method_name in self._method_extensions:
            raise ValueError(f"Method extension '{method_name}' already registered")
        self._method_extensions[method_name] = func

    def register_initialization_hook(self, hook: InitializationHook) -> None:
        """Register an initialization hook (legacy support)."""
        self._initialization_hooks.append(hook)

    def get_function_extension(self, name: str) -> ExtensionFunction | None:
        """Get a function extension by name (legacy support)."""
        return self._function_extensions.get(name)

    def get_method_extensions(self) -> dict[str, ExtensionFunction]:
        """Get all registered method extensions (for testing)."""
        return self._method_extensions.copy()

    def get_initialization_hooks(self) -> list[InitializationHook]:
        """Get all registered initialization hooks (for testing)."""
        return self._initialization_hooks.copy()

    def extend_flow_class(self, flow_class: type) -> None:
        """Extend a flow class with all registered extensions."""
        # Apply FlowExtension instances
        for name in self.enabled_extensions:
            extension = self.extensions[name]
            extension.on_flow_init(flow_class)

            # Add methods from extension
            for method_name, method in extension.get_methods().items():
                setattr(flow_class, method_name, method)

        # Apply legacy method extensions
        for method_name, method in self._method_extensions.items():
            setattr(flow_class, method_name, method)

        # Run initialization hooks
        for hook in self._initialization_hooks:
            hook(flow_class)
