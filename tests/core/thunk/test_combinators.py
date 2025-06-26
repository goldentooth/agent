"""Comprehensive tests for thunk combinators."""

import asyncio
import pytest
import logging
from unittest.mock import Mock, patch
from goldentooth_agent.core.thunk import (
    Thunk,
    while_true,
    run_fold,
    compose,
    filter,
    map,
    flat_map,
    flat_map_ctx,
    log_ctx,
    identity,
    if_then,
    tap,
    delay,
    recover,
    memoize,
    repeat,
    retry,
    switch,
    race,
)


# Test fixtures
def sync_increment(x: int) -> int:
    """Increment a number."""
    return x + 1


def sync_double(x: int) -> int:
    """Double a number."""
    return x * 2


def sync_decrement(x: int) -> int:
    """Decrement a number."""
    return x - 1


async def async_increment(x: int) -> int:
    """Asynchronously increment a number."""
    await asyncio.sleep(0.01)
    return x + 1


async def async_double(x: int) -> int:
    """Asynchronously double a number."""
    await asyncio.sleep(0.01)
    return x * 2


def sync_exception_raiser(x: int) -> int:
    """Raise an exception."""
    raise ValueError(f"Error with {x}")


async def async_exception_raiser(x: int) -> int:
    """Asynchronously raise an exception."""
    await asyncio.sleep(0.01)
    raise ValueError(f"Async error with {x}")


# Predicate functions
def is_positive(x: int) -> bool:
    """Check if a number is positive."""
    return x > 0


def is_even(x: int) -> bool:
    """Check if a number is even."""
    return x % 2 == 0


def less_than_10(x: int) -> bool:
    """Check if a number is less than 10."""
    return x < 10


class TestRunFold:
    """Test cases for run_fold function."""

    @pytest.mark.asyncio
    async def test_run_fold_empty_list(self):
        """Test run_fold with an empty list of steps."""
        result = await run_fold(5, [])
        assert result == 5

    @pytest.mark.asyncio
    async def test_run_fold_single_step(self):
        """Test run_fold with a single step."""
        step = Thunk(sync_increment, name="increment")
        result = await run_fold(5, [step])
        assert result == 6

    @pytest.mark.asyncio
    async def test_run_fold_multiple_steps(self):
        """Test run_fold with multiple steps."""
        step1 = Thunk(sync_increment, name="increment")
        step2 = Thunk(sync_double, name="double")
        step3 = Thunk(sync_decrement, name="decrement")

        result = await run_fold(5, [step1, step2, step3])
        assert result == 11  # ((5 + 1) * 2) - 1 = 11

    @pytest.mark.asyncio
    async def test_run_fold_async_steps(self):
        """Test run_fold with async steps."""
        step1 = Thunk(async_increment, name="async_increment")
        step2 = Thunk(async_double, name="async_double")

        result = await run_fold(5, [step1, step2])
        assert result == 12  # (5 + 1) * 2 = 12


class TestCompose:
    """Test cases for compose function."""

    @pytest.mark.asyncio
    async def test_compose_sync_thunks(self):
        """Test composing two sync thunks."""
        first = Thunk(sync_increment, name="increment")
        second = Thunk(sync_double, name="double")

        composed = compose(first, second)
        assert composed.name == "increment ∘ double"

        result = await composed(5)
        assert result == 12  # (5 + 1) * 2 = 12

    @pytest.mark.asyncio
    async def test_compose_async_thunks(self):
        """Test composing two async thunks."""
        first = Thunk(async_increment, name="async_increment")
        second = Thunk(async_double, name="async_double")

        composed = compose(first, second)
        assert composed.name == "async_increment ∘ async_double"

        result = await composed(5)
        assert result == 12  # (5 + 1) * 2 = 12

    @pytest.mark.asyncio
    async def test_compose_mixed_thunks(self):
        """Test composing sync and async thunks."""
        first = Thunk(sync_increment, name="sync_increment")
        second = Thunk(async_double, name="async_double")

        composed = compose(first, second)
        result = await composed(5)
        assert result == 12  # (5 + 1) * 2 = 12


