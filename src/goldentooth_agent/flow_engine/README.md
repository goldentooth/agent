# Flow Engine

Flow Engine module

## Overview

- **Complexity**: Medium
- **Files**: 5 Python files
- **Lines of Code**: ~692
- **Classes**: 5
- **Functions**: 35

## API Reference

### Classes

#### ContextKeyProtocol
Protocol for context keys that can store typed values.

**Public Methods:**
- `name()`
- `value_type()`

#### ContextProtocol
Protocol for context objects that can store keyed values.

**Public Methods:**
- `get()`
- `set()`
- `contains()`

#### FlowProtocol
Protocol for Flow objects to avoid concrete dependencies.

**Public Methods:**
- `name()`

#### FlowExtensionRegistry
Registry for Flow extensions that can be added without circular imports.

**Public Methods:**
- `register_extension()`
- `register_method_extension()`
- `register_initialization_hook()`
- `get_extension()`
- `get_method_extension()`
- `extend_flow_class()`

#### TrampolineFlowCombinators
Flow combinators for trampoline-style execution patterns.

**Public Methods:**
- `set_should_exit()`
- `set_should_break()`
- `set_should_skip()`
- `check_should_exit()`
- `check_should_break()`
- `check_should_skip()`
- `clear_break_flag()`
- `clear_skip_flag()`
- `exitable_chain()`
- `trampoline()`
- `trampoline_chain()`
- `conditional_flow()`
- `skip_if()`

### Functions

#### `def register_flow_extension(name: str) -> Callable[[ExtensionFunction], ExtensionFunction]`
Decorator to register flow extensions.

#### `def register_flow_method(method_name: str) -> Callable[[ExtensionFunction], ExtensionFunction]`
Decorator to register flow method extensions.

#### `def get_context_module() -> Any`
Lazily import the context module to avoid circular imports.

#### `def get_context_key_class() -> type[ContextKey]`
Lazily get the ContextKey class.

#### `def get_context_class() -> type[Context]`
Lazily get the Context class.

#### `def create_context_key(name: str, value_type: type[T], description: str) -> ContextKey[T]`
Create a context key without direct import.

#### `def extend_flow_with_trampoline() -> None`
Extend Flow class with trampoline manipulation methods.

### Constants

#### `T`

#### `K`

#### `V`

#### `T`

#### `T`

#### `SHOULD_EXIT_KEY`

#### `SHOULD_BREAK_KEY`

#### `SHOULD_SKIP_KEY`

## Dependencies

### Internal Dependencies
- `goldentooth_agent.core.context`
- `goldentooth_agent.core.context.flow_integration`

### External Dependencies
- `__future__`
- `collections`
- `combinators`
- `core`
- `importlib`
- `integrations`
- `observability`
- `registry`
- `trampoline`
- `typing`

## Exports

This module exports the following symbols:

- `Flow`
- `FlowAnalyzer`
- `FlowConfigValidator`
- `FlowConfigurationError`
- `FlowDebugger`
- `FlowEdge`
- `FlowError`
- `FlowExecutionContext`
- `FlowExecutionError`
- `FlowGraph`
- `FlowHealthMonitor`
- `FlowMetrics`
- `FlowNode`
- `FlowRegistry`
- `FlowTimeoutError`
- `FlowValidationError`
- `HealthCheck`
- `HealthCheckResult`
- `HealthStatus`
- `OnComplete`
- `OnError`
- `OnNext`
- `PerformanceMonitor`
- `SHOULD_BREAK_KEY`
- `SHOULD_EXIT_KEY`
- `SHOULD_SKIP_KEY`
- `StreamNotification`
- `SystemHealth`
- `TrampolineFlowCombinators`
- `add_flow_breakpoint`
- `analyze_flow`
- `analyze_flow_composition`
- `batch_stream`
- `benchmark_stream`
- `branch_flows`
- `buffer_stream`
- `catch_and_continue_stream`
- `chain_flows`
- `chain_stream`
- `check_system_health`
- `chunk_stream`
- `circuit_breaker_stream`
- `collect_stream`
- `combine_latest_stream`
- `compose`
- `debounce_stream`
- `debug_session`
- `debug_stream`
- `delay_stream`
- `detect_flow_patterns`
- `disable_flow_debugging`
- `distinct_stream`
- `empty_flow`
- `enable_flow_debugging`
- `enable_memory_tracking`
- `expand_stream`
- `export_execution_trace`
- `export_flow_analysis`
- `export_health_report`
- `export_performance_metrics`
- `extend_flow_with_trampoline`
- `filter_stream`
- `finalize_stream`
- `flat_map_ctx_stream`
- `flat_map_stream`
- `flatten_stream`
- `flow_registry`
- `generate_flow_optimizations`
- `get_config_validator`
- `get_execution_trace`
- `get_flow`
- `get_flow_analyzer`
- `get_flow_debugger`
- `get_health_monitor`
- `get_performance_monitor`
- `get_performance_summary`
- `group_by_stream`
- `guard_stream`
- `health_check_stream`
- `identity_stream`
- `if_then_stream`
- `initialize_context_integration`
- `inspect_flow`
- `inspect_stream`
- `list_flows`
- `log_stream`
- `map_stream`
- `materialize_stream`
- `memoize_stream`
- `merge_flows`
- `merge_stream`
- `metrics_stream`
- `monitored_stream`
- `pairwise_stream`
- `parallel_stream`
- `parallel_stream_successful`
- `performance_stream`
- `race_stream`
- `range_flow`
- `recover_stream`
- `register_flow`
- `register_health_check`
- `registered_flow`
- `remove_flow_breakpoint`
- `repeat_flow`
- `retry_stream`
- `run_fold`
- `sample_stream`
- `scan_stream`
- `search_flows`
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
- `traced_flow`
- `until_stream`
- `validate_flow_configuration`
- `while_condition_stream`
- `window_stream`
- `zip_stream`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
