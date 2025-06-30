# Observability

Observability module

## Overview

- **Complexity**: High
- **Files**: 5 Python files
- **Lines of Code**: ~1693
- **Classes**: 15
- **Functions**: 110

## API Reference

### Classes

#### FlowNode
Represents a node in a Flow composition graph.

**Public Methods:**
- `to_dict()`

#### FlowEdge
Represents an edge (connection) between Flow nodes.

**Public Methods:**
- `to_dict()`

#### FlowGraph
Represents a complete Flow composition as a directed graph.

**Public Methods:**
- `complexity_score()`
- `depth()`
- `get_critical_path()`
- `find_cycles()`
- `to_dict()`

#### FlowAnalyzer
Analyzer for Flow compositions and structures.

**Public Methods:**
- `analyze_flow()`
- `analyze_composition()`
- `detect_patterns()`
- `generate_optimization_suggestions()`
- `export_analysis()`

#### HealthStatus
Health status levels.

#### HealthCheck
Individual health check definition.

**Public Methods:**
- `run()`

#### HealthCheckResult
Result of a health check execution.

**Public Methods:**
- `to_dict()`

#### SystemHealth
Overall system health status.

**Public Methods:**
- `healthy_checks()`
- `warning_checks()`
- `critical_checks()`
- `to_dict()`

#### FlowHealthMonitor
Health monitoring system for Flow applications.

**Public Methods:**
- `register_check()`
- `unregister_check()`
- `run_check()`
- `run_all_checks()`
- `get_health_history()`
- `export_health_report()`

#### FlowConfigValidator
Configuration validation for Flow systems.

**Public Methods:**
- `register_validator()`
- `set_config_schema()`
- `validate_config()`
- `validate_flow_config()`

#### FlowExecutionContext
Context information for a Flow execution.

**Public Methods:**
- `to_dict()`

#### FlowDebugger
Debugging system for Flow executions.

**Public Methods:**
- `enable_debugging()`
- `disable_debugging()`
- `add_breakpoint()`
- `remove_breakpoint()`
- `execution_context()`
- `check_breakpoint()`
- `print_execution_stack()`
- `print_item_inspection()`
- `get_execution_trace()`
- `export_trace()`

#### FlowExecutionErrorWithContext
Enhanced flow execution error with debugging context.

**Public Methods:**
- `get_debug_info()`
- `print_debug_info()`

#### FlowMetrics
Metrics collected for a Flow execution.

**Public Methods:**
- `duration_ms()`
- `throughput_items_per_sec()`
- `yield_rate()`
- `to_dict()`

#### PerformanceMonitor
Performance monitoring system for Flow executions.

**Public Methods:**
- `enable_memory_tracking()`
- `start_monitoring()`
- `record_item_processed()`
- `record_item_yielded()`
- `record_error()`
- `record_memory_usage()`
- `finish_monitoring()`
- `get_summary_stats()`
- `export_metrics()`

### Functions

#### `def analyze_flow(flow: AnyFlow) -> FlowGraph`
Analyze a single Flow and return its graph representation.

#### `def analyze_flow_composition(flows: FlowList) -> FlowGraph`
Analyze a composition of multiple flows.

#### `def detect_flow_patterns(graph: FlowGraph) -> PatternList`
Detect common patterns in a flow graph.

#### `def generate_flow_optimizations(graph: FlowGraph) -> OptimizationList`
Generate optimization suggestions for a flow graph.

#### `def export_flow_analysis(graph: FlowGraph, filepath: str) -> None`
Export comprehensive flow analysis to JSON file.

#### `def get_flow_analyzer() -> FlowAnalyzer`
Get the global flow analyzer instance.

#### `def health_check_stream(health_monitor: FlowHealthMonitor | None) -> HealthCheckStream`
Create a flow that performs health checks during stream processing.

    Args:
        health_monitor: Optional health monitor instance. Uses global if None.

    Returns:
        A flow that runs health checks and passes items through unchanged.

#### `def get_health_monitor() -> FlowHealthMonitor`
Get the global health monitor instance.

#### `def get_config_validator() -> FlowConfigValidator`
Get the global configuration validator instance.

#### `async def check_system_health() -> SystemHealth`
Check overall system health.

#### `def validate_flow_configuration(config: ConfigData) -> list[str]`
Validate flow configuration.

#### `def register_health_check(name: str, description: str, check_function: Callable[[], AsyncIterator[bool]], **kwargs: AnyValue) -> None`
Register a custom health check.

#### `def export_health_report(filepath: str) -> None`
Export system health report to file.

#### `def debug_stream(breakpoint_condition: ItemCondition | None, log_items: bool) -> Flow[Input, Input]`
Create a flow that adds debugging capabilities to the pipeline.

    Args:
        breakpoint_condition: Optional condition to trigger breakpoints
        log_items: Whether to log items as they pass through

    Returns:
        A flow that provides debugging and passes items through unchanged.

