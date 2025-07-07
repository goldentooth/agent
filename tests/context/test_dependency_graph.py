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


class TestDependencyGraphAddDependency:
    """Test suite for DependencyGraph.add_dependency method."""

    def test_add_dependency_basic(self):
        """Test adding a basic dependency relationship."""
        graph = DependencyGraph()

        graph.add_dependency("source_key", "dependent_key")

        internal_graph = graph.get_internal_graph_for_testing()
        assert "source_key" in internal_graph
        assert "dependent_key" in internal_graph["source_key"]
        assert len(internal_graph["source_key"]) == 1

    def test_add_dependency_creates_set(self):
        """Test that add_dependency creates a new set if source key doesn't exist."""
        graph = DependencyGraph()

        graph.add_dependency("new_source", "dependent")

        internal_graph = graph.get_internal_graph_for_testing()
        assert "new_source" in internal_graph
        assert isinstance(internal_graph["new_source"], set)
        assert "dependent" in internal_graph["new_source"]

    def test_add_dependency_multiple_to_same_source(self):
        """Test adding multiple dependencies to the same source key."""
        graph = DependencyGraph()

        graph.add_dependency("source", "dependent1")
        graph.add_dependency("source", "dependent2")
        graph.add_dependency("source", "dependent3")

        internal_graph = graph.get_internal_graph_for_testing()
        dependents = internal_graph["source"]
        assert len(dependents) == 3
        assert "dependent1" in dependents
        assert "dependent2" in dependents
        assert "dependent3" in dependents

    def test_add_dependency_different_sources(self):
        """Test adding dependencies to different source keys."""
        graph = DependencyGraph()

        graph.add_dependency("source1", "dependent1")
        graph.add_dependency("source2", "dependent2")

        internal_graph = graph.get_internal_graph_for_testing()
        assert "source1" in internal_graph
        assert "source2" in internal_graph
        assert "dependent1" in internal_graph["source1"]
        assert "dependent2" in internal_graph["source2"]
        assert len(internal_graph) == 2

    def test_add_dependency_duplicate_ignored(self):
        """Test that adding the same dependency twice is ignored (sets don't allow duplicates)."""
        graph = DependencyGraph()

        graph.add_dependency("source", "dependent")
        graph.add_dependency("source", "dependent")  # Duplicate

        internal_graph = graph.get_internal_graph_for_testing()
        dependents = internal_graph["source"]
        assert len(dependents) == 1
        assert "dependent" in dependents

    def test_add_dependency_empty_strings(self):
        """Test adding dependencies with empty string keys."""
        graph = DependencyGraph()

        graph.add_dependency("", "dependent")
        graph.add_dependency("source", "")

        internal_graph = graph.get_internal_graph_for_testing()
        assert "" in internal_graph  # Empty source key
        assert "source" in internal_graph
        assert "dependent" in internal_graph[""]
        assert "" in internal_graph["source"]

    def test_add_dependency_self_reference(self):
        """Test adding a dependency where source and dependent are the same."""
        graph = DependencyGraph()

        graph.add_dependency("key", "key")  # Self-reference

        internal_graph = graph.get_internal_graph_for_testing()
        assert "key" in internal_graph
        assert "key" in internal_graph["key"]
        assert len(internal_graph["key"]) == 1

    def test_add_dependency_maintains_existing_dependencies(self):
        """Test that adding new dependencies preserves existing ones."""
        graph = DependencyGraph()

        # Add initial dependency
        graph.add_dependency("source", "existing")

        # Add new dependency to same source
        graph.add_dependency("source", "new")

        internal_graph = graph.get_internal_graph_for_testing()
        dependents = internal_graph["source"]
        assert len(dependents) == 2
        assert "existing" in dependents
        assert "new" in dependents

    def test_add_dependency_return_value(self):
        """Test that add_dependency returns None."""
        graph = DependencyGraph()

        result = graph.add_dependency("source", "dependent")

        assert result is None
