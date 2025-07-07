"""Tests for ComputedProperty.invalidate method."""

from typing import Any

from context.main import ComputedProperty


class MockContext:
    """Mock Context class for testing purposes."""

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        super().__init__()
        self.data = data or {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from context data."""
        return self.data.get(key, default)


class TestComputedPropertyInvalidate:
    """Test suite for ComputedProperty.invalidate method."""

    def test_invalidate_basic(self) -> None:
        """Test basic invalidate functionality."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, ["dep"])

        # Call invalidate
        prop.invalidate()

        # Verify state after invalidation
        assert prop._is_cached is False  # type: ignore[reportPrivateUsage]
        assert prop._cached_value is None  # type: ignore[reportPrivateUsage]

    def test_invalidate_after_compute(self) -> None:
        """Test invalidate after computing a value."""

        def test_func(context: Any) -> str:
            return "computed_value"

        prop = ComputedProperty(test_func, ["dep"])
        context = MockContext({"dep": "value"})

        # Compute value first
        prop.compute(context)
        assert prop._is_cached is True  # type: ignore[reportPrivateUsage]
        assert prop._cached_value == "computed_value"  # type: ignore[reportPrivateUsage]

        # Invalidate
        prop.invalidate()

        # Should clear cached state
        assert prop._is_cached is False  # type: ignore[reportPrivateUsage]
        assert prop._cached_value is None  # type: ignore[reportPrivateUsage]

    def test_invalidate_allows_recomputation(self) -> None:
        """Test that invalidate allows recomputation of value."""
        call_count = 0

        def counting_func(context: Any) -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        prop = ComputedProperty(counting_func, [])
        context = MockContext()

        # First computation
        result1 = prop.compute(context)
        assert result1 == 1
        assert call_count == 1

        # Second call returns cached value
        result2 = prop.compute(context)
        assert result2 == 1  # Same cached value
        assert call_count == 1  # Function not called again

        # Invalidate and recompute
        prop.invalidate()
        result3 = prop.compute(context)
        assert result3 == 2  # New computation
        assert call_count == 2  # Function called again

    def test_invalidate_multiple_times(self) -> None:
        """Test calling invalidate multiple times."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, [])

        # Multiple invalidations should be safe
        prop.invalidate()
        prop.invalidate()
        prop.invalidate()

        # Should still be in invalidated state
        assert prop._is_cached is False  # type: ignore[reportPrivateUsage]
        assert prop._cached_value is None  # type: ignore[reportPrivateUsage]

    def test_invalidate_without_prior_compute(self) -> None:
        """Test invalidate on property that was never computed."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, [])

        # Should start in invalidated state
        assert prop._is_cached is False  # type: ignore[reportPrivateUsage]
        assert prop._cached_value is None  # type: ignore[reportPrivateUsage]

        # Invalidate without computing first
        prop.invalidate()

        # Should remain in same state
        assert prop._is_cached is False  # type: ignore[reportPrivateUsage]
        assert prop._cached_value is None  # type: ignore[reportPrivateUsage]

    def test_invalidate_with_none_cached_value(self) -> None:
        """Test invalidate when cached value is None."""

        def none_func(context: Any) -> None:
            return None

        prop = ComputedProperty(none_func, [])
        context = MockContext()

        # Compute None value
        result = prop.compute(context)
        assert result is None
        assert prop._is_cached is True  # type: ignore[reportPrivateUsage]
        assert prop._cached_value is None  # type: ignore[reportPrivateUsage]

        # Invalidate
        prop.invalidate()

        # Should clear cached flag even though value is None
        assert prop._is_cached is False  # type: ignore[reportPrivateUsage]
        assert prop._cached_value is None  # type: ignore[reportPrivateUsage]

    def test_invalidate_compute_cycle(self) -> None:
        """Test multiple compute-invalidate cycles."""
        values = ["first", "second", "third"]
        call_index = 0

        def changing_func(context: Any) -> str:
            nonlocal call_index
            value = values[call_index % len(values)]
            call_index += 1
            return value

        prop = ComputedProperty(changing_func, [])
        context = MockContext()

        # First cycle
        assert prop.compute(context) == "first"
        prop.invalidate()

        # Second cycle
        assert prop.compute(context) == "second"
        prop.invalidate()

        # Third cycle
        assert prop.compute(context) == "third"
        prop.invalidate()

        # Verify final state
        assert prop._is_cached is False  # type: ignore[reportPrivateUsage]
        assert prop._cached_value is None  # type: ignore[reportPrivateUsage]

    def test_invalidate_returns_none(self) -> None:
        """Test that invalidate returns None."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, [])

        # Invalidate should return None
        result = prop.invalidate()
        assert result is None

    def test_invalidate_preserves_function_and_dependencies(self) -> None:
        """Test that invalidate doesn't affect function or dependencies."""

        def test_func(context: Any) -> str:
            return "value"

        dependencies = ["dep1", "dep2"]
        prop = ComputedProperty(test_func, dependencies)

        # Store references
        original_func = prop.func
        original_deps = prop.dependencies.copy()

        # Invalidate
        prop.invalidate()

        # Function and dependencies should be unchanged
        assert prop.func is original_func
        assert prop.dependencies == original_deps

    def test_invalidate_with_complex_cached_value(self) -> None:
        """Test invalidate with complex cached value."""

        def complex_func(context: Any) -> dict[str, Any]:
            return {
                "data": [1, 2, 3],
                "nested": {"key": "value"},
                "flag": True,
            }

        prop = ComputedProperty(complex_func, [])
        context = MockContext()

        # Compute complex value
        result = prop.compute(context)
        assert isinstance(result, dict)
        assert prop._is_cached is True  # type: ignore[reportPrivateUsage]

        # Invalidate
        prop.invalidate()

        # Should clear everything
        assert prop._is_cached is False  # type: ignore[reportPrivateUsage]
        assert prop._cached_value is None  # type: ignore[reportPrivateUsage]

    def test_invalidate_enables_different_computation(self) -> None:
        """Test that invalidate allows different computation results."""

        def context_dependent_func(context: Any) -> str:
            return f"Value: {context.get('key', 'default')}"

        prop = ComputedProperty(context_dependent_func, ["key"])

        # First computation with one context
        context1 = MockContext({"key": "first"})
        result1 = prop.compute(context1)
        assert result1 == "Value: first"

        # Invalidate
        prop.invalidate()

        # Second computation with different context
        context2 = MockContext({"key": "second"})
        result2 = prop.compute(context2)
        assert result2 == "Value: second"

    def test_invalidate_performance(self) -> None:
        """Test that invalidate is a fast operation."""
        import time

        def slow_func(context: Any) -> str:
            # Simulate expensive computation
            total = 0
            for i in range(10000):
                total += i
            return f"Result: {total}"

        prop = ComputedProperty(slow_func, [])
        context = MockContext()

        # Compute (this will be slow)
        prop.compute(context)

        # Invalidate should be fast
        start_time = time.time()
        for _ in range(1000):
            prop.invalidate()
        elapsed = time.time() - start_time

        # Should complete 1000 invalidations quickly
        assert elapsed < 0.1  # Less than 100ms for 1000 calls
