"""Property-based tests for Flow combinators using hypothesis.

These tests verify that Flow combinators satisfy mathematical properties
and behave correctly across a wide range of inputs.
"""

import asyncio
import pytest
from typing import AsyncIterator, List
from hypothesis import given, strategies as st, assume, settings
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant, initialize

from goldentooth_agent.core.flow import Flow
from goldentooth_agent.core.flow.combinators import (
    map_stream,
    filter_stream,
    flat_map_stream,
    take_stream,
    skip_stream,
    batch_stream,
    distinct_stream,
    compose,
    identity_stream,
    scan_stream,
    zip_stream,
    chunk_stream,
    window_stream,
    pairwise_stream,
    start_with_stream,
)


# Async test utilities
async def list_from_async_iter(async_iter: AsyncIterator) -> List:
    """Convert async iterator to list."""
    return [item async for item in async_iter]


async def async_iter_from_list(items: List) -> AsyncIterator:
    """Convert list to async iterator."""
    for item in items:
        yield item


class TestMapStreamProperties:
    """Property-based tests for map_stream."""

    @given(st.lists(st.integers()))
    @pytest.mark.asyncio
    async def test_map_functor_identity(self, items):
        """Test that map(identity) == identity."""
        identity_flow = map_stream(lambda x: x)
        input_stream = async_iter_from_list(items)
        result = await list_from_async_iter(identity_flow(input_stream))
        assert result == items

    @given(st.lists(st.integers()))
    @pytest.mark.asyncio
    async def test_map_functor_composition(self, items):
        """Test that map(f ∘ g) == map(f) ∘ map(g)."""
        f = lambda x: x * 2
        g = lambda x: x + 1

        # map(f ∘ g)
        composed_fn = lambda x: f(g(x))
        direct_flow = map_stream(composed_fn)

        # map(f) ∘ map(g)
        composed_flow = compose(map_stream(g), map_stream(f))

        input_stream1 = async_iter_from_list(items)
        input_stream2 = async_iter_from_list(items)

        result1 = await list_from_async_iter(direct_flow(input_stream1))
        result2 = await list_from_async_iter(composed_flow(input_stream2))

        assert result1 == result2

    @given(st.lists(st.integers(), min_size=0, max_size=100))
    @pytest.mark.asyncio
    async def test_map_preserves_length(self, items):
        """Test that map preserves stream length."""
        map_flow = map_stream(lambda x: x * 3)
        input_stream = async_iter_from_list(items)
        result = await list_from_async_iter(map_flow(input_stream))
        assert len(result) == len(items)


class TestFilterStreamProperties:
    """Property-based tests for filter_stream."""

    @given(st.lists(st.integers()))
    @pytest.mark.asyncio
    async def test_filter_with_true_predicate(self, items):
        """Test that filter with always-true predicate preserves all items."""
        filter_flow = filter_stream(lambda x: True)
        input_stream = async_iter_from_list(items)
        result = await list_from_async_iter(filter_flow(input_stream))
        assert result == items

    @given(st.lists(st.integers()))
    @pytest.mark.asyncio
    async def test_filter_with_false_predicate(self, items):
        """Test that filter with always-false predicate removes all items."""
        filter_flow = filter_stream(lambda x: False)
        input_stream = async_iter_from_list(items)
        result = await list_from_async_iter(filter_flow(input_stream))
        assert result == []

    @given(st.lists(st.integers()))
    @pytest.mark.asyncio
    async def test_filter_is_idempotent(self, items):
        """Test that filter(p) ∘ filter(p) == filter(p)."""
        predicate = lambda x: x % 2 == 0
        single_filter = filter_stream(predicate)
        double_filter = compose(filter_stream(predicate), filter_stream(predicate))

        input_stream1 = async_iter_from_list(items)
        input_stream2 = async_iter_from_list(items)

        result1 = await list_from_async_iter(single_filter(input_stream1))
        result2 = await list_from_async_iter(double_filter(input_stream2))

        assert result1 == result2

    @given(st.lists(st.integers()))
    @pytest.mark.asyncio
    async def test_filter_respects_predicate(self, items):
        """Test that filter only keeps items matching the predicate."""
        predicate = lambda x: x > 0
        filter_flow = filter_stream(predicate)
        input_stream = async_iter_from_list(items)
        result = await list_from_async_iter(filter_flow(input_stream))

        assert all(predicate(item) for item in result)
        assert all(item in items for item in result)


class TestTakeSkipProperties:
    """Property-based tests for take_stream and skip_stream."""

    @given(
        st.lists(st.integers(), min_size=0, max_size=100),
        st.integers(min_value=0, max_value=100),
    )
    @pytest.mark.asyncio
    async def test_take_skip_complementary(self, items, n):
        """Test that take(n) + skip(n) reconstructs the original stream."""
        take_flow = take_stream(n)
        skip_flow = skip_stream(n)

        input_stream1 = async_iter_from_list(items)
        input_stream2 = async_iter_from_list(items)

        taken = await list_from_async_iter(take_flow(input_stream1))
        skipped = await list_from_async_iter(skip_flow(input_stream2))

        reconstructed = taken + skipped
        assert reconstructed == items

    @given(
        st.lists(st.integers(), min_size=0, max_size=50),
        st.integers(min_value=0, max_value=25),
    )
    @pytest.mark.asyncio
    async def test_take_never_exceeds_length(self, items, n):
        """Test that take never produces more items than available."""
        take_flow = take_stream(n)
        input_stream = async_iter_from_list(items)
        result = await list_from_async_iter(take_flow(input_stream))

        assert len(result) <= len(items)
        assert len(result) <= n
        assert result == items[:n]

    @given(st.lists(st.integers()), st.integers(min_value=0))
    @pytest.mark.asyncio
    async def test_skip_reduces_length_correctly(self, items, n):
        """Test that skip reduces length by the correct amount."""
        skip_flow = skip_stream(n)
        input_stream = async_iter_from_list(items)
        result = await list_from_async_iter(skip_flow(input_stream))

        expected_length = max(0, len(items) - n)
        assert len(result) == expected_length
        assert result == items[n:]


class TestBatchChunkProperties:
    """Property-based tests for batch_stream and chunk_stream."""

    @given(
        st.lists(st.integers(), min_size=1, max_size=100),
        st.integers(min_value=1, max_value=20),
    )
    @pytest.mark.asyncio
    async def test_batch_preserves_all_items(self, items, batch_size):
        """Test that batching preserves all items when flattened."""
        batch_flow = batch_stream(batch_size)
        input_stream = async_iter_from_list(items)
        batches = await list_from_async_iter(batch_flow(input_stream))

        flattened = []
        for batch in batches:
            flattened.extend(batch)

        assert flattened == items

    @given(
        st.lists(st.integers(), min_size=1, max_size=100),
        st.integers(min_value=1, max_value=20),
    )
    @pytest.mark.asyncio
    async def test_batch_size_constraints(self, items, batch_size):
        """Test that all batches except possibly the last have correct size."""
        batch_flow = batch_stream(batch_size)
        input_stream = async_iter_from_list(items)
        batches = await list_from_async_iter(batch_flow(input_stream))

        if batches:
            # All batches except the last should have size == batch_size
            for batch in batches[:-1]:
                assert len(batch) == batch_size

            # Last batch should have size <= batch_size
            assert len(batches[-1]) <= batch_size
            assert len(batches[-1]) > 0


class TestDistinctStreamProperties:
    """Property-based tests for distinct_stream."""

    @given(st.lists(st.integers()))
    @pytest.mark.asyncio
    async def test_distinct_removes_duplicates(self, items):
        """Test that distinct removes all duplicates."""
        distinct_flow = distinct_stream()
        input_stream = async_iter_from_list(items)
        result = await list_from_async_iter(distinct_flow(input_stream))

        # Result should have no duplicates
        assert len(result) == len(set(str(item) for item in result))

        # All items in result should be from original items
        assert all(item in items for item in result)

        # First occurrence of each item should be preserved
        seen = set()
        expected = []
        for item in items:
            key = str(item)
            if key not in seen:
                seen.add(key)
                expected.append(item)

        assert result == expected

    @given(st.lists(st.integers()))
    @pytest.mark.asyncio
    async def test_distinct_is_idempotent(self, items):
        """Test that distinct applied twice gives same result as once."""
        single_distinct = distinct_stream()
        double_distinct = compose(distinct_stream(), distinct_stream())

        input_stream1 = async_iter_from_list(items)
        input_stream2 = async_iter_from_list(items)

        result1 = await list_from_async_iter(single_distinct(input_stream1))
        result2 = await list_from_async_iter(double_distinct(input_stream2))

        assert result1 == result2


