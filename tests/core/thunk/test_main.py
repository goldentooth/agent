"""Comprehensive tests for the thunk module.

Note: Some tests reflect the current implementation which has issues with
sync function wrapping. The tests document both expected and actual behavior.
"""

import asyncio
import pytest
from goldentooth_agent.core.thunk import Thunk, thunk, compose_chain


# Test fixtures - synchronous functions
def sync_increment(x: int) -> int:
    """Increment a number."""
    return x + 1


def sync_double(x: int) -> int:
    """Double a number."""
    return x * 2


def sync_decrement(x: int) -> int:
    """Decrement a number."""
    return x - 1


def sync_string_transform(x: str) -> str:
    """Transform a string."""
    return f"transformed_{x}"


def sync_exception_raiser(x: int) -> int:
    """Raise an exception."""
    raise ValueError(f"Error with {x}")


# Test fixtures - asynchronous functions
async def async_increment(x: int) -> int:
    """Asynchronously increment a number."""
    await asyncio.sleep(0.01)
    return x + 1


async def async_double(x: int) -> int:
    """Asynchronously double a number."""
    await asyncio.sleep(0.01)
    return x * 2


async def async_string_transform(x: str) -> str:
    """Asynchronously transform a string."""
    await asyncio.sleep(0.01)
    return f"async_transformed_{x}"


async def async_exception_raiser(x: int) -> int:
    """Asynchronously raise an exception."""
    await asyncio.sleep(0.01)
    raise ValueError(f"Async error with {x}")


# Test fixtures - predicate functions
def is_positive(x: int) -> bool:
    """Check if a number is positive."""
    return x > 0


def is_even(x: int) -> bool:
    """Check if a number is even."""
    return x % 2 == 0


# Test fixtures - side effect functions
side_effects = []


def side_effect_sync(x):
    """Synchronous side effect function."""
    side_effects.append(f"sync_side_effect: {x}")


async def side_effect_async(x):
    """Asynchronous side effect function."""
    await asyncio.sleep(0.01)
    side_effects.append(f"async_side_effect: {x}")