#### `def traced_flow(flow: Flow[Input, Output]) -> Flow[Input, Output]`
Wrap a flow with execution tracing and enhanced error reporting.

    Args:
        flow: The flow to wrap with tracing

    Returns:
        A flow with enhanced debugging and error reporting.

#### `def get_flow_debugger() -> FlowDebugger`
Get the global flow debugger instance.

#### `def enable_flow_debugging() -> None`
Enable flow debugging globally.

#### `def disable_flow_debugging() -> None`
Disable flow debugging globally.

#### `def add_flow_breakpoint(flow_name: str, condition: BreakpointCondition) -> None`
Add a breakpoint for a specific flow.

#### `def remove_flow_breakpoint(flow_name: str) -> None`
Remove a breakpoint for a flow.

#### `def get_execution_trace() -> TraceData`
Get the current execution trace.

#### `def export_execution_trace(filepath: str) -> None`
Export execution trace to a JSON file.

#### `def inspect_flow(flow: AnyFlow) -> DebugData`
Inspect a flow and return metadata about its structure.

    Args:
        flow: The flow to inspect

    Returns:
        Dictionary containing flow metadata and structure information.

#### `async def debug_session(enable_breakpoints: bool) -> AsyncGenerator[FlowDebugger]`
Context manager for a temporary debugging session.

    Args:
        enable_breakpoints: Whether to enable breakpoint functionality

    Example:
        async with debug_session():
            # All flows will have debugging enabled
            result = await my_flow.to_list(test_stream)

#### `def monitored_stream(monitor_name: str | None) -> Callable[[Callable[[], AnyFlow]], AnyFlow]`
Decorator to add performance monitoring to a Flow.

    Args:
        monitor_name: Optional custom name for monitoring. Defaults to flow name.

    Returns:
        Decorated flow with performance monitoring.

    Example:
        @monitored_stream("my_pipeline")
        def my_flow():
            return Flow(...)

#### `def performance_stream() -> AnyFlow`
Create a flow that adds performance monitoring to the pipeline.

    This combinator automatically tracks timing, throughput, and memory usage
    for the stream processing without requiring decoration.

    Returns:
        A flow that monitors performance and passes items through unchanged.

#### `def benchmark_stream(iterations: int, warmup_iterations: int) -> Callable[[AnyFlow], Callable[[AnyIteratorFactory], Awaitable[BenchmarkResult]]]`
Benchmark a Flow's performance over multiple iterations.

    Args:
        iterations: Number of benchmark iterations to run
        warmup_iterations: Number of warmup iterations (not counted in results)

    Returns:
        Function that benchmarks the given flow and returns performance stats.

    Example:
        benchmark = benchmark_stream(iterations=1000)
        stats = await benchmark(my_flow)
        print(f"Average duration: {stats['avg_duration_ms']:.2f}ms")

#### `def get_performance_monitor() -> PerformanceMonitor`
Get the global performance monitor instance.

#### `def enable_memory_tracking() -> None`
Enable memory tracking for all monitored flows.

#### `def get_performance_summary() -> PerformanceData`
Get summary of all performance metrics.

#### `def export_performance_metrics(filepath: str) -> None`
Export all performance metrics to a JSON file.

## Dependencies

### External Dependencies
- `__future__`
- `analysis`
- `asyncio`
- `collections`
- `contextlib`
- `core`
- `dataclasses`
- `datetime`
- `debugging`
- `enum`
- `hashlib`
- `health`
- `json`
- `performance`
- `time`
- `traceback`
- `typing`

## Exports

This module exports the following symbols:

- `FlowAnalyzer`
- `FlowConfigValidator`
- `FlowDebugger`
- `FlowEdge`
- `FlowExecutionContext`
- `FlowGraph`
- `FlowHealthMonitor`
- `FlowMetrics`
- `FlowNode`
- `HealthCheck`
- `HealthCheckResult`
- `HealthStatus`
- `PerformanceMonitor`
- `SystemHealth`
- `add_flow_breakpoint`
- `analyze_flow`
- `analyze_flow_composition`
- `benchmark_stream`
- `check_system_health`
- `debug_session`
- `debug_stream`
- `detect_flow_patterns`
- `disable_flow_debugging`
- `enable_flow_debugging`
- `enable_memory_tracking`
- `export_execution_trace`
- `export_flow_analysis`
- `export_health_report`
- `export_performance_metrics`
- `generate_flow_optimizations`
- `get_config_validator`
- `get_execution_trace`
- `get_flow_analyzer`
- `get_flow_debugger`
- `get_health_monitor`
- `get_performance_monitor`
- `get_performance_summary`
- `health_check_stream`
- `inspect_flow`
- `monitored_stream`
- `performance_stream`
- `register_health_check`
- `remove_flow_breakpoint`
- `traced_flow`
- `validate_flow_configuration`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
