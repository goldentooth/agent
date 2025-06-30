# Combinators

Combinators module

## Overview

- **Complexity**: High
- **Files**: 9 Python files
- **Lines of Code**: ~1608
- **Classes**: 4
- **Functions**: 66

## API Reference

### Classes

#### StreamNotification
Represents a stream notification (item, error, or completion).

#### OnNext
Class for onnext functionality.

#### OnError
Class for onerror functionality.

#### OnComplete
Class for oncomplete functionality.

### Functions

#### `def race_stream(*flows: Flow[Input, Output]) -> Flow[Input, Output]`
Create a flow that races multiple flows and yields the first result.

    For each input item, runs all flows in parallel and yields the result
    from whichever flow completes first.

    Args:
        *flows: Flows to race against each other

    Returns:
        A flow that yields first results from racing flows

#### `def parallel_stream(*flows: Flow[Input, Output]) -> Flow[Input, list[Output]]`
Create a flow that runs multiple flows in parallel and collects all results.

    For each input item, runs all flows in parallel and yields a list of all results.

    Args:
        *flows: Flows to run in parallel

    Returns:
        A flow that yields lists of results from parallel execution

#### `def parallel_stream_successful(*flows: Flow[Input, Output]) -> Flow[Input, list[Output]]`
Create a flow that runs flows in parallel and yields only successful results.

    Ignores flows that raise exceptions and yields results from successful flows only.

    Args:
        *flows: Flows to run in parallel

    Returns:
        A flow that yields lists of successful results

#### `def zip_stream(other: AsyncIterator[OtherInput]) -> Flow[Input, tuple[Input, OtherInput]]`
Create a flow that zips items with another stream.

    Pairs each item from the main stream with the corresponding item
    from the other stream.

    Args:
        other: The other stream to zip with

    Returns:
        A flow that yields tuples of paired items

#### `def chain_stream(*streams: AsyncIterator[Input]) -> Flow[None, Input]`
Create a flow that chains multiple streams sequentially.

    Yields all items from the first stream, then all from the second, etc.

    Args:
        *streams: Streams to chain together

    Returns:
        A flow that yields items from all streams in sequence

#### `def merge_stream(*flows: Flow[Input, Output]) -> Flow[Input, Output]`
Create a flow that merges results from multiple flows concurrently.

    Runs all flows on the same input stream and merges their outputs
    as they become available.

    Args:
        *flows: Flows to merge

    Returns:
        A flow that yields merged results from all flows

#### `def merge_flows(*flows: Flow[Input, Input]) -> Flow[Input, Input]`
Create a flow that merges multiple flows that operate on the same input.

    Similar to merge_stream but for flows that have the same input/output types.

    Args:
        *flows: Flows to merge (must have same input/output types)

    Returns:
        A flow that merges all input flows

#### `def combine_latest_stream(other: AsyncIterator[OtherInput]) -> Flow[Input, tuple[Input, OtherInput]]`
Create a flow that combines items with the latest value from another stream.

    For each item in the main stream, emits a tuple with that item and
    the most recent item from the other stream.

    Args:
        other: The other stream to combine with

    Returns:
        A flow that yields tuples of (current_item, latest_other_item)

#### `def flat_map_ctx_stream(fn: Callable[[Output, Input], AsyncIterator[Newput]]) -> Flow[Input, Newput]`
Create a flow that flat-maps with access to both item and original context.

    Unlike flat_map_stream which only gets the current item, this passes both
    the current item and the original stream input to the mapping function.

    Args:
        fn: Function that takes (current_item, original_input) and returns async iterator

    Returns:
        A flow that flat-maps with context access

#### `async def merge_async_generators(*generators: AsyncIterator[Input]) -> AsyncIterator[Input]`
Utility function to merge multiple async generators.

    This is a utility function used by other combinators to merge async iterators.

    Args:
        *generators: Async generators to merge

    Returns:
        Async iterator that yields from all generators concurrently

#### `def delay_stream(seconds: float) -> Flow[Input, Input]`
Create a flow that delays each item in the stream by a given number of seconds.

