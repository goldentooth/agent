Flow Engine Quick Reference
===========================

The Flow Engine is a functional reactive programming library providing type-safe stream processing with zero external dependencies.

Core Concepts
-------------

Flow[Input, Output]
~~~~~~~~~~~~~~~~~~~

The ``Flow`` class is the fundamental building block representing an asynchronous stream of values:

.. code-block:: python

   from flowengine import Flow
   
   # Create flows from various sources
   flow1 = Flow.from_iterable([1, 2, 3])
   flow2 = Flow.from_value_fn(lambda: 42)
   flow3 = Flow.from_sync_fn(lambda x: x * 2)

Creating Flows
--------------

Static Factory Methods
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # From a single value function
   flow = Flow.from_value_fn(lambda: "hello")
   
   # From a synchronous function
   flow = Flow.from_sync_fn(lambda x: x.upper())
   
   # From an async function
   flow = Flow.from_event_fn(async_fetch_data)
   
   # From an iterable
   flow = Flow.from_iterable([1, 2, 3, 4, 5])
   
   # From an async emitter
   flow = Flow.from_emitter(event_emitter)
   
   # Identity flow (returns input unchanged)
   flow = Flow.identity()
   
   # Pure value flow
   flow = Flow.pure(42)

Source Combinators
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flowengine.combinators import (
       range_flow, repeat_flow, empty_flow, start_with_stream
   )
   
   # Generate range of numbers
   numbers = range_flow(0, 10, 2)  # 0, 2, 4, 6, 8
   
   # Repeat a value
   repeated = repeat_flow("ping", times=3)  # "ping", "ping", "ping"
   
   # Empty flow
   nothing = empty_flow()
   
   # Prepend items to a stream
   flow = Flow.from_iterable([3, 4, 5]).pipe(
       start_with_stream(1, 2)  # 1, 2, 3, 4, 5
   )

Transforming Flows
------------------

Basic Transformations
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flowengine.combinators import (
       map_stream, filter_stream, flat_map_stream, take_stream, skip_stream
   )
   
   flow = Flow.from_iterable([1, 2, 3, 4, 5])
   
   # Map values
   doubled = flow.pipe(map_stream(lambda x: x * 2))
   
   # Filter values
   evens = flow.pipe(filter_stream(lambda x: x % 2 == 0))
   
   # Flat map (expand each value to multiple)
   expanded = flow.pipe(flat_map_stream(lambda x: [x, x * 10]))
   
   # Take first N values
   first_three = flow.pipe(take_stream(3))
   
   # Skip first N values
   skip_two = flow.pipe(skip_stream(2))

Aggregation Operations
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flowengine.combinators import (
       batch_stream, buffer_stream, scan_stream, 
       distinct_stream, pairwise_stream, window_stream
   )
   
   # Batch into groups
   batched = flow.pipe(batch_stream(size=3))
   
   # Buffer with time window
   buffered = flow.pipe(buffer_stream(count=10, timeout=1.0))
   
   # Running accumulation
   sums = flow.pipe(scan_stream(lambda acc, x: acc + x, initial=0))
   
   # Remove duplicates
   unique = flow.pipe(distinct_stream())
   
   # Consecutive pairs
   pairs = flow.pipe(pairwise_stream())  # (1,2), (2,3), (3,4), ...
   
   # Sliding window
   windowed = flow.pipe(window_stream(size=3))

Time-Based Operations
---------------------

Temporal Combinators
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flowengine.combinators import (
       delay_stream, debounce_stream, throttle_stream, 
       timeout_stream, sample_stream
   )
   
   # Delay each item
   delayed = flow.pipe(delay_stream(seconds=0.5))
   
   # Debounce rapid changes
   debounced = flow.pipe(debounce_stream(seconds=0.2))
   
   # Rate limit
   throttled = flow.pipe(throttle_stream(rate_per_second=10))
   
   # Timeout if no items
   with_timeout = flow.pipe(timeout_stream(seconds=5.0))
   
   # Sample periodically
   sampled = flow.pipe(sample_stream(interval=1.0))

Control Flow
------------

Conditional and Error Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flowengine.combinators import (
       if_then_stream, retry_stream, recover_stream,
       catch_and_continue_stream, circuit_breaker_stream
   )
   
   # Conditional processing
   processed = flow.pipe(
       if_then_stream(
           predicate=lambda x: x > 0,
           then_flow=map_stream(lambda x: x * 2),
           else_flow=map_stream(lambda x: 0)
       )
   )
   
   # Retry on failure
   reliable = flow.pipe(retry_stream(n=3, flow=api_call_flow))
   
   # Recover from errors
   safe = flow.pipe(
       recover_stream(
           recovery_fn=lambda error: Flow.pure("default"),
           error_type=ValueError
       )
   )
   
   # Continue on errors
   resilient = flow.pipe(
       catch_and_continue_stream(
           error_handler=lambda e: print(f"Error: {e}")
       )
   )
   
   # Circuit breaker pattern
   protected = flow.pipe(
       circuit_breaker_stream(
           failure_threshold=5,
           timeout=30.0,
           fallback=lambda: "service unavailable"
       )
   )

Advanced Patterns
-----------------