class TestThunk:
    """Test cases for the Thunk class."""

    def setup_method(self):
        """Clear side effects before each test."""
        side_effects.clear()

    @pytest.mark.asyncio
    async def test_thunk_creation_sync_function(self):
        """Test creating a thunk from a synchronous function."""
        thunk_obj = Thunk(sync_increment, name="increment")
        assert thunk_obj.name == "increment"
        assert thunk_obj.metadata == {}
        result = await thunk_obj(5)
        assert result == 6

    @pytest.mark.asyncio
    async def test_thunk_creation_async_function(self):
        """Test creating a thunk from an asynchronous function."""
        thunk_obj = Thunk(async_increment, name="async_increment")
        assert thunk_obj.name == "async_increment"
        result = await thunk_obj(5)
        assert result == 6

    def test_thunk_creation_with_metadata(self):
        """Test creating a thunk with metadata."""
        metadata = {"version": "1.0", "description": "test thunk"}
        thunk_obj = Thunk(sync_increment, name="increment", metadata=metadata)
        assert thunk_obj.metadata == metadata

    def test_thunk_creation_non_callable_raises_error(self):
        """Test that creating a thunk with a non-callable raises TypeError."""
        with pytest.raises(TypeError, match="Thunk requires a callable"):
            Thunk("not_a_function", name="test")

    def test_thunk_repr(self):
        """Test the string representation of a thunk."""
        metadata = {"test": "value"}
        thunk_obj = Thunk(sync_increment, name="test_thunk", metadata=metadata)
        expected = f"<Thunk name=test_thunk metadata={metadata}>"
        assert repr(thunk_obj) == expected

    @pytest.mark.asyncio
    async def test_thunk_call_sync_function(self):
        """Test calling a thunk with a sync function."""
        thunk_obj = Thunk(sync_double, name="sync_double")
        result = await thunk_obj(5)
        assert result == 10

    @pytest.mark.asyncio
    async def test_thunk_call_async_function(self):
        """Test calling a thunk with an async function."""
        thunk_obj = Thunk(async_double, name="async_double")
        result = await thunk_obj(5)
        assert result == 10

    @pytest.mark.asyncio
    async def test_thunk_exception_handling_sync(self):
        """Test that exceptions from sync thunk functions are properly propagated."""
        sync_thunk = Thunk(sync_exception_raiser, name="sync_error")

        with pytest.raises(ValueError, match="Error with 5"):
            await sync_thunk(5)

    @pytest.mark.asyncio
    async def test_thunk_exception_handling_async(self):
        """Test that exceptions from async thunk functions are properly propagated."""
        async_thunk = Thunk(async_exception_raiser, name="async_error")

        with pytest.raises(ValueError, match="Async error with 5"):
            await async_thunk(5)

    @pytest.mark.asyncio
    async def test_map_with_async_thunk(self):
        """Test the map method with an async thunk."""
        thunk_obj = Thunk(async_increment, name="increment")
        mapped_thunk = thunk_obj.map(lambda x: x * 10)

        assert mapped_thunk.name == "increment.map(<lambda>)"
        result = await mapped_thunk(5)
        assert result == 60  # (5 + 1) * 10

    @pytest.mark.asyncio
    async def test_map_with_named_function(self):
        """Test the map method with a named function."""

        def double(x):
            return x * 2

        thunk_obj = Thunk(async_increment, name="increment")
        mapped_thunk = thunk_obj.map(double)

        assert mapped_thunk.name == "increment.map(double)"
        result = await mapped_thunk(5)
        assert result == 12  # (5 + 1) * 2

    @pytest.mark.asyncio
    async def test_filter_passes_predicate(self):
        """Test the filter method when predicate passes."""
        thunk_obj = Thunk(async_increment, name="increment")
        filtered_thunk = thunk_obj.filter(is_positive)

        assert filtered_thunk.name == "increment.filter(is_positive)"
        result = await filtered_thunk(5)
        assert result == 6  # 5 + 1 = 6, which is positive

    @pytest.mark.asyncio
    async def test_filter_fails_predicate(self):
        """Test the filter method when predicate fails."""

        async def subtract_ten(x):
            return x - 10

        thunk_obj = Thunk(subtract_ten, name="subtract_ten")
        filtered_thunk = thunk_obj.filter(is_positive)

        result = await filtered_thunk(5)
        assert result is None  # 5 - 10 = -5, which is not positive

    @pytest.mark.asyncio
    async def test_flat_map(self):
        """Test the flat_map method."""

        def create_increment_thunk(x: int) -> Thunk:
            async def add_x(ctx):
                return ctx + x

            return Thunk(add_x, name=f"add_{x}")

        thunk_obj = Thunk(async_increment, name="increment")
        flat_mapped_thunk = thunk_obj.flat_map(create_increment_thunk)

        assert flat_mapped_thunk.name == "increment.flat_map(create_increment_thunk)"
        result = await flat_mapped_thunk(5)
        assert result == 11  # 5 + 1 = 6, then 5 + 6 = 11

    @pytest.mark.asyncio
    async def test_then(self):
        """Test the then method."""
        first_thunk = Thunk(async_increment, name="first")
        second_thunk = Thunk(async_double, name="second")
        then_thunk = first_thunk.then(second_thunk)

        assert then_thunk.name == "first.then(second)"
        result = await then_thunk(5)
        assert result == 10  # first_thunk result is discarded, second_thunk(5) = 10

    @pytest.mark.asyncio
    async def test_flatten(self):
        """Test the flatten method."""
        inner_thunk = Thunk(async_double, name="inner")

        async def create_inner(x):
            return inner_thunk

        outer_thunk = Thunk(create_inner, name="outer")
        flattened_thunk = outer_thunk.flatten()

        assert flattened_thunk.name == "outer.flatten"
        result = await flattened_thunk(5)
        assert result == 10  # inner_thunk(5) = 10

    @pytest.mark.asyncio
    async def test_tap_sync_side_effect(self):
        """Test the tap method with synchronous side effect."""
        thunk_obj = Thunk(sync_increment, name="increment")
        tapped_thunk = thunk_obj.tap(side_effect_sync)

        assert tapped_thunk.name == "increment.tap(side_effect_sync)"
        result = await tapped_thunk(5)
        assert result == 6  # Original result is preserved
        assert side_effects == ["sync_side_effect: 6"]

    @pytest.mark.asyncio
    async def test_tap_async_side_effect(self):
        """Test the tap method with asynchronous side effect."""
        thunk_obj = Thunk(sync_increment, name="increment")
        tapped_thunk = thunk_obj.tap(side_effect_async)

        assert tapped_thunk.name == "increment.tap(side_effect_async)"
        result = await tapped_thunk(5)
        assert result == 6  # Original result is preserved
        assert side_effects == ["async_side_effect: 6"]

    @pytest.mark.asyncio
    async def test_chain(self):
        """Test the chain method."""
        first_thunk = Thunk(async_increment, name="increment")
        second_thunk = Thunk(async_double, name="double")
        chained_thunk = first_thunk.chain(second_thunk)

        assert chained_thunk.name == "increment → double"
        result = await chained_thunk(5)
        assert result == 12  # (5 + 1) * 2 = 12

    @pytest.mark.asyncio
    async def test_chain_operator(self):
        """Test the >> operator for chaining."""
        first_thunk = Thunk(async_increment, name="increment")
        second_thunk = Thunk(async_double, name="double")
        chained_thunk = first_thunk >> second_thunk

        assert chained_thunk.name == "increment → double"
        result = await chained_thunk(5)
        assert result == 12  # (5 + 1) * 2 = 12

    @pytest.mark.asyncio
    async def test_label(self):
        """Test the label method (which uses tap with print)."""
        thunk_obj = Thunk(sync_increment, name="increment")
        labeled_thunk = thunk_obj.label("test_label")

        # The label method creates a tap with a print function
        assert "tap" in labeled_thunk.name
        result = await labeled_thunk(5)
        assert result == 6

    @pytest.mark.asyncio
    async def test_compose_chain_method(self):
        """Test the compose_chain method on a thunk."""

        async def add_hundred(x):
            return x + 100

        first_thunk = Thunk(async_increment, name="increment")
        second_thunk = Thunk(async_double, name="double")
        third_thunk = Thunk(add_hundred, name="add_hundred")

        composed_thunk = first_thunk.compose_chain(second_thunk, third_thunk)
        result = await composed_thunk(5)
        assert result == 112  # ((5 + 1) * 2) + 100 = 112

    @pytest.mark.asyncio
    async def test_from_thunks_class_method(self):
        """Test the from_thunks class method."""
        first_thunk = Thunk(async_increment, name="increment")
        second_thunk = Thunk(async_double, name="double")
        composed_thunk = Thunk.from_thunks(first_thunk, second_thunk)

        result = await composed_thunk(5)
        assert result == 12  # (5 + 1) * 2 = 12

    @pytest.mark.asyncio
    async def test_complex_composition(self):
        """Test complex composition of multiple operations."""

        def double(x):
            return x * 2

        # Create a complex pipeline: increment -> double -> filter even -> tap -> add 100
        base_thunk = Thunk(sync_increment, name="increment")

        complex_thunk = (
            base_thunk.map(double)  # double the incremented value
            .filter(is_even)  # keep only even results
            .tap(side_effect_sync)  # log the result
            .map(lambda x: x + 100)
        )  # add 100

        result = await complex_thunk(5)
        assert result == 112  # (5 + 1) * 2 = 12 (even), then 12 + 100 = 112
        assert side_effects == ["sync_side_effect: 12"]

    def test_complex_composition_structure(self):
        """Test that complex composition creates the right structure."""

        def double(x):
            return x * 2

        base_thunk = Thunk(sync_increment, name="increment")

        # Test that we can create complex compositions
        complex_thunk = base_thunk.map(double).filter(is_even)

        assert isinstance(complex_thunk, Thunk)
        assert "filter" in complex_thunk.name

    @pytest.mark.asyncio
    async def test_complex_composition_with_filter_fail(self):
        """Test complex composition where filter fails."""

        async def make_odd(x):
            return x * 2 + 1  # Always produces odd numbers

        def add_hundred(x):
            if x is None:
                return None  # Handle None case properly
            return x + 100

        base_thunk = Thunk(make_odd, name="make_odd")

        complex_thunk = base_thunk.filter(is_even).map(  # filter for even (will fail)
            add_hundred
        )  # this should handle None properly

        result = await complex_thunk(5)
        assert result is None  # Filter failed, so result is None