class TestScanStreamProperties:
    """Property-based tests for scan_stream."""

    @given(st.lists(st.integers(), max_size=50), st.integers())
    @pytest.mark.asyncio
    async def test_scan_length(self, items, initial):
        """Test that scan produces one more item than input (includes initial)."""
        scan_flow = scan_stream(lambda acc, x: acc + x, initial)
        input_stream = async_iter_from_list(items)
        result = await list_from_async_iter(scan_flow(input_stream))

        assert len(result) == len(items) + 1
        assert result[0] == initial

    @given(st.lists(st.integers(), min_size=1, max_size=20))
    @pytest.mark.asyncio
    async def test_scan_sum_correctness(self, items):
        """Test that scan with addition produces running sums."""
        scan_flow = scan_stream(lambda acc, x: acc + x, 0)
        input_stream = async_iter_from_list(items)
        result = await list_from_async_iter(scan_flow(input_stream))

        # Check that each element is the cumulative sum
        expected = [0]  # Initial value
        running_sum = 0
        for item in items:
            running_sum += item
            expected.append(running_sum)

        assert result == expected


class TestPairwiseStreamProperties:
    """Property-based tests for pairwise_stream."""

    @given(st.lists(st.integers(), min_size=0, max_size=50))
    @pytest.mark.asyncio
    async def test_pairwise_length(self, items):
        """Test that pairwise produces n-1 pairs for n items."""
        pairwise_flow = pairwise_stream()
        input_stream = async_iter_from_list(items)
        result = await list_from_async_iter(pairwise_flow(input_stream))

        expected_length = max(0, len(items) - 1)
        assert len(result) == expected_length

    @given(st.lists(st.integers(), min_size=2, max_size=20))
    @pytest.mark.asyncio
    async def test_pairwise_consecutive(self, items):
        """Test that pairwise produces consecutive pairs."""
        assume(len(items) >= 2)

        pairwise_flow = pairwise_stream()
        input_stream = async_iter_from_list(items)
        result = await list_from_async_iter(pairwise_flow(input_stream))

        for i, (prev, curr) in enumerate(result):
            assert prev == items[i]
            assert curr == items[i + 1]


class TestWindowStreamProperties:
    """Property-based tests for window_stream."""

    @given(
        st.lists(st.integers(), min_size=1, max_size=30),
        st.integers(min_value=1, max_value=10),
        st.integers(min_value=1, max_value=5),
    )
    @pytest.mark.asyncio
    async def test_window_properties(self, items, window_size, step):
        """Test window_stream properties."""
        assume(window_size <= len(items))

        window_flow = window_stream(window_size, step)
        input_stream = async_iter_from_list(items)
        result = await list_from_async_iter(window_flow(input_stream))

        # Each window should have the correct size
        for window in result:
            assert len(window) == window_size

        # Windows should overlap correctly based on step size
        if len(result) >= 2:
            first_window = result[0]
            second_window = result[1]

            # The overlap should be window_size - step
            overlap_size = window_size - step
            if overlap_size > 0:
                assert first_window[step:] == second_window[:overlap_size]


