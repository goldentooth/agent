# Flow Engine Migration Plans - Part 1: Foundation & Core Combinators

## Phase 1: Foundation Infrastructure (Epics 1-8)

### Epic 1: Create flowengine package structure
**Unit**: Package initialization
**Files Created**:
- `src/flowengine/__init__.py` (empty initially)
- `src/flowengine/py.typed` (empty marker file)
- `tests/flowengine/__init__.py` (empty)

**pyproject.toml Changes**:
```toml
[tool.poetry]
packages = [
    { include = "goldentooth_agent", from = "src" },
    { include = "git_hooks", from = "src" },
    { include = "flowengine", from = "src" }  # ADD THIS LINE
]
```

**Tests**: Basic import test in `tests/flowengine/test_package_structure.py`
```python
def test_flowengine_package_imports():
    """Test that flowengine package can be imported."""
    import flowengine
    assert flowengine is not None
```

**Dependencies**: None
**Coverage**: 100% (trivial)

---

### Epic 2: Migrate core exceptions
**Unit**: Exception classes
**Source**: `old/goldentooth_agent/flow_engine/core/exceptions.py` (31 lines)
**Target**: `src/flowengine/exceptions.py`

**Classes to migrate**:
1. `FlowError(Exception)` - Base flow exception
2. `FlowValidationError(FlowError)` - Validation failures
3. `FlowExecutionError(FlowError)` - Runtime execution errors
4. `FlowTimeoutError(FlowError)` - Timeout conditions
5. `FlowConfigurationError(FlowError)` - Configuration issues

**Test file**: `tests/flowengine/test_exceptions.py`
**Test coverage**:
- Exception instantiation
- Exception inheritance hierarchy
- Error message preservation
- Exception chaining

**Dependencies**: None
**Coverage**: 100% - all exception paths

---

### Epic 3: Migrate protocols
**Unit**: Protocol definitions
**Source**: `old/goldentooth_agent/flow_engine/protocols.py` (56 lines)
**Target**: `src/flowengine/protocols.py`

**Protocols to migrate**:
1. `ContextKeyProtocol[T]` - Typed context key interface
2. `ContextProtocol` - Context storage interface
3. `FlowProtocol[T, V]` - Flow execution interface

**Test file**: `tests/flowengine/test_protocols.py`
**Test coverage**:
- Protocol compliance checking with `isinstance()`
- Protocol method signatures
- Generic type parameter handling
- Runtime checkable behavior

**Dependencies**: None
**Coverage**: 100% - all protocol methods and properties

---

### Epic 4: Migrate core Flow class
**Unit**: Core Flow class
**Source**: `old/goldentooth_agent/flow_engine/core/flow.py` (342 lines)
**Target**: `src/flowengine/flow.py`

**Flow class methods to migrate**:
1. `__init__(fn, name, metadata)` - Flow constructor ✅ DONE
2. `__call__(stream)` - Flow execution ✅ DONE
3. `__repr__()` - Debug representation ✅ DONE
4. `__aiter__()` - Prevent direct iteration ✅ DONE
5. `__rshift__(other)` - Flow composition operator ✅ DONE
6. `map(fn)` - Transform output values ✅ DONE
7. `filter(predicate)` - Filter output values ✅ DONE
8. `flat_map(fn)` - Flatten mapped results ✅ DONE
9. `for_each(fn)` - Consume flow with side effects ✅ DONE
10. `to_list()` - Collect to list ✅ DONE
11. `collect()` - Alias for to_list
12. `label(label)` - Add debug labels
13. `preview(stream, limit)` - REPL-friendly preview
14. `print()` - Chainable debug printing
15. `with_fallback(default)` - Default value handling
16. `batch(size)` - Batch output into groups

**Static factory methods**:
17. `from_value_fn(fn)` - Create from async value function
18. `from_sync_fn(fn)` - Create from sync function
19. `from_event_fn(fn)` - Create from async iterator function
20. `from_iterable(iterable)` - Create from iterable
21. `from_emitter(register)` - Create from callback emitter
22. `identity()` - Identity flow
23. `pure(value)` - Single value flow

**Test file**: `tests/flowengine/test_flow.py`
**Test coverage**:
- All 23 methods with multiple scenarios each
- Generic type parameter preservation
- Error conditions and edge cases
- Async iterator behavior
- Method chaining
- Metadata handling

**Dependencies**: `flowengine.exceptions`
**Coverage**: 100% - all methods, all branches, all error paths

