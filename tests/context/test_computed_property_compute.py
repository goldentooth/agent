"""Tests for ComputedProperty.compute method."""

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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MockContext):
            return False
        return self.data == other.data


class TestComputedPropertyCompute:
    """Test suite for ComputedProperty.compute method."""

    def test_compute_basic(self) -> None:
        """Test basic compute functionality."""

        def test_func(context: Any) -> str:
            return "computed_value"

        prop = ComputedProperty(test_func, ["dep"])
        context = MockContext({"dep": "value"})

        result = prop.compute(context)

        # Verify result
        assert result == "computed_value"

    def test_compute_uses_context(self) -> None:
        """Test that compute passes context to function."""

        def compute_func(context: Any) -> str:
            return f"Value: {context.get('key', 'default')}"

        prop = ComputedProperty(compute_func, ["key"])
        context = MockContext({"key": "test_value"})

        result = prop.compute(context)

        # Verify context was used
        assert result == "Value: test_value"

    def test_compute_caches_result(self) -> None:
        """Test that compute caches the result."""
        call_count = 0

        def counting_func(context: Any) -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        prop = ComputedProperty(counting_func, [])
        context = MockContext()

        # First call
        result1 = prop.compute(context)
        assert result1 == 1
        assert call_count == 1

        # Second call should return cached value
        result2 = prop.compute(context)
        assert result2 == 1  # Same value, not 2
        assert call_count == 1  # Function not called again

    def test_compute_sets_cached_flag(self) -> None:
        """Test that compute sets the _is_cached flag."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, [])
        context = MockContext()

        # Initially not cached
        assert prop._is_cached is False  # type: ignore[reportPrivateUsage]

        # After compute, should be cached
        prop.compute(context)
        assert prop._is_cached is True  # type: ignore[reportPrivateUsage]

    def test_compute_stores_cached_value(self) -> None:
        """Test that compute stores the cached value."""

        def test_func(context: Any) -> str:
            return "cached_result"

        prop = ComputedProperty(test_func, [])
        context = MockContext()

        # Initially no cached value
        assert prop._cached_value is None  # type: ignore[reportPrivateUsage]

        # After compute, should store value
        result = prop.compute(context)
        assert prop._cached_value == "cached_result"  # type: ignore[reportPrivateUsage]
        assert result == "cached_result"

    def test_compute_with_complex_function(self) -> None:
        """Test compute with complex function using multiple context values."""

        def complex_func(context: Any) -> dict[str, Any]:
            return {
                "sum": context.get("a", 0) + context.get("b", 0),
                "product": context.get("a", 0) * context.get("b", 0),
                "concatenated": f"{context.get('str1', '')}{context.get('str2', '')}",
            }

        prop = ComputedProperty(complex_func, ["a", "b", "str1", "str2"])
        context = MockContext({"a": 5, "b": 3, "str1": "Hello", "str2": "World"})

        result = prop.compute(context)

        # Verify complex computation
        assert result["sum"] == 8
        assert result["product"] == 15
        assert result["concatenated"] == "HelloWorld"

    def test_compute_returns_cached_value_when_cached(self) -> None:
        """Test that compute returns cached value without recomputing."""

        def expensive_func(context: Any) -> str:
            # Simulate expensive computation
            return "expensive_result"

        prop = ComputedProperty(expensive_func, [])
        context = MockContext()

        # Manually set cached state
        prop._cached_value = "cached_result"  # type: ignore[reportPrivateUsage]
        prop._is_cached = True  # type: ignore[reportPrivateUsage]

        # Should return cached value, not compute new one
        result = prop.compute(context)
        assert result == "cached_result"

    def test_compute_with_none_return(self) -> None:
        """Test compute with function that returns None."""

        def none_func(context: Any) -> None:
            return None

        prop = ComputedProperty(none_func, [])
        context = MockContext()

        result = prop.compute(context)

        # Verify None is handled correctly
        assert result is None
        assert prop._cached_value is None  # type: ignore[reportPrivateUsage]
        assert prop._is_cached is True  # type: ignore[reportPrivateUsage]

    def test_compute_with_different_contexts(self) -> None:
        """Test compute with different context objects."""

        def context_dependent_func(context: Any) -> str:
            return f"Result: {context.get('value', 'empty')}"

        prop = ComputedProperty(context_dependent_func, ["value"])

        context1 = MockContext({"value": "first"})
        context2 = MockContext({"value": "second"})

        # Compute with first context
        result1 = prop.compute(context1)
        assert result1 == "Result: first"

        # Cached value should still be returned for second context
        # (This demonstrates caching behavior - not context-specific)
        result2 = prop.compute(context2)
        assert result2 == "Result: first"  # Still cached from first call

    def test_compute_preserves_function_exceptions(self) -> None:
        """Test that compute doesn't catch exceptions from the function."""

        def failing_func(context: Any) -> str:
            raise ValueError("Computation failed")

        prop = ComputedProperty(failing_func, [])
        context = MockContext()

        # Should raise the exception
        try:
            prop.compute(context)
            assert False, "Expected ValueError"
        except ValueError as e:
            assert str(e) == "Computation failed"

        # Should not be cached after exception
        assert prop._is_cached is False  # type: ignore[reportPrivateUsage]

    def test_compute_with_lambda_function(self) -> None:
        """Test compute with lambda function."""
        prop = ComputedProperty(
            lambda ctx: ctx.get("x", 0) * 2,  # type: ignore[reportUnknownArgumentType, reportUnknownLambdaType]
            ["x"],
        )
        context = MockContext({"x": 21})

        result = prop.compute(context)

        assert result == 42

    def test_compute_caching_performance(self) -> None:
        """Test that caching improves performance for repeated calls."""
        computation_count = 0

        def slow_func(context: Any) -> str:
            nonlocal computation_count
            computation_count += 1
            # Simulate slow computation
            total = 0
            for i in range(1000):
                total += i
            return f"Result: {total}"

        prop = ComputedProperty(slow_func, [])
        context = MockContext()

        # Multiple calls
        for _ in range(10):
            result = prop.compute(context)
            assert result == "Result: 499500"

        # Function should only be called once
        assert computation_count == 1
