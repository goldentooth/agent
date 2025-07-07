"""Tests for ComputedProperty.__init__ method."""

from typing import Any
from weakref import WeakSet

from context.main import ComputedProperty


class MockContext:
    """Mock Context class for testing purposes."""

    def __init__(self, data: dict[str, str] | None = None) -> None:
        super().__init__()
        self.data = data or {}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MockContext):
            return False
        return self.data == other.data


class TestComputedPropertyInit:
    """Test suite for ComputedProperty.__init__ method."""

    def test_computed_property_init_basic(self) -> None:
        """Test basic ComputedProperty initialization."""

        def test_func(context: Any) -> str:
            return "test_value"

        dependencies = ["dep1", "dep2"]
        prop = ComputedProperty(test_func, dependencies)

        # Verify basic attributes
        assert prop.func is test_func
        assert prop.dependencies == dependencies
        assert prop._cached_value is None  # type: ignore[reportPrivateUsage]
        assert prop._is_cached is False  # type: ignore[reportPrivateUsage]
        assert isinstance(prop._subscribers, WeakSet)  # type: ignore[reportPrivateUsage]

    def test_computed_property_init_with_dependencies_list(self) -> None:
        """Test ComputedProperty initialization with dependencies list."""

        def compute_func(context: Any) -> int:
            return 42

        dependencies = ["key1", "key2", "key3"]
        prop = ComputedProperty(compute_func, dependencies)

        # Verify dependencies are stored correctly
        assert prop.dependencies == dependencies
        assert prop.dependencies is not dependencies  # Should be a copy
        assert len(prop.dependencies) == 3
        assert "key1" in prop.dependencies
        assert "key2" in prop.dependencies
        assert "key3" in prop.dependencies

    def test_computed_property_init_without_dependencies(self) -> None:
        """Test ComputedProperty initialization with None dependencies."""

        def compute_func(context: Any) -> str:
            return "computed"

        prop = ComputedProperty(compute_func, None)

        # Should default to empty list
        assert prop.dependencies == []
        assert isinstance(prop.dependencies, list)
        assert len(prop.dependencies) == 0

    def test_computed_property_init_with_empty_dependencies(self) -> None:
        """Test ComputedProperty initialization with empty dependencies list."""

        def compute_func(context: Any) -> bool:
            return True

        empty_deps: list[str] = []
        prop = ComputedProperty(compute_func, empty_deps)

        # Should use the provided empty list
        assert prop.dependencies == []
        assert prop.dependencies is not empty_deps  # Should be a copy
        assert isinstance(prop.dependencies, list)

    def test_computed_property_init_function_reference(self) -> None:
        """Test that function reference is preserved correctly."""

        def original_func(context: Any) -> str:
            return "original"

        prop = ComputedProperty(original_func, ["dep"])

        # Function reference should be exact same object
        assert prop.func is original_func
        assert prop.func("test") == "original"

    def test_computed_property_init_lambda_function(self) -> None:
        """Test ComputedProperty initialization with lambda function."""
        lambda_func = lambda context: context.get("value", "default")  # type: ignore[reportUnknownArgumentType, reportUnknownLambdaType, reportUnknownMemberType, reportUnknownVariableType]
        dependencies = ["value"]

        prop = ComputedProperty(lambda_func, dependencies)

        # Verify lambda function is stored correctly
        assert prop.func is lambda_func
        assert prop.dependencies == dependencies

    def test_computed_property_init_cached_value_defaults(self) -> None:
        """Test that cached value attributes have correct defaults."""

        def test_func(context: Any) -> None:
            return None

        prop = ComputedProperty(test_func, ["dep"])

        # Verify caching attributes
        assert prop._cached_value is None  # type: ignore[reportPrivateUsage]
        assert prop._is_cached is False  # type: ignore[reportPrivateUsage]
        assert hasattr(prop, "_cached_value")
        assert hasattr(prop, "_is_cached")

    def test_computed_property_init_subscribers_weakset(self) -> None:
        """Test that subscribers is initialized as WeakSet."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, ["dep"])

        # Verify subscribers is WeakSet
        assert isinstance(prop._subscribers, WeakSet)  # type: ignore[reportPrivateUsage]
        assert len(prop._subscribers) == 0  # type: ignore[reportPrivateUsage]

    def test_computed_property_init_complex_function(self) -> None:
        """Test ComputedProperty with complex function and dependencies."""

        def complex_func(context: Any) -> dict[str, Any]:
            """Complex function that processes context data."""
            return {
                "processed": True,
                "data": context.get("input", {}),
                "timestamp": 12345,
            }

        complex_deps = ["input", "config", "state", "metadata"]
        prop = ComputedProperty(complex_func, complex_deps)

        # Verify all attributes are set correctly
        assert prop.func is complex_func
        assert prop.dependencies == complex_deps
        assert prop._cached_value is None  # type: ignore[reportPrivateUsage]
        assert prop._is_cached is False  # type: ignore[reportPrivateUsage]
        assert isinstance(prop._subscribers, WeakSet)  # type: ignore[reportPrivateUsage]

    def test_computed_property_init_dependencies_independence(self) -> None:
        """Test that dependencies list is independent from original."""
        original_deps = ["dep1", "dep2"]
        prop = ComputedProperty(lambda c: "value", original_deps)  # type: ignore[reportUnknownArgumentType, reportUnknownLambdaType]

        # Modify original list
        original_deps.append("dep3")

        # ComputedProperty dependencies should be unchanged
        assert len(prop.dependencies) == 2
        assert "dep3" not in prop.dependencies
        assert prop.dependencies == ["dep1", "dep2"]

    def test_computed_property_init_multiple_instances(self) -> None:
        """Test creating multiple ComputedProperty instances."""

        def func1(context: Any) -> str:
            return "func1"

        def func2(context: Any) -> int:
            return 42

        prop1 = ComputedProperty(func1, ["dep1"])
        prop2 = ComputedProperty(func2, ["dep2"])

        # Verify instances are independent
        assert prop1.func is not prop2.func
        assert prop1.dependencies != prop2.dependencies
        assert prop1._subscribers is not prop2._subscribers  # type: ignore[reportPrivateUsage]
        assert prop1.func("test") == "func1"
        assert prop2.func("test") == 42

    def test_computed_property_init_single_dependency(self) -> None:
        """Test ComputedProperty with single dependency."""

        def single_dep_func(context: Any) -> str:
            return context.get("single", "default")

        prop = ComputedProperty(single_dep_func, ["single"])

        # Verify single dependency handling
        assert len(prop.dependencies) == 1
        assert prop.dependencies[0] == "single"
        assert prop.dependencies == ["single"]
