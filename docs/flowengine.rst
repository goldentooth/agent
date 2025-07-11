Flow Engine Documentation
==========================

The Flow Engine is a comprehensive functional reactive programming library for Python that provides type-safe, composable stream processing with comprehensive error handling and observability.

.. contents::
   :local:
   :depth: 2

Overview
--------

The Flow Engine is built around three core concepts:

* **Flow**: The central abstraction for composable stream processing
* **Combinators**: 67+ functions for stream transformation and composition
* **Type Safety**: Full generic type preservation with strict typing

Key Features
~~~~~~~~~~~~

* **Type-safe composition**: Full generic type preservation through transformations
* **Functional patterns**: Identity, pure values, and monadic operations
* **67+ combinators**: Comprehensive library of stream processing functions
* **Async streaming**: Built on async iterators for efficient processing
* **Zero dependencies**: Standalone package with no external dependencies
* **100% test coverage**: Comprehensive test suite with 150+ test cases

Core Flow Class
---------------

The ``Flow`` class is the central abstraction for stream processing. It provides methods for creating, transforming, and composing streams.

Creating Flows
~~~~~~~~~~~~~~

.. code-block:: python

   from flow import Flow

   # From sync functions
   double_flow = Flow.from_sync_fn(lambda x: x * 2)

   # From async functions
   async_flow = Flow.from_async_fn(async_processor)

   # From iterables
   list_flow = Flow.from_iterable([1, 2, 3, 4, 5])

   # From values
   value_flow = Flow.from_value(42)

   # Identity flow
   identity_flow = Flow.identity()

Basic Operations
~~~~~~~~~~~~~~~

.. code-block:: python

   # Transform values
   transformed = flow.map(lambda x: x * 2)

   # Filter values
   filtered = flow.filter(lambda x: x > 0)

   # Compose flows
   composed = flow1 >> flow2

   # Apply transformations
   result = flow.transform(some_combinator)

Combinators Reference
--------------------

The Flow Engine provides 67+ combinators organized into 8 categories:

