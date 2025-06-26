"""Tests for Flow ergonomic improvements and developer experience features."""

import asyncio
import pytest
from typing import AsyncIterator

from goldentooth_agent.core.flow import (
    Flow,
    map_stream,
    # Registry functionality
    register_flow,
    get_flow,
    list_flows,
    search_flows,
    registered_flow,
    flow_registry,
)


# Test fixtures
async def async_range(n: int) -> AsyncIterator[int]:
    """Generate numbers from 0 to n-1."""
    for i in range(n):
        yield i


async def empty_stream() -> AsyncIterator[None]:
    """Generate a single None for testing from_iterable flows."""
    yield None


class TestFluentAPI:
    """Test fluent API improvements."""

    @pytest.mark.asyncio
    async def test_collect_method(self):
        """Test .collect() method for ergonomic data collection."""
        flow = map_stream(lambda x: x * 2)
        input_stream = async_range(5)

        # Use .collect() instead of .to_list()
        result = await flow.collect()(input_stream)

        assert result == [0, 2, 4, 6, 8]

    @pytest.mark.asyncio
    async def test_preview_method(self):
        """Test .preview() method for REPL development."""
        flow = map_stream(lambda x: x**2)
        input_stream = async_range(20)

        # Preview first 5 items
        result = await flow.preview(input_stream, limit=5)

        assert result == [0, 1, 4, 9, 16]
        assert len(result) == 5

    def test_print_method(self):
        """Test .print() method for debugging (chainable)."""
        flow = map_stream(lambda x: x * 3)

        # Should return self for chaining
        result = flow.print()
        assert result is flow

    def test_with_fallback_method(self):
        """Test .with_fallback() method for error handling."""
        # Create a flow that might be empty
        empty_flow = Flow.from_iterable([]).filter(lambda x: x > 0)
        fallback_flow = empty_flow.with_fallback("default")

        assert (
            fallback_flow.name
            == "from_iterable.filter(<lambda>).with_fallback(default)"
        )


class TestConvenienceConstructors:
    """Test convenience constructor methods."""

    @pytest.mark.asyncio
    async def test_identity_constructor(self):
        """Test Flow.identity() constructor."""
        identity_flow = Flow.identity()
        input_stream = async_range(3)

        result = await identity_flow.collect()(input_stream)

        assert result == [0, 1, 2]
        assert identity_flow.name == "identity"

    @pytest.mark.asyncio
    async def test_pure_constructor(self):
        """Test Flow.pure() constructor."""
        pure_flow = Flow.pure("hello")
        input_stream = empty_stream()

        result = await pure_flow.collect()(input_stream)

        assert result == ["hello"]
        assert pure_flow.name == "pure(hello)"


class TestDebuggingAndRepr:
    """Test debugging and representation improvements."""

    def test_flow_repr(self):
        """Test rich __repr__ for Flow."""
        flow = map_stream(lambda x: x + 1)
        repr_str = repr(flow)

        assert "<Flow name=" in repr_str
        assert "fn=" in repr_str
        assert "metadata=" in repr_str

    def test_flow_aiter_error(self):
        """Test that __aiter__ raises helpful error."""
        flow = map_stream(lambda x: x)

        with pytest.raises(TypeError, match="Flows must be called with a stream"):
            aiter(flow)


class TestDecoratorSupport:
    """Test decorator support for Flow constructors."""

    @pytest.mark.asyncio
    async def test_from_sync_fn_decorator(self):
        """Test @Flow.from_sync_fn decorator."""

        @Flow.from_sync_fn
        def triple(x):
            return x * 3

        input_stream = async_range(3)
        result = await triple.collect()(input_stream)

        assert result == [0, 3, 6]
        assert triple.name == "triple"

    @pytest.mark.asyncio
    async def test_from_value_fn_decorator(self):
        """Test @Flow.from_value_fn decorator."""

        @Flow.from_value_fn
        async def async_square(x):
            return x**2

        input_stream = async_range(4)
        result = await async_square.collect()(input_stream)

        assert result == [0, 1, 4, 9]
        assert async_square.name == "async_square"

    @pytest.mark.asyncio
    async def test_from_event_fn_decorator(self):
        """Test @Flow.from_event_fn decorator."""

        @Flow.from_event_fn
        async def split_string(text):
            for char in text:
                yield char

        input_stream = Flow.from_iterable(["abc", "def"])(empty_stream())
        result = await split_string.collect()(input_stream)

        assert result == ["a", "b", "c", "d", "e", "f"]
        assert split_string.name == "split_string"

    @pytest.mark.asyncio
    async def test_from_sync_fn_direct_call(self):
        """Test Flow.from_sync_fn with direct function call."""

        def quadruple(x):
            return x * 4

        flow = Flow.from_sync_fn(quadruple)
        input_stream = async_range(3)
        result = await flow.collect()(input_stream)

        assert result == [0, 4, 8]
        assert flow.name == "quadruple"