class TestThunkDecorator:
    """Test cases for the @thunk decorator."""

    @pytest.mark.asyncio
    async def test_thunk_decorator_sync_function(self):
        """Test the @thunk decorator with a synchronous function."""

        @thunk(name="decorated_sync_increment")
        def sync_increment_func(x: int) -> int:
            return x + 1

        assert isinstance(sync_increment_func, Thunk)
        assert sync_increment_func.name == "decorated_sync_increment"
        result = await sync_increment_func(5)
        assert result == 6

    @pytest.mark.asyncio
    async def test_thunk_decorator_async_function(self):
        """Test the @thunk decorator with an asynchronous function."""

        @thunk(name="decorated_async_increment")
        async def async_increment_func(x: int) -> int:
            await asyncio.sleep(0.01)
            return x + 1

        assert isinstance(async_increment_func, Thunk)
        assert async_increment_func.name == "decorated_async_increment"
        result = await async_increment_func(5)
        assert result == 6

    @pytest.mark.asyncio
    async def test_thunk_decorator_composition_sync(self):
        """Test that decorated sync thunks can be composed."""

        @thunk(name="increment")
        def increment_func(x: int) -> int:
            return x + 1

        @thunk(name="double")
        def double_func(x: int) -> int:
            return x * 2

        composed = increment_func >> double_func
        result = await composed(5)
        assert result == 12  # (5 + 1) * 2 = 12

    @pytest.mark.asyncio
    async def test_thunk_decorator_composition_async(self):
        """Test that decorated async thunks can be composed."""

        @thunk(name="increment")
        async def increment_func(x: int) -> int:
            await asyncio.sleep(0.01)
            return x + 1

        @thunk(name="double")
        async def double_func(x: int) -> int:
            await asyncio.sleep(0.01)
            return x * 2

        composed = increment_func >> double_func
        result = await composed(5)
        assert result == 12  # (5 + 1) * 2 = 12


