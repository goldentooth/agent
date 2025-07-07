"""Flow extension system for dynamic functionality."""

from abc import ABC, abstractmethod
from typing import Any, Callable


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
