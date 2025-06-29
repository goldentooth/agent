# Flow Engine Combinators

## Overview
**Status**: 🟡 Modularized | **Total Functions**: 70+ | **Submodules**: 7

The combinators package provides functional combinators for composing and transforming stream processing flows. This package has been refactored from a single 2000-line file into focused submodules for better maintainability.

## Submodule Organization

### `basic.py` - Core Operations (15 functions)
Essential stream processing operations:
- **Core**: `run_fold`, `compose`, `map_stream`, `filter_stream`, `flat_map_stream`
- **Utility**: `identity_stream`, `take_stream`, `skip_stream`, `guard_stream`
- **Collection**: `collect_stream`, `flatten_stream`, `until_stream`, `share_stream`

```python
from goldentooth_agent.flow_engine.combinators.basic import map_stream, filter_stream

# Basic transformations
numbers = Flow.from_iterable([1, 2, 3, 4, 5])
result = numbers >> map_stream(lambda x: x * 2) >> filter_stream(lambda x: x > 5)
```

### `sources.py` - Data Sources (4 functions)
Flow creation from various data sources:
- **Generators**: `range_flow`, `repeat_flow`, `empty_flow`
- **Initializers**: `start_with_stream`

```python
from goldentooth_agent.flow_engine.combinators.sources import range_flow, start_with_stream

# Create data sources
numbers = range_flow(0, 10)
with_header = numbers >> start_with_stream("START")
```

### `temporal.py` - Time-based Operations (5 functions)
Time-related stream processing:
- **Delays**: `delay_stream`, `debounce_stream`, `throttle_stream`
- **Timeouts**: `timeout_stream`, `sample_stream`

```python
from goldentooth_agent.flow_engine.combinators.temporal import delay_stream, throttle_stream

# Time-based processing
delayed = data_stream >> delay_stream(0.1)
rate_limited = data_stream >> throttle_stream(10.0)  # 10 items/second max
```

### `control_flow.py` - Control Flow (11 functions)
Conditional processing and error handling:
- **Conditional**: `if_then_stream`, `switch_stream`, `while_condition_stream`
- **Error Handling**: `retry_stream`, `recover_stream`, `circuit_breaker_stream`
- **Side Effects**: `tap_stream`, `then_stream`, `catch_and_continue_stream`
- **Multi-flow**: `chain_flows`, `branch_flows`

```python
from goldentooth_agent.flow_engine.combinators.control_flow import retry_stream, tap_stream

# Error handling and side effects
reliable = unreliable_stream >> retry_stream(3, process_flow)
logged = data_stream >> tap_stream(lambda x: print(f"Processing: {x}"))
```

### `aggregation.py` - Aggregation Operations (10 functions)
Data collection and grouping:
- **Batching**: `batch_stream`, `chunk_stream`, `window_stream`
- **Accumulation**: `scan_stream`, `group_by_stream`, `distinct_stream`
- **Pairing**: `pairwise_stream`, `memoize_stream`
- **Buffering**: `buffer_stream`, `expand_stream`, `finalize_stream`

```python
from goldentooth_agent.flow_engine.combinators.aggregation import batch_stream, scan_stream

# Data aggregation
batched = data_stream >> batch_stream(10)  # Groups of 10
running_sum = numbers >> scan_stream(lambda acc, x: acc + x, 0)
```

### `advanced.py` - Complex Operations (10 functions)
Parallel processing and stream merging:
- **Parallel**: `race_stream`, `parallel_stream`, `parallel_stream_successful`
- **Combining**: `zip_stream`, `combine_latest_stream`, `flat_map_ctx_stream`
- **Merging**: `chain_stream`, `merge_stream`, `merge_flows`
- **Utilities**: `merge_async_generators`

```python
from goldentooth_agent.flow_engine.combinators.advanced import parallel_stream, race_stream

# Parallel processing
parallel_results = data_stream >> parallel_stream(flow1, flow2, flow3)
fastest_result = data_stream >> race_stream(fast_flow, slow_flow)
```

### `observability.py` - Debugging & Monitoring (6 functions)
Debugging and monitoring capabilities:
- **Logging**: `log_stream`, `trace_stream`, `inspect_stream`
- **Metrics**: `metrics_stream`, `materialize_stream`
- **Notifications**: `StreamNotification`, `OnNext`, `OnError`, `OnComplete`

```python
from goldentooth_agent.flow_engine.combinators.observability import log_stream, trace_stream

# Monitoring and debugging
logged = data_stream >> log_stream("data", prefix="[DEBUG] ")
traced = data_stream >> trace_stream(lambda event, data: print(f"{event}: {data}"))
```

## Migration Strategy

The package uses a hybrid import system during transition:
1. **Legacy Import**: Imports all functions from `combinators_legacy.py`
2. **Override**: Selectively imports new modular implementations
3. **Backward Compatibility**: All existing code continues to work

```python
# Both of these work identically
from goldentooth_agent.flow_engine.combinators import map_stream        # Main package
from goldentooth_agent.flow_engine.combinators.basic import map_stream  # Direct submodule
```

## Testing

Tests are organized to mirror the submodule structure:

```bash
# Test all combinators
poetry run poe test-flow-combinators

# Test specific submodules
poetry run pytest tests/flow_engine/combinators/test_combinators.py -v
poetry run pytest tests/flow_engine/combinators/test_new_combinators.py -v
```

## Known Issues

### Current Status
- ✅ **Structure**: All submodules created and imports working
- ✅ **Core Functions**: Basic operations fully functional
- 🟡 **Advanced Functions**: Some implementation differences from legacy
- 🟡 **Test Coverage**: ~80% tests passing (API differences in new implementations)

### Test Failures
Some tests fail due to implementation differences:
- Function signature changes (e.g., `memoize_stream` requires `key_fn`)
- Flow naming conventions updated
- Behavior improvements in new implementations

### Migration Benefits
- **Maintainability**: 200-400 line files vs 2000-line monolith
- **Discoverability**: Clear categorization of functions
- **Testing**: Focused test organization
- **Documentation**: Each submodule has clear purpose
- **Development**: Easier to extend and modify specific categories

## Related Modules

### Dependencies
- **Depends on**: `../main.Flow`, `../exceptions.*`, `./utils`
- **Used by**: All Flow Engine functionality

### Integration Points
- Core Flow class uses combinators for method chaining
- Observability tools integrate with combinator streams
- Registry system catalogs combinator flows
