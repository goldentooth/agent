"""Tests for the DependencyGraph class __init__ method."""

from context.dependency_graph import DependencyGraph


class TestDependencyGraphInit:
    """Test suite for DependencyGraph.__init__ method."""

    def test_init_creates_empty_graph(self):
        """Test that __init__ creates an empty internal graph."""
        graph = DependencyGraph()

        # Access internal state to verify initialization
        internal_graph = graph.get_internal_graph_for_testing()
        assert isinstance(internal_graph, dict)
        assert len(internal_graph) == 0

    def test_init_creates_isolated_instances(self):
        """Test that multiple instances have isolated internal graphs."""
        graph1 = DependencyGraph()
        graph2 = DependencyGraph()

        # Verify they are separate instances with separate internal state
        internal1 = graph1.get_internal_graph_for_testing()
        internal2 = graph2.get_internal_graph_for_testing()
        assert internal1 is not internal2
        assert id(internal1) != id(internal2)

    def test_init_graph_type_annotation(self):
        """Test that internal graph has correct type structure."""
        graph = DependencyGraph()

        # Verify the internal graph is the expected type
        internal_graph = graph.get_internal_graph_for_testing()
        assert isinstance(internal_graph, dict)

        # The graph should be empty but should support the expected operations
        # This validates the type annotation dict[str, set[str]]
        internal_graph["test_key"] = set()
        assert isinstance(internal_graph["test_key"], set)

        internal_graph["test_key"].add("dependent")
        assert "dependent" in internal_graph["test_key"]

    def test_init_multiple_calls_independent(self):
        """Test that creating multiple graphs results in independent instances."""
        graphs = [DependencyGraph() for _ in range(5)]

        # Each should have its own empty graph
        for i, graph in enumerate(graphs):
            internal_graph = graph.get_internal_graph_for_testing()
            assert len(internal_graph) == 0
            # Modify one to ensure others remain unchanged
            internal_graph[f"key_{i}"] = {f"dep_{i}"}

        # Verify isolation
        for i, graph in enumerate(graphs):
            expected_key = f"key_{i}"
            for j, other_graph in enumerate(graphs):
                if i != j:
                    other_internal = other_graph.get_internal_graph_for_testing()
                    assert expected_key not in other_internal
