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


class TestDependencyGraphLen:
    """Test suite for DependencyGraph.__len__ method."""

    def test_len_empty_graph(self):
        """Test __len__ returns 0 for empty graph."""
        graph = DependencyGraph()

        assert len(graph) == 0

    def test_len_single_source(self):
        """Test __len__ returns 1 for single source."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep")

        assert len(graph) == 1

    def test_len_multiple_sources(self):
        """Test __len__ with multiple sources."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source2", "dep2")
        graph.add_dependency("source3", "dep3")

        assert len(graph) == 3

    def test_len_multiple_dependencies_same_source(self):
        """Test __len__ counts source keys, not individual dependencies."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep1")
        graph.add_dependency("source", "dep2")
        graph.add_dependency("source", "dep3")

        # Should be 1 source, not 3 dependencies
        assert len(graph) == 1

    def test_len_after_adding_dependencies(self):
        """Test __len__ changes as dependencies are added."""
        graph = DependencyGraph()

        assert len(graph) == 0

        graph.add_dependency("source1", "dep1")
        assert len(graph) == 1

        graph.add_dependency("source2", "dep2")
        assert len(graph) == 2

        # Adding more deps to existing source shouldn't change len
        graph.add_dependency("source1", "dep3")
        assert len(graph) == 2

    def test_len_after_removing_dependencies(self):
        """Test __len__ changes as dependencies are removed."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source1", "dep2")
        graph.add_dependency("source2", "dep3")

        assert len(graph) == 2

        # Remove one dependency (source still has another)
        graph.remove_dependency("source1", "dep1")
        assert len(graph) == 2

        # Remove last dependency from source1
        graph.remove_dependency("source1", "dep2")
        assert len(graph) == 1

        # Remove all from source2
        graph.remove_all_dependencies("source2")
        assert len(graph) == 0

    def test_len_after_clear(self):
        """Test __len__ returns 0 after clear."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source2", "dep2")
        graph.add_dependency("source3", "dep3")

        assert len(graph) == 3

        graph.clear()
        assert len(graph) == 0

    def test_len_with_empty_string_keys(self):
        """Test __len__ with empty string source keys."""
        graph = DependencyGraph()
        graph.add_dependency("", "dep1")
        graph.add_dependency("source", "dep2")

        assert len(graph) == 2

    def test_len_consistency_with_get_all_source_keys(self):
        """Test __len__ is consistent with get_all_source_keys."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source2", "dep2")
        graph.add_dependency("source3", "dep3")

        source_keys = graph.get_all_source_keys()
        assert len(graph) == len(source_keys)

        # Test after modifications
        graph.remove_dependency("source1", "dep1")
        source_keys = graph.get_all_source_keys()
        assert len(graph) == len(source_keys)

    def test_len_return_type(self):
        """Test that __len__ returns int type."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep")

        length = len(graph)
        assert isinstance(length, int)
        assert length == 1

    def test_len_builtin_compatibility(self):
        """Test that __len__ works with built-in functions."""
        graph = DependencyGraph()

        # Empty graph
        assert bool(graph) is False  # __bool__ uses __len__ when not defined

        graph.add_dependency("source", "dep")
        assert bool(graph) is True

        # Can be used in boolean context
        if graph:
            assert len(graph) == 1
        else:
            assert False, "Graph should be truthy"


class TestDependencyGraphContains:
    """Test suite for DependencyGraph.__contains__ method."""

    def test_contains_empty_graph(self):
        """Test __contains__ returns False for empty graph."""
        graph = DependencyGraph()

        assert "any_key" not in graph

    def test_contains_existing_source(self):
        """Test __contains__ returns True for existing source."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep")

        assert "source" in graph

    def test_contains_nonexistent_source(self):
        """Test __contains__ returns False for nonexistent source."""
        graph = DependencyGraph()
        graph.add_dependency("existing", "dep")

        assert "nonexistent" not in graph
        assert "existing" in graph

    def test_contains_multiple_sources(self):
        """Test __contains__ with multiple sources."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source2", "dep2")
        graph.add_dependency("source3", "dep3")

        assert "source1" in graph
        assert "source2" in graph
        assert "source3" in graph
        assert "nonexistent" not in graph

    def test_contains_after_adding_dependencies(self):
        """Test __contains__ changes as dependencies are added."""
        graph = DependencyGraph()

        assert "source" not in graph

        graph.add_dependency("source", "dep1")
        assert "source" in graph

        # Adding more deps to same source shouldn't change contains
        graph.add_dependency("source", "dep2")
        assert "source" in graph

    def test_contains_after_removing_dependencies(self):
        """Test __contains__ changes as dependencies are removed."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep1")
        graph.add_dependency("source", "dep2")

        assert "source" in graph

        # Remove one dependency (source still has another)
        graph.remove_dependency("source", "dep1")
        assert "source" in graph

        # Remove last dependency from source
        graph.remove_dependency("source", "dep2")
        assert "source" not in graph

    def test_contains_after_remove_all_dependencies(self):
        """Test __contains__ after remove_all_dependencies."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep1")
        graph.add_dependency("source", "dep2")

        assert "source" in graph

        graph.remove_all_dependencies("source")
        assert "source" not in graph

    def test_contains_after_clear(self):
        """Test __contains__ returns False after clear."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source2", "dep2")

        assert "source1" in graph
        assert "source2" in graph

        graph.clear()
        assert "source1" not in graph
        assert "source2" not in graph

    def test_contains_empty_string_key(self):
        """Test __contains__ with empty string source key."""
        graph = DependencyGraph()
        graph.add_dependency("", "dep")
        graph.add_dependency("normal", "dep2")

        assert "" in graph
        assert "normal" in graph

    def test_contains_consistency_with_has_dependents(self):
        """Test __contains__ is consistent with has_dependents."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source2", "dep2")

        # Existing sources
        assert "source1" in graph
        assert graph.has_dependents("source1")
        assert "source2" in graph
        assert graph.has_dependents("source2")

        # Nonexistent source
        assert "nonexistent" not in graph
        assert not graph.has_dependents("nonexistent")

    def test_contains_return_type(self):
        """Test that __contains__ returns bool type."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep")

        result_true = "source" in graph
        result_false = "nonexistent" in graph

        assert isinstance(result_true, bool)
        assert isinstance(result_false, bool)
        assert result_true is True
        assert result_false is False

    def test_contains_builtin_compatibility(self):
        """Test that __contains__ works with built-in functions."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source2", "dep2")

        # List comprehension
        sources_in_graph = [
            key for key in ["source1", "source2", "source3"] if key in graph
        ]
        assert sources_in_graph == ["source1", "source2"]

        # Filter function
        all_keys = ["source1", "source2", "source3", "source4"]
        existing_keys = list(filter(lambda x: x in graph, all_keys))
        assert existing_keys == ["source1", "source2"]

    def test_contains_case_sensitivity(self):
        """Test __contains__ is case sensitive."""
        graph = DependencyGraph()
        graph.add_dependency("Source", "dep")

        assert "Source" in graph
        assert "source" not in graph
        assert "SOURCE" not in graph