class TestFlowRegistry:
    """Test Flow registry functionality."""

    def setup_method(self):
        """Clear registry before each test."""
        flow_registry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        flow_registry.clear()

    def test_register_and_get_flow(self):
        """Test basic flow registration and retrieval."""
        flow = map_stream(lambda x: x * 2)

        # Register flow
        registered = register_flow("doubler", flow, "math")
        assert registered is flow

        # Retrieve flow
        retrieved = get_flow("doubler")
        assert retrieved is flow

        # Non-existent flow
        assert get_flow("nonexistent") is None

    def test_list_flows(self):
        """Test listing flows."""
        flow1 = map_stream(lambda x: x * 2)
        flow2 = map_stream(lambda x: x + 1)

        register_flow("doubler", flow1, "math")
        register_flow("incrementer", flow2, "math")
        register_flow("special", flow1, "other")

        # List all flows
        all_flows = list_flows()
        assert set(all_flows) == {"doubler", "incrementer", "special"}

        # List by category
        math_flows = list_flows("math")
        assert set(math_flows) == {"doubler", "incrementer"}

        other_flows = list_flows("other")
        assert other_flows == ["special"]

    def test_search_flows(self):
        """Test searching flows."""
        flow1 = map_stream(lambda x: x * 2)
        flow2 = Flow(
            lambda stream: stream, metadata={"description": "special processor"}
        )

        register_flow("text_doubler", flow1)
        register_flow("processor", flow2)

        # Search by name
        results = search_flows("double")
        assert "text_doubler" in results

        # Search by metadata
        results = search_flows("special")
        assert "processor" in results

    def test_registered_flow_decorator(self):
        """Test @registered_flow decorator."""

        @registered_flow("custom_transform", "transforms")
        @Flow.from_sync_fn
        def custom_transform(x):
            return x * 5

        # Should be registered
        retrieved = get_flow("custom_transform")
        assert retrieved is custom_transform

        # Should be in category
        category_flows = list_flows("transforms")
        assert "custom_transform" in category_flows

    def test_flow_registry_info(self):
        """Test getting detailed flow information."""
        flow = map_stream(lambda x: x * 2)
        register_flow("test_flow", flow, "testing")

        info = flow_registry.info("test_flow")

        assert info is not None
        assert info["name"] == "test_flow"
        assert info["flow_name"] == "map(<lambda>)"
        assert "testing" in info["categories"]
        assert "repr" in info

    def test_flow_registry_remove(self):
        """Test removing flows from registry."""
        flow = map_stream(lambda x: x)
        register_flow("to_remove", flow)

        # Verify it's there
        assert get_flow("to_remove") is not None

        # Remove it
        removed = flow_registry.remove("to_remove")
        assert removed is True

        # Verify it's gone
        assert get_flow("to_remove") is None

        # Try to remove non-existent
        removed = flow_registry.remove("nonexistent")
        assert removed is False


class TestErrorHandling:
    """Test error handling improvements."""

    @pytest.mark.asyncio
    async def test_with_fallback_empty_stream(self):
        """Test with_fallback when stream is empty."""
        # Create an empty flow
        empty_flow = Flow.from_iterable([])
        fallback_flow = empty_flow.with_fallback("fallback_value")

        input_stream = empty_stream()
        result = await fallback_flow.collect()(input_stream)

        assert result == ["fallback_value"]

    @pytest.mark.asyncio
    async def test_with_fallback_non_empty_stream(self):
        """Test with_fallback when stream has items."""
        # Create a non-empty flow
        flow = Flow.from_iterable(["a", "b"])
        fallback_flow = flow.with_fallback("fallback_value")

        input_stream = empty_stream()
        result = await fallback_flow.collect()(input_stream)

        # Should not include fallback since stream wasn't empty
        assert result == ["a", "b"]


class TestIntegratedWorkflow:
    """Test integrated developer workflow scenarios."""

    @pytest.mark.asyncio
    async def test_complete_development_workflow(self):
        """Test a complete development workflow using ergonomic features."""

        # 1. Create flows using decorators
        @Flow.from_sync_fn
        def double(x):
            return x * 2

        @Flow.from_sync_fn
        def add_one(x):
            return x + 1

        # 2. Register them for reuse
        register_flow("doubler", double, "math")
        register_flow("incrementer", add_one, "math")

        # 3. Compose a pipeline
        pipeline = double >> add_one >> Flow.identity()

        # 4. Preview during development
        preview = await pipeline.preview(async_range(10), limit=3)
        assert preview == [1, 3, 5]  # (0*2)+1, (1*2)+1, (2*2)+1

        # 5. Add fallback for robustness
        robust_pipeline = pipeline.with_fallback(-1)

        # 6. Full execution
        result = await robust_pipeline.collect()(async_range(5))
        assert result == [1, 3, 5, 7, 9]

        # 7. Verify registry state
        math_flows = list_flows("math")
        assert len(math_flows) == 2
        assert "doubler" in math_flows
        assert "incrementer" in math_flows

    def test_repr_and_debugging(self):
        """Test debugging and repr functionality."""

        # Create a complex flow
        flow = (
            Flow.from_iterable([1, 2, 3])
            .map(lambda x: x * 2)
            .filter(lambda x: x > 2)
            .with_fallback(0)
        )

        # Test repr
        repr_str = repr(flow)
        assert "<Flow name=" in repr_str

        # Test print (should not raise)
        result = flow.print()
        assert result is flow

    def setup_method(self):
        """Clear registry before each test."""
        flow_registry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        flow_registry.clear()
