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
- `name(self) -> str` - The unique name/identifier for this context key
- `value_type(self) -> type[T]` - The type of values this key can store

#### ContextProtocol
Protocol for context objects that can store keyed values.

**Public Methods:**
- `get(self, key: ContextKeyProtocol[T]) -> T` - Get a value by key
- `set(self, key: ContextKeyProtocol[T], value: T) -> None` - Set a value by key
- `contains(self, key: ContextKeyProtocol[Any]) -> bool` - Check if key exists in context

#### FlowProtocol
Protocol for Flow objects to avoid concrete dependencies.

**Public Methods:**
- `name(self) -> str` - The name of this flow

#### FlowExtensionRegistry
Registry for Flow extensions that can be added without circular imports.

**Public Methods:**
- `register_extension(self, name: str, func: ExtensionFunction) -> None` - Register a function extension
- `register_method_extension(self, method_name: str, func: ExtensionFunction) -> None` - Register a method extension for Flow classes
- `register_initialization_hook(self, hook: Callable[[Any], None]) -> None` - Register a hook that runs when Flow classes are extended
- `get_extension(self, name: str) -> ExtensionFunction | None` - Get a registered extension
- `get_method_extension(self, method_name: str) -> ExtensionFunction | None` - Get a registered method extension
- `extend_flow_class(self, flow_class: type) -> None` - Apply all registered extensions to a Flow class

#### TrampolineFlowCombinators
Flow combinators for trampoline-style execution patterns.

**Public Methods:**
- `set_should_exit(value: bool) -> Flow[Context, Context]` - Create a Flow that sets the exit signal in the context
- `set_should_break(value: bool) -> Flow[Context, Context]` - Create a Flow that sets the break/restart signal in the context
- `set_should_skip(value: bool) -> Flow[Context, Context]` - Create a Flow that sets the skip signal in the context
- `check_should_exit() -> Flow[Context, bool]` - Create a Flow that checks if exit has been signaled
- `check_should_break() -> Flow[Context, bool]` - Create a Flow that checks if break/restart has been signaled
- `check_should_skip() -> Flow[Context, bool]` - Create a Flow that checks if skip has been signaled
- `clear_break_flag() -> Flow[Context, Context]` - Create a Flow that clears the break flag
- `clear_skip_flag() -> Flow[Context, Context]` - Create a Flow that clears the skip flag
- `exitable_chain(*flows: Flow[Context, Context]) -> Flow[Context, Context]` - Create a Flow that executes a chain of flows with exit/break checking
- `trampoline(flow: Flow[Context, Context]) -> Flow[Context, Context]` - Create a Flow that runs another flow in trampoline style until exit
- `trampoline_chain(*flows: Flow[Context, Context]) -> Flow[Context, Context]` - Create a Flow that runs a chain of flows in trampoline style
- `conditional_flow(condition_flow: Flow[Context, bool], then_flow: Flow[Context, Context], else_flow: Flow[Context, Context] | None) -> Flow[Context, Context]` - Create a Flow that conditionally executes based on a boolean flow result
- `skip_if(condition_flow: Flow[Context, bool], target_flow: Flow[Context, Context]) -> Flow[Context, Context]` - Create a Flow that skips execution of target_flow if condition is True

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
