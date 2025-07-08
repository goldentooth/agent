"""Test Context.__contains__ method."""

import pytest

from context.main import Context


def test_context_contains_basic() -> None:
    """Test basic __contains__ functionality."""
    # Create a context and add a value
    context = Context()
    context["test_key"] = "test_value"

    # Test that the key exists
    assert "test_key" in context

    # Test that a non-existent key doesn't exist
    assert "non_existent_key" not in context


def test_context_contains_none_values() -> None:
    """Test __contains__ with None values."""
    # Create a context with None value
    context = Context()
    context["none_key"] = None

    # Test that None values are considered as existing
    assert "none_key" in context


def test_context_contains_empty_context() -> None:
    """Test __contains__ with empty context."""
    # Create an empty context
    context = Context()

    # Test that no keys are found
    assert "any_key" not in context


def test_context_contains_edge_cases() -> None:
    """Test __contains__ with edge cases."""
    # Create a context with various edge cases
    context = Context()
    context[""] = "empty_string_key"
    context["0"] = "zero_string_key"
    context["False"] = "false_string_key"

    # Test that all keys are found
    assert "" in context
    assert "0" in context
    assert "False" in context
