"""Tests for ContextFlowBridge _create_* methods."""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from context_flow.bridge import ContextFlowBridge


class TestContextFlowBridgeCreateSetExitMethod:
    """Test cases for ContextFlowBridge._create_set_exit_method method."""

    def test_create_set_exit_method_import(self) -> None:
        """Test that _create_set_exit_method exists and is callable."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()

        # Method should exist and be callable
        assert hasattr(bridge, "_create_set_exit_method")
        assert callable(getattr(bridge, "_create_set_exit_method"))

    def test_create_set_exit_method_returns_callable(self) -> None:
        """Test that _create_set_exit_method returns a callable function."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()
        bridge.register_trampoline_support()

        # Should return a callable function
        set_exit_func = bridge._create_set_exit_method()
        assert callable(set_exit_func)

    def test_create_set_exit_method_sets_context_value(self) -> None:
        """Test that the returned function sets exit signal in context."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()
        bridge.register_trampoline_support()

        # Create mock context with set method
        class MockContext:
            def __init__(self) -> None:
                super().__init__()
                self.values: dict[str, bool] = {}

            def set(self, key: str, value: bool) -> None:
                self.values[key] = value

        context = MockContext()
        set_exit_func = bridge._create_set_exit_method()

        # Set exit signal
        set_exit_func(None, context, True)

        # Should have set the exit key
        exit_key = bridge.get_trampoline_key("should_exit")
        assert exit_key in context.values
        assert context.values[exit_key] is True

    def test_create_set_exit_method_with_false_value(self) -> None:
        """Test setting exit signal to False."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()
        bridge.register_trampoline_support()

        class MockContext:
            def __init__(self) -> None:
                super().__init__()
                self.values: dict[str, bool] = {}

            def set(self, key: str, value: bool) -> None:
                self.values[key] = value

        context = MockContext()
        set_exit_func = bridge._create_set_exit_method()

        # Set exit signal to False
        set_exit_func(None, context, False)

        # Should have set the exit key to False
        exit_key = bridge.get_trampoline_key("should_exit")
        assert exit_key in context.values
        assert context.values[exit_key] is False

    def test_create_set_exit_method_default_value(self) -> None:
        """Test that explicit True value works correctly."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()
        bridge.register_trampoline_support()

        class MockContext:
            def __init__(self) -> None:
                super().__init__()
                self.values: dict[str, bool] = {}

            def set(self, key: str, value: bool) -> None:
                self.values[key] = value

        context = MockContext()
        set_exit_func = bridge._create_set_exit_method()

        # Set exit signal with explicit True value
        set_exit_func(None, context, True)

        # Should have set the exit key to True
        exit_key = bridge.get_trampoline_key("should_exit")
        assert exit_key in context.values
        assert context.values[exit_key] is True

    def test_create_set_exit_method_handles_missing_set_method(self) -> None:
        """Test graceful handling when context lacks set method."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()
        bridge.register_trampoline_support()

        class MockContextWithoutSet:
            def __init__(self) -> None:
                super().__init__()

        context = MockContextWithoutSet()
        set_exit_func = bridge._create_set_exit_method()

        # Should not raise error when context lacks set method
        set_exit_func(None, context, True)  # Should complete without error

    def test_create_set_exit_method_type_annotations(self) -> None:
        """Test that _create_set_exit_method has proper type annotations."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()

        # Check method annotations
        method = getattr(bridge, "_create_set_exit_method")
        assert hasattr(method, "__annotations__")

        # Should have return annotation
        annotations = method.__annotations__
        assert "return" in annotations

    def test_create_set_exit_method_documentation(self) -> None:
        """Test that _create_set_exit_method has proper documentation."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()

        # Method should have docstring
        assert bridge._create_set_exit_method.__doc__ is not None
        assert len(bridge._create_set_exit_method.__doc__.strip()) > 0

        # Docstring should describe the method purpose
        docstring = bridge._create_set_exit_method.__doc__.lower()
        assert "create" in docstring or "method" in docstring
        assert "exit" in docstring