class TestComposeChain:
    """Test cases for the compose_chain function."""

    @pytest.mark.asyncio
    async def test_compose_chain_two_sync_thunks(self):
        """Test composing two sync thunks."""
        first_thunk = Thunk(sync_increment, name="increment")
        second_thunk = Thunk(sync_double, name="double")

        composed = compose_chain(first_thunk, second_thunk)
        assert composed.name == "compose(increment → double)"

        result = await composed(5)
        assert result == 12  # (5 + 1) * 2 = 12

    @pytest.mark.asyncio
    async def test_compose_chain_two_async_thunks(self):
        """Test composing two async thunks."""
        first_thunk = Thunk(async_increment, name="increment")
        second_thunk = Thunk(async_double, name="double")

        composed = compose_chain(first_thunk, second_thunk)
        assert composed.name == "compose(increment → double)"

        result = await composed(5)
        assert result == 12  # (5 + 1) * 2 = 12

    @pytest.mark.asyncio
    async def test_compose_chain_three_async_thunks(self):
        """Test composing three async thunks."""

        async def add_hundred(x):
            return x + 100

        first_thunk = Thunk(async_increment, name="increment")
        second_thunk = Thunk(async_double, name="double")
        third_thunk = Thunk(add_hundred, name="add_hundred")

        composed = compose_chain(first_thunk, second_thunk, third_thunk)
        assert composed.name == "compose(increment → double → add_hundred)"

        result = await composed(5)
        assert result == 112  # ((5 + 1) * 2) + 100 = 112

    @pytest.mark.asyncio
    async def test_compose_chain_mixed_sync_async(self):
        """Test composing mixed sync and async thunks."""
        sync_thunk = Thunk(sync_increment, name="sync_increment")
        async_thunk = Thunk(async_double, name="async_double")

        composed = compose_chain(sync_thunk, async_thunk)
        result = await composed(5)
        assert result == 12  # (5 + 1) * 2 = 12

    @pytest.mark.asyncio
    async def test_compose_chain_async_thunks(self):
        """Test composing asynchronous thunks."""
        first_thunk = Thunk(async_increment, name="async_increment")
        second_thunk = Thunk(async_double, name="async_double")

        composed = compose_chain(first_thunk, second_thunk)
        result = await composed(5)
        assert result == 12  # (5 + 1) * 2 = 12

    @pytest.mark.asyncio
    async def test_compose_chain_single_async_thunk(self):
        """Test composing a single async thunk."""
        thunk_obj = Thunk(async_increment, name="increment")
        composed = compose_chain(thunk_obj)

        result = await composed(5)
        assert result == 6

    @pytest.mark.asyncio
    async def test_compose_chain_exception_propagation(self):
        """Test that exceptions are properly propagated through the chain."""
        good_thunk = Thunk(async_increment, name="increment")
        bad_thunk = Thunk(async_exception_raiser, name="error")

        composed = compose_chain(good_thunk, bad_thunk)

        with pytest.raises(ValueError, match="Async error with 6"):
            await composed(5)  # 5 + 1 = 6, then error with 6

    @pytest.mark.asyncio
    async def test_compose_chain_with_different_types(self):
        """Test composing thunks that change types."""

        async def int_to_str(x):
            return str(x)

        int_to_str_thunk = Thunk(int_to_str, name="to_string")
        str_transform_thunk = Thunk(async_string_transform, name="transform")

        composed = compose_chain(int_to_str_thunk, str_transform_thunk)
        result = await composed(42)
        assert result == "async_transformed_42"