class TestFilter:
    """Test cases for filter combinator."""

    @pytest.mark.asyncio
    async def test_filter_passes(self):
        """Test filter when predicate passes."""
        filter_thunk = filter(is_positive)
        assert filter_thunk.name == "filter(is_positive)"

        result = await filter_thunk(5)
        assert result == 5

    @pytest.mark.asyncio
    async def test_filter_fails(self):
        """Test filter when predicate fails."""
        filter_thunk = filter(is_positive)

        result = await filter_thunk(-5)
        assert result is None

    @pytest.mark.asyncio
    async def test_filter_with_even_predicate(self):
        """Test filter with even number predicate."""
        filter_thunk = filter(is_even)

        result_even = await filter_thunk(4)
        assert result_even == 4

        result_odd = await filter_thunk(5)
        assert result_odd is None


class TestMapCombinator:
    """Test cases for map combinator."""

    @pytest.mark.asyncio
    async def test_map_decorator(self):
        """Test map decorator usage."""
        base_thunk = Thunk(sync_increment, name="increment")

        # Apply map decorator to the thunk directly
        mapped_thunk = map(lambda x: x * 10)(base_thunk)

        assert mapped_thunk.name == "increment.map(<lambda>)"

        result = await mapped_thunk(5)
        assert result == 60  # (5 + 1) * 10 = 60

    @pytest.mark.asyncio
    async def test_map_with_named_function(self):
        """Test map with a named function."""
        base_thunk = Thunk(sync_increment, name="increment")

        def multiply_by_3(x):
            return x * 3

        # Apply map decorator to the thunk directly
        mapped_thunk = map(multiply_by_3)(base_thunk)

        assert mapped_thunk.name == "increment.map(multiply_by_3)"

        result = await mapped_thunk(5)
        assert result == 18  # (5 + 1) * 3 = 18


class TestFlatMap:
    """Test cases for flat_map combinator."""

    @pytest.mark.asyncio
    async def test_flat_map_decorator(self):
        """Test flat_map decorator usage."""
        base_thunk = Thunk(sync_increment, name="increment")

        def create_double_thunk(x):
            return Thunk(lambda ctx: ctx * x, name=f"multiply_by_{x}")

        # Apply flat_map decorator to the thunk directly
        flat_mapped_thunk = flat_map(create_double_thunk)(base_thunk)

        assert flat_mapped_thunk.name == "increment.flat_map(create_double_thunk)"

        result = await flat_mapped_thunk(5)
        assert result == 30  # 5 * (5 + 1) = 30


class TestFlatMapCtx:
    """Test cases for flat_map_ctx combinator."""

    @pytest.mark.asyncio
    async def test_flat_map_ctx_decorator(self):
        """Test flat_map_ctx decorator with context access."""
        base_thunk = Thunk(sync_increment, name="increment")

        def create_ctx_aware_thunk(result, ctx):
            return Thunk(lambda _: result + ctx, name=f"add_ctx_{ctx}")

        # Apply flat_map_ctx decorator to the thunk directly
        ctx_mapped_thunk = flat_map_ctx(create_ctx_aware_thunk)(base_thunk)

        assert ctx_mapped_thunk.name == "increment.flat_map_ctx(create_ctx_aware_thunk)"

        result = await ctx_mapped_thunk(5)
        assert result == 11  # (5 + 1) + 5 = 11


class TestLogCtx:
    """Test cases for log_ctx combinator."""

    @pytest.mark.asyncio
    async def test_log_ctx_basic(self):
        """Test basic log_ctx functionality."""
        log_thunk = log_ctx("test_log")
        assert log_thunk.name == "log_ctx(test_log)"
        assert log_thunk.metadata["prefix"] == ""
        assert log_thunk.metadata["level"] == logging.DEBUG

        with patch("loguru.logger.log") as mock_log:
            result = await log_thunk(42)
            assert result == 42
            mock_log.assert_called_once_with(logging.DEBUG, "42")

    @pytest.mark.asyncio
    async def test_log_ctx_with_prefix(self):
        """Test log_ctx with prefix."""
        log_thunk = log_ctx("test_log", prefix="VALUE: ")

        with patch("loguru.logger.log") as mock_log:
            result = await log_thunk(42)
            assert result == 42
            mock_log.assert_called_once_with(logging.DEBUG, "VALUE: 42")

    @pytest.mark.asyncio
    async def test_log_ctx_with_level(self):
        """Test log_ctx with custom level."""
        log_thunk = log_ctx("test_log", level=logging.INFO)

        with patch("loguru.logger.log") as mock_log:
            result = await log_thunk(42)
            assert result == 42
            mock_log.assert_called_once_with(logging.INFO, "42")


