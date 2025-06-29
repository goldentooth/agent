"""Context integration bridge using protocols to avoid circular imports."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..extensions import flow_registry
from ..lazy_imports import create_context_key
from ..protocols import ContextKeyProtocol, ContextProtocol

if TYPE_CHECKING:
    # Only for type checking, not runtime imports
    pass


class ContextFlowBridge:
    """Bridge between Flow Engine and Context system using protocols."""

    def __init__(self) -> None:
        """Initialize the context bridge."""
        self._context_keys_created = False
        self._trampoline_keys: dict[str, Any] = {}

    def ensure_context_keys(self) -> None:
        """Lazily create context keys for trampoline functionality."""
        if self._context_keys_created:
            return

        try:
            # Create trampoline control keys
            self._trampoline_keys = {
                "SHOULD_EXIT_KEY": create_context_key(
                    "flow.trampoline.should_exit",
                    bool,
                    "Signal to exit trampoline loop",
                ),
                "SHOULD_BREAK_KEY": create_context_key(
                    "flow.trampoline.should_break",
                    bool,
                    "Signal to break/restart current iteration",
                ),
                "SHOULD_SKIP_KEY": create_context_key(
                    "flow.trampoline.should_skip",
                    bool,
                    "Signal to skip certain operations",
                ),
            }
            self._context_keys_created = True

        except ImportError:
            # Context system not available, skip registration
            pass

    def get_trampoline_key(self, key_name: str) -> ContextKeyProtocol[bool] | None:
        """Get a trampoline context key by name."""
        self.ensure_context_keys()
        return self._trampoline_keys.get(key_name)

    def register_trampoline_support(self) -> None:
        """Register trampoline functionality with the Flow system."""
        self.ensure_context_keys()

        if not self._context_keys_created:
            return  # Context system not available

        # Register trampoline methods as Flow extensions
        flow_registry.register_method_extension(
            "set_should_exit", self._create_set_exit_method()
        )
        flow_registry.register_method_extension(
            "set_should_break", self._create_set_break_method()
        )
        flow_registry.register_method_extension(
            "set_should_skip", self._create_set_skip_method()
        )
        flow_registry.register_method_extension(
            "check_should_exit", self._create_check_exit_method()
        )
        flow_registry.register_method_extension(
            "check_should_break", self._create_check_break_method()
        )
        flow_registry.register_method_extension(
            "check_should_skip", self._create_check_skip_method()
        )

    def _create_set_exit_method(self):
        """Create method for setting exit signal."""
        exit_key = self.get_trampoline_key("SHOULD_EXIT_KEY")

        def set_should_exit(
            flow_instance, context: ContextProtocol, value: bool = True
        ) -> None:
            """Set the exit signal in the context."""
            if exit_key:
                context.set(exit_key, value)

        return set_should_exit

    def _create_set_break_method(self):
        """Create method for setting break signal."""
        break_key = self.get_trampoline_key("SHOULD_BREAK_KEY")

        def set_should_break(
            flow_instance, context: ContextProtocol, value: bool = True
        ) -> None:
            """Set the break signal in the context."""
            if break_key:
                context.set(break_key, value)

        return set_should_break

    def _create_set_skip_method(self):
        """Create method for setting skip signal."""
        skip_key = self.get_trampoline_key("SHOULD_SKIP_KEY")

        def set_should_skip(
            flow_instance, context: ContextProtocol, value: bool = True
        ) -> None:
            """Set the skip signal in the context."""
            if skip_key:
                context.set(skip_key, value)

        return set_should_skip

    def _create_check_exit_method(self):
        """Create method for checking exit signal."""
        exit_key = self.get_trampoline_key("SHOULD_EXIT_KEY")

        def check_should_exit(flow_instance, context: ContextProtocol) -> bool:
            """Check if exit has been signaled."""
            if exit_key and context.contains(exit_key):
                return context.get(exit_key)
            return False

        return check_should_exit

    def _create_check_break_method(self):
        """Create method for checking break signal."""
        break_key = self.get_trampoline_key("SHOULD_BREAK_KEY")

        def check_should_break(flow_instance, context: ContextProtocol) -> bool:
            """Check if break has been signaled."""
            if break_key and context.contains(break_key):
                return context.get(break_key)
            return False

        return check_should_break

    def _create_check_skip_method(self):
        """Create method for checking skip signal."""
        skip_key = self.get_trampoline_key("SHOULD_SKIP_KEY")

        def check_should_skip(flow_instance, context: ContextProtocol) -> bool:
            """Check if skip has been signaled."""
            if skip_key and context.contains(skip_key):
                return context.get(skip_key)
            return False

        return check_should_skip


# Global bridge instance
context_bridge = ContextFlowBridge()


def initialize_context_integration() -> None:
    """Initialize context integration if available."""
    context_bridge.register_trampoline_support()


def get_context_bridge() -> ContextFlowBridge:
    """Get the global context bridge instance."""
    return context_bridge
