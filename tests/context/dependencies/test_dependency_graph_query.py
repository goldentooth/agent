"""Tests for DependencyGraph query operations."""

from context.dependency_graph import DependencyGraph


class TestDependencyGraphGetDependents:
    """Test suite for DependencyGraph.get_dependents method."""

    def test_get_dependents_basic(self):
        """Test getting dependents for a source key with dependencies."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep1")
        graph.add_dependency("source", "dep2")
        graph.add_dependency("source", "dep3")

        dependents = graph.get_dependents("source")

        assert isinstance(dependents, set)
        assert len(dependents) == 3
        assert "dep1" in dependents
        assert "dep2" in dependents
        assert "dep3" in dependents

    def test_get_dependents_nonexistent_source(self):
        """Test getting dependents for a nonexistent source key."""
        graph = DependencyGraph()
        graph.add_dependency("existing", "dep")

        dependents = graph.get_dependents("nonexistent")

        assert isinstance(dependents, set)
        assert len(dependents) == 0

    def test_get_dependents_empty_graph(self):
        """Test getting dependents from an empty graph."""
        graph = DependencyGraph()

        dependents = graph.get_dependents("any_key")

        assert isinstance(dependents, set)
        assert len(dependents) == 0

    def test_get_dependents_returns_copy(self):
        """Test that get_dependents returns a copy, not the original set."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep1")
        graph.add_dependency("source", "dep2")

        dependents1 = graph.get_dependents("source")
        dependents2 = graph.get_dependents("source")

        # Should be equal but not the same object
        assert dependents1 == dependents2
        assert dependents1 is not dependents2

        # Modifying one shouldn't affect the other
        dependents1.add("new_dep")
        assert "new_dep" not in dependents2

        # Original graph should be unaffected
        original_dependents = graph.get_dependents("source")
        assert "new_dep" not in original_dependents

    def test_get_dependents_after_adding(self):
        """Test getting dependents after adding dependencies."""
        graph = DependencyGraph()

        # Initially empty
        dependents = graph.get_dependents("source")
        assert len(dependents) == 0

        # After adding first
        graph.add_dependency("source", "dep1")
        dependents = graph.get_dependents("source")
        assert len(dependents) == 1
        assert "dep1" in dependents

        # After adding second
        graph.add_dependency("source", "dep2")
        dependents = graph.get_dependents("source")
        assert len(dependents) == 2
        assert "dep1" in dependents
        assert "dep2" in dependents

    def test_get_dependents_after_removing(self):
        """Test getting dependents after removing dependencies."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep1")
        graph.add_dependency("source", "dep2")

        # After removing one
        graph.remove_dependency("source", "dep1")
        dependents = graph.get_dependents("source")
        assert len(dependents) == 1
        assert "dep1" not in dependents
        assert "dep2" in dependents

        # After removing all
        graph.remove_all_dependencies("source")
        dependents = graph.get_dependents("source")
        assert len(dependents) == 0

    def test_get_dependents_multiple_sources(self):
        """Test getting dependents when multiple sources exist."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source1", "dep2")
        graph.add_dependency("source2", "dep3")
        graph.add_dependency("source3", "dep4")

        # Check each source has correct dependents
        deps1 = graph.get_dependents("source1")
        assert len(deps1) == 2
        assert "dep1" in deps1 and "dep2" in deps1

        deps2 = graph.get_dependents("source2")
        assert len(deps2) == 1
        assert "dep3" in deps2

        deps3 = graph.get_dependents("source3")
        assert len(deps3) == 1
        assert "dep4" in deps3

    def test_get_dependents_isolation(self):
        """Test that dependents are isolated between sources."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source2", "dep3")

        deps1 = graph.get_dependents("source1")
        deps2 = graph.get_dependents("source2")

        # Ensure no cross-contamination
        assert "dep3" not in deps1
        assert "dep1" not in deps2

    def test_get_dependents_empty_string_key(self):
        """Test getting dependents for empty string key."""
        graph = DependencyGraph()
        graph.add_dependency("", "dep1")
        graph.add_dependency("", "dep2")

        dependents = graph.get_dependents("")

        assert len(dependents) == 2
        assert "dep1" in dependents
        assert "dep2" in dependents

    def test_get_dependents_self_reference(self):
        """Test getting dependents when source depends on itself."""
        graph = DependencyGraph()
        graph.add_dependency("key", "key")
        graph.add_dependency("key", "other")

        dependents = graph.get_dependents("key")

        assert len(dependents) == 2
        assert "key" in dependents
        assert "other" in dependents

    def test_get_dependents_immutability_guarantee(self):
        """Test that modifying returned set doesn't affect internal state."""
        graph = DependencyGraph()
        graph.add_dependency("source", "original")

        dependents = graph.get_dependents("source")
        dependents.add("modified")
        dependents.remove("original")

        # Original state should be preserved
        original_state = graph.get_dependents("source")
        assert "original" in original_state
        assert "modified" not in original_state
        assert len(original_state) == 1