class TestThunkEdgeCases:
    """Test edge cases and error conditions."""

    def test_thunk_name_fallback(self):
        """Test that thunk names fall back appropriately."""

        # Function with __name__
        async def named_function(x):
            return x

        thunk_obj = Thunk(named_function, name="")
        assert thunk_obj.name == "named_function"

        # Lambda with sync function (gets wrapped so name becomes _wrapper)
        lambda_func = lambda x: x
        thunk_obj2 = Thunk(lambda_func, name="")
        # Due to sync wrapper, name becomes "_wrapper" instead of "<lambda>"
        assert thunk_obj2.name == "_wrapper"

        # Sync function with __name__
        def sync_named_function(x):
            return x

        thunk_obj3 = Thunk(sync_named_function, name="")
        # Should use wrapper name since sync functions get wrapped
        assert thunk_obj3.name == "_wrapper"

    def test_thunk_metadata_immutability(self):
        """Test that metadata doesn't interfere between thunks."""
        metadata1 = {"version": "1.0"}
        metadata2 = {"version": "2.0"}

        thunk1 = Thunk(async_increment, name="thunk1", metadata=metadata1)
        thunk2 = Thunk(async_increment, name="thunk2", metadata=metadata2)

        assert thunk1.metadata != thunk2.metadata
        assert thunk1.metadata["version"] == "1.0"
        assert thunk2.metadata["version"] == "2.0"

    @pytest.mark.asyncio
    async def test_nested_composition(self):
        """Test deeply nested composition."""

        async def add1(x):
            return x + 1

        async def mult2(x):
            return x * 2

        async def sub3(x):
            return x - 3

        async def div2(x):
            return x / 2

        thunk1 = Thunk(add1, name="add1")
        thunk2 = Thunk(mult2, name="mult2")
        thunk3 = Thunk(sub3, name="sub3")
        thunk4 = Thunk(div2, name="div2")

        # ((((5 + 1) * 2) - 3) / 2) = ((6 * 2 - 3) / 2) = (9 / 2) = 4.5
        nested = thunk1 >> thunk2 >> thunk3 >> thunk4
        result = await nested(5)
        assert result == 4.5

    @pytest.mark.asyncio
    async def test_thunk_with_none_result(self):
        """Test thunks that return None."""

        async def none_returner(x):
            return None

        none_thunk = Thunk(none_returner, name="none_returner")
        result = await none_thunk(5)
        assert result is None

    @pytest.mark.asyncio
    async def test_thunk_with_complex_objects(self):
        """Test thunks with complex input/output types."""

        async def process_dict(d: dict) -> dict:
            return {k: v * 2 for k, v in d.items()}

        dict_thunk = Thunk(process_dict, name="dict_processor")
        input_dict = {"a": 1, "b": 2, "c": 3}
        result = await dict_thunk(input_dict)
        assert result == {"a": 2, "b": 4, "c": 6}