Basic Combinators (13 functions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Core stream processing operations:

.. code-block:: python

   from flow.combinators import (
       map_stream, filter_stream, compose, collect_stream,
       guard_stream, flatten_stream, take_stream, skip_stream,
       until_stream, share_stream, identity_stream, flat_map_stream,
       run_fold
   )

   # Transform stream values
   doubled = flow.transform(map_stream(lambda x: x * 2))

   # Filter stream values
   positives = flow.transform(filter_stream(lambda x: x > 0))

   # Take first N items
   first_ten = flow.transform(take_stream(10))

   # Skip first N items
   skip_header = flow.transform(skip_stream(1))

   # Collect to list
   collected = flow.transform(collect_stream())

Aggregation Combinators (11 functions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Batching, grouping, and windowing operations:

.. code-block:: python

   from flow.combinators import (
       batch_stream, buffer_stream, chunk_stream, distinct_stream,
       expand_stream, finalize_stream, group_by_stream, memoize_stream,
       pairwise_stream, scan_stream, window_stream
   )

   # Batch items
   batched = flow.transform(batch_stream(size=10))

   # Buffer with backpressure
   buffered = flow.transform(buffer_stream(size=100))

   # Group by key
   grouped = flow.transform(group_by_stream(key_fn=lambda x: x.category))

   # Sliding window
   windowed = flow.transform(window_stream(size=5))

   # Scan with accumulator
   accumulated = flow.transform(scan_stream(0, lambda acc, x: acc + x))

Temporal Combinators (5 functions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Time-based stream operations:

.. code-block:: python

   from flow.combinators import (
       debounce_stream, throttle_stream, delay_stream,
       timeout_stream, sample_stream
   )

   # Debounce events
   debounced = flow.transform(debounce_stream(delay=0.1))

   # Throttle rate
   throttled = flow.transform(throttle_stream(rate=10))

   # Add delay
   delayed = flow.transform(delay_stream(delay=0.5))

   # Timeout operations
   timed_out = flow.transform(timeout_stream(timeout=5.0))

   # Sample at intervals
   sampled = flow.transform(sample_stream(interval=1.0))

Control Flow Combinators (11 functions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Conditional processing and error handling:

.. code-block:: python

   from flow.combinators import (
       retry_stream, recover_stream, circuit_breaker_stream,
       if_then_stream, switch_stream, tap_stream, while_condition_stream,
       then_stream, catch_and_continue_stream, chain_flows, branch_flows
   )

   # Retry failed operations
   retried = flow.transform(retry_stream(max_retries=3))

   # Recover from errors
   recovered = flow.transform(recover_stream(fallback_fn))

   # Circuit breaker pattern
   protected = flow.transform(circuit_breaker_stream(threshold=5))

   # Conditional processing
   conditional = flow.transform(if_then_stream(condition, then_flow, else_flow))

   # Side effects
   tapped = flow.transform(tap_stream(side_effect_fn))

Observability Combinators (5 functions + 4 classes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Logging, tracing, and monitoring:

.. code-block:: python

   from flow.combinators import (
       log_stream, trace_stream, metrics_stream, inspect_stream,
       materialize_stream, OnNext, OnError, OnComplete, StreamNotification
   )

   # Log stream events
   logged = flow.transform(log_stream("Processing"))

   # Trace execution
   traced = flow.transform(trace_stream("pipeline"))

   # Collect metrics
   measured = flow.transform(metrics_stream("throughput"))

   # Inspect values
   inspected = flow.transform(inspect_stream(print))

   # Materialize notifications
   materialized = flow.transform(materialize_stream())

Advanced Combinators (10 functions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Parallel processing and advanced composition:

.. code-block:: python

   from flow.combinators import (
       parallel_stream, parallel_stream_successful, merge_stream,
       merge_flows, race_stream, zip_stream, chain_stream,
       combine_latest_stream, flat_map_ctx_stream, merge_async_generators
   )

   # Parallel processing
   parallel = flow.transform(parallel_stream(workers=4))

   # Merge multiple streams
   merged = flow.transform(merge_stream([stream1, stream2, stream3]))

   # Race multiple streams
   raced = flow.transform(race_stream([stream1, stream2]))

   # Zip streams together
   zipped = flow.transform(zip_stream([stream1, stream2]))

   # Combine latest values
   combined = flow.transform(combine_latest_stream([stream1, stream2]))

Source Combinators (4 functions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Stream creation and initialization:

.. code-block:: python

   from flow.combinators import (
       range_flow, repeat_flow, empty_flow, start_with_stream
   )

   # Create range stream
   numbers = Flow.from_iterable([]).transform(range_flow(0, 10))

   # Repeat value
   repeated = Flow.from_iterable([]).transform(repeat_flow(value, count=10))

   # Empty stream
   empty = Flow.from_iterable([]).transform(empty_flow())

   # Start with value
   started = flow.transform(start_with_stream(initial_value))

Utility Functions (2 functions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Helper functions for flow creation:

.. code-block:: python

   from flow.combinators import get_function_name, create_single_item_stream

   # Get function name for debugging
   name = get_function_name(my_function)

   # Create single item stream
   single = create_single_item_stream(value)

Usage Patterns
--------------

Simple Pipeline
~~~~~~~~~~~~~~~

.. code-block:: python

   from flow import Flow
   from flow.combinators import map_stream, filter_stream, take_stream

   # Create a simple data processing pipeline
   pipeline = (
       Flow.from_iterable(range(100))
       .transform(map_stream(lambda x: x * 2))
       .transform(filter_stream(lambda x: x % 4 == 0))
       .transform(take_stream(10))
   )

   # Process the data
   results = []
   async for item in pipeline(async_data_source()):
       results.append(item)

Robust Error Handling
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flow.combinators import (
       retry_stream, recover_stream, circuit_breaker_stream,
       catch_and_continue_stream, log_stream
   )

   # Create resilient pipeline
   robust_pipeline = (
       Flow.identity()
       .transform(log_stream("Input"))
       .transform(retry_stream(max_retries=3))
       .transform(recover_stream(fallback_processor))
       .transform(circuit_breaker_stream(threshold=5))
       .transform(catch_and_continue_stream())
       .transform(log_stream("Output"))
   )

High-Performance Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flow.combinators import (
       batch_stream, parallel_stream, buffer_stream,
       debounce_stream, throttle_stream
   )

   # High-throughput pipeline
   performance_pipeline = (
       Flow.identity()
       .transform(debounce_stream(delay=0.01))    # Debounce rapid events
       .transform(batch_stream(size=100))         # Process in batches
       .transform(buffer_stream(size=1000))       # Buffer for backpressure
       .transform(parallel_stream(workers=8))      # Parallel processing
       .transform(throttle_stream(rate=1000))     # Rate limiting
   )

Observable Pipeline
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flow.combinators import (
       log_stream, trace_stream, metrics_stream,
       inspect_stream, materialize_stream
   )

   # Fully observable pipeline
   observable_pipeline = (
       Flow.identity()
       .transform(log_stream("Start"))
       .transform(trace_stream("processing"))
       .transform(metrics_stream("throughput"))
       .transform(inspect_stream(lambda x: print(f"Processing: {x}")))
       .transform(materialize_stream())
       .transform(log_stream("Complete"))
   )

Type Safety
-----------

The Flow Engine maintains strict type safety throughout the pipeline:

Generic Type Preservation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from typing import TypeVar
   from flow import Flow

   T = TypeVar('T')
   R = TypeVar('R')

   # Type-safe transformations
   def typed_pipeline(flow: Flow[T]) -> Flow[R]:
       return (
           flow
           .map(transform_fn)      # T -> R
           .filter(type_guard)     # R -> R
           .take(10)               # R -> R
       )

   # MyPy and Pyright will enforce type correctness
   numbers: Flow[int] = Flow.from_iterable([1, 2, 3])
   strings: Flow[str] = typed_pipeline(numbers)  # int -> str

Error Handling Types
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flow.exceptions import (
       FlowError, FlowExecutionError, FlowTimeoutError,
       FlowValidationError, FlowConfigurationError
   )

   try:
       result = await flow.run()
   except FlowExecutionError as e:
       # Handle execution errors
       logger.error(f"Flow execution failed: {e}")
   except FlowTimeoutError as e:
       # Handle timeout errors
       logger.error(f"Flow timed out: {e}")
   except FlowValidationError as e:
       # Handle validation errors
       logger.error(f"Flow validation failed: {e}")

Performance Considerations
--------------------------

Memory Efficiency
~~~~~~~~~~~~~~~~~

The Flow Engine uses async iterators for memory-efficient stream processing:

.. code-block:: python

   # Memory-efficient processing of large datasets
   large_dataset = Flow.from_iterable(range(1_000_000))

   # Processes one item at a time, not loading entire dataset
   async for item in large_dataset.map(expensive_operation):
       process_item(item)

Async Performance
~~~~~~~~~~~~~~~~~

Built for high-concurrency scenarios:

.. code-block:: python

   # Concurrent processing with multiple workers
   concurrent_pipeline = (
       Flow.identity()
       .transform(parallel_stream(workers=10))
       .transform(batch_stream(size=50))
   )

   # Efficient async iteration
   async for batch in concurrent_pipeline(async_data_source()):
       await process_batch_async(batch)

Benchmarking
~~~~~~~~~~~~

.. code-block:: python

   import time
   from flow.combinators import metrics_stream

   # Benchmark pipeline performance
   benchmarked = (
       Flow.identity()
       .transform(metrics_stream("pipeline_performance"))
       .tap(lambda x: time.time())  # Add timing
   )

Best Practices
--------------

1. **Use Type Hints**: Always provide complete type annotations
2. **Compose Small Functions**: Build complex pipelines from simple components
3. **Handle Errors Gracefully**: Use retry, recover, and circuit breaker patterns
4. **Monitor Performance**: Use observability combinators for monitoring
5. **Test Thoroughly**: Test individual combinators and complete pipelines
6. **Keep Functions Pure**: Avoid side effects in transformation functions
7. **Use Async Appropriately**: Leverage async for I/O-bound operations

Testing
-------

Test Individual Combinators
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pytest
   from flow import Flow
   from flow.combinators import map_stream

   @pytest.mark.asyncio
   async def test_map_stream():
       # Test map combinator
       flow = Flow.from_iterable([1, 2, 3]).transform(map_stream(lambda x: x * 2))
       result = [item async for item in flow]
       assert result == [2, 4, 6]

Test Complete Pipelines
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   @pytest.mark.asyncio
   async def test_complete_pipeline():
       # Test end-to-end pipeline
       pipeline = (
           Flow.from_iterable(range(10))
           .transform(map_stream(lambda x: x * 2))
           .transform(filter_stream(lambda x: x > 5))
           .transform(take_stream(3))
       )

       result = [item async for item in pipeline]
       assert result == [6, 8, 10]

Performance Testing
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import time
   import pytest

   @pytest.mark.benchmark
   async def test_pipeline_performance():
       start_time = time.time()

       pipeline = Flow.from_iterable(range(1000)).transform(
           map_stream(lambda x: x * 2)
       )

       result = [item async for item in pipeline]

       end_time = time.time()
       assert end_time - start_time < 0.1  # Should complete in < 100ms
       assert len(result) == 1000