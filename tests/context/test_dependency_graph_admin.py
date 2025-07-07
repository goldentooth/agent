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


class TestDependencyGraphGetGraphCopy:
    """Test suite for DependencyGraph.get_graph_copy method."""

    def test_get_graph_copy_empty_graph(self):
        """Test getting copy of empty graph."""
        graph = DependencyGraph()

        graph_copy = graph.get_graph_copy()

        assert isinstance(graph_copy, dict)
        assert len(graph_copy) == 0

    def test_get_graph_copy_single_dependency(self):
        """Test getting copy with single dependency."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep")

        graph_copy = graph.get_graph_copy()

        assert len(graph_copy) == 1
        assert "source" in graph_copy
        assert isinstance(graph_copy["source"], set)
        assert "dep" in graph_copy["source"]
        assert len(graph_copy["source"]) == 1

    def test_get_graph_copy_multiple_sources(self):
        """Test getting copy with multiple source keys."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source1", "dep2")
        graph.add_dependency("source2", "dep3")
        graph.add_dependency("source3", "dep4")

        graph_copy = graph.get_graph_copy()

        assert len(graph_copy) == 3
        assert "source1" in graph_copy
        assert "source2" in graph_copy
        assert "source3" in graph_copy

    def test_get_graph_copy_multiple_dependencies_content(self):
        """Test content of copied dependencies for multiple sources."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source1", "dep2")
        graph.add_dependency("source2", "dep3")
        graph.add_dependency("source3", "dep4")

        graph_copy = graph.get_graph_copy()

        assert len(graph_copy["source1"]) == 2
        assert "dep1" in graph_copy["source1"]
        assert "dep2" in graph_copy["source1"]
        assert "dep3" in graph_copy["source2"]
        assert "dep4" in graph_copy["source3"]

    def test_get_graph_copy_returns_deep_copy(self):
        """Test that get_graph_copy returns a deep copy."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source2", "dep2")

        graph_copy = graph.get_graph_copy()

        # Modifying the copy shouldn't affect the original
        graph_copy["source1"].add("new_dep")
        graph_copy["new_source"] = {"fake_dep"}

        # Original should be unchanged
        original_deps = graph.get_dependents("source1")
        assert "new_dep" not in original_deps
        assert len(original_deps) == 1
        assert not graph.has_dependents("new_source")

    def test_get_graph_copy_vs_internal_state(self):
        """Test that copy matches internal state."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source1", "dep2")
        graph.add_dependency("source2", "dep3")

        graph_copy = graph.get_graph_copy()
        internal_graph = graph.get_internal_graph_for_testing()

        # Structure should match
        assert len(graph_copy) == len(internal_graph)
        for key in internal_graph:
            assert key in graph_copy
            assert graph_copy[key] == internal_graph[key]
            # But sets should be different objects
            assert graph_copy[key] is not internal_graph[key]

    def test_get_graph_copy_with_empty_string_keys(self):
        """Test getting copy with empty string keys."""
        graph = DependencyGraph()
        graph.add_dependency("", "dep1")
        graph.add_dependency("source", "")

        graph_copy = graph.get_graph_copy()

        assert len(graph_copy) == 2
        assert "" in graph_copy
        assert "source" in graph_copy
        assert "dep1" in graph_copy[""]
        assert "" in graph_copy["source"]

    def test_get_graph_copy_after_modifications(self):
        """Test copy reflects current state after modifications."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source2", "dep2")

        # Get initial copy
        copy1 = graph.get_graph_copy()
        assert len(copy1) == 2

        # Modify graph
        graph.add_dependency("source3", "dep3")
        graph.remove_dependency("source1", "dep1")

        # Get new copy
        copy2 = graph.get_graph_copy()

        # Old copy unchanged
        assert len(copy1) == 2
        assert "source3" not in copy1

        # New copy reflects changes
        assert len(copy2) == 2  # source1 removed, source3 added
        assert "source1" not in copy2
        assert "source3" in copy2
        assert "dep3" in copy2["source3"]

    def test_get_graph_copy_immutability_guarantee(self):
        """Test that modifying copy doesn't affect subsequent copies."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep1")

        copy1 = graph.get_graph_copy()
        copy1["source"].add("fake_dep")
        copy1["fake_source"] = {"fake_dep2"}

        copy2 = graph.get_graph_copy()

        # Second copy should be clean
        assert len(copy2) == 1
        assert "source" in copy2
        assert "fake_dep" not in copy2["source"]
        assert "fake_source" not in copy2
        assert len(copy2["source"]) == 1
        assert "dep1" in copy2["source"]

    def test_get_graph_copy_consistency_with_other_methods(self):
        """Test consistency between get_graph_copy and other methods."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source1", "dep2")
        graph.add_dependency("source2", "dep3")

        graph_copy = graph.get_graph_copy()

        # Should match get_all_source_keys
        copy_keys = set(graph_copy.keys())
        method_keys = graph.get_all_source_keys()
        assert copy_keys == method_keys

        # Should match get_dependents for each key
        for key in graph_copy:
            copy_deps = graph_copy[key]
            method_deps = graph.get_dependents(key)
            assert copy_deps == method_deps

        # Should match has_dependents
        for key in ["source1", "source2", "nonexistent"]:
            has_deps_in_copy = key in graph_copy and len(graph_copy[key]) > 0
            has_deps_method = graph.has_dependents(key)
            assert has_deps_in_copy == has_deps_method

    def test_get_graph_copy_self_reference(self):
        """Test copy with self-reference dependencies."""
        graph = DependencyGraph()
        graph.add_dependency("key", "key")
        graph.add_dependency("key", "other")

        graph_copy = graph.get_graph_copy()

        assert len(graph_copy) == 1
        assert "key" in graph_copy
        assert len(graph_copy["key"]) == 2
        assert "key" in graph_copy["key"]
        assert "other" in graph_copy["key"]