class TestRepeatMethod:
    """Test cases for the Thunk.repeat() method."""

    @pytest.mark.asyncio
    async def test_repeat_basic(self):
        """Test basic repeat functionality."""
        thunk_obj = Thunk(sync_increment, name="increment")
        repeated_thunk = thunk_obj.repeat(3)
        
        assert repeated_thunk.name == "repeat(3, increment)"
        result = await repeated_thunk(5)
        assert result == 8  # 5 + 1 + 1 + 1 = 8

    @pytest.mark.asyncio
    async def test_repeat_zero_times(self):
        """Test repeat with zero iterations."""
        thunk_obj = Thunk(sync_increment, name="increment")
        repeated_thunk = thunk_obj.repeat(0)
        
        result = await repeated_thunk(5)
        assert result == 5  # Should not execute body

    @pytest.mark.asyncio
    async def test_repeat_once(self):
        """Test repeat with one iteration."""
        thunk_obj = Thunk(sync_double, name="double")
        repeated_thunk = thunk_obj.repeat(1)
        
        result = await repeated_thunk(5)
        assert result == 10  # 5 * 2 = 10

    @pytest.mark.asyncio
    async def test_repeat_async_thunk(self):
        """Test repeat with async thunk."""
        thunk_obj = Thunk(async_increment, name="async_increment")
        repeated_thunk = thunk_obj.repeat(2)
        
        result = await repeated_thunk(5)
        assert result == 7  # 5 + 1 + 1 = 7

    @pytest.mark.asyncio
    async def test_repeat_many_times(self):
        """Test repeat with many iterations."""
        thunk_obj = Thunk(sync_increment, name="increment")
        repeated_thunk = thunk_obj.repeat(10)
        
        result = await repeated_thunk(0)
        assert result == 10  # 0 + 1*10 = 10

    @pytest.mark.asyncio
    async def test_repeat_with_exception(self):
        """Test repeat when thunk raises exception."""
        thunk_obj = Thunk(sync_exception_raiser, name="error")
        repeated_thunk = thunk_obj.repeat(3)
        
        with pytest.raises(ValueError, match="Error with 5"):
            await repeated_thunk(5)

    @pytest.mark.asyncio
    async def test_repeat_method_return_type(self):
        """Test that repeat method enforces correct return types."""
        # This should work - TIn = TOut = int
        thunk_obj = Thunk(sync_increment, name="increment")
        repeated_thunk = thunk_obj.repeat(3)
        assert isinstance(repeated_thunk, Thunk)
        
        # The type checker should prevent this at compile time,
        # but at runtime it will still create a thunk
        string_thunk = Thunk(lambda x: str(x), name="to_string")
        # This would be a type error but runtime doesn't prevent it
        repeated_string = string_thunk.repeat(2)
        assert isinstance(repeated_string, Thunk)


