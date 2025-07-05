System Overview
===============

Migration Status
----------------

**Flow Engine Migration: Epic 13 Complete ✅**

The Goldentooth Agent has **completed** its comprehensive migration to a new functional reactive system built on the Flow Engine. The migration represents a complete transformation from legacy architecture to a modern, type-safe, and highly performant system.

Current Architecture (Migration Complete)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   src/
   ├── flowengine/                    # Flow Engine (COMPLETE ✅)
   │   ├── __init__.py               # Package exports
   │   ├── flow.py                   # Core Flow class (23+ methods)
   │   ├── exceptions.py             # Flow-specific errors 
   │   ├── protocols.py              # Type protocols
   │   ├── observability/            # Performance monitoring
   │   │   ├── __init__.py          # Observability exports
   │   │   ├── analysis.py          # Performance analysis
   │   │   └── performance.py       # Performance metrics
   │   ├── combinators/              # 67+ stream processing functions
   │   │   ├── __init__.py          # Combinator exports
   │   │   ├── advanced.py          # Advanced combinators (10 functions)
   │   │   ├── aggregation.py       # Aggregation combinators (11 functions)
   │   │   ├── basic.py             # Basic combinators (13 functions)
   │   │   ├── control_flow.py      # Control flow combinators (11 functions)
   │   │   ├── observability.py     # Observability combinators (5 functions + 4 classes)
   │   │   ├── sources.py           # Source combinators (4 functions)
   │   │   ├── temporal.py          # Temporal combinators (5 functions)
   │   │   └── utils.py             # Utility functions (2 functions)
   │   └── py.typed                  # Type marker
   ├── git_hooks/                    # Development tooling
   │   ├── cli.py                   # Quality assurance CLI
   │   ├── core.py                  # Hook utilities
   │   ├── config.py                # Configuration management
   │   └── __init__.py              # Package exports
   └── goldentooth_agent/            # Agent core
       ├── cli/                     # CLI interface
       │   ├── __init__.py         # CLI exports
       │   └── main.py             # CLI entry point
       ├── core/                    # Core agent functionality
       │   ├── __init__.py         # Core exports
       │   └── background_loop/    # Background processing
       └── __init__.py              # Package exports

Flow Engine Features (Complete)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**✅ Migration Complete - All 13 Epics:**

**Epic 1-4: Core Infrastructure**
* Package structure and initialization
* Exception handling system
* Type protocols and interfaces
* Core Flow class with 23+ methods

**Epic 5: Utils (2 functions)**
* ``get_function_name`` - Function name extraction
* ``create_single_item_stream`` - Single item stream creation

**Epic 6: Sources (4 functions)**
* ``range_flow`` - Range-based stream generation
* ``repeat_flow`` - Repeating value streams
* ``empty_flow`` - Empty stream creation
* ``start_with_stream`` - Stream initialization

**Epic 7: Basic Combinators (13 functions)**
* ``map_stream`` - Transform stream values
* ``filter_stream`` - Filter stream values
* ``compose`` - Function composition
* ``collect_stream`` - Collect stream to list
* ``guard_stream`` - Type guard filtering
* ``flatten_stream`` - Flatten nested streams
* ``take_stream`` - Take first N items
* ``skip_stream`` - Skip first N items
* ``until_stream`` - Stream until condition
* ``share_stream`` - Share stream across consumers
* ``identity_stream`` - Identity transformation
* ``flat_map_stream`` - Flat map transformation
* ``run_fold`` - Fold stream to single value

**Epic 9: Aggregation Combinators (11 functions)**
* ``batch_stream`` - Batch stream items
* ``buffer_stream`` - Buffer stream with backpressure
* ``chunk_stream`` - Chunk stream into groups
* ``distinct_stream`` - Remove duplicate items
* ``expand_stream`` - Expand stream items
* ``finalize_stream`` - Finalize stream processing
* ``group_by_stream`` - Group stream by key
* ``memoize_stream`` - Cache stream results
* ``pairwise_stream`` - Pair consecutive items
* ``scan_stream`` - Scan stream with accumulator
* ``window_stream`` - Sliding window processing

**Epic 10: Temporal Combinators (5 functions)**
* ``debounce_stream`` - Debounce stream events
* ``throttle_stream`` - Throttle stream rate
* ``delay_stream`` - Delay stream processing
* ``timeout_stream`` - Timeout stream operations
* ``sample_stream`` - Sample stream at intervals

**Epic 11: Observability Combinators (5 functions + 4 classes)**
* ``log_stream`` - Log stream events
* ``trace_stream`` - Trace stream execution
* ``metrics_stream`` - Collect stream metrics
* ``inspect_stream`` - Inspect stream values
* ``materialize_stream`` - Materialize stream notifications
* ``OnNext``, ``OnError``, ``OnComplete``, ``StreamNotification`` - Notification classes

