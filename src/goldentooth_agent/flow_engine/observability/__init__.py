"""Flow Engine Observability - monitoring, debugging, analysis, and health checking.

This package provides comprehensive observability capabilities for the Flow Engine:
- debugging: Interactive debugging and tracing
- analysis: Flow composition analysis and optimization
- performance: Performance monitoring and benchmarking
- health: Health monitoring and configuration validation
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
]
