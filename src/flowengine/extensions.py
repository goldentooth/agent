"""Flow extension system for dynamic functionality."""

from abc import ABC, abstractmethod
from typing import Any, Callable

# Type aliases for legacy support
ExtensionFunction = Callable[..., Any]
InitializationHook = Callable[[type], None]


class FlowExtension(ABC):
    """Base class for all flow extensions.

    This class provides the foundation for extension metadata and lifecycle management.
    Extensions can be installed, uninstalled, configured, and queried for information.
    Subclasses must implement the abstract methods for flow initialization.
    """

    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        description: str = "",
        enabled: bool = True,
    ) -> None:
        """Initialize a FlowExtension.

        Args:
            name: The name of the extension
            version: The version of the extension (default: "1.0.0")
            description: A description of the extension (default: "")
            enabled: Whether the extension is enabled (default: True)
        """
        super().__init__()
        self._name = name
        self._version = version
        self._description = description
        self._enabled = enabled
        self._config: dict[str, Any] = {}

    @property
    def name(self) -> str:
        """Extension name."""
        return self._name

    @property
    def version(self) -> str:
        """Extension version."""
        return self._version

    @property
    def description(self) -> str:
        """Extension description."""
        return self._description

    @property
    def enabled(self) -> bool:
        """Whether extension is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Set enabled state."""
        self._enabled = value

    def install(self) -> None:
        """Install the extension.

        This method should be overridden by subclasses to implement
        installation logic.
        """
        pass

    def uninstall(self) -> None:
        """Uninstall the extension.

        This method should be overridden by subclasses to implement
        uninstallation logic.
        """
        pass

    def configure(self, config: dict[str, Any]) -> None:
        """Configure the extension.

        Args:
            config: Configuration dictionary for the extension

        This method should be overridden by subclasses to implement
        configuration logic.
        """
        self.set_config(config)

    def get_info(self) -> dict[str, Any]:
        """Get information about the extension.

        Returns:
            Dictionary containing extension information including
            name, version, description, and enabled status.
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "enabled": self.enabled,
        }

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

    def __repr__(self) -> str:
        """Return string representation of the extension."""
        return (
            f"FlowExtension(name='{self.name}', version='{self.version}', "
            f"enabled={self.enabled})"
        )


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
                "version": extension.version,
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


# Global extension registry instance
_registry = ExtensionRegistry()


def install_extension(extension: FlowExtension) -> None:
    """Install a flow extension.

    Args:
        extension: The FlowExtension instance to install

    Raises:
        ValueError: If extension is already registered
    """
    _registry.register_extension(extension)


def uninstall_extension(name: str) -> None:
    """Remove an extension.

    Args:
        name: Name of the extension to remove

    Raises:
        ValueError: If extension is not found
    """
    _registry.unregister_extension(name)


def enable_extension(name: str) -> None:
    """Enable an extension.

    Args:
        name: Name of the extension to enable

    Raises:
        ValueError: If extension is not found
    """
    _registry.enable(name)


def disable_extension(name: str) -> None:
    """Disable an extension.

    Args:
        name: Name of the extension to disable

    Raises:
        ValueError: If extension is not found
    """
    _registry.disable(name)


def list_extensions() -> list[dict[str, Any]]:
    """List available extensions.

    Returns:
        List of dictionaries containing extension information
        including name, version, description, and enabled status
    """
    return _registry.list_extensions()


def get_extension_info(name: str) -> dict[str, Any]:
    """Get extension details.

    Args:
        name: Name of the extension

    Returns:
        Dictionary containing extension information

    Raises:
        ValueError: If extension is not found
    """
    if name not in _registry.extensions:
        raise ValueError(f"Extension '{name}' not found")
    return _registry.extensions[name].get_info()


def get_global_registry() -> ExtensionRegistry:
    """Get the global extension registry instance (for testing)."""
    return _registry
