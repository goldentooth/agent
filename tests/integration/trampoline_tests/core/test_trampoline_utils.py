"""Tests for context_flow.trampoline utility functions."""

from typing import Any

import pytest

from context_flow.trampoline import async_iter_from_item, extend_flow_with_trampoline


class TestAsyncIterFromItem:
    """Test cases for async_iter_from_item utility function."""

    @pytest.mark.asyncio
    async def testasync_iter_from_item_basic_functionality(self) -> None:
        """Test that async_iter_from_item creates an async iterator from a single item."""
        # Test with string item
        item = "test_value"
        async_iter = async_iter_from_item(item)

        # Collect all items from the iterator
        items: list[object] = []
        async for value in async_iter:
            items.append(value)

        # Should yield exactly one item
        assert len(items) == 1
        assert items[0] == "test_value"

    @pytest.mark.asyncio
    async def testasync_iter_from_item_with_different_types(self) -> None:
        """Test that async_iter_from_item works with different data types."""
        # Test with integer
        await self._test_async_iter_with_integer()

        # Test with list
        await self._test_async_iter_with_list()

        # Test with dict
        await self._test_async_iter_with_dict()

    async def _test_async_iter_with_integer(self) -> None:
        """Test async_iter_from_item with integer type."""
        item = 42
        async_iter = async_iter_from_item(item)

        items: list[object] = []
        async for value in async_iter:
            items.append(value)

        assert len(items) == 1
        assert items[0] == 42
        assert isinstance(items[0], int)

    async def _test_async_iter_with_list(self) -> None:
        """Test async_iter_from_item with list type."""
        item = [1, 2, 3]
        async_iter = async_iter_from_item(item)

        items: list[object] = []
        async for value in async_iter:
            items.append(value)

        assert len(items) == 1
        assert items[0] == [1, 2, 3]
        assert isinstance(items[0], list)

    async def _test_async_iter_with_dict(self) -> None:
        """Test async_iter_from_item with dict type."""
        item = {"key": "value", "count": 1}
        async_iter = async_iter_from_item(item)

        items: list[object] = []
        async for value in async_iter:
            items.append(value)

        assert len(items) == 1
        assert items[0] == {"key": "value", "count": 1}
        assert isinstance(items[0], dict)

    @pytest.mark.asyncio
    async def testasync_iter_from_item_with_none(self) -> None:
        """Test that async_iter_from_item works with None value."""
        item = None
        async_iter = async_iter_from_item(item)

        items: list[object] = []
        async for value in async_iter:
            items.append(value)

        assert len(items) == 1
        assert items[0] is None

    @pytest.mark.asyncio
    async def testasync_iter_from_item_with_custom_objects(self) -> None:
        """Test that async_iter_from_item works with custom objects."""

        # Create a custom class
        class TestObject:
            def __init__(self, name: str, value: int):
                super().__init__()
                self.name = name
                self.value = value

            def __eq__(self, other: object) -> bool:
                return (
                    isinstance(other, TestObject)
                    and self.name == other.name
                    and self.value == other.value
                )

        # Test with custom object
        test_obj = TestObject("test", 123)
        async_iter = async_iter_from_item(test_obj)

        items: list[object] = []
        async for value in async_iter:
            items.append(value)

        assert len(items) == 1
        assert items[0] == test_obj
        assert isinstance(items[0], TestObject)
        assert items[0].name == "test"
        assert items[0].value == 123

    @pytest.mark.asyncio
    async def testasync_iter_from_item_iterator_protocol(self) -> None:
        """Test that async_iter_from_item returns proper async iterator."""
        item = "test"
        async_iter = async_iter_from_item(item)

        # Check that it has async iterator methods
        assert hasattr(async_iter, "__aiter__")
        assert hasattr(async_iter, "__anext__")

        # Test that __aiter__ returns itself
        assert async_iter.__aiter__() is async_iter

    @pytest.mark.asyncio
    async def testasync_iter_from_item_single_consumption(self) -> None:
        """Test that async_iter_from_item can only be consumed once."""
        item = "test_value"
        async_iter = async_iter_from_item(item)

        # First consumption
        items1 = []
        async for value in async_iter:
            items1.append(value)

        assert len(items1) == 1
        assert items1[0] == "test_value"

        # Second consumption should yield nothing (iterator exhausted)
        items2 = []
        async for value in async_iter:
            items2.append(value)

        assert len(items2) == 0

    @pytest.mark.asyncio
    async def testasync_iter_from_item_with_context_objects(self) -> None:
        """Test that async_iter_from_item works with Context objects."""
        from context.main import Context

        # Create a context object
        context = Context()
        context["test_key"] = "test_value"
        context["count"] = 42

        async_iter = async_iter_from_item(context)

        items: list[object] = []
        async for value in async_iter:
            items.append(value)

        assert len(items) == 1
        assert items[0] is context
        assert isinstance(items[0], Context)
        assert items[0]["test_key"] == "test_value"
        assert items[0]["count"] == 42

    @pytest.mark.asyncio
    async def testasync_iter_from_item_memory_efficiency(self) -> None:
        """Test that async_iter_from_item doesn't unnecessarily copy data."""
        # Create a large-ish object to test memory efficiency
        large_list = list(range(1000))

        async_iter = async_iter_from_item(large_list)

        items: list[object] = []
        async for value in async_iter:
            items.append(value)

        # Should be the same object (not copied)
        assert len(items) == 1
        assert items[0] is large_list

    @pytest.mark.asyncio
    async def testasync_iter_from_item_with_async_break(self) -> None:
        """Test that async_iter_from_item works with early break."""
        item = "test_value"
        async_iter = async_iter_from_item(item)

        # Break after first item (which should be the only item anyway)
        items: list[object] = []
        async for value in async_iter:
            items.append(value)
            break  # Early break

        assert len(items) == 1
        assert items[0] == "test_value"

        # Try to get more items - should be exhausted
        additional_items = []
        async for value in async_iter:
            additional_items.append(value)

        assert len(additional_items) == 0

    @pytest.mark.asyncio
    async def testasync_iter_from_item_exception_handling(self) -> None:
        """Test that async_iter_from_item properly handles exceptions."""
        item = "test_value"
        async_iter = async_iter_from_item(item)

        # Test that exceptions during iteration are properly propagated
        with pytest.raises(ValueError, match="test exception"):
            async for value in async_iter:
                assert value == "test_value"
                raise ValueError("test exception")

    @pytest.mark.asyncio
    async def testasync_iter_from_item_multiple_iterators(self) -> None:
        """Test that each call to async_iter_from_item creates independent iterators."""
        item = "shared_value"

        # Create two independent iterators
        iter1 = async_iter_from_item(item)
        iter2 = async_iter_from_item(item)

        # They should be different objects
        assert iter1 is not iter2

        # Consume first iterator
        items1 = []
        async for value in iter1:
            items1.append(value)

        # Second iterator should still work
        items2 = []
        async for value in iter2:
            items2.append(value)

        assert len(items1) == 1
        assert len(items2) == 1
        assert items1[0] == "shared_value"
        assert items2[0] == "shared_value"


