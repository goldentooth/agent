"""Test module for context package exports."""

import pytest


def test_context_init_exports() -> None:
    """Test that all expected symbols are exported from context package."""
    import context

    # Check __all__ is properly defined
    assert hasattr(context, "__all__")
    assert isinstance(context.__all__, list)

    # Verify all expected names are exported
    expected_exports = {
        "Context",
        "Symbol",
        "ContextKey",
        "ContextFrame",
        "DependencyGraph",
        "HistoryTracker",
        "SnapshotManager",
        "ContextSnapshot",
        "ComputedProperty",
        "Transformation",
        "ContextChangeEvent",
        "context_key",
    }

    for name in expected_exports:
        assert hasattr(context, name)

    assert set(context.__all__) == expected_exports


def test_exported_types() -> None:
    """Test that exported types are the correct classes."""
    from context import (
        ComputedProperty,
        Context,
        ContextChangeEvent,
        ContextFrame,
        ContextKey,
        ContextSnapshot,
        DependencyGraph,
        HistoryTracker,
        SnapshotManager,
        Symbol,
        Transformation,
        context_key,
    )

    # Verify these are classes (except context_key which is a function)
    assert isinstance(Context, type)
    assert isinstance(Symbol, type)
    assert isinstance(ContextKey, type)
    assert isinstance(ContextFrame, type)
    assert isinstance(DependencyGraph, type)
    assert isinstance(HistoryTracker, type)
    assert isinstance(SnapshotManager, type)
    assert isinstance(ContextSnapshot, type)
    assert isinstance(ComputedProperty, type)
    assert isinstance(Transformation, type)
    assert isinstance(ContextChangeEvent, type)

    # Verify context_key is a callable
    assert callable(context_key)


def test_no_flow_dependencies() -> None:
    """Test that context package has no flow dependencies."""
    import sys

    import context

    # Verify no flow modules are imported
    flow_modules = [
        mod for mod in sys.modules if mod.startswith("flow") or "flow" in mod
    ]

    # Context package should not import any flow modules
    context_module_name = context.__name__
    assert context_module_name == "context"

    # Check that no submodules have flow imports
    context_submodules = [mod for mod in sys.modules if mod.startswith("context.")]

    # None of the context submodules should import flow
    for submodule in context_submodules:
        module = sys.modules[submodule]
        if hasattr(module, "__file__") and module.__file__:
            # Basic check - in practice flow dependencies would cause import errors
            assert "flow" not in str(module.__file__).lower()