class TestDependencyGraphHasDependents:
    """Test suite for DependencyGraph.has_dependents method."""

    def test_has_dependents_with_dependencies(self):
        """Test has_dependents returns True when source has dependencies."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep1")
        graph.add_dependency("source", "dep2")

        result = graph.has_dependents("source")

        assert result is True

    def test_has_dependents_single_dependency(self):
        """Test has_dependents returns True with single dependency."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep")

        result = graph.has_dependents("source")

        assert result is True

    def test_has_dependents_no_dependencies(self):
        """Test has_dependents returns False for nonexistent source."""
        graph = DependencyGraph()
        graph.add_dependency("other", "dep")

        result = graph.has_dependents("source")

        assert result is False

    def test_has_dependents_empty_graph(self):
        """Test has_dependents returns False in empty graph."""
        graph = DependencyGraph()

        result = graph.has_dependents("any_key")

        assert result is False

    def test_has_dependents_after_adding(self):
        """Test has_dependents changes after adding dependencies."""
        graph = DependencyGraph()

        # Initially false
        assert graph.has_dependents("source") is False

        # After adding dependency
        graph.add_dependency("source", "dep")
        assert graph.has_dependents("source") is True

    def test_has_dependents_after_removing_all(self):
        """Test has_dependents after removing all dependencies."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep1")
        graph.add_dependency("source", "dep2")

        # Initially true
        assert graph.has_dependents("source") is True

        # After removing all
        graph.remove_all_dependencies("source")
        assert graph.has_dependents("source") is False

    def test_has_dependents_after_removing_some(self):
        """Test has_dependents after removing some but not all dependencies."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep1")
        graph.add_dependency("source", "dep2")

        # Initially true
        assert graph.has_dependents("source") is True

        # After removing one (should still be true)
        graph.remove_dependency("source", "dep1")
        assert graph.has_dependents("source") is True

        # After removing last one
        graph.remove_dependency("source", "dep2")
        assert graph.has_dependents("source") is False

    def test_has_dependents_empty_string_key(self):
        """Test has_dependents with empty string key."""
        graph = DependencyGraph()

        # Initially false
        assert graph.has_dependents("") is False

        # After adding dependency
        graph.add_dependency("", "dep")
        assert graph.has_dependents("") is True

    def test_has_dependents_multiple_sources(self):
        """Test has_dependents with multiple independent sources."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source2", "dep2")

        assert graph.has_dependents("source1") is True
        assert graph.has_dependents("source2") is True
        assert graph.has_dependents("source3") is False

    def test_has_dependents_return_type(self):
        """Test that has_dependents returns boolean type."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep")

        result_true = graph.has_dependents("source")
        result_false = graph.has_dependents("nonexistent")

        assert isinstance(result_true, bool)
        assert isinstance(result_false, bool)
        assert result_true is True
        assert result_false is False


