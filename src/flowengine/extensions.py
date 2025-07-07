"""Flow extension base class for Flow Engine extensions."""

from __future__ import annotations

from typing import Any


class FlowExtension:
    """Base class for Flow Engine extensions.

    This class provides the foundation for extension metadata and lifecycle management.
    Extensions can be installed, uninstalled, configured, and queried for information.
    """

    def __init__(
        self,
        name: str,
        version: str,
        description: str,
        enabled: bool = False,
    ) -> None:
        """Initialize a FlowExtension.

        Args:
            name: The name of the extension
            version: The version of the extension
            description: A description of the extension
            enabled: Whether the extension is enabled (default: False)
        """
        super().__init__()
        self.name = name
        self.version = version
        self.description = description
        self.enabled = enabled

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
        pass

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

    def __repr__(self) -> str:
        """Return string representation of the extension."""
        return (
            f"FlowExtension(name='{self.name}', version='{self.version}', "
            f"enabled={self.enabled})"
        )
