"""
Flow_Engine package - extracted from core/flow.

This package provides flow composition and execution capabilities
for the Goldentooth Agent system.
"""

# Flow analysis and composition tools
from .analysis import (
    FlowAnalyzer,
    FlowEdge,
    FlowGraph,
    FlowNode,
    analyze_flow,
    analyze_flow_composition,
    detect_flow_patterns,
    export_flow_analysis,
    generate_flow_optimizations,
    get_flow_analyzer,
)
from .combinators import (  # Advanced combinators; New combinators batch 2; Notification classes
    OnComplete,
    OnError,
    OnNext,
    StreamNotification,
    batch_stream,
    branch_flows,
    buffer_stream,
    catch_and_continue_stream,
    chain_flows,
    chain_stream,
    chunk_stream,
    circuit_breaker_stream,
    collect_stream,
    combine_latest_stream,
    compose,
    debounce_stream,
    delay_stream,
    distinct_stream,
    empty_flow,
    expand_stream,
    filter_stream,
    finalize_stream,
    flat_map_ctx_stream,
    flat_map_stream,
    flatten_stream,
    group_by_stream,
    guard_stream,
    identity_stream,
    if_then_stream,
    inspect_stream,
    log_stream,
    map_stream,
    materialize_stream,
    memoize_stream,
    merge_flows,
    merge_stream,
    metrics_stream,
    pairwise_stream,
    parallel_stream,
    parallel_stream_successful,
    race_stream,
    range_flow,
    recover_stream,
    repeat_flow,
    retry_stream,
    run_fold,
    sample_stream,
    scan_stream,
    share_stream,
    skip_stream,
    start_with_stream,
    switch_stream,
    take_stream,
    tap_stream,
    then_stream,
    throttle_stream,
    timeout_stream,
    trace_stream,
    until_stream,
    while_condition_stream,
    window_stream,
    zip_stream,
)

# Debugging and introspection
from .debugging import (
    FlowDebugger,
    FlowExecutionContext,
    add_flow_breakpoint,
    debug_session,
    debug_stream,
    disable_flow_debugging,
    enable_flow_debugging,
    export_execution_trace,
    get_execution_trace,
    get_flow_debugger,
    inspect_flow,
    remove_flow_breakpoint,
    traced_flow,
)
from .exceptions import (
    FlowConfigurationError,
    FlowError,
    FlowExecutionError,
    FlowTimeoutError,
    FlowValidationError,
)

# Health monitoring and configuration validation
from .health import (
    FlowConfigValidator,
    FlowHealthMonitor,
    HealthCheck,
    HealthCheckResult,
    HealthStatus,
    SystemHealth,
    check_system_health,
    export_health_report,
    get_config_validator,
    get_health_monitor,
    health_check_stream,
    register_health_check,
    validate_flow_configuration,
)

# Trampoline execution patterns (using protocol-based integration)
from .integrations.context_bridge import initialize_context_integration
from .main import Flow

# Performance monitoring
from .performance import (
    FlowMetrics,
    PerformanceMonitor,
    benchmark_stream,
    enable_memory_tracking,
    export_performance_metrics,
    get_performance_monitor,
    get_performance_summary,
    monitored_stream,
    performance_stream,
)

# Flow registry and discoverability
from .registry import (
    FlowRegistry,
    flow_registry,
    get_flow,
    list_flows,
    register_flow,
    registered_flow,
    search_flows,
)

# Initialize context integration if available
try:
    initialize_context_integration()
    _context_integration_available = True
except Exception:
    _context_integration_available = False

__all__ = [
    "Flow",
    # Exception classes
    "FlowError",
    "FlowValidationError",
    "FlowExecutionError",
    "FlowTimeoutError",
    "FlowConfigurationError",
    # Performance monitoring
    "FlowMetrics",
    "PerformanceMonitor",
    "monitored_stream",
    "performance_stream",
    "benchmark_stream",
    "get_performance_monitor",
    "enable_memory_tracking",
    "get_performance_summary",
    "export_performance_metrics",
    # Debugging and introspection
    "FlowExecutionContext",
    "FlowDebugger",
    "debug_stream",
    "traced_flow",
    "get_flow_debugger",
    "enable_flow_debugging",
    "disable_flow_debugging",
    "add_flow_breakpoint",
    "remove_flow_breakpoint",
    "get_execution_trace",
    "export_execution_trace",
    "inspect_flow",
    "debug_session",
    # Health monitoring and configuration validation
    "HealthStatus",
    "HealthCheck",
    "HealthCheckResult",
    "SystemHealth",
    "FlowHealthMonitor",
    "FlowConfigValidator",
    "health_check_stream",
    "get_health_monitor",
    "get_config_validator",
    "check_system_health",
    "validate_flow_configuration",
    "register_health_check",
    "export_health_report",
    # Flow analysis and composition tools
    "FlowNode",
    "FlowEdge",
    "FlowGraph",
    "FlowAnalyzer",
    "analyze_flow",
    "analyze_flow_composition",
    "detect_flow_patterns",
    "generate_flow_optimizations",
    "export_flow_analysis",
    "get_flow_analyzer",
    # Flow registry and discoverability
    "FlowRegistry",
    "flow_registry",
    "register_flow",
    "get_flow",
    "list_flows",
    "search_flows",
    "registered_flow",
    # Core combinators
    "run_fold",
    "compose",
    "filter_stream",
    "map_stream",
    "flat_map_stream",
    "flat_map_ctx_stream",
    # Utility combinators
    "log_stream",
    "identity_stream",
    "if_then_stream",
    "tap_stream",
    "then_stream",
    "delay_stream",
    "recover_stream",
    "guard_stream",
    # Stream manipulation
    "take_stream",
    "skip_stream",
    "batch_stream",
    "debounce_stream",
    "collect_stream",
    "flatten_stream",
    # Control flow
    "retry_stream",
    "switch_stream",
    "race_stream",
    "parallel_stream",
    "parallel_stream_successful",
    "while_condition_stream",
    # Caching
    "memoize_stream",
    # Source flows
    "range_flow",
    "repeat_flow",
    "empty_flow",
    # Advanced combinators
    "timeout_stream",
    "circuit_breaker_stream",
    "catch_and_continue_stream",
    "throttle_stream",
    "until_stream",
    "scan_stream",
    "zip_stream",
    "chain_stream",
    "merge_stream",
    "distinct_stream",
    "chunk_stream",
    "window_stream",
    # New combinators batch 2
    "pairwise_stream",
    "start_with_stream",
    "sample_stream",
    "combine_latest_stream",
    "group_by_stream",
    "finalize_stream",
    "buffer_stream",
    "expand_stream",
    "share_stream",
    "materialize_stream",
    # Debugging and monitoring
    "trace_stream",
    "metrics_stream",
    "inspect_stream",
    # Multi-flow combinators
    "chain_flows",
    "branch_flows",
    "merge_flows",
    # Notification classes
    "StreamNotification",
    "OnNext",
    "OnError",
    "OnComplete",
    # Trampoline execution patterns (disabled due to circular import with context)
    # "TrampolineFlowCombinators",
    # "SHOULD_EXIT_KEY",
    # "SHOULD_BREAK_KEY",
    # "SHOULD_SKIP_KEY",
    # "extend_flow_with_trampoline",
]

# Automatically extend Flow with trampoline methods (disabled due to circular import)
# extend_flow_with_trampoline()