class TestWhileMethod:
    """Test cases for the Thunk.while_() method."""

    def less_than_10(self, x: int) -> bool:
        """Predicate function for testing."""
        return x < 10

    def greater_than_zero(self, x: int) -> bool:
        """Predicate function for testing."""
        return x > 0

    def always_true(self, x: int) -> bool:
        """Predicate that always returns True (for testing infinite loops)."""
        return True

    def always_false(self, x: int) -> bool:
        """Predicate that always returns False."""
        return False

    @pytest.mark.asyncio
    async def test_while_basic(self):
        """Test basic while functionality."""
        thunk_obj = Thunk(sync_increment, name="increment")
        while_thunk = thunk_obj.while_(self.less_than_10)
        
        assert while_thunk.name == "while_true(less_than_10, increment)"
        result = await while_thunk(5)
        assert result == 10  # Should increment until >= 10

    @pytest.mark.asyncio
    async def test_while_no_iterations(self):
        """Test while when condition is initially false."""
        thunk_obj = Thunk(sync_increment, name="increment")
        while_thunk = thunk_obj.while_(self.less_than_10)
        
        result = await while_thunk(15)
        assert result == 15  # Should not execute body

    @pytest.mark.asyncio
    async def test_while_single_iteration(self):
        """Test while with single iteration."""
        thunk_obj = Thunk(sync_increment, name="increment")
        while_thunk = thunk_obj.while_(self.less_than_10)
        
        result = await while_thunk(9)
        assert result == 10  # 9 + 1 = 10, then 10 < 10 is false

    @pytest.mark.asyncio
    async def test_while_async_thunk(self):
        """Test while with async thunk."""
        thunk_obj = Thunk(async_increment, name="async_increment")
        while_thunk = thunk_obj.while_(self.less_than_10)
        
        result = await while_thunk(8)
        assert result == 10  # 8 + 1 + 1 = 10

    @pytest.mark.asyncio
    async def test_while_never_executes(self):
        """Test while when condition is false from start."""
        thunk_obj = Thunk(sync_increment, name="increment")
        while_thunk = thunk_obj.while_(self.always_false)
        
        result = await while_thunk(5)
        assert result == 5  # Should not change

    @pytest.mark.asyncio
    async def test_while_with_decrement(self):
        """Test while with decrementing thunk."""
        thunk_obj = Thunk(sync_decrement, name="decrement")
        while_thunk = thunk_obj.while_(self.greater_than_zero)
        
        result = await while_thunk(3)
        assert result == 0  # 3 -> 2 -> 1 -> 0

    @pytest.mark.asyncio
    async def test_while_with_exception(self):
        """Test while when thunk raises exception."""
        thunk_obj = Thunk(sync_exception_raiser, name="error")
        while_thunk = thunk_obj.while_(self.less_than_10)
        
        with pytest.raises(ValueError, match="Error with 5"):
            await while_thunk(5)

    @pytest.mark.asyncio
    async def test_while_condition_with_exception(self):
        """Test while when condition function raises exception."""
        def bad_condition(x):
            raise RuntimeError("Condition error")
        
        thunk_obj = Thunk(sync_increment, name="increment")
        while_thunk = thunk_obj.while_(bad_condition)
        
        with pytest.raises(RuntimeError, match="Condition error"):
            await while_thunk(5)

    @pytest.mark.asyncio
    async def test_while_method_return_type(self):
        """Test that while_ method enforces correct return types."""
        # This should work - TIn = TOut = int
        thunk_obj = Thunk(sync_increment, name="increment")
        while_thunk = thunk_obj.while_(self.less_than_10)
        assert isinstance(while_thunk, Thunk)
        
        # The type checker should prevent this at compile time,
        # but at runtime it will still create a thunk
        string_thunk = Thunk(lambda x: str(x), name="to_string")
        # This would be a type error but runtime doesn't prevent it
        while_string = string_thunk.while_(lambda x: True)
        assert isinstance(while_string, Thunk)

    @pytest.mark.asyncio
    async def test_while_complex_condition(self):
        """Test while with complex condition logic."""
        def complex_condition(x: int) -> bool:
            return x < 20 and x % 3 != 0
        
        # Custom increment that adds 2
        def add_two(x: int) -> int:
            return x + 2
        
        thunk_obj = Thunk(add_two, name="add_two")
        while_thunk = thunk_obj.while_(complex_condition)
        
        result = await while_thunk(1)
        # 1 -> 3 (3 < 20 and 3 % 3 == 0, so condition is False)
        # Stop at 3 because 3 % 3 == 0
        assert result == 3