#### `def debounce_stream(seconds: float) -> Flow[Input, Input]`
Create a flow that debounces stream items by waiting for a quiet period.

#### `def throttle_stream(rate_per_second: float) -> Flow[Input, Input]`
Create a flow that throttles the rate of item processing.

    Ensures that items are processed at most at the specified rate,
    introducing delays as necessary.

    Args:
        rate_per_second: Maximum items per second to process

    Returns:
        A flow that throttles processing rate

#### `def timeout_stream(seconds: float) -> Flow[Input, Input]`
Create a flow that adds a timeout to each item's processing.

    If processing an item takes longer than the specified timeout,
    a TimeoutError is raised.

    Args:
        seconds: Maximum time to wait for each item

    Returns:
        A flow that enforces timeouts on item processing

#### `def sample_stream(interval: float) -> Flow[Input, Input]`
Create a flow that samples the stream at regular intervals.

    Emits the most recent item at each interval. If no new items have arrived
    since the last sample, nothing is emitted. Essential for rate limiting
    and real-time applications.

    Args:
        interval: Sampling interval in seconds

    Returns:
        A flow that samples items at regular intervals

#### `def batch_stream(size: int) -> Flow[Input, list[Input]]`
Create a flow that batches stream items into lists of specified size.

#### `def chunk_stream(size: int) -> Flow[Input, list[Input]]`
Create a flow that groups items into fixed-size chunks.

    Similar to batch_stream but emphasizes the chunking concept.

    Args:
        size: Number of items per chunk

    Returns:
        A flow that yields lists of items

#### `def window_stream(size: int, step: int) -> Flow[Input, list[Input]]`
Create a flow that generates sliding windows over the stream.

    Creates overlapping windows of items with specified size and step.

    Args:
        size: Window size
        step: Step size between windows (default 1)

    Returns:
        A flow that yields sliding windows

#### `def scan_stream(fn: Callable[[Output, Input], Output], initial: Output) -> Flow[Input, Output]`
Create a flow that performs a running accumulation with intermediate results.

    Like a fold/reduce but emits all intermediate accumulator values.

    Args:
        fn: Accumulator function
        initial: Initial accumulator value

    Returns:
        A flow that yields intermediate accumulation results

#### `def group_by_stream(key_fn: Callable[[Input], K]) -> Flow[Input, tuple[K, list[Input]]]`
Create a flow that groups items by a key function.

    Collects all items with the same key and emits them as groups.

    Args:
        key_fn: Function that extracts grouping key from each item

    Returns:
        A flow that yields (key, items) tuples

#### `def distinct_stream(key_fn: Callable[[Input], K] | None) -> Flow[Input, Input]`
Create a flow that filters out duplicate items.

    Uses a key function to determine uniqueness, or the items themselves if no key function.

    Args:
        key_fn: Optional function to extract comparison key (defaults to item itself)

    Returns:
        A flow that yields only distinct items

#### `def pairwise_stream() -> Flow[Input, tuple[Input, Input]]`
Create a flow that emits consecutive pairs of items.

    Emits tuples of (previous_item, current_item) for each item after the first.

    Returns:
        A flow that yields consecutive pairs

#### `def memoize_stream(key_fn: Callable[[Input], K]) -> Flow[Input, Input]`
Create a flow that caches items based on a key function.

    Items with the same key are only processed once; subsequent items
    with the same key yield the cached result.

    Args:
        key_fn: Function that extracts caching key from each item

    Returns:
        A flow that caches items by key

#### `def buffer_stream(trigger: AsyncIterator[AnyValue]) -> Flow[Input, list[Input]]`
Create a flow that buffers items until a trigger emits.

    Collects items in a buffer and emits the buffer contents when
    the trigger stream produces a value.

    Args:
        trigger: Stream that triggers buffer emission

    Returns:
        A flow that buffers items until triggered

#### `def expand_stream(expander: Callable[[Input], AsyncIterator[Input]], max_depth: int) -> Flow[Input, Input]`
Create a flow that recursively expands items using an expander function.

    Applies the expander function to each item and recursively processes
    the results until no more expansions are possible or max depth is reached.

    Args:
        expander: Function that expands an item into multiple items
        max_depth: Maximum recursion depth

    Returns:
        A flow that recursively expands items

