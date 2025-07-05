"""Observability module for Flow system monitoring and analysis.

This module provides comprehensive monitoring, health checking, performance analysis,
and debugging capabilities for Flow-based applications.
"""

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
    # Performance monitoring (9 exports)
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
