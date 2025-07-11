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
    calculate_dependencies,
    detect_flow_patterns,
    export_flow_analysis,
    find_cycles,
    generate_flow_optimizations,
    get_flow_analyzer,
    optimize_flow_composition,
    visualize_flow_graph,
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
    step_debugger,
    traced_flow,
)
from .health.checks import FlowHealthMonitor

# Health monitoring
from .health.core import HealthCheck, HealthCheckResult, HealthStatus, SystemHealth
from .health.reporting import (
    FlowConfigValidator,
    check_system_health,
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
    monitored_stream,
    performance_stream,
)

__all__ = [
    # Performance (9 exports)
    "FlowMetrics",
    "PerformanceMonitor",
    "monitored_stream",
    "performance_stream",
    "benchmark_stream",
    "get_performance_monitor",
    "enable_memory_tracking",
    "get_performance_summary",
    "export_performance_metrics",
    # Analysis (14 exports)
    "FlowNode",
    "FlowEdge",
    "FlowGraph",
    "FlowAnalyzer",
    "analyze_flow",
    "analyze_flow_composition",
    "detect_flow_patterns",
    "find_cycles",
    "calculate_dependencies",
    "visualize_flow_graph",
    "generate_flow_optimizations",
    "export_flow_analysis",
    "get_flow_analyzer",
    "optimize_flow_composition",
    # Debugging (14 exports)
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
    "step_debugger",
    # Health (13 exports)
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
]
