"""Tests for Context class with DependencyGraph integration."""

import pytest

from goldentooth_agent.core.context import Context


class TestContextWithDependencyGraph:
    """Test Context class with DependencyGraph integration."""

    def test_context_dependency_methods_still_work(self):
        """Test that Context dependency methods still work after refactoring."""
        context = Context()

        # Add computed properties with dependencies
        context["base"] = 10
        context.add_computed_property("doubled", lambda ctx: ctx["base"] * 2, ["base"])
        context.add_computed_property("tripled", lambda ctx: ctx["base"] * 3, ["base"])

        # Test computed values work
        assert context["doubled"] == 20
        assert context["tripled"] == 30

        # Test that changing base invalidates computed properties
        context["base"] = 5
        assert context["doubled"] == 10
        assert context["tripled"] == 15

    def test_context_dependency_invalidation(self):
        """Test that dependency invalidation still works."""
        context = Context()

        context["x"] = 1
        context["y"] = 2

        # Add computed property that depends on both x and y
        context.add_computed_property(
            "sum", lambda ctx: ctx["x"] + ctx["y"], ["x", "y"]
        )

        assert context["sum"] == 3

        # Change x, sum should update
        context["x"] = 10
        assert context["sum"] == 12

        # Change y, sum should update
        context["y"] = 20
        assert context["sum"] == 30

    def test_context_remove_computed_property(self):
        """Test removing computed properties cleans up dependencies."""
        context = Context()

        context["base"] = 5
        context.add_computed_property("doubled", lambda ctx: ctx["base"] * 2, ["base"])

        # Verify it works
        assert context["doubled"] == 10

        # Remove the computed property
        context.remove_computed_property("doubled")

        # Should no longer be accessible
        with pytest.raises(KeyError):
            _ = context["doubled"]

        # Changing base should not cause any issues
        context["base"] = 10  # Should not crash

    def test_context_computed_property_chains(self):
        """Test chains of computed properties."""
        context = Context()

        context["base"] = 2

        # Create a chain: base -> doubled -> quadrupled
        context.add_computed_property("doubled", lambda ctx: ctx["base"] * 2, ["base"])

        context.add_computed_property(
            "quadrupled", lambda ctx: ctx["doubled"] * 2, ["doubled"]
        )

        assert context["base"] == 2
        assert context["doubled"] == 4
        assert context["quadrupled"] == 8

        # Change base, everything should update
        context["base"] = 3
        assert context["doubled"] == 6
        assert context["quadrupled"] == 12

    def test_context_fork_preserves_dependencies(self):
        """Test that forking preserves computed property dependencies."""
        context = Context()

        context["base"] = 10
        context.add_computed_property("doubled", lambda ctx: ctx["base"] * 2, ["base"])

        forked = context.fork()

        # Both contexts should have the computed property
        assert context["doubled"] == 20
        assert forked["doubled"] == 20

        # They should be independent
        context["base"] = 5
        forked["base"] = 15

        assert context["doubled"] == 10
        assert forked["doubled"] == 30

    def test_context_dependency_isolation(self):
        """Test that dependencies are isolated between Context instances."""
        context1 = Context()
        context2 = Context()

        context1["value"] = 10
        context2["value"] = 20

        context1.add_computed_property(
            "doubled", lambda ctx: ctx["value"] * 2, ["value"]
        )

        context2.add_computed_property(
            "tripled", lambda ctx: ctx["value"] * 3, ["value"]
        )

        # Each should only have its own computed property
        assert context1["doubled"] == 20
        assert context2["tripled"] == 60

        with pytest.raises(KeyError):
            _ = context1["tripled"]

        with pytest.raises(KeyError):
            _ = context2["doubled"]

    def test_context_complex_dependency_patterns(self):
        """Test complex dependency patterns work correctly."""
        context = Context()

        # Set up multiple base values
        context["a"] = 1
        context["b"] = 2
        context["c"] = 3

        # Create computed properties with multiple dependencies
        context.add_computed_property(
            "a_plus_b", lambda ctx: ctx["a"] + ctx["b"], ["a", "b"]
        )

        context.add_computed_property(
            "all_sum", lambda ctx: ctx["a"] + ctx["b"] + ctx["c"], ["a", "b", "c"]
        )

        context.add_computed_property(
            "derived", lambda ctx: ctx["a_plus_b"] * ctx["c"], ["a_plus_b", "c"]
        )

        # Test initial values
        assert context["a_plus_b"] == 3
        assert context["all_sum"] == 6
        assert context["derived"] == 9

        # Change a base value and verify cascading updates
        context["a"] = 10
        assert context["a_plus_b"] == 12
        assert context["all_sum"] == 15
        assert context["derived"] == 36
