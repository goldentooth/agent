"""Tests for control flow combinators."""

import asyncio
from typing import Any, Union

import pytest

from flowengine.combinators.basic import map_stream
from flowengine.combinators.control_flow import (
    catch_and_continue_stream,
    if_then_stream,
    recover_stream,
    retry_stream,
    switch_stream,
    tap_stream,
    then_stream,
    while_condition_stream,
)
from flowengine.exceptions import FlowExecutionError


# Helper functions
def increment(x: int) -> int:
    """Increment a number by 1."""
    return x + 1


def double(x: int) -> int:
    """Double a number."""
    return x * 2


def is_even(x: int) -> bool:
    """Check if a number is even."""
    return x % 2 == 0


async def async_range(n: int):
    """Generate an async range of integers."""
    for i in range(n):
        yield i


async def async_increment(x: int) -> int:
    """Async increment function."""
    await asyncio.sleep(0.001)
    return x + 1


class TestIfThenStream:
    """Tests for if_then_stream function."""

    @pytest.mark.asyncio
    async def test_if_then_basic(self):
        """Test basic if-then functionality."""
        increment_flow = map_stream(increment)
        double_flow = map_stream(double)
        if_then_flow = if_then_stream(is_even, increment_flow, double_flow)

        assert "if_then(is_even, map(increment), map(double))" in if_then_flow.name

        input_stream = async_range(4)  # [0, 1, 2, 3]
        result_stream = if_then_flow(input_stream)
        values = [item async for item in result_stream]
        # 0 (even): 0+1=1, 1 (odd): 1*2=2, 2 (even): 2+1=3, 3 (odd): 3*2=6
        assert values == [1, 2, 3, 6]

    @pytest.mark.asyncio
    async def test_if_then_no_else(self):
        """Test if-then without else clause."""
        increment_flow = map_stream(increment)
        if_then_flow = if_then_stream(is_even, increment_flow)

        assert "if_then(is_even, map(increment))" in if_then_flow.name

        input_stream = async_range(5)  # [0, 1, 2, 3, 4]
        result_stream = if_then_flow(input_stream)
        values = [item async for item in result_stream]
        # Only even numbers are processed: 0->1, 2->3, 4->5
        assert values == [1, 3, 5]


class TestRetryStream:
    """Tests for retry_stream function."""

    @pytest.mark.asyncio
    async def test_retry_success_first_try(self):
        """Test retry when first attempt succeeds."""
        attempt_count = 0

        def count_attempts(x: int) -> int:
            nonlocal attempt_count
            attempt_count += 1
            return x * 2

        process_flow = map_stream(count_attempts)
        retry_flow = retry_stream(3, process_flow)

        assert "retry(3, map(count_attempts))" in retry_flow.name

        input_stream = async_range(2)
        result_stream = retry_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [0, 2]
        assert attempt_count == 2  # One per item, no retries

    @pytest.mark.asyncio
    async def test_retry_with_eventual_success(self):
        """Test retry with failures then success."""
        attempts = {}

        def flaky_operation(x: int) -> int:
            if x not in attempts:
                attempts[x] = 0
            attempts[x] += 1

            # Fail first 2 attempts for each item
            if attempts[x] < 3:
                raise ValueError(f"Attempt {attempts[x]} failed")
            return x * 2

        process_flow = map_stream(flaky_operation)
        retry_flow = retry_stream(3, process_flow)

        input_stream = async_range(2)
        result_stream = retry_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [0, 2]
        assert attempts == {0: 3, 1: 3}  # 3 attempts each

    @pytest.mark.asyncio
    async def test_retry_all_attempts_fail(self):
        """Test retry when all attempts fail."""

        def always_fail(x: int) -> int:
            raise ValueError("Always fails")

        process_flow = map_stream(always_fail)
        retry_flow = retry_stream(2, process_flow)

        input_stream = async_range(1)
        result_stream = retry_flow(input_stream)

        with pytest.raises(FlowExecutionError) as exc_info:
            _ = [item async for item in result_stream]

        assert "Failed after 2 retries" in str(exc_info.value)
        assert "Always fails" in str(exc_info.value)


