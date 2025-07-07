"""Tests for DependencyGraph administrative operations."""

from context.dependency_graph import DependencyGraph


class TestDependencyGraphClear:
    """Test suite for DependencyGraph.clear method."""

    def test_clear_empty_graph(self):
        """Test clearing an already empty graph."""
        graph = DependencyGraph()

        graph.clear()

        internal_graph = graph.get_internal_graph_for_testing()
        assert len(internal_graph) == 0

    def test_clear_single_dependency(self):
        """Test clearing a graph with single dependency."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep")

        graph.clear()

        internal_graph = graph.get_internal_graph_for_testing()
        assert len(internal_graph) == 0
        assert "source" not in internal_graph

    def test_clear_multiple_dependencies(self):
        """Test clearing a graph with multiple dependencies."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source1", "dep2")
        graph.add_dependency("source2", "dep3")
        graph.add_dependency("source3", "dep4")

        graph.clear()

        internal_graph = graph.get_internal_graph_for_testing()
        assert len(internal_graph) == 0
        assert "source1" not in internal_graph
        assert "source2" not in internal_graph
        assert "source3" not in internal_graph

    def test_clear_affects_all_methods(self):
        """Test that clear affects all query methods."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source2", "dep2")

        graph.clear()

        # All query methods should return empty results
        assert not graph.has_dependents("source1")
        assert not graph.has_dependents("source2")
        assert len(graph.get_dependents("source1")) == 0
        assert len(graph.get_dependents("source2")) == 0
        assert len(graph.get_all_source_keys()) == 0

    def test_clear_idempotent(self):
        """Test that multiple clear calls are safe."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep")

        graph.clear()
        graph.clear()  # Second clear should be safe

        internal_graph = graph.get_internal_graph_for_testing()
        assert len(internal_graph) == 0

    def test_clear_enables_fresh_start(self):
        """Test that after clear, graph can be used normally."""
        graph = DependencyGraph()
        graph.add_dependency("old_source", "old_dep")

        graph.clear()

        # Should be able to add new dependencies
        graph.add_dependency("new_source", "new_dep")

        assert graph.has_dependents("new_source")
        assert not graph.has_dependents("old_source")
        assert "new_dep" in graph.get_dependents("new_source")
        assert "new_source" in graph.get_all_source_keys()
        assert "old_source" not in graph.get_all_source_keys()

    def test_clear_with_empty_string_keys(self):
        """Test clearing graph with empty string keys."""
        graph = DependencyGraph()
        graph.add_dependency("", "dep1")
        graph.add_dependency("source", "")

        graph.clear()

        internal_graph = graph.get_internal_graph_for_testing()
        assert len(internal_graph) == 0
        assert "" not in internal_graph
        assert "source" not in internal_graph

    def test_clear_return_value(self):
        """Test that clear returns None."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep")

        result = graph.clear()

        assert result is None

    def test_clear_vs_individual_removal(self):
        """Test that clear is equivalent to removing all dependencies individually."""
        # Create two identical graphs
        graph1 = DependencyGraph()
        graph2 = DependencyGraph()

        # Add same dependencies to both
        dependencies = [
            ("source1", "dep1"),
            ("source1", "dep2"),
            ("source2", "dep3"),
            ("source3", "dep4"),
        ]
        for source, dep in dependencies:
            graph1.add_dependency(source, dep)
            graph2.add_dependency(source, dep)

        # Clear graph1 all at once
        graph1.clear()

        # Remove all from graph2 individually
        for source in ["source1", "source2", "source3"]:
            graph2.remove_all_dependencies(source)

        # Both should have same result
        internal1 = graph1.get_internal_graph_for_testing()
        internal2 = graph2.get_internal_graph_for_testing()
        assert internal1 == internal2
        assert len(internal1) == 0

    def test_clear_preserves_graph_type(self):
        """Test that clear preserves the internal graph type."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep")

        graph.clear()

        internal_graph = graph.get_internal_graph_for_testing()
        assert isinstance(internal_graph, dict)
        # Should still support expected operations
        internal_graph["test"] = {"dep"}
        assert "dep" in internal_graph["test"]