class TestNewMethodIntegration:
    """Test integration between new methods and existing functionality."""

    @pytest.mark.asyncio
    async def test_repeat_then_while(self):
        """Test composing repeat and while methods."""
        thunk_obj = Thunk(sync_increment, name="increment")
        
        # Create a while loop that repeatedly runs "repeat increment 3 times"
        composed = thunk_obj.repeat(3).while_(lambda x: x < 15)
        
        result = await composed(5)
        # 5 -> 8 (repeat 3x), 8 < 15 continue
        # 8 -> 11 (repeat 3x), 11 < 15 continue  
        # 11 -> 14 (repeat 3x), 14 < 15 continue
        # 14 -> 17 (repeat 3x), 17 >= 15 stop
        assert result == 17

    @pytest.mark.asyncio
    async def test_while_then_repeat(self):
        """Test composing while and repeat methods."""
        thunk_obj = Thunk(sync_increment, name="increment")
        
        # Create a repeat that runs "while increment < 10" two times
        composed = thunk_obj.while_(lambda x: x < 10).repeat(2)
        
        result = await composed(8)
        # First repeat: 8 -> 10 (while < 10), 10 >= 10 stop
        # Second repeat: 10 -> 10 (while < 10 is false from start)
        # Result: 10
        assert result == 10

    @pytest.mark.asyncio
    async def test_new_methods_with_map(self):
        """Test new methods with map."""
        thunk_obj = Thunk(sync_increment, name="increment")
        
        # Repeat 3 times, then map to double
        composed = thunk_obj.repeat(3).map(lambda x: x * 2)
        
        result = await composed(5)
        # 5 + 1 + 1 + 1 = 8, then 8 * 2 = 16
        assert result == 16

    @pytest.mark.asyncio
    async def test_new_methods_with_filter(self):
        """Test new methods with filter."""
        thunk_obj = Thunk(sync_increment, name="increment")
        
        # While < 12, then filter for even numbers
        composed = thunk_obj.while_(lambda x: x < 12).filter(lambda x: x % 2 == 0)
        
        result_even = await composed(10)  # 10 + 1 + 1 = 12 (even)
        assert result_even == 12
        
        result_odd = await composed(9)   # 9 + 1 + 1 + 1 = 12 (even)
        assert result_odd == 12

    @pytest.mark.asyncio
    async def test_new_methods_with_tap(self):
        """Test new methods with tap for side effects."""
        side_effects = []
        
        def log_value(x):
            side_effects.append(x)
        
        thunk_obj = Thunk(sync_increment, name="increment")
        
        # Repeat 2 times, then tap to log
        composed = thunk_obj.repeat(2).tap(log_value)
        
        result = await composed(5)
        # 5 + 1 + 1 = 7
        assert result == 7
        assert side_effects == [7]

    @pytest.mark.asyncio
    async def test_new_methods_with_chain(self):
        """Test new methods with chain operator."""
        increment_thunk = Thunk(sync_increment, name="increment")
        double_thunk = Thunk(sync_double, name="double")
        
        # Repeat increment 2 times, then chain with double
        composed = increment_thunk.repeat(2) >> double_thunk
        
        result = await composed(5)
        # 5 + 1 + 1 = 7, then 7 * 2 = 14
        assert result == 14


class TestFixedIssues:
    """Test cases that verify previously fixed issues."""

    @pytest.mark.asyncio
    async def test_sync_function_wrapper_fixed(self):
        """Verify that sync function wrapping now works correctly."""
        thunk_obj = Thunk(sync_increment, name="sync_increment")

        # Test basic properties
        assert thunk_obj.name == "sync_increment"
        assert thunk_obj.metadata == {}

        # Test that execution works properly
        result = await thunk_obj(5)
        assert result == 6
        assert isinstance(result, int)

    @pytest.mark.asyncio
    async def test_tap_method_fixed(self):
        """Verify that the tap method now works correctly with maybe_await."""
        thunk_obj = Thunk(sync_increment, name="sync_increment")

        side_effects = []

        def log_effect(x):
            side_effects.append(f"logged: {x}")

        tapped_thunk = thunk_obj.tap(log_effect)
        result = await tapped_thunk(5)

        assert result == 6  # Original result preserved
        assert side_effects == ["logged: 6"]  # Side effect executed