class TestRecoverStream:
    """Tests for recover_stream function."""

    @pytest.mark.asyncio
    async def test_recover_basic(self):
        """Test basic recovery functionality."""

        async def handler(error: Exception, item: int) -> int:
            return -1  # Return -1 for any error

        recover_flow = recover_stream(handler)
        assert "recover(handler)" in recover_flow.name

        async def failing_stream():
            yield 1
            raise ValueError("Test error")

        result_stream = recover_flow(failing_stream())
        values = [item async for item in result_stream]

        # First item passes through, second triggers recovery
        assert values == [1, -1]


class TestSwitchStream:
    """Tests for switch_stream function."""

    @pytest.mark.asyncio
    async def test_switch_basic(self):
        """Test basic switch functionality."""

        def categorize(x: int) -> str:
            if x < 0:
                return "negative"
            elif x == 0:
                return "zero"
            else:
                return "positive"

        def neg_transform(x: int) -> str:
            return f"neg_{x}"

        def zero_transform(x: int) -> str:
            return "ZERO"

        def pos_transform(x: int) -> str:
            return f"pos_{x}"

        negative_flow = map_stream(neg_transform)
        zero_flow = map_stream(zero_transform)
        positive_flow = map_stream(pos_transform)

        cases = {
            "negative": negative_flow,
            "zero": zero_flow,
            "positive": positive_flow,
        }

        switch_flow = switch_stream(categorize, cases)
        assert "switch(categorize, 3 cases)" in switch_flow.name

        async def mixed_stream():
            yield -2
            yield 0
            yield 3

        result_stream = switch_flow(mixed_stream())
        values = [item async for item in result_stream]
        assert values == ["neg_-2", "ZERO", "pos_3"]

    @pytest.mark.asyncio
    async def test_switch_with_default(self):
        """Test switch with default case."""

        def size_category(x: int) -> str:
            if x < 10:
                return "small"
            elif x < 100:
                return "medium"
            else:
                return "large"

        def small_transform(x: int) -> int:
            return x * 2

        def medium_transform(x: int) -> int:
            return x + 10

        def default_transform(x: int) -> int:
            return x // 10

        small_flow = map_stream(small_transform)
        medium_flow = map_stream(medium_transform)
        default_flow = map_stream(default_transform)

        cases = {
            "small": small_flow,
            "medium": medium_flow,
        }
        switch_flow = switch_stream(size_category, cases, default=default_flow)

        async def number_stream():
            yield 5  # small: 5 * 2 = 10
            yield 50  # medium: 50 + 10 = 60
            yield 500  # large (default): 500 // 10 = 50

        result_stream = switch_flow(number_stream())
        values = [item async for item in result_stream]
        assert values == [10, 60, 50]

    @pytest.mark.asyncio
    async def test_switch_no_case_no_default(self):
        """Test switch with unmatched case and no default."""

        def always_unknown(x: Any) -> str:
            return "unknown"

        cases = {"known": map_stream(double)}
        switch_flow = switch_stream(always_unknown, cases)

        input_stream = async_range(3)
        result_stream = switch_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == []  # All items filtered out


class TestTapStream:
    """Tests for tap_stream function."""

    @pytest.mark.asyncio
    async def test_tap_basic(self):
        """Test basic tap functionality."""
        side_effects: list[int] = []

        def record_item(x: int) -> None:
            side_effects.append(x)

        tap_flow = tap_stream(record_item)
        assert "tap(record_item)" in tap_flow.name

        input_stream = async_range(3)
        result_stream = tap_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [0, 1, 2]
        assert side_effects == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_tap_with_async_function(self):
        """Test tap with async side effect."""
        side_effects: list[int] = []

        async def async_record(x: int) -> None:
            await asyncio.sleep(0.001)
            side_effects.append(x)

        tap_flow = tap_stream(async_record)

        input_stream = async_range(3)
        result_stream = tap_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [0, 1, 2]
        assert side_effects == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_tap_empty_stream(self):
        """Test tap on empty stream."""
        side_effects: list[int] = []

        def append_effect(x: int) -> None:
            side_effects.append(x)

        tap_flow = tap_stream(append_effect)

        async def empty_stream():
            if False:
                yield 0

        result_stream = tap_flow(empty_stream())
        values = [item async for item in result_stream]

        assert values == []
        assert side_effects == []


