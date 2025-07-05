"""Observability module for Flow system monitoring and analysis.

This module provides comprehensive monitoring, health checking, performance analysis,
and debugging capabilities for Flow-based applications.
"""

# Analysis and optimization
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

# Health monitoring exports
from .health import (  # Core health types; Health monitoring; Configuration validation; Built-in health checks; Convenience functions
    FlowConfigValidator,
    FlowHealthMonitor,
    HealthCheck,
    HealthCheckResult,
    HealthStatus,
    SystemHealth,
    check_flow_configuration,
    check_flow_dependencies,
    check_flow_errors,
    check_flow_performance,
    check_flow_responsiveness,
    check_memory_usage,
    check_resource_limits,
    check_system_health,
    check_system_resources,
    export_health_report,
    get_config_validator,
    get_health_monitor,
    health_check_stream,
    register_health_check,
    validate_flow_configuration,
)

# Performance monitoring
from .performance import (
    FlowMetrics,
    PerformanceMonitor,
    benchmark_stream,
    enable_memory_tracking,
    export_performance_metrics,
    get_performance_monitor,
    get_performance_summary,
    memory_profile_stream,
    monitored_stream,
    performance_stream,
)

__all__ = [
    # Analysis (10 exports)
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
    # Debugging (13 exports)
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
    # Core health types
    "HealthStatus",
    "HealthCheck",
    "HealthCheckResult",
    "SystemHealth",
    # Health monitoring
    "FlowHealthMonitor",
    # Configuration validation
    "FlowConfigValidator",
    # Built-in health checks
    "check_flow_performance",
    "check_flow_errors",
    "check_memory_usage",
    "check_flow_dependencies",
    "check_flow_configuration",
    "check_resource_limits",
    "check_flow_responsiveness",
    "check_system_resources",
    # Convenience functions
    "health_check_stream",
    "get_health_monitor",
    "get_config_validator",
    "check_system_health",
    "validate_flow_configuration",
    "register_health_check",
    "export_health_report",
    # Performance monitoring (10 exports)
    "FlowMetrics",
    "PerformanceMonitor",
    "monitored_stream",
    "performance_stream",
    "benchmark_stream",
    "get_performance_monitor",
    "enable_memory_tracking",
    "get_performance_summary",
    "export_performance_metrics",
    "memory_profile_stream",
]