**Epic 12: Control Flow Combinators (11 functions)**
* ``retry_stream`` - Retry failed operations
* ``recover_stream`` - Recover from errors
* ``circuit_breaker_stream`` - Circuit breaker pattern
* ``if_then_stream`` - Conditional processing
* ``switch_stream`` - Switch between streams
* ``tap_stream`` - Side-effect processing
* ``while_condition_stream`` - While loop streams
* ``then_stream`` - Sequential processing
* ``catch_and_continue_stream`` - Error handling
* ``chain_flows`` - Chain multiple flows
* ``branch_flows`` - Branch flow processing

**Epic 13: Advanced Combinators (10 functions)**
* ``parallel_stream`` - Parallel stream processing
* ``parallel_stream_successful`` - Parallel with success filtering
* ``merge_stream`` - Merge multiple streams
* ``merge_flows`` - Merge flow compositions
* ``race_stream`` - Race multiple streams
* ``zip_stream`` - Zip multiple streams
* ``chain_stream`` - Chain stream operations
* ``combine_latest_stream`` - Combine latest values
* ``flat_map_ctx_stream`` - Flat map with context
* ``merge_async_generators`` - Merge async generators

**Migration Statistics:**
* ✅ **67+ combinators** implemented with full type safety
* ✅ **150+ test cases** with 96%+ test coverage
* ✅ **100% type safety** - Full Pyright/MyPy compliance
* ✅ **Zero dependencies** - Standalone flowengine package
* ✅ **33 source files** with comprehensive functionality
* ✅ **50 test files** covering all functionality

Flow Engine Architecture
~~~~~~~~~~~~~~~~~~~~~~~~

**Core Design Principles:**

* **Type-safe composition** - Full generic type preservation through transformations
* **Functional patterns** - Identity, pure values, and monadic operations
* **Static factory methods** - Multiple ways to create flows from various sources
* **Async streaming** - Built on async iterators for efficient stream processing
* **Comprehensive testing** - 150+ test cases with full coverage
* **Zero dependencies** - No external dependencies for core functionality

**Performance Characteristics:**

* **Low overhead** - <50ms overhead per flow stage
* **Memory efficient** - Streaming with minimal memory footprint
* **Async-first** - Built for high-concurrency scenarios
* **Composable** - Complex pipelines from simple building blocks

Development Standards
---------------------

Type Safety Requirements
~~~~~~~~~~~~~~~~~~~~~~~

This project maintains **strict type safety**. All code must pass both ``mypy --strict`` and Pylance checks.

Required annotations:

.. code-block:: python

   # ✅ Required: Complete function annotations
   def process_data(items: list[str], count: int = 10) -> dict[str, Any]:
       """Process data with proper typing."""
       ...

   # ✅ Required: Optional for nullable parameters
   def create_flow(fn: Optional[Callable[[Input], Output]] = None) -> Flow:
       ...

   # ✅ Required: Generic type variables
   T = TypeVar("T")
   R = TypeVar("R")
   
   def transform(flow: Flow[T], fn: Callable[[T], R]) -> Flow[R]:
       ...

Testing Standards
~~~~~~~~~~~~~~~~~

* **Coverage**: Minimum 85% overall, 90% for new code
* **Speed**: Unit tests <100ms, integration tests <1s
* **TDD**: Test-driven development practices
* **API Focus**: Test behavior through public APIs, not implementation details
* **Comprehensive**: 50 test files covering all functionality

Performance Guidelines
~~~~~~~~~~~~~~~~~~~~~~

Critical performance areas:

* **Flow execution**: <50ms overhead per flow stage
* **Stream processing**: Memory-efficient async iteration
* **Type checking**: Full static analysis without runtime overhead
* **Test suite**: <60s for full test run

Quality Assurance
~~~~~~~~~~~~~~~~~

* **Pre-commit hooks**: Code formatting, linting, and type checking
* **File size validation**: Maximum file sizes enforced
* **Module complexity**: Module size and complexity monitoring
* **Documentation**: Comprehensive docstrings and RST documentation

Usage Examples
~~~~~~~~~~~~~~

**Basic Flow Composition:**

.. code-block:: python

   from flowengine import Flow
   
   # Create flows from functions
   double_flow = Flow.from_sync_fn(lambda x: x * 2)
   filter_even = Flow.identity().filter(lambda x: x % 2 == 0)
   
   # Compose flows
   pipeline = double_flow >> filter_even

**Advanced Stream Processing:**

.. code-block:: python

   from flowengine.combinators import (
       batch_stream, debounce_stream, parallel_stream,
       retry_stream, circuit_breaker_stream
   )
   
   # Create robust data processing pipeline
   pipeline = (
       Flow.identity()
       .transform(debounce_stream(delay=0.1))
       .transform(batch_stream(size=10))
       .transform(parallel_stream(workers=4))
       .transform(retry_stream(max_retries=3))
       .transform(circuit_breaker_stream(threshold=5))
   )

**Error Handling and Observability:**

.. code-block:: python

   from flowengine.combinators import (
       log_stream, trace_stream, metrics_stream,
       recover_stream, materialize_stream
   )
   
   # Observable and resilient pipeline
   pipeline = (
       Flow.identity()
       .transform(log_stream("Processing"))
       .transform(trace_stream("pipeline"))
       .transform(metrics_stream("throughput"))
       .transform(recover_stream(fallback_fn))
       .transform(materialize_stream())
   )