class TestWhileConditionStream:
    """Tests for while_condition_stream function."""

    @pytest.mark.asyncio
    async def test_while_condition_basic(self):
        """Test basic while condition functionality."""

        def less_than_3(x: int) -> bool:
            return x < 3

        double_flow = map_stream(double)
        while_flow = while_condition_stream(less_than_3, double_flow)

        assert "while(less_than_3, map(double))" in while_flow.name

        input_stream = async_range(5)
        result_stream = while_flow(input_stream)
        values = [item async for item in result_stream]

        # Process 0, 1, 2 (all < 3), stop at 3
        assert values == [0, 2, 4]

    @pytest.mark.asyncio
    async def test_while_condition_immediate_false(self):
        """Test while condition that's false immediately."""

        def always_false(x: int) -> bool:
            return False

        process_flow = map_stream(double)
        while_flow = while_condition_stream(always_false, process_flow)

        input_stream = async_range(3)
        result_stream = while_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == []


class TestThenStream:
    """Tests for then_stream function."""

    @pytest.mark.asyncio
    async def test_then_basic(self):
        """Test basic then functionality."""
        side_effects: list[str] = []

        def record_after(x: int) -> None:
            side_effects.append(f"after_{x}")

        then_flow = then_stream(record_after)
        assert "then(record_after)" in then_flow.name

        input_stream = async_range(3)
        result_stream = then_flow(input_stream)
        values: list[int] = []

        async for item in result_stream:
            values.append(item)
            # Side effects run after the yield, so they won't be visible until the next iteration
            if item == 1:
                assert side_effects == ["after_0"]  # after_0 ran after yielding 0
            elif item == 2:
                assert side_effects == [
                    "after_0",
                    "after_1",
                ]  # after_1 ran after yielding 1

        assert values == [0, 1, 2]
        assert side_effects == ["after_0", "after_1", "after_2"]

    @pytest.mark.asyncio
    async def test_then_with_async_function(self):
        """Test then with async side effect."""
        side_effects: list[int] = []

        async def async_record_after(x: int) -> None:
            await asyncio.sleep(0.001)
            side_effects.append(x)

        then_flow = then_stream(async_record_after)

        input_stream = async_range(2)
        result_stream = then_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [0, 1]
        assert side_effects == [0, 1]


class TestCatchAndContinueStream:
    """Tests for catch_and_continue_stream function."""

    @pytest.mark.asyncio
    async def test_catch_and_continue_basic(self):
        """Test basic catch and continue functionality."""
        errors: list[str] = []

        def error_handler(e: Exception) -> None:
            errors.append(str(e))

        catch_flow = catch_and_continue_stream(error_handler)  # type: ignore
        assert "catch_and_continue(error_handler)" in catch_flow.name

        async def flaky_stream():
            for i in [1]:
                yield i
            raise ValueError("Error 1")

        # Note: The current implementation catches exceptions during yielding,
        # not exceptions from the stream itself
        result_stream = catch_flow(flaky_stream())  # type: ignore
        values: list[int] = []

        with pytest.raises(ValueError):
            async for item in result_stream:  # type: ignore
                values.append(item)  # type: ignore

        assert values == [1]

    @pytest.mark.asyncio
    async def test_catch_and_continue_no_handler(self):
        """Test catch and continue without handler."""
        catch_flow = catch_and_continue_stream()  # type: ignore
        assert catch_flow.name == "catch_and_continue"

        input_stream = async_range(3)
        result_stream = catch_flow(input_stream)  # type: ignore
        values = [item async for item in result_stream]  # type: ignore
        assert values == [0, 1, 2]