---

### Epic 5: Migrate combinator utilities
**Unit**: Combinator helper functions
**Source**: `old/goldentooth_agent/flow_engine/combinators/utils.py` (28 lines)
**Target**: `src/flowengine/combinators/utils.py`

**Functions to migrate**:
1. `get_function_name(fn)` - Extract function name for debugging
2. `create_single_item_stream(item)` - Create stream with single item

**Directory creation**: `src/flowengine/combinators/__init__.py` (empty initially)

**Test file**: `tests/flowengine/combinators/test_utils.py`
**Test coverage**:
- Function name extraction for various function types
- Lambda function name handling
- Single item stream creation and consumption
- Edge cases (None values, empty streams)

**Dependencies**: None
**Coverage**: 100% - all utility functions

---

### Epic 6: Migrate sources combinators
**Unit**: Source flow generators
**Source**: `old/goldentooth_agent/flow_engine/combinators/sources.py` (85 lines)
**Target**: `src/flowengine/combinators/sources.py`

**Functions to migrate**:
1. `range_flow(start, end, step)` - Generate numeric range
2. `repeat_flow(value, count)` - Repeat value N times
3. `empty_flow()` - Empty flow generator

**Test file**: `tests/flowengine/combinators/test_sources.py`
**Test coverage**:
- Range generation with various parameters
- Repeat with different value types
- Empty flow behavior
- Edge cases (negative ranges, zero counts)
- Large range handling

**Dependencies**: `flowengine.flow`, `flowengine.combinators.utils`
**Coverage**: 100% - all source generators

---

### Epic 7: Migrate basic combinators
**Unit**: Fundamental stream operations
**Source**: `old/goldentooth_agent/flow_engine/combinators/basic.py` (231 lines)
**Target**: `src/flowengine/combinators/basic.py`

**Functions to migrate** (23 functions):
1. `run_fold(initial_stream, steps)` - Sequential flow execution
2. `compose(*flows)` - Flow composition
3. `filter_stream(predicate)` - Stream filtering
4. `map_stream(fn)` - Stream mapping
5. `flat_map_stream(fn)` - Stream flat mapping
6. `flat_map_ctx_stream(fn)` - Context-aware flat mapping
7. `identity_stream()` - Pass-through stream
8. `log_stream(label, level)` - Debug logging
9. `if_then_stream(condition, then_flow, else_flow)` - Conditional execution
10. `tap_stream(fn)` - Side effect execution
11. `then_stream(fn)` - Sequential transformation
12. `delay_stream(seconds)` - Add delays
13. `recover_stream(fn)` - Error recovery
14. `guard_stream(predicate, error_fn)` - Validation guards
15. `take_stream(count)` - Take first N items
16. `skip_stream(count)` - Skip first N items
17. `collect_stream()` - Collect to list
18. `flatten_stream()` - Flatten nested iterators
19. `share_stream()` - Share stream across consumers
20. `until_stream(predicate)` - Take until condition
21. `chain_flows(*flows)` - Chain multiple flows
22. `branch_flows(flows)` - Branch to multiple flows
23. `merge_flows(*flows)` - Merge multiple flows

**Test file**: `tests/flowengine/combinators/test_basic.py`
**Test coverage**:
- Each function with multiple input scenarios
- Error conditions and exception handling
- Async iterator behavior
- Stream composition patterns
- Edge cases (empty streams, None values)

**Dependencies**: `flowengine.flow`, `flowengine.exceptions`, `flowengine.combinators.utils`
**Coverage**: 100% - all 23 functions, all branches

---

### Epic 8: Create basic combinators __init__.py
**Unit**: Basic combinators module exports
**Target**: `src/flowengine/combinators/__init__.py` (partial)

**Exports to add**:
```python
from .utils import get_function_name, create_single_item_stream
from .sources import range_flow, repeat_flow, empty_flow
from .basic import (
    run_fold, compose, filter_stream, map_stream, flat_map_stream,
    flat_map_ctx_stream, identity_stream, log_stream, if_then_stream,
    tap_stream, then_stream, delay_stream, recover_stream, guard_stream,
    take_stream, skip_stream, collect_stream, flatten_stream, share_stream,
    until_stream, chain_flows, branch_flows, merge_flows
)

__all__ = [
    # Utils
    "get_function_name", "create_single_item_stream",
    # Sources
    "range_flow", "repeat_flow", "empty_flow",
    # Basic combinators (23 functions)
    "run_fold", "compose", "filter_stream", "map_stream", "flat_map_stream",
    "flat_map_ctx_stream", "identity_stream", "log_stream", "if_then_stream",
    "tap_stream", "then_stream", "delay_stream", "recover_stream", "guard_stream",
    "take_stream", "skip_stream", "collect_stream", "flatten_stream", "share_stream",
    "until_stream", "chain_flows", "branch_flows", "merge_flows"
]
```

