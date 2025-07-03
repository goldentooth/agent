"""Tests for basic flow combinators."""

from __future__ import annotations

import pytest

from flowengine.combinators.basic import compose, filter_stream, run_fold
from flowengine.flow import Flow


# Helper functions to replace lambdas and eliminate type: ignore comments
def increment(x: int) -> int:
    """Add 1 to the input."""
    return x + 1


def double(x: int) -> int:
    """Multiply input by 2."""
    return x * 2


def identity(x: int) -> int:
    """Return input unchanged."""
    return x


def int_to_str(x: int) -> str:
    """Convert integer to string."""
    return str(x)


def str_length(s: str) -> int:
    """Get length of string."""
    return len(s)


def is_even(x: int) -> bool:
    """Check if number is even."""
    return x % 2 == 0


def always_true(x: int) -> bool:
    """Always return True."""
    return True


class TestRunFold:
    """Test the run_fold function."""

    @pytest.mark.asyncio
    async def test_run_fold_empty_steps(self) -> None:
        """Test run_fold with empty steps list."""

        async def source():
            yield 1
            yield 2
            yield 3

        result_stream = await run_fold(source(), [])
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_run_fold_single_step(self) -> None:
        """Test run_fold with a single step."""

        async def source():
            yield 1
            yield 2
            yield 3

        increment_flow = Flow.from_sync_fn(increment)
        result_stream = await run_fold(source(), [increment_flow])
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [2, 3, 4]

    @pytest.mark.asyncio
    async def test_run_fold_multiple_steps(self) -> None:
        """Test run_fold with multiple steps."""

        async def source():
            yield 1
            yield 2
            yield 3

        increment_flow = Flow.from_sync_fn(increment)
        double_flow = Flow.from_sync_fn(double)
        result_stream = await run_fold(source(), [increment_flow, double_flow])
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [4, 6, 8]  # (1+1)*2, (2+1)*2, (3+1)*2

    @pytest.mark.asyncio
    async def test_run_fold_empty_stream(self) -> None:
        """Test run_fold with empty input stream."""

        async def empty_source():
            return
            yield  # pragma: no cover

        increment_flow = Flow.from_sync_fn(increment)
        result_stream = await run_fold(empty_source(), [increment_flow])
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == []

    @pytest.mark.asyncio
    async def test_run_fold_identity_steps(self) -> None:
        """Test run_fold with identity flows."""

        async def source():
            yield 1
            yield 2
            yield 3

        identity_flow = Flow.from_sync_fn(identity)
        result_stream = await run_fold(source(), [identity_flow, identity_flow])
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [1, 2, 3]


class TestCompose:
    """Test the compose function."""

    @pytest.mark.asyncio
    async def test_compose_two_flows(self) -> None:
        """Test composing two flows."""

        async def source():
            yield 1
            yield 2
            yield 3

        # First flow: add 1
        first_flow = Flow.from_sync_fn(increment)
        # Second flow: multiply by 2
        second_flow = Flow.from_sync_fn(double)

        # Compose: (x + 1) * 2
        composed_flow = compose(first_flow, second_flow)
        results: list[int] = []
        async for item in composed_flow(source()):
            results.append(item)

        assert results == [4, 6, 8]  # (1+1)*2, (2+1)*2, (3+1)*2

    @pytest.mark.asyncio
    async def test_compose_name_generation(self) -> None:
        """Test that compose generates appropriate names."""
        first_flow = Flow.from_sync_fn(increment)
        second_flow = Flow.from_sync_fn(double)

        # Set custom names
        first_flow.name = "add_one"
        second_flow.name = "double"

        composed_flow = compose(first_flow, second_flow)
        assert composed_flow.name == "add_one ∘ double"

    @pytest.mark.asyncio
    async def test_compose_empty_stream(self) -> None:
        """Test compose with empty input stream."""

        async def empty_source():
            return
            yield  # pragma: no cover

        first_flow = Flow.from_sync_fn(increment)
        second_flow = Flow.from_sync_fn(double)

        composed_flow = compose(first_flow, second_flow)
        results: list[int] = []
        async for item in composed_flow(empty_source()):
            results.append(item)

        assert results == []

    @pytest.mark.asyncio
    async def test_compose_identity_flows(self) -> None:
        """Test compose with identity flows."""

        async def source():
            yield 1
            yield 2
            yield 3

        identity_flow = Flow.from_sync_fn(identity)

        composed_flow = compose(identity_flow, identity_flow)
        results: list[int] = []
        async for item in composed_flow(source()):
            results.append(item)

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_compose_type_transformation(self) -> None:
        """Test compose with type transformation."""

        async def source():
            yield 1
            yield 2
            yield 3

        # First flow: int to string
        int_to_str_flow = Flow.from_sync_fn(int_to_str)
        # Second flow: string to length
        str_to_len_flow = Flow.from_sync_fn(str_length)

        composed_flow = compose(int_to_str_flow, str_to_len_flow)
        results: list[int] = []
        async for item in composed_flow(source()):
            results.append(item)

        assert results == [1, 1, 1]  # len("1"), len("2"), len("3")


class TestFilterStream:
    """Test the filter_stream function."""

    @pytest.mark.asyncio
    async def test_filter_stream_basic(self) -> None:
        """Test filter_stream with basic predicate."""

        async def source():
            for i in [1, 2, 3, 4, 5, 6]:
                yield i

        even_filter = filter_stream(is_even)
        result_stream = even_filter(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_filter_stream_empty_result(self) -> None:
        """Test filter_stream when no items match predicate."""

        async def source():
            for i in [1, 3, 5]:
                yield i

        even_filter = filter_stream(is_even)
        result_stream = even_filter(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == []

    @pytest.mark.asyncio
    async def test_filter_stream_all_match(self) -> None:
        """Test filter_stream when all items match predicate."""

        async def source():
            for i in [2, 4, 6]:
                yield i

        even_filter = filter_stream(is_even)
        result_stream = even_filter(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_filter_stream_empty_input(self) -> None:
        """Test filter_stream with empty input stream."""

        async def empty_source():
            return
            yield  # pragma: no cover

        filter_flow = filter_stream(always_true)
        result_stream = filter_flow(empty_source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == []

    def test_filter_stream_name_generation(self) -> None:
        """Test that filter_stream generates appropriate names."""

        def is_positive(x: int) -> bool:
            return x > 0

        positive_filter = filter_stream(is_positive)
        assert "filter(is_positive)" in positive_filter.name