class TestExtendFlowWithTrampoline:
    """Test cases for extend_flow_with_trampoline utility function."""

    def test_extend_flow_with_trampoline_basic_functionality(self) -> None:
        """Test that extend_flow_with_trampoline adds trampoline methods to Flow class."""
        from flow.flow import Flow

        # Store original methods to restore later
        original_methods = {}
        trampoline_methods = [
            "run_single",
            "as_single_stream",
            "repeat_until",
            "exit_on",
        ]

        for method_name in trampoline_methods:
            if hasattr(Flow, method_name):
                original_methods[method_name] = getattr(Flow, method_name)

        try:
            # Call extend_flow_with_trampoline
            extend_flow_with_trampoline()

            # Check that trampoline methods were added to Flow class
            assert hasattr(Flow, "run_single")
            assert callable(getattr(Flow, "run_single"))
            assert hasattr(Flow, "as_single_stream")
            assert callable(getattr(Flow, "as_single_stream"))
            assert hasattr(Flow, "repeat_until")
            assert callable(getattr(Flow, "repeat_until"))
            assert hasattr(Flow, "exit_on")
            assert callable(getattr(Flow, "exit_on"))

        finally:
            # Clean up: remove added methods or restore originals
            for method_name in trampoline_methods:
                if method_name in original_methods:
                    setattr(Flow, method_name, original_methods[method_name])
                elif hasattr(Flow, method_name):
                    delattr(Flow, method_name)

    def test_extend_flow_with_trampoline_run_single_method(self) -> None:
        """Test that the added run_single method works correctly."""
        from context.main import Context
        from flow.flow import Flow

        # Store original method to restore later
        original_run_single = getattr(Flow, "run_single", None)

        try:
            # Call extend_flow_with_trampoline
            extend_flow_with_trampoline()

            # Create a simple flow for testing
            def simple_flow_func(stream: Any) -> Any:
                async def _flow() -> Any:
                    async for item in stream:
                        yield f"processed_{item}"

                return _flow()

            test_flow = Flow(simple_flow_func)

            # Test run_single method
            input_item = "test_input"
            result = test_flow.run_single(input_item)  # type: ignore[attr-defined]

            assert result == "processed_test_input"

        finally:
            # Clean up: remove or restore method
            if original_run_single is not None:
                setattr(Flow, "run_single", original_run_single)
            elif hasattr(Flow, "run_single"):
                delattr(Flow, "run_single")

    def test_extend_flow_with_trampoline_as_single_stream_method(self) -> None:
        """Test that the added as_single_stream method works correctly."""
        from flow.flow import Flow

        # Store original method to restore later
        original_as_single_stream = getattr(Flow, "as_single_stream", None)

        try:
            # Call extend_flow_with_trampoline
            extend_flow_with_trampoline()

            # Create a simple flow for testing
            def simple_flow_func(stream: Any) -> Any:
                async def _flow() -> Any:
                    async for item in stream:
                        yield f"streamed_{item}"

                return _flow()

            test_flow = Flow(simple_flow_func)

            # Test as_single_stream method
            input_item = "test_input"
            result_flow = test_flow.as_single_stream(input_item)  # type: ignore[attr-defined]

            # Verify it returns a Flow
            assert isinstance(result_flow, Flow)

        finally:
            # Clean up: remove or restore method
            if original_as_single_stream is not None:
                setattr(Flow, "as_single_stream", original_as_single_stream)
            elif hasattr(Flow, "as_single_stream"):
                delattr(Flow, "as_single_stream")

    def test_extend_flow_with_trampoline_repeat_until_method(self) -> None:
        """Test that the added repeat_until method works correctly."""
        from flow.flow import Flow

        # Store original method to restore later
        original_repeat_until = getattr(Flow, "repeat_until", None)

        try:
            # Call extend_flow_with_trampoline
            extend_flow_with_trampoline()

            # Create a simple flow for testing
            def simple_flow_func(stream: Any) -> Any:
                async def _flow() -> Any:
                    async for item in stream:
                        yield item + 1

                return _flow()

            test_flow = Flow(simple_flow_func)

            # Test repeat_until method
            def condition(value: Any) -> bool:
                return bool(value >= 5)

            result_flow = test_flow.repeat_until(condition)  # type: ignore[attr-defined]

            # Verify it returns a Flow
            assert isinstance(result_flow, Flow)

        finally:
            # Clean up: remove or restore method
            if original_repeat_until is not None:
                setattr(Flow, "repeat_until", original_repeat_until)
            elif hasattr(Flow, "repeat_until"):
                delattr(Flow, "repeat_until")

    def test_extend_flow_with_trampoline_exit_on_method(self) -> None:
        """Test that the added exit_on method works correctly."""
        from flow.flow import Flow

        # Store original method to restore later
        original_exit_on = getattr(Flow, "exit_on", None)

        try:
            # Call extend_flow_with_trampoline
            extend_flow_with_trampoline()

            # Create a simple flow for testing
            def simple_flow_func(stream: Any) -> Any:
                async def _flow() -> Any:
                    async for item in stream:
                        yield item

                return _flow()

            test_flow = Flow(simple_flow_func)

            # Test exit_on method
            def exit_condition(value: Any) -> bool:
                return bool(value == "exit")

            result_flow = test_flow.exit_on(exit_condition)  # type: ignore[attr-defined]

            # Verify it returns a Flow
            assert isinstance(result_flow, Flow)

        finally:
            # Clean up: remove or restore method
            if original_exit_on is not None:
                setattr(Flow, "exit_on", original_exit_on)
            elif hasattr(Flow, "exit_on"):
                delattr(Flow, "exit_on")

    def test_extend_flow_with_trampoline_multiple_calls(self) -> None:
        """Test that extend_flow_with_trampoline can be called multiple times safely."""
        from flow.flow import Flow

        # Store original methods to restore later
        original_methods = {}
        trampoline_methods = [
            "run_single",
            "as_single_stream",
            "repeat_until",
            "exit_on",
        ]

        for method_name in trampoline_methods:
            if hasattr(Flow, method_name):
                original_methods[method_name] = getattr(Flow, method_name)

        try:
            # Call extend_flow_with_trampoline multiple times
            extend_flow_with_trampoline()
            extend_flow_with_trampoline()
            extend_flow_with_trampoline()

            # Check that methods are still present and callable
            for method_name in trampoline_methods:
                assert hasattr(Flow, method_name)
                assert callable(getattr(Flow, method_name))

        finally:
            # Clean up: remove added methods or restore originals
            for method_name in trampoline_methods:
                if method_name in original_methods:
                    setattr(Flow, method_name, original_methods[method_name])
                elif hasattr(Flow, method_name):
                    delattr(Flow, method_name)

    def test_extend_flow_with_trampoline_preserves_existing_methods(self) -> None:
        """Test that extend_flow_with_trampoline preserves existing Flow methods."""
        from flow.flow import Flow

        # Store original methods to restore later
        original_methods = {}
        trampoline_methods = [
            "run_single",
            "as_single_stream",
            "repeat_until",
            "exit_on",
        ]

        for method_name in trampoline_methods:
            if hasattr(Flow, method_name):
                original_methods[method_name] = getattr(Flow, method_name)

        # Store some core Flow methods to verify they're preserved
        core_methods = ["__init__", "__call__", "__rshift__"]
        core_method_objects = {name: getattr(Flow, name) for name in core_methods}

        try:
            # Call extend_flow_with_trampoline
            extend_flow_with_trampoline()

            # Verify core methods are still present and unchanged
            for method_name, original_method in core_method_objects.items():
                assert hasattr(Flow, method_name)
                current_method = getattr(Flow, method_name)
                assert current_method is original_method

        finally:
            # Clean up: remove added methods or restore originals
            for method_name in trampoline_methods:
                if method_name in original_methods:
                    setattr(Flow, method_name, original_methods[method_name])
                elif hasattr(Flow, method_name):
                    delattr(Flow, method_name)

    def test_extend_flow_with_trampoline_method_signatures(self) -> None:
        """Test that the added methods have proper signatures."""
        import inspect

        from flow.flow import Flow

        # Store original methods to restore later
        original_methods = {}
        trampoline_methods = [
            "run_single",
            "as_single_stream",
            "repeat_until",
            "exit_on",
        ]

        for method_name in trampoline_methods:
            if hasattr(Flow, method_name):
                original_methods[method_name] = getattr(Flow, method_name)

        try:
            # Call extend_flow_with_trampoline
            extend_flow_with_trampoline()

            # Check method signatures
            run_single_sig = inspect.signature(Flow.run_single)  # type: ignore[attr-defined]
            assert "self" in run_single_sig.parameters
            assert "item" in run_single_sig.parameters

            as_single_stream_sig = inspect.signature(Flow.as_single_stream)  # type: ignore[attr-defined]
            assert "self" in as_single_stream_sig.parameters
            assert "item" in as_single_stream_sig.parameters

            repeat_until_sig = inspect.signature(Flow.repeat_until)  # type: ignore[attr-defined]
            assert "self" in repeat_until_sig.parameters
            assert "condition" in repeat_until_sig.parameters

            exit_on_sig = inspect.signature(Flow.exit_on)  # type: ignore[attr-defined]
            assert "self" in exit_on_sig.parameters
            assert "condition" in exit_on_sig.parameters

        finally:
            # Clean up: remove added methods or restore originals
            for method_name in trampoline_methods:
                if method_name in original_methods:
                    setattr(Flow, method_name, original_methods[method_name])
                elif hasattr(Flow, method_name):
                    delattr(Flow, method_name)

    def test_extend_flow_with_trampoline_documentation(self) -> None:
        """Test that the added methods have proper documentation."""
        from flow.flow import Flow

        # Store original methods to restore later
        original_methods = {}
        trampoline_methods = [
            "run_single",
            "as_single_stream",
            "repeat_until",
            "exit_on",
        ]

        for method_name in trampoline_methods:
            if hasattr(Flow, method_name):
                original_methods[method_name] = getattr(Flow, method_name)

        try:
            # Call extend_flow_with_trampoline
            extend_flow_with_trampoline()

            # Check that methods have docstrings
            assert Flow.run_single.__doc__ is not None  # type: ignore[attr-defined]
            assert len(Flow.run_single.__doc__.strip()) > 0  # type: ignore[attr-defined]

            assert Flow.as_single_stream.__doc__ is not None  # type: ignore[attr-defined]
            assert len(Flow.as_single_stream.__doc__.strip()) > 0  # type: ignore[attr-defined]

            assert Flow.repeat_until.__doc__ is not None  # type: ignore[attr-defined]
            assert len(Flow.repeat_until.__doc__.strip()) > 0  # type: ignore[attr-defined]

            assert Flow.exit_on.__doc__ is not None  # type: ignore[attr-defined]
            assert len(Flow.exit_on.__doc__.strip()) > 0  # type: ignore[attr-defined]

        finally:
            # Clean up: remove added methods or restore originals
            for method_name in trampoline_methods:
                if method_name in original_methods:
                    setattr(Flow, method_name, original_methods[method_name])
                elif hasattr(Flow, method_name):
                    delattr(Flow, method_name)