class TestCompositionProperties:
    """Property-based tests for flow composition."""

    @given(st.lists(st.integers()))
    @pytest.mark.asyncio
    async def test_identity_composition(self, items):
        """Test that compose(identity, f) == f == compose(f, identity)."""
        f = map_stream(lambda x: x * 2)
        identity = identity_stream()

        input_stream1 = async_iter_from_list(items)
        input_stream2 = async_iter_from_list(items)
        input_stream3 = async_iter_from_list(items)

        result_f = await list_from_async_iter(f(input_stream1))
        result_left = await list_from_async_iter(compose(identity, f)(input_stream2))
        result_right = await list_from_async_iter(compose(f, identity)(input_stream3))

        assert result_f == result_left == result_right

    @given(st.lists(st.integers(), max_size=50))
    @pytest.mark.asyncio
    async def test_composition_associativity(self, items):
        """Test that compose(f, compose(g, h)) == compose(compose(f, g), h)."""
        f = map_stream(lambda x: x + 1)
        g = map_stream(lambda x: x * 2)
        h = filter_stream(lambda x: x % 2 == 0)

        # compose(f, compose(g, h))
        left_assoc = compose(f, compose(g, h))

        # compose(compose(f, g), h)
        right_assoc = compose(compose(f, g), h)

        input_stream1 = async_iter_from_list(items)
        input_stream2 = async_iter_from_list(items)

        result1 = await list_from_async_iter(left_assoc(input_stream1))
        result2 = await list_from_async_iter(right_assoc(input_stream2))

        assert result1 == result2


class FlowStateMachine(RuleBasedStateMachine):
    """Stateful property-based testing for Flow operations."""

    def __init__(self):
        super().__init__()
        self.items = []
        self.transformations = []

    @initialize()
    def init_state(self):
        self.items = []
        self.transformations = []

    @rule(item=st.integers())
    def add_item(self, item):
        """Add an item to the stream."""
        self.items.append(item)

    @rule()
    def apply_map_double(self):
        """Apply a doubling map transformation."""
        self.transformations.append(("map", lambda x: x * 2))

    @rule()
    def apply_filter_positive(self):
        """Apply a filter for positive numbers."""
        self.transformations.append(("filter", lambda x: x > 0))

    @rule(n=st.integers(min_value=1, max_value=20))
    def apply_take(self, n):
        """Apply a take transformation."""
        self.transformations.append(("take", n))

    @invariant()
    def results_are_consistent(self):
        """Test that applying transformations gives consistent results."""
        if not self.items:
            return

        # Build the flow from transformations
        flow = identity_stream()
        for transform_type, param in self.transformations:
            if transform_type == "map":
                flow = compose(flow, map_stream(param))
            elif transform_type == "filter":
                flow = compose(flow, filter_stream(param))
            elif transform_type == "take":
                flow = compose(flow, take_stream(param))

        # Apply transformations manually for comparison
        expected = list(self.items)
        for transform_type, param in self.transformations:
            if transform_type == "map":
                expected = [param(x) for x in expected]
            elif transform_type == "filter":
                expected = [x for x in expected if param(x)]
            elif transform_type == "take":
                expected = expected[:param]

        # Test the flow
        async def run_test():
            input_stream = async_iter_from_list(self.items)
            result = await list_from_async_iter(flow(input_stream))
            return result

        result = asyncio.run(run_test())
        assert result == expected


# Configure hypothesis for faster test runs during development
@settings(max_examples=50, deadline=5000)
class TestFlowStateMachine:
    """Test runner for the Flow state machine."""

    def test_flow_state_machine(self):
        """Run the stateful property-based tests."""
        FlowStateMachine.TestCase().runTest()


# Edge case tests with specific strategies
class TestEdgeCases:
    """Property-based tests for edge cases."""

    @given(st.lists(st.nothing()))
    @pytest.mark.asyncio
    async def test_empty_stream_handling(self, items):
        """Test that flows handle empty streams correctly."""
        # This will always be an empty list
        assert items == []

        map_flow = map_stream(lambda x: x * 2)
        input_stream = async_iter_from_list(items)
        result = await list_from_async_iter(map_flow(input_stream))

        assert result == []

    @given(st.lists(st.integers(min_value=-1000000, max_value=1000000), max_size=5))
    @pytest.mark.asyncio
    async def test_extreme_values(self, items):
        """Test flows with extreme integer values."""
        map_flow = map_stream(lambda x: x + 1)
        input_stream = async_iter_from_list(items)
        result = await list_from_async_iter(map_flow(input_stream))

        assert len(result) == len(items)
        for i, item in enumerate(items):
            if item < 1000000:  # Avoid overflow
                assert result[i] == item + 1