#### `def finalize_stream(finalizer: Callable[[], AnyValue]) -> Flow[Input, Input]`
Create a flow that executes a finalizer function when the stream completes.

    The finalizer is called whether the stream completes normally or with an error.

    Args:
        finalizer: Function to call when stream processing finishes

    Returns:
        A flow that executes cleanup on completion

#### `def if_then_stream(predicate: Callable[[Input], bool], then_flow: Flow[Input, Output], else_flow: Flow[Input, Output] | None) -> Flow[Input, Output]`
Create a flow that conditionally applies different flows based on a predicate.

    For each item in the stream, evaluates the predicate and applies either
    the then_flow or else_flow accordingly.

    Args:
        predicate: Function that determines which flow to apply
        then_flow: Flow to apply when predicate returns True
        else_flow: Flow to apply when predicate returns False (optional)

    Returns:
        A flow that conditionally processes items

#### `def retry_stream(n: int, flow: Flow[Input, Output]) -> Flow[Input, Output]`
Create a flow that retries processing items with another flow on failure.

#### `def recover_stream(handler: Callable[[Exception, Input], Awaitable[Output]]) -> Flow[Input, Output]`
Create a flow that handles exceptions and provides fallback values.

    When an exception occurs during stream processing, the handler function
    is called with the exception and the current item to provide a fallback value.

#### `def switch_stream(selector: Callable[[Input], str], cases: dict[str, Flow[Input, Output]], default: Flow[Input, Output] | None) -> Flow[Input, Output]`
Create a flow that routes items to different flows based on a selector function.

    For each item, applies the selector function to determine which case flow
    to use for processing.

    Args:
        selector: Function that returns a case key for each item
        cases: Dictionary mapping case keys to flows
        default: Optional default flow for unmatched cases

    Returns:
        A flow that routes items based on selector

#### `def while_condition_stream(condition: Callable[[Input], bool], transform: Flow[Input, Output]) -> Flow[Input, Output]`
Create a flow that applies a transformation while a condition is true.

    Continues processing items with the transform flow as long as the condition
    returns True for each item.

    Args:
        condition: Function that determines whether to continue processing
        transform: Flow to apply while condition is true

    Returns:
        A flow that processes while condition holds

#### `def circuit_breaker_stream(failure_threshold: int, recovery_timeout: float) -> Flow[Input, Input]`
Create a flow that implements the circuit breaker pattern.

    Tracks failures and "opens" the circuit after too many failures,
    preventing further processing until a recovery timeout elapses.

    Args:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Seconds to wait before attempting recovery

    Returns:
        A flow that implements circuit breaker behavior

#### `def catch_and_continue_stream(handler: Callable[[Exception], AnyValue] | None) -> Flow[Input, Input]`
Create a flow that catches exceptions and continues processing.

    When an exception occurs, optionally calls a handler function and
    continues with the next item instead of propagating the exception.

    Args:
        handler: Optional function to handle exceptions

    Returns:
        A flow that catches exceptions and continues processing

#### `def tap_stream(side_effect: Callable[[Input], AnyValue]) -> Flow[Input, Input]`
Create a flow that applies a side effect to each item without changing the stream.

    Useful for logging, debugging, or triggering side effects while preserving
    the original stream data.

    Args:
        side_effect: Function to call for each item (can be sync or async)

    Returns:
        A flow that applies side effects and passes items through

#### `def then_stream(side_effect: Callable[[Input], AnyValue]) -> Flow[Input, Input]`
Create a flow that applies a side effect sequentially after each item.

    Similar to tap_stream but emphasizes sequential execution.

    Args:
        side_effect: Function to call for each item (can be sync or async)

    Returns:
        A flow that applies side effects sequentially

#### `def chain_flows(*flows: Flow[Input, Input]) -> Flow[Input, Input]`
Create a flow that chains multiple flows sequentially.

    Applies each flow in sequence to the same input stream.
    Each flow processes the original stream independently.

    Args:
        *flows: Flows to chain sequentially

    Returns:
        A flow that applies all flows to the input stream