class TestIdentity:
    """Test cases for identity combinator."""

    @pytest.mark.asyncio
    async def test_identity_basic(self):
        """Test basic identity functionality."""
        identity_thunk = identity()
        assert identity_thunk.name == "identity"

        result = await identity_thunk(42)
        assert result == 42

    @pytest.mark.asyncio
    async def test_identity_with_complex_object(self):
        """Test identity with complex objects."""
        identity_thunk = identity()

        test_dict = {"a": 1, "b": [2, 3, 4]}
        result = await identity_thunk(test_dict)
        assert result == test_dict
        assert result is test_dict  # Should be the same object


class TestIfThen:
    """Test cases for if_then combinator."""

    @pytest.mark.asyncio
    async def test_if_then_condition_true(self):
        """Test if_then when condition is true."""
        if_thunk = Thunk(sync_double, name="double")
        else_thunk = Thunk(sync_increment, name="increment")

        conditional = if_then(is_positive, if_thunk, else_thunk)
        assert conditional.name == "if_else(is_positive, double, increment)"

        result = await conditional(5)
        assert result == 10  # 5 * 2 = 10

    @pytest.mark.asyncio
    async def test_if_then_condition_false(self):
        """Test if_then when condition is false."""
        if_thunk = Thunk(sync_double, name="double")
        else_thunk = Thunk(sync_increment, name="increment")

        conditional = if_then(is_positive, if_thunk, else_thunk)

        result = await conditional(-5)
        assert result == -4  # -5 + 1 = -4

    @pytest.mark.asyncio
    async def test_if_then_with_default_else(self):
        """Test if_then with default identity else clause."""
        if_thunk = Thunk(sync_double, name="double")

        conditional = if_then(is_positive, if_thunk)

        # When condition is true
        result_true = await conditional(5)
        assert result_true == 10  # 5 * 2 = 10

        # When condition is false (should use identity)
        result_false = await conditional(-5)
        assert result_false == -5  # identity returns unchanged


class TestTapCombinator:
    """Test cases for tap combinator."""

    @pytest.mark.asyncio
    async def test_tap_decorator(self):
        """Test tap decorator usage."""
        side_effects = []

        async def log_result(x):
            side_effects.append(f"logged: {x}")

        base_thunk = Thunk(sync_increment, name="increment")

        # Apply tap decorator to the thunk directly
        tapped_thunk = tap(log_result)(base_thunk)

        assert tapped_thunk.name == "increment.tap(log_result)"

        result = await tapped_thunk(5)
        assert result == 6  # Original result preserved
        assert side_effects == ["logged: 6"]


class TestDelay:
    """Test cases for delay combinator."""

    @pytest.mark.asyncio
    async def test_delay_basic(self):
        """Test basic delay functionality."""
        delay_thunk = delay(0.01)
        assert delay_thunk.name == "delay(0.01)"

        start_time = asyncio.get_event_loop().time()
        result = await delay_thunk(42)
        end_time = asyncio.get_event_loop().time()

        assert result == 42
        assert (end_time - start_time) >= 0.01


class TestRecover:
    """Test cases for recover combinator."""

    @pytest.mark.asyncio
    async def test_recover_no_exception(self):
        """Test recover when no exception occurs."""

        async def error_handler(exc, ctx):
            return -1

        base_thunk = Thunk(sync_increment, name="increment")

        # Apply recover decorator to the thunk directly
        recovered_thunk = recover(error_handler)(base_thunk)

        assert recovered_thunk.name == "increment.recover(error_handler)"

        result = await recovered_thunk(5)
        assert result == 6  # Normal execution

    @pytest.mark.asyncio
    async def test_recover_with_exception(self):
        """Test recover when exception occurs."""

        async def error_handler(exc, ctx):
            assert isinstance(exc, ValueError)
            return ctx * -1  # Return negative of input

        base_thunk = Thunk(sync_exception_raiser, name="error")

        # Apply recover decorator to the thunk directly
        recovered_thunk = recover(error_handler)(base_thunk)

        result = await recovered_thunk(5)
        assert result == -5  # Error handler result

    @pytest.mark.asyncio
    async def test_recover_async_handler(self):
        """Test recover with async error handler."""

        async def async_error_handler(exc, ctx):
            await asyncio.sleep(0.01)
            return 999

        base_thunk = Thunk(sync_exception_raiser, name="error")

        # Apply recover decorator to the thunk directly
        recovered_thunk = recover(async_error_handler)(base_thunk)

        result = await recovered_thunk(5)
        assert result == 999


