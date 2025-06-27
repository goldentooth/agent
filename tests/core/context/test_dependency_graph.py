"""Tests for the ContextDependencyGraph class."""

from goldentooth_agent.core.context import Context
from goldentooth_agent.core.context.dependency_graph import DependencyGraph


class TestDependencyGraph:
    """Test suite for DependencyGraph."""

    def test_add_dependency(self):
        """Test adding a dependency relationship."""
        graph = DependencyGraph()

        graph.add_dependency("source_key", "dependent_key")

        dependents = graph.get_dependents("source_key")
        assert "dependent_key" in dependents
        assert len(dependents) == 1

    def test_add_multiple_dependencies(self):
        """Test adding multiple dependencies for the same source."""
        graph = DependencyGraph()

        graph.add_dependency("source_key", "dependent1")
        graph.add_dependency("source_key", "dependent2")
        graph.add_dependency("source_key", "dependent3")

        dependents = graph.get_dependents("source_key")
        assert len(dependents) == 3
        assert "dependent1" in dependents
        assert "dependent2" in dependents
        assert "dependent3" in dependents

    def test_remove_dependency(self):
        """Test removing a specific dependency."""
        graph = DependencyGraph()

        graph.add_dependency("source_key", "dependent1")
        graph.add_dependency("source_key", "dependent2")

        graph.remove_dependency("source_key", "dependent1")

        dependents = graph.get_dependents("source_key")
        assert "dependent1" not in dependents
        assert "dependent2" in dependents

    def test_remove_all_dependencies_for_key(self):
        """Test removing all dependencies for a source key."""
        graph = DependencyGraph()

        graph.add_dependency("source_key", "dependent1")
        graph.add_dependency("source_key", "dependent2")
        graph.add_dependency("other_key", "dependent3")

        graph.remove_all_dependencies("source_key")

        assert len(graph.get_dependents("source_key")) == 0
        assert len(graph.get_dependents("other_key")) == 1

    def test_get_dependents_empty(self):
        """Test getting dependents for a key with no dependencies."""
        graph = DependencyGraph()

        dependents = graph.get_dependents("nonexistent_key")
        assert len(dependents) == 0

    def test_has_dependents(self):
        """Test checking if a key has dependents."""
        graph = DependencyGraph()

        assert not graph.has_dependents("key1")

        graph.add_dependency("key1", "dependent")
        assert graph.has_dependents("key1")

        graph.remove_dependency("key1", "dependent")
        assert not graph.has_dependents("key1")

    def test_get_all_source_keys(self):
        """Test getting all source keys."""
        graph = DependencyGraph()

        graph.add_dependency("key1", "dep1")
        graph.add_dependency("key2", "dep2")
        graph.add_dependency("key3", "dep3")

        source_keys = graph.get_all_source_keys()
        assert "key1" in source_keys
        assert "key2" in source_keys
        assert "key3" in source_keys
        assert len(source_keys) == 3

    def test_clear_graph(self):
        """Test clearing the entire dependency graph."""
        graph = DependencyGraph()

        graph.add_dependency("key1", "dep1")
        graph.add_dependency("key2", "dep2")

        graph.clear()

        assert len(graph.get_all_source_keys()) == 0
        assert not graph.has_dependents("key1")
        assert not graph.has_dependents("key2")

    def test_duplicate_dependency_ignored(self):
        """Test that adding the same dependency twice is ignored."""
        graph = DependencyGraph()

        graph.add_dependency("source", "dependent")
        graph.add_dependency("source", "dependent")  # Duplicate

        dependents = graph.get_dependents("source")
        assert len(dependents) == 1
        assert "dependent" in dependents

    def test_dependency_graph_with_computed_properties(self):
        """Test dependency graph integration with computed properties."""
        context = Context()
        graph = DependencyGraph()

        # Simulate computed property dependencies
        context["base_value"] = 10

        # Add dependencies for computed properties
        graph.add_dependency("base_value", "doubled")
        graph.add_dependency("base_value", "tripled")
        graph.add_dependency("doubled", "quadrupled")

        # Test dependency lookup
        direct_deps = graph.get_dependents("base_value")
        assert "doubled" in direct_deps
        assert "tripled" in direct_deps

        indirect_deps = graph.get_dependents("doubled")
        assert "quadrupled" in indirect_deps

    def test_complex_dependency_chains(self):
        """Test complex dependency chains."""
        graph = DependencyGraph()

        # Create a chain: A -> B -> C -> D
        graph.add_dependency("A", "B")
        graph.add_dependency("B", "C")
        graph.add_dependency("C", "D")

        # And a branch: A -> E
        graph.add_dependency("A", "E")

        # Test direct dependencies
        assert "B" in graph.get_dependents("A")
        assert "E" in graph.get_dependents("A")
        assert "C" in graph.get_dependents("B")
        assert "D" in graph.get_dependents("C")

        # Test that removing B affects its dependents but not A's other dependents
        graph.remove_all_dependencies("B")
        assert "B" in graph.get_dependents("A")  # A still depends on B
        assert len(graph.get_dependents("B")) == 0  # But B has no dependents

    def test_circular_dependencies_handling(self):
        """Test that circular dependencies don't break the system."""
        graph = DependencyGraph()

        # Create circular dependency: A -> B -> A
        graph.add_dependency("A", "B")
        graph.add_dependency("B", "A")

        # Should not crash and should store both relationships
        assert "B" in graph.get_dependents("A")
        assert "A" in graph.get_dependents("B")

    def test_remove_nonexistent_dependency(self):
        """Test removing a dependency that doesn't exist."""
        graph = DependencyGraph()

        graph.add_dependency("key1", "dep1")

        # Should not raise an error
        graph.remove_dependency("key1", "nonexistent")
        graph.remove_dependency("nonexistent_key", "dep1")

        # Original dependency should still exist
        assert "dep1" in graph.get_dependents("key1")

    def test_dependency_graph_isolation(self):
        """Test that different dependency graphs are isolated."""
        graph1 = DependencyGraph()
        graph2 = DependencyGraph()

        graph1.add_dependency("key", "dep1")
        graph2.add_dependency("key", "dep2")

        assert "dep1" in graph1.get_dependents("key")
        assert "dep1" not in graph2.get_dependents("key")
        assert "dep2" in graph2.get_dependents("key")
        assert "dep2" not in graph1.get_dependents("key")

    def test_dependency_graph_performance(self):
        """Test dependency graph performance with many dependencies."""
        graph = DependencyGraph()

        # Add many dependencies
        for i in range(100):
            for j in range(10):
                graph.add_dependency(f"source_{i}", f"dep_{i}_{j}")

        # Test lookup performance
        dependents = graph.get_dependents("source_50")
        assert len(dependents) == 10

        # Test removal performance
        graph.remove_all_dependencies("source_50")
        assert len(graph.get_dependents("source_50")) == 0

        # Other sources should be unaffected
        assert len(graph.get_dependents("source_49")) == 10