#### `def branch_flows(predicate: Callable[[Input], bool], true_flow: Flow[Input, Output], false_flow: Flow[Input, Output] | None) -> Flow[Input, Output]`
Create a flow that branches processing based on a predicate.

    Splits the input stream and applies different flows to items based
    on the predicate result.

    Args:
        predicate: Function that determines which branch to take
        true_flow: Flow for items where predicate returns True
        false_flow: Flow for items where predicate returns False

    Returns:
        A flow that branches processing based on predicate

#### `def log_stream(name: str) -> Flow[Input, Input]`
Create a flow that logs each stream item and passes it through unchanged.

    Useful for debugging flow pipelines by observing intermediate values
    without affecting the data flow.

    Args:
        name: Name for the flow (used in pipeline visualization)
        prefix: Optional prefix to add before the logged item
        level: Logging level (defaults to DEBUG)

#### `def trace_stream(tracer: Callable[[str, AnyValue], None]) -> Flow[Input, Input]`
Create a flow that provides detailed tracing of stream processing.

    Calls the tracer function for each item with event type and item data.
    Useful for debugging and monitoring stream behavior.

    Args:
        tracer: Function that receives (event_type, item) for tracing

    Returns:
        A flow that traces processing and passes items through

#### `def metrics_stream(counter: Callable[[str], None]) -> Flow[Input, Input]`
Create a flow that emits metrics for stream processing.

    Calls the counter function with metric names as items are processed.
    Useful for monitoring and observability.

    Args:
        counter: Function that receives metric names

    Returns:
        A flow that emits metrics and passes items through

#### `def inspect_stream(inspector: Callable[[Input, dict[str, AnyValue]], None]) -> Flow[Input, Input]`
Create a flow that inspects stream items with context metadata.

    Calls the inspector function with each item and a context dictionary
    containing processing metadata. Useful for debugging and analysis.

    Args:
        inspector: Function that receives (item, context_dict)

    Returns:
        A flow that inspects items and passes them through

#### `def materialize_stream() -> Flow[Input, StreamNotification]`
Create a flow that converts items and errors into notification objects.

    Converts the stream into a meta-stream where each emission is a notification
    about what happened (OnNext, OnError, OnComplete). Allows treating errors
    as values for complex error handling patterns.

    Returns:
        A flow that yields StreamNotification objects

#### `def range_flow(start: int, stop: int, step: int) -> Flow[None, int]`
Create a flow that generates a range of integers.

#### `def repeat_flow(value: A, times: int | None) -> Flow[None, A]`
Create a flow that repeats a value a specified number of times (or infinitely).

#### `def empty_flow() -> Flow[None, AnyValue]`
Create a flow that produces no items.

#### `def start_with_stream(*items: Input) -> Flow[Input, Input]`
Create a flow that prepends specified items to the beginning of the stream.

    Very useful for providing default values, initialization, or ensuring
    non-empty streams.

    Args:
        *items: Items to prepend to the stream

    Returns:
        A flow that starts with the specified items, then continues with stream items

#### `async def run_fold(initial_stream: AsyncIterator[Input], steps: list[Flow[Input, Input]]) -> AsyncIterator[Input]`
Execute a list of flows sequentially, piping the stream through each step.

    This is a fold/reduce operation where each flow receives the output stream of the
    previous flow as its input. Useful for building sequential processing pipelines.

    Args:
        initial_stream: The initial input stream
        steps: List of flows to execute in order

    Returns:
        The final output stream after all steps have been executed

    Example:
        increment_flow = Flow.from_sync_fn(lambda x: x + 1)
        double_flow = Flow.from_sync_fn(lambda x: x * 2)
        input_stream = async_range(3)  # [0, 1, 2]
        result_stream = run_fold(input_stream, [increment_flow, double_flow])
        # Result: [2, 4, 6] -> (0+1)*2, (1+1)*2, (2+1)*2

#### `def compose(first: Flow[A, B], second: Flow[B, C]) -> Flow[A, C]`
Compose two flows, where the output of the first is the input to the second.

#### `def filter_stream(predicate: Callable[[Input], bool]) -> Flow[Input, Input]`
Create a flow that filters stream items based on a predicate.

#### `def map_stream(fn: Callable[[Input], Output]) -> Flow[Input, Output]`
Create a flow that maps a function over each item in the stream.

#### `def flat_map_stream(fn: Callable[[Input], AsyncIterator[Output]]) -> Flow[Input, Output]`
Create a flow that flat-maps a function over each item in the stream.

#### `def identity_stream() -> Flow[Input, Input]`
Create a flow that passes the stream through unchanged.

#### `def take_stream(n: int) -> Flow[Input, Input]`
Create a flow that takes the first n items from the stream.

#### `def skip_stream(n: int) -> Flow[Input, Input]`
Create a flow that skips the first n items from the stream.

#### `def guard_stream(predicate: Callable[[Input], bool], message: str) -> Flow[Input, Input]`
Create a flow that validates items or raises an exception.

    Args:
        predicate: Function that returns True for valid items
        message: Error message if validation fails

    Raises:
        FlowValidationError: If any item fails the guard condition

#### `def flatten_stream() -> Flow[AsyncIterator[Input], Input]`
Create a flow that flattens nested async iterators.

#### `def collect_stream() -> Flow[Input, list[Input]]`
Create a flow that collects all items into a single list.

#### `def until_stream(predicate: Callable[[Input], bool]) -> Flow[Input, Input]`
Create a flow that processes items until a predicate becomes true.

    Once the predicate returns True for an item, that item is yielded
    and processing stops (the predicate item is included in output).

    Args:
        predicate: Function that determines when to stop processing

    Returns:
        A flow that processes until predicate is satisfied

#### `def share_stream() -> Flow[Input, Input]`
Create a flow that shares a single stream subscription among multiple subscribers.

#### `def get_function_name(fn: AnyCallable) -> str`
Extract function name for flow naming.

#### `def create_single_item_stream(item: Input) -> AsyncIterator[Input]`
Create an async iterator that yields a single item.

### Constants

#### `K`

#### `A`

#### `A`

#### `B`

#### `C`

#### `STREAM_END`

## Dependencies

### Internal Dependencies
- `goldentooth_agent.core.util.maybe_await`

### External Dependencies
- `__future__`
- `advanced`
- `aggregation`
- `asyncio`
- `basic`
- `collections`
- `control_flow`
- `core`
- `logging`
- `observability`
- `sources`
- `temporal`
- `typing`
- `utils`

## Exports

This module exports the following symbols:

- `OnComplete`
- `OnError`
- `OnNext`
- `StreamNotification`
- `batch_stream`
- `branch_flows`
- `buffer_stream`
- `catch_and_continue_stream`
- `chain_flows`
- `chain_stream`
- `chunk_stream`
- `circuit_breaker_stream`
- `collect_stream`
- `combine_latest_stream`
- `compose`
- `debounce_stream`
- `delay_stream`
- `distinct_stream`
- `empty_flow`
- `expand_stream`
- `filter_stream`
- `finalize_stream`
- `flat_map_ctx_stream`
- `flat_map_stream`
- `flatten_stream`
- `group_by_stream`
- `guard_stream`
- `identity_stream`
- `if_then_stream`
- `inspect_stream`
- `log_stream`
- `map_stream`
- `materialize_stream`
- `memoize_stream`
- `merge_async_generators`
- `merge_flows`
- `merge_stream`
- `metrics_stream`
- `pairwise_stream`
- `parallel_stream`
- `parallel_stream_successful`
- `race_stream`
- `range_flow`
- `recover_stream`
- `repeat_flow`
- `retry_stream`
- `run_fold`
- `sample_stream`
- `scan_stream`
- `share_stream`
- `skip_stream`
- `start_with_stream`
- `switch_stream`
- `take_stream`
- `tap_stream`
- `then_stream`
- `throttle_stream`
- `timeout_stream`
- `trace_stream`
- `until_stream`
- `while_condition_stream`
- `window_stream`
- `zip_stream`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