class TestMemoize:
    """Test cases for memoize combinator."""

    @pytest.mark.asyncio
    async def test_memoize_basic(self):
        """Test basic memoization functionality."""
        call_count = 0

        async def expensive_function(x):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)
            return x * 2

        memoized = memoize(expensive_function)
        assert memoized.name == "memoize(expensive_function)"

        # First call
        result1 = await memoized(5)
        assert result1 == 10
        assert call_count == 1

        # Second call with same input (should use cache)
        result2 = await memoized(5)
        assert result2 == 10
        assert call_count == 1  # Should not increase

        # Call with different input
        result3 = await memoized(10)
        assert result3 == 20
        assert call_count == 2  # Should increase

    @pytest.mark.asyncio
    async def test_memoize_different_instances(self):
        """Test that different memoize instances have separate caches."""

        async def test_func(x):
            return x * 2

        memoized1 = memoize(test_func)
        memoized2 = memoize(test_func)

        # They should be different thunks with separate caches
        assert memoized1 is not memoized2


class TestWhileTrue:
    """Test cases for while_true combinator."""

    @pytest.mark.asyncio
    async def test_while_true_basic(self):
        """Test basic while_true functionality."""
        body = Thunk(sync_increment, name="increment")

        while_thunk = while_true(less_than_10, body)
        assert while_thunk.name == "while_true(less_than_10, increment)"

        result = await while_thunk(5)
        assert result == 10  # Should increment until >= 10

    @pytest.mark.asyncio
    async def test_while_true_no_iterations(self):
        """Test while_true when condition is initially false."""
        body = Thunk(sync_increment, name="increment")

        while_thunk = while_true(less_than_10, body)

        result = await while_thunk(15)
        assert result == 15  # Should not execute body

    @pytest.mark.asyncio
    async def test_while_true_async_body(self):
        """Test while_true with async body."""
        body = Thunk(async_increment, name="async_increment")

        while_thunk = while_true(less_than_10, body)

        result = await while_thunk(8)
        assert result == 10


class TestRepeat:
    """Test cases for repeat combinator."""

    @pytest.mark.asyncio
    async def test_repeat_basic(self):
        """Test basic repeat functionality."""
        body = Thunk(sync_increment, name="increment")

        repeat_thunk = repeat(3, body)
        assert repeat_thunk.name == "repeat(3, increment)"

        result = await repeat_thunk(5)
        assert result == 8  # 5 + 1 + 1 + 1 = 8

    @pytest.mark.asyncio
    async def test_repeat_zero_times(self):
        """Test repeat with zero iterations."""
        body = Thunk(sync_increment, name="increment")

        repeat_thunk = repeat(0, body)

        result = await repeat_thunk(5)
        assert result == 5  # Should not execute body

    @pytest.mark.asyncio
    async def test_repeat_async_body(self):
        """Test repeat with async body."""
        body = Thunk(async_increment, name="async_increment")

        repeat_thunk = repeat(2, body)

        result = await repeat_thunk(5)
        assert result == 7  # 5 + 1 + 1 = 7


class TestRetry:
    """Test cases for retry combinator."""

    @pytest.mark.asyncio
    async def test_retry_success_first_try(self):
        """Test retry when first attempt succeeds."""
        thunk = Thunk(sync_increment, name="increment")

        retry_thunk = retry(3, thunk)
        assert retry_thunk.name == "retry(3, increment)"

        result = await retry_thunk(5)
        assert result == 6

    @pytest.mark.asyncio
    async def test_retry_success_after_failures(self):
        """Test retry when later attempts succeed."""
        attempt_count = 0

        def flaky_function(x):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError("Temporary failure")
            return x + 1

        thunk = Thunk(flaky_function, name="flaky")
        retry_thunk = retry(3, thunk)

        result = await retry_thunk(5)
        assert result == 6
        assert attempt_count == 3

    @pytest.mark.asyncio
    async def test_retry_all_attempts_fail(self):
        """Test retry when all attempts fail."""
        thunk = Thunk(sync_exception_raiser, name="error")
        retry_thunk = retry(3, thunk)

        with pytest.raises(ValueError, match="Error with 5"):
            await retry_thunk(5)

    @pytest.mark.asyncio
    async def test_retry_async_thunk(self):
        """Test retry with async thunk."""
        attempt_count = 0

        async def async_flaky_function(x):
            nonlocal attempt_count
            attempt_count += 1
            await asyncio.sleep(0.01)
            if attempt_count < 2:
                raise ValueError("Temporary failure")
            return x + 1

        thunk = Thunk(async_flaky_function, name="async_flaky")
        retry_thunk = retry(3, thunk)

        result = await retry_thunk(5)
        assert result == 6
        assert attempt_count == 2