class TestContextFlowBridgeCreateSetBreakMethod:
    """Test cases for ContextFlowBridge._create_set_break_method method."""

    def test_create_set_break_method_import(self) -> None:
        """Test that _create_set_break_method exists and is callable."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()

        # Method should exist and be callable
        assert hasattr(bridge, "_create_set_break_method")
        assert callable(getattr(bridge, "_create_set_break_method"))

    def test_create_set_break_method_returns_callable(self) -> None:
        """Test that _create_set_break_method returns a callable function."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()
        bridge.register_trampoline_support()

        # Should return a callable function
        set_break_func = bridge._create_set_break_method()
        assert callable(set_break_func)

    def test_create_set_break_method_sets_context_value(self) -> None:
        """Test that the returned function sets break signal in context."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()
        bridge.register_trampoline_support()

        # Create mock context with set method
        class MockContext:
            def __init__(self) -> None:
                super().__init__()
                self.values: dict[str, bool] = {}

            def set(self, key: str, value: bool) -> None:
                self.values[key] = value

        context = MockContext()
        set_break_func = bridge._create_set_break_method()

        # Set break signal
        set_break_func(None, context, True)

        # Should have set the break key
        break_key = bridge.get_trampoline_key("should_break")
        assert break_key in context.values
        assert context.values[break_key] is True

    def test_create_set_break_method_with_false_value(self) -> None:
        """Test setting break signal to False."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()
        bridge.register_trampoline_support()

        class MockContext:
            def __init__(self) -> None:
                super().__init__()
                self.values: dict[str, bool] = {}

            def set(self, key: str, value: bool) -> None:
                self.values[key] = value

        context = MockContext()
        set_break_func = bridge._create_set_break_method()

        # Set break signal to False
        set_break_func(None, context, False)

        # Should have set the break key to False
        break_key = bridge.get_trampoline_key("should_break")
        assert break_key in context.values
        assert context.values[break_key] is False

    def test_create_set_break_method_default_value(self) -> None:
        """Test that explicit True value works correctly."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()
        bridge.register_trampoline_support()

        class MockContext:
            def __init__(self) -> None:
                super().__init__()
                self.values: dict[str, bool] = {}

            def set(self, key: str, value: bool) -> None:
                self.values[key] = value

        context = MockContext()
        set_break_func = bridge._create_set_break_method()

        # Set break signal with explicit True value
        set_break_func(None, context, True)

        # Should have set the break key to True
        break_key = bridge.get_trampoline_key("should_break")
        assert break_key in context.values
        assert context.values[break_key] is True

    def test_create_set_break_method_handles_missing_set_method(self) -> None:
        """Test graceful handling when context lacks set method."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()
        bridge.register_trampoline_support()

        class MockContextWithoutSet:
            def __init__(self) -> None:
                super().__init__()

        context = MockContextWithoutSet()
        set_break_func = bridge._create_set_break_method()

        # Should not raise error when context lacks set method
        set_break_func(None, context, True)  # Should complete without error

    def test_create_set_break_method_type_annotations(self) -> None:
        """Test that _create_set_break_method has proper type annotations."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()

        # Check method annotations
        method = getattr(bridge, "_create_set_break_method")
        assert hasattr(method, "__annotations__")

        # Should have return annotation
        annotations = method.__annotations__
        assert "return" in annotations

    def test_create_set_break_method_documentation(self) -> None:
        """Test that _create_set_break_method has proper documentation."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()

        # Method should have docstring
        assert bridge._create_set_break_method.__doc__ is not None
        assert len(bridge._create_set_break_method.__doc__.strip()) > 0

        # Docstring should describe the method purpose
        docstring = bridge._create_set_break_method.__doc__.lower()
        assert "create" in docstring or "method" in docstring
        assert "break" in docstring
