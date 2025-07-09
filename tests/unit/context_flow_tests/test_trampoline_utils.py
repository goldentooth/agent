"""Tests for context_flow.trampoline utility functions."""

import pytest

from context_flow.trampoline import _async_iter_from_item


class TestAsyncIterFromItem:
    """Test cases for _async_iter_from_item utility function."""

    @pytest.mark.asyncio
    async def test_async_iter_from_item_basic_functionality(self) -> None:
        """Test that _async_iter_from_item creates an async iterator from a single item."""
        # Test with string item
        item = "test_value"
        async_iter = _async_iter_from_item(item)

        # Collect all items from the iterator
        items: list[object] = []
        async for value in async_iter:
            items.append(value)

        # Should yield exactly one item
        assert len(items) == 1
        assert items[0] == "test_value"

    @pytest.mark.asyncio
    async def test_async_iter_from_item_with_different_types(self) -> None:
        """Test that _async_iter_from_item works with different data types."""
        # Test with integer
        await self._test_async_iter_with_integer()

        # Test with list
        await self._test_async_iter_with_list()

        # Test with dict
        await self._test_async_iter_with_dict()

    async def _test_async_iter_with_integer(self) -> None:
        """Test _async_iter_from_item with integer type."""
        item = 42
        async_iter = _async_iter_from_item(item)

        items: list[object] = []
        async for value in async_iter:
            items.append(value)

        assert len(items) == 1
        assert items[0] == 42
        assert isinstance(items[0], int)

    async def _test_async_iter_with_list(self) -> None:
        """Test _async_iter_from_item with list type."""
        item = [1, 2, 3]
        async_iter = _async_iter_from_item(item)

        items: list[object] = []
        async for value in async_iter:
            items.append(value)

        assert len(items) == 1
        assert items[0] == [1, 2, 3]
        assert isinstance(items[0], list)

    async def _test_async_iter_with_dict(self) -> None:
        """Test _async_iter_from_item with dict type."""
        item = {"key": "value", "count": 1}
        async_iter = _async_iter_from_item(item)

        items: list[object] = []
        async for value in async_iter:
            items.append(value)

        assert len(items) == 1
        assert items[0] == {"key": "value", "count": 1}
        assert isinstance(items[0], dict)

    @pytest.mark.asyncio
    async def test_async_iter_from_item_with_none(self) -> None:
        """Test that _async_iter_from_item works with None value."""
        item = None
        async_iter = _async_iter_from_item(item)

        items: list[object] = []
        async for value in async_iter:
            items.append(value)

        assert len(items) == 1
        assert items[0] is None

    @pytest.mark.asyncio
    async def test_async_iter_from_item_with_custom_objects(self) -> None:
        """Test that _async_iter_from_item works with custom objects."""

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
        async_iter = _async_iter_from_item(test_obj)

        items: list[object] = []
        async for value in async_iter:
            items.append(value)

        assert len(items) == 1
        assert items[0] == test_obj
        assert isinstance(items[0], TestObject)
        assert items[0].name == "test"
        assert items[0].value == 123

    @pytest.mark.asyncio
    async def test_async_iter_from_item_iterator_protocol(self) -> None:
        """Test that _async_iter_from_item returns proper async iterator."""
        item = "test"
        async_iter = _async_iter_from_item(item)

        # Check that it has async iterator methods
        assert hasattr(async_iter, "__aiter__")
        assert hasattr(async_iter, "__anext__")

        # Test that __aiter__ returns itself
        assert async_iter.__aiter__() is async_iter

    @pytest.mark.asyncio
    async def test_async_iter_from_item_single_consumption(self) -> None:
        """Test that _async_iter_from_item can only be consumed once."""
        item = "test_value"
        async_iter = _async_iter_from_item(item)

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
    async def test_async_iter_from_item_with_context_objects(self) -> None:
        """Test that _async_iter_from_item works with Context objects."""
        from context.main import Context

        # Create a context object
        context = Context()
        context["test_key"] = "test_value"
        context["count"] = 42

        async_iter = _async_iter_from_item(context)

        items: list[object] = []
        async for value in async_iter:
            items.append(value)

        assert len(items) == 1
        assert items[0] is context
        assert isinstance(items[0], Context)
        assert items[0]["test_key"] == "test_value"
        assert items[0]["count"] == 42

    @pytest.mark.asyncio
    async def test_async_iter_from_item_memory_efficiency(self) -> None:
        """Test that _async_iter_from_item doesn't unnecessarily copy data."""
        # Create a large-ish object to test memory efficiency
        large_list = list(range(1000))

        async_iter = _async_iter_from_item(large_list)

        items: list[object] = []
        async for value in async_iter:
            items.append(value)

        # Should be the same object (not copied)
        assert len(items) == 1
        assert items[0] is large_list

    @pytest.mark.asyncio
    async def test_async_iter_from_item_with_async_break(self) -> None:
        """Test that _async_iter_from_item works with early break."""
        item = "test_value"
        async_iter = _async_iter_from_item(item)

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
    async def test_async_iter_from_item_exception_handling(self) -> None:
        """Test that _async_iter_from_item properly handles exceptions."""
        item = "test_value"
        async_iter = _async_iter_from_item(item)

        # Test that exceptions during iteration are properly propagated
        with pytest.raises(ValueError, match="test exception"):
            async for value in async_iter:
                assert value == "test_value"
                raise ValueError("test exception")

    @pytest.mark.asyncio
    async def test_async_iter_from_item_multiple_iterators(self) -> None:
        """Test that each call to _async_iter_from_item creates independent iterators."""
        item = "shared_value"

        # Create two independent iterators
        iter1 = _async_iter_from_item(item)
        iter2 = _async_iter_from_item(item)

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