**Test updates**: Verify imports work correctly
**Dependencies**: All previous combinator modules
**Coverage**: 100% - import verification

---

## Phase 2: Core Combinators (Epics 9-14)

### Epic 9: Migrate aggregation combinators
**Unit**: Stream aggregation operations
**Source**: `old/goldentooth_agent/flow_engine/combinators/aggregation.py` (360 lines)
**Target**: `src/flowengine/combinators/aggregation.py`

**Functions to migrate** (15 functions):
1. `batch_stream(size)` - Batch items into groups
2. `debounce_stream(delay)` - Debounce rapid events
3. `throttle_stream(interval)` - Throttle event rate
4. `window_stream(size, step)` - Sliding window
5. `chunk_stream(size)` - Fixed-size chunks
6. `group_by_stream(key_fn)` - Group by key function
7. `distinct_stream(key_fn)` - Remove duplicates
8. `pairwise_stream()` - Emit pairs of consecutive items
9. `scan_stream(fn, initial)` - Accumulate with function
10. `buffer_stream(time, count)` - Buffer by time or count
11. `sample_stream(interval)` - Sample at intervals
12. `combine_latest_stream(*streams)` - Combine latest values
13. `zip_stream(*streams)` - Zip multiple streams
14. `merge_stream(*streams)` - Merge multiple streams
15. `start_with_stream(*values)` - Prepend values

**Test file**: `tests/flowengine/combinators/test_aggregation.py`
**Test coverage**:
- Each aggregation function with various inputs
- Timing-based functions with different intervals
- Window and buffering operations
- Multi-stream operations
- Edge cases (empty streams, single items)

**Dependencies**: `flowengine.flow`, `flowengine.combinators.basic`
**Coverage**: 100% - all 15 functions, all timing scenarios

---

### Epic 10: Migrate temporal combinators
**Unit**: Time-based stream operations
**Source**: `old/goldentooth_agent/flow_engine/combinators/temporal.py` (160 lines)
**Target**: `src/flowengine/combinators/temporal.py`

**Functions to migrate** (8 functions):
1. `delay_stream(seconds)` - Add delays between items
2. `timeout_stream(seconds)` - Timeout individual operations
3. `interval_stream(seconds)` - Emit at regular intervals
4. `debounce_stream(delay)` - Debounce rapid events
5. `throttle_stream(rate)` - Rate limiting
6. `sample_stream(interval)` - Periodic sampling
7. `buffer_time_stream(duration)` - Time-based buffering
8. `take_until_time_stream(duration)` - Time-limited taking

**Test file**: `tests/flowengine/combinators/test_temporal.py`
**Test coverage**:
- Time-based operations with various durations
- Timeout scenarios and error handling
- Interval and sampling behavior
- Async timing accuracy
- Edge cases (zero delays, very long timeouts)

**Dependencies**: `flowengine.flow`, `flowengine.combinators.basic`
**Coverage**: 100% - all timing functions, timeout scenarios

---

### Epic 11: Migrate observability combinators
**Unit**: Debug and monitoring combinators
**Source**: `old/goldentooth_agent/flow_engine/combinators/observability.py` (197 lines)
**Target**: `src/flowengine/combinators/observability.py`

**Functions to migrate** (10 functions):
1. `trace_stream(label)` - Trace flow execution
2. `metrics_stream(collector)` - Collect metrics
3. `inspect_stream(inspector)` - Inspect values
4. `log_stream(level, label)` - Logging integration
5. `debug_stream(breakpoint_fn)` - Debug breakpoints
6. `profile_stream(profiler)` - Performance profiling
7. `measure_stream()` - Measure throughput
8. `count_stream()` - Count items
9. `time_stream()` - Add timestamps
10. `finalize_stream(cleanup_fn)` - Cleanup on completion

**Test file**: `tests/flowengine/combinators/test_observability.py`
**Test coverage**:
- Debug tracing and logging
- Metrics collection and aggregation
- Performance measurement
- Cleanup and finalization
- Integration with various loggers/profilers