class TestDependencyGraphGetAllSourceKeys:
    """Test suite for DependencyGraph.get_all_source_keys method."""

    def test_get_all_source_keys_empty_graph(self):
        """Test get_all_source_keys returns empty set for empty graph."""
        graph = DependencyGraph()

        source_keys = graph.get_all_source_keys()

        assert isinstance(source_keys, set)
        assert len(source_keys) == 0

    def test_get_all_source_keys_single_source(self):
        """Test get_all_source_keys with single source key."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep")

        source_keys = graph.get_all_source_keys()

        assert isinstance(source_keys, set)
        assert len(source_keys) == 1
        assert "source" in source_keys

    def test_get_all_source_keys_multiple_sources(self):
        """Test get_all_source_keys with multiple source keys."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source2", "dep2")
        graph.add_dependency("source3", "dep3")

        source_keys = graph.get_all_source_keys()

        assert len(source_keys) == 3
        assert "source1" in source_keys
        assert "source2" in source_keys
        assert "source3" in source_keys

    def test_get_all_source_keys_excludes_removed_sources(self):
        """Test that removed sources are excluded from result."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source2", "dep2")

        # Remove all dependencies for source1
        graph.remove_all_dependencies("source1")

        source_keys = graph.get_all_source_keys()

        assert len(source_keys) == 1
        assert "source1" not in source_keys
        assert "source2" in source_keys

    def test_get_all_source_keys_after_individual_removal(self):
        """Test source keys after removing last dependency individually."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep")

        # Remove the only dependency
        graph.remove_dependency("source", "dep")

        source_keys = graph.get_all_source_keys()

        assert len(source_keys) == 0
        assert "source" not in source_keys

    def test_get_all_source_keys_returns_copy(self):
        """Test that get_all_source_keys returns a copy."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source2", "dep2")

        keys1 = graph.get_all_source_keys()
        keys2 = graph.get_all_source_keys()

        # Should be equal but different objects
        assert keys1 == keys2
        assert keys1 is not keys2

        # Modifying one shouldn't affect the other or the graph
        keys1.add("new_source")
        assert "new_source" not in keys2
        assert "new_source" not in graph.get_all_source_keys()

    def test_get_all_source_keys_empty_string(self):
        """Test get_all_source_keys with empty string source."""
        graph = DependencyGraph()
        graph.add_dependency("", "dep")
        graph.add_dependency("normal", "dep2")

        source_keys = graph.get_all_source_keys()

        assert len(source_keys) == 2
        assert "" in source_keys
        assert "normal" in source_keys

    def test_get_all_source_keys_with_empty_dependents(self):
        """Test that sources with no remaining dependents are excluded."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source1", "dep2")
        graph.add_dependency("source2", "dep3")

        # Remove all dependents from source1
        graph.remove_dependency("source1", "dep1")
        graph.remove_dependency("source1", "dep2")

        source_keys = graph.get_all_source_keys()

        assert len(source_keys) == 1
        assert "source1" not in source_keys
        assert "source2" in source_keys

    def test_get_all_source_keys_consistency_with_has_dependents(self):
        """Test consistency between get_all_source_keys and has_dependents."""
        graph = DependencyGraph()
        graph.add_dependency("source1", "dep1")
        graph.add_dependency("source2", "dep2")
        graph.add_dependency("source3", "dep3")

        source_keys = graph.get_all_source_keys()

        # Every key returned should have dependents
        for key in source_keys:
            assert graph.has_dependents(key)

        # Every key with dependents should be in the result
        all_possible_keys = ["source1", "source2", "source3", "nonexistent"]
        for key in all_possible_keys:
            if graph.has_dependents(key):
                assert key in source_keys
            else:
                assert key not in source_keys

    def test_get_all_source_keys_immutability_guarantee(self):
        """Test that modifying returned set doesn't affect internal state."""
        graph = DependencyGraph()
        graph.add_dependency("source", "dep")

        source_keys = graph.get_all_source_keys()
        source_keys.add("fake_source")
        source_keys.remove("source")

        # Original state should be preserved
        original_keys = graph.get_all_source_keys()
        assert "source" in original_keys
        assert "fake_source" not in original_keys
        assert len(original_keys) == 1