class TestSwitch:
    """Test cases for switch combinator."""

    @pytest.mark.asyncio
    async def test_switch_basic(self):
        """Test basic switch functionality."""

        def selector(x):
            return "even" if x % 2 == 0 else "odd"

        cases = {
            "even": Thunk(sync_double, name="double"),
            "odd": Thunk(sync_increment, name="increment"),
        }

        switch_thunk = switch(selector, cases)
        assert switch_thunk.name == "switch(selector, ['even', 'odd'], None)"

        # Test even case
        result_even = await switch_thunk(4)
        assert result_even == 8  # 4 * 2 = 8

        # Test odd case
        result_odd = await switch_thunk(5)
        assert result_odd == 6  # 5 + 1 = 6

    @pytest.mark.asyncio
    async def test_switch_with_default(self):
        """Test switch with default case."""

        def selector(x):
            return "positive" if x > 0 else "negative" if x < 0 else "zero"

        cases = {
            "positive": Thunk(sync_double, name="double"),
        }
        default = Thunk(sync_increment, name="increment")

        switch_thunk = switch(selector, cases, default)
        assert switch_thunk.name == "switch(selector, ['positive'], increment)"

        # Test positive case
        result_positive = await switch_thunk(5)
        assert result_positive == 10  # 5 * 2 = 10

        # Test default case
        result_default = await switch_thunk(-5)
        assert result_default == -4  # -5 + 1 = -4

    @pytest.mark.asyncio
    async def test_switch_no_case_no_default(self):
        """Test switch when no case matches and no default."""

        def selector(x):
            return "unknown"

        cases = {
            "known": Thunk(sync_double, name="double"),
        }

        switch_thunk = switch(selector, cases)

        with pytest.raises(KeyError, match="No case for key: unknown"):
            await switch_thunk(5)


class TestRace:
    """Test cases for race combinator."""

    @pytest.mark.asyncio
    async def test_race_first_succeeds(self):
        """Test race when first thunk succeeds."""
        thunk1 = Thunk(sync_increment, name="increment")
        thunk2 = Thunk(sync_double, name="double")

        race_thunk = race([thunk1, thunk2])
        assert race_thunk.name == "race(increment, double)"

        result = await race_thunk(5)
        assert result == 6  # First thunk result

    @pytest.mark.asyncio
    async def test_race_first_fails_second_succeeds(self):
        """Test race when first thunk fails but second succeeds."""
        thunk1 = Thunk(sync_exception_raiser, name="error")
        thunk2 = Thunk(sync_increment, name="increment")

        race_thunk = race([thunk1, thunk2])

        result = await race_thunk(5)
        assert result == 6  # Second thunk result

    @pytest.mark.asyncio
    async def test_race_all_fail(self):
        """Test race when all thunks fail."""
        thunk1 = Thunk(sync_exception_raiser, name="error1")
        thunk2 = Thunk(sync_exception_raiser, name="error2")

        race_thunk = race([thunk1, thunk2])

        with pytest.raises(ValueError, match="Error with 5"):
            await race_thunk(5)

    @pytest.mark.asyncio
    async def test_race_empty_list(self):
        """Test race with empty list of thunks."""
        race_thunk = race([])

        with pytest.raises(RuntimeError, match="All thunks failed"):
            await race_thunk(5)

    @pytest.mark.asyncio
    async def test_race_async_thunks(self):
        """Test race with async thunks."""
        thunk1 = Thunk(async_exception_raiser, name="async_error")
        thunk2 = Thunk(async_increment, name="async_increment")

        race_thunk = race([thunk1, thunk2])

        result = await race_thunk(5)
        assert result == 6  # Second thunk result