**Dependencies**: `flowengine.flow`
**Coverage**: 100% - all observability functions

---

### Epic 12: Migrate control flow combinators (without context)
**Unit**: Control flow operations (context-independent parts)
**Source**: `old/goldentooth_agent/flow_engine/combinators/control_flow.py` (419 lines)
**Target**: `src/flowengine/combinators/control_flow.py`

**Functions to migrate** (12 functions, context features temporarily removed):
1. `retry_stream(max_attempts, delay)` - Retry on failure
2. `circuit_breaker_stream(threshold, timeout)` - Circuit breaker pattern
3. `catch_and_continue_stream(handler)` - Error handling
4. `switch_stream(selector)` - Switch between streams
5. `race_stream(*streams)` - Race multiple streams
6. `parallel_stream(concurrency)` - Parallel execution
7. `parallel_stream_successful(streams)` - Parallel with success tracking
8. `while_condition_stream(condition)` - Conditional looping
9. `expand_stream(fn, max_depth)` - Recursive expansion
10. `materialize_stream()` - Materialize notifications
11. `finalize_stream(cleanup)` - Resource cleanup
12. `memoize_stream(key_fn)` - Result memoization

**Context-dependent features removed temporarily**:
- Context-aware retry strategies
- Context-based circuit breaker state
- Context propagation in parallel execution

**Test file**: `tests/flowengine/combinators/test_control_flow.py`
**Test coverage**:
- Retry mechanisms with various failure scenarios
- Circuit breaker state transitions
- Error handling and recovery
- Parallel execution patterns
- Resource cleanup verification

**Dependencies**: `flowengine.flow`, `flowengine.exceptions`
**Coverage**: 100% - all control flow functions (minus context features)

---

### Epic 13: Migrate advanced combinators
**Unit**: Complex stream operations
**Source**: `old/goldentooth_agent/flow_engine/combinators/advanced.py` (474 lines)
**Target**: `src/flowengine/combinators/advanced.py`

**Functions to migrate** (18 functions):
1. `expand_stream(fn, max_depth)` - Recursive stream expansion
2. `materialize_stream()` - Convert to notification objects
3. `dematerialize_stream()` - Convert from notifications
4. `publish_stream()` - Hot stream conversion
5. `ref_count_stream()` - Reference counting
6. `replay_stream(buffer_size)` - Replay buffering
7. `share_replay_stream(buffer_size)` - Shared replay
8. `multicast_stream(selector)` - Multicast to subscribers
9. `partition_stream(predicate)` - Partition into two streams
10. `group_by_stream(key_selector)` - Group by key
11. `window_toggle_stream(openings, closings)` - Toggle-based windowing
12. `window_when_stream(boundary_selector)` - Boundary-based windowing
13. `exhaust_map_stream(fn)` - Exhaust previous inner streams
14. `concat_map_stream(fn)` - Concatenate inner streams
15. `merge_map_stream(fn, concurrent)` - Merge with concurrency
16. `switch_map_stream(fn)` - Switch to latest inner stream
17. `catch_error_stream(selector)` - Error catching with selector
18. `on_error_resume_next_stream(*streams)` - Resume on error

**Test file**: `tests/flowengine/combinators/test_advanced.py`
**Test coverage**:
- Advanced streaming patterns
- Error recovery scenarios
- Resource management
- Concurrency control
- Complex composition patterns

**Dependencies**: `flowengine.flow`, `flowengine.combinators.basic`
**Coverage**: 100% - all 18 advanced functions

---

### Epic 14: Complete combinators __init__.py
**Unit**: Complete combinator module exports
**Source**: `old/goldentooth_agent/flow_engine/combinators/__init__.py` (171 lines)
**Target**: `src/flowengine/combinators/__init__.py` (complete)

**Complete export list** (68 total exports):
```python
from .utils import get_function_name, create_single_item_stream
from .sources import range_flow, repeat_flow, empty_flow
from .basic import (
    # 23 basic combinators
)
from .aggregation import (
    # 15 aggregation combinators
)
from .temporal import (
    # 8 temporal combinators
)
from .observability import (
    # 10 observability combinators
)
from .control_flow import (
    # 12 control flow combinators
)
from .advanced import (
    # 18 advanced combinators
)

__all__ = [
    # All 68 combinator functions
]
```

**Test updates**: Complete integration tests for all combinators
**Dependencies**: All combinator modules
**Coverage**: 100% - complete combinator API verification