Parallel and Concurrent Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flowengine.combinators import (
       parallel_stream, merge_stream, zip_stream,
       race_stream, combine_latest_stream
   )
   
   # Process in parallel
   parallel = flow.pipe(
       parallel_stream(
           max_concurrency=4,
           ordered=True  # Maintain order
       )
   )
   
   # Merge multiple streams
   merged = merge_stream(flow1, flow2, flow3)
   
   # Zip streams together
   zipped = zip_stream(flow1, flow2)  # (a1, b1), (a2, b2), ...
   
   # Race streams (first to emit wins)
   fastest = race_stream(slow_api, fast_cache)
   
   # Combine latest values
   combined = combine_latest_stream(sensor1, sensor2, sensor3)

Observability
-------------

Monitoring and Debugging
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flowengine.combinators import (
       log_stream, trace_stream, metrics_stream,
       inspect_stream, materialize_stream
   )
   
   # Logging
   logged = flow.pipe(
       log_stream(
           logger=my_logger,
           message_fn=lambda x: f"Processing: {x}"
       )
   )
   
   # Tracing
   traced = flow.pipe(
       trace_stream(tracer=lambda tag, value: print(f"{tag}: {value}"))
   )
   
   # Metrics
   metered = flow.pipe(
       metrics_stream(counter=metrics.increment)
   )
   
   # Inspection
   inspected = flow.pipe(
       inspect_stream(
           on_next=lambda x: print(f"Next: {x}"),
           on_error=lambda e: print(f"Error: {e}"),
           on_complete=lambda: print("Complete")
       )
   )
   
   # Materialize notifications
   notifications = flow.pipe(materialize_stream())
   # Emits: OnNext(1), OnNext(2), OnComplete()

Performance Monitoring
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flowengine.observability import (
       PerformanceMonitor, monitored_stream, benchmark_stream
   )
   
   # Monitor performance
   monitored = flow.pipe(
       monitored_stream(
           name="data_processing",
           monitor=PerformanceMonitor()
       )
   )
   
   # Benchmark operations
   benchmarked = flow.pipe(
       benchmark_stream(
           name="transform",
           warmup_runs=10,
           benchmark_runs=100
       )
   )

Terminal Operations
-------------------

Consuming Flows
~~~~~~~~~~~~~~~

.. code-block:: python

   # Collect all values to a list
   values = await flow.to_list()
   
   # Process each value
   await flow.for_each(lambda x: print(x))
   
   # Reduce to single value
   total = await flow.reduce(lambda acc, x: acc + x, initial=0)
   
   # Get first value
   first = await flow.first()
   
   # Get last value
   last = await flow.last()
   
   # Check if any match
   has_even = await flow.any(lambda x: x % 2 == 0)
   
   # Check if all match
   all_positive = await flow.all(lambda x: x > 0)
   
   # Count items
   count = await flow.count()

Composition
-----------

Combining Flows
~~~~~~~~~~~~~~~

.. code-block:: python

   from flowengine.combinators import compose, chain_flows
   
   # Compose two flows
   transform = compose(
       filter_stream(lambda x: x > 0),
       map_stream(lambda x: x * 2)
   )
   
   # Chain multiple flows
   pipeline = chain_flows(
       filter_stream(lambda x: x > 0),
       map_stream(lambda x: x * 2),
       take_stream(10)
   )
   
   # Using pipe for composition
   result = flow.pipe(
       filter_stream(lambda x: x > 0),
       map_stream(lambda x: x * 2),
       batch_stream(size=5),
       timeout_stream(seconds=10)
   )
   
   # Using >> operator
   transform = filter_stream(lambda x: x > 0) >> map_stream(lambda x: x * 2)
   result = flow >> transform

Error Handling
--------------

Exception Types
~~~~~~~~~~~~~~~

.. code-block:: python

   from flowengine.exceptions import (
       FlowError,                # Base exception
       FlowValidationError,      # Invalid flow configuration
       FlowExecutionError,       # Runtime execution error
       FlowTimeoutError,         # Timeout occurred
       FlowConfigurationError    # Configuration error
   )
   
   try:
       result = await flow.to_list()
   except FlowTimeoutError:
       print("Flow timed out")
   except FlowExecutionError as e:
       print(f"Execution failed: {e}")

Best Practices
--------------

1. **Type Safety**: Always use type hints for better IDE support and error catching
2. **Composition**: Build complex flows from simple, reusable combinators
3. **Error Handling**: Use recover_stream or catch_and_continue_stream for resilience
4. **Performance**: Use parallel_stream for CPU-bound operations
5. **Memory**: Use streaming operations instead of collecting large datasets
6. **Testing**: Test individual combinators before composing them
7. **Debugging**: Use inspect_stream or log_stream during development

Example: Complete Pipeline
--------------------------

.. code-block:: python

   from flowengine import Flow
   from flowengine.combinators import *
   
   async def process_data(input_file: str) -> dict[str, int]:
       """Process data with comprehensive error handling and monitoring."""
       
       return await (
           Flow.from_iterable(read_lines(input_file))
           .pipe(
               # Parse and validate
               map_stream(parse_json),
               filter_stream(lambda x: x.get("valid", False)),
               
               # Transform
               map_stream(extract_metrics),
               
               # Handle errors gracefully
               catch_and_continue_stream(
                   error_handler=lambda e: logger.error(f"Failed: {e}")
               ),
               
               # Process in parallel for performance
               parallel_stream(max_concurrency=8),
               
               # Aggregate results
               scan_stream(
                   lambda acc, x: {**acc, x["key"]: acc.get(x["key"], 0) + x["value"]},
                   initial={}
               ),
               
               # Add timeout protection
               timeout_stream(seconds=30),
               
               # Monitor performance
               inspect_stream(
                   on_complete=lambda: logger.info("Processing complete")
               )
           )
           .last()  # Get final aggregated result
       )