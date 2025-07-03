# Flow Engine Migration Plans - Part 2: Observability & Registry Systems

## Phase 3: Observability System (Epics 15-22)

### Epic 15: Migrate performance monitoring
**Unit**: Performance measurement and monitoring
**Source**: `old/goldentooth_agent/flow_engine/observability/performance.py` (362 lines)
**Target**: `src/flowengine/observability/performance.py`

**Classes to migrate**:
1. `FlowMetrics` - Performance metrics data class
   - Properties: `execution_count`, `total_duration`, `average_duration`, `min_duration`, `max_duration`, `error_count`, `success_rate`
   - Methods: `record_execution()`, `record_error()`, `reset()`, `to_dict()`

2. `PerformanceMonitor` - Performance monitoring system
   - Methods: `start_monitoring()`, `stop_monitoring()`, `get_metrics()`, `reset_metrics()`, `export_metrics()`

**Functions to migrate** (8 functions):
3. `monitored_stream(name)` - Add monitoring to stream
4. `performance_stream()` - Performance measurement wrapper
5. `benchmark_stream(iterations)` - Benchmarking utilities
6. `get_performance_monitor()` - Global monitor access
7. `enable_memory_tracking()` - Memory usage tracking
8. `get_performance_summary()` - Summary statistics
9. `export_performance_metrics(format)` - Export in various formats
10. `memory_profile_stream()` - Memory profiling

**Test file**: `tests/flowengine/observability/test_performance.py`
**Test coverage**:
- Metrics collection and calculation accuracy
- Performance monitoring lifecycle
- Memory tracking functionality
- Export format validation (JSON, CSV)
- Concurrent monitoring scenarios
- Reset and cleanup operations

**Dependencies**: `flowengine.flow`
**Coverage**: 100% - all classes, methods, and functions

---

### Epic 16: Migrate analysis tools
**Unit**: Flow analysis and optimization
**Source**: `old/goldentooth_agent/flow_engine/observability/analysis.py` (551 lines)
**Target**: Split into 3 files due to size constraints

#### File 1: `src/flowengine/observability/analysis/core.py` (300 lines)
**Classes to migrate**:
1. `FlowNode` - Flow graph node representation
   - Properties: `id`, `name`, `flow_type`, `metadata`, `inputs`, `outputs`
   - Methods: `add_input()`, `add_output()`, `to_dict()`

2. `FlowEdge` - Flow graph edge representation
   - Properties: `source`, `target`, `metadata`, `weight`
   - Methods: `to_dict()`

3. `FlowGraph` - Complete flow graph
   - Properties: `nodes`, `edges`, `metadata`
   - Methods: `add_node()`, `add_edge()`, `remove_node()`, `remove_edge()`, `find_cycles()`, `topological_sort()`

4. `FlowAnalyzer` - Main analysis engine
   - Methods: `analyze_flow()`, `detect_patterns()`, `find_bottlenecks()`, `calculate_complexity()`

#### File 2: `src/flowengine/observability/analysis/graph.py` (151 lines)
**Functions to migrate** (6 functions):
5. `analyze_flow(flow)` - Analyze single flow
6. `analyze_flow_composition(flows)` - Analyze flow composition
7. `detect_flow_patterns(graph)` - Pattern detection
8. `find_cycles(graph)` - Cycle detection
9. `calculate_dependencies(graph)` - Dependency analysis
10. `visualize_flow_graph(graph)` - Graph visualization

#### File 3: `src/flowengine/observability/analysis/optimization.py` (100 lines)
**Functions to migrate** (4 functions):
11. `generate_flow_optimizations(analysis)` - Optimization suggestions
12. `export_flow_analysis(analysis, format)` - Export analysis results
13. `get_flow_analyzer()` - Global analyzer access
14. `optimize_flow_composition(flows)` - Automatic optimization

**Test files**:
- `tests/flowengine/observability/test_analysis_core.py`
- `tests/flowengine/observability/test_analysis_graph.py`
- `tests/flowengine/observability/test_analysis_optimization.py`

**Test coverage**:
- Graph construction and manipulation
- Cycle detection algorithms
- Pattern recognition accuracy
- Optimization suggestion quality
- Export format validation
- Complex flow composition analysis

**Dependencies**: `flowengine.flow`, `flowengine.combinators`
**Coverage**: 100% - all analysis functionality

---

### Epic 17: Migrate debugging tools
**Unit**: Flow debugging and introspection
**Source**: `old/goldentooth_agent/flow_engine/observability/debugging.py` (436 lines)
**Target**: `src/flowengine/observability/debugging.py`

**Classes to migrate**:
1. `FlowExecutionContext` - Execution context tracking
   - Properties: `flow_id`, `execution_id`, `start_time`, `end_time`, `status`, `variables`, `stack_trace`
   - Methods: `set_variable()`, `get_variable()`, `add_breakpoint()`, `remove_breakpoint()`

2. `FlowDebugger` - Main debugging interface
   - Properties: `active_sessions`, `breakpoints`, `trace_enabled`
   - Methods: `start_session()`, `end_session()`, `step_through()`, `inspect_state()`

**Functions to migrate** (12 functions):
3. `debug_stream(label)` - Add debugging to stream
4. `traced_flow(flow)` - Add execution tracing
5. `get_flow_debugger()` - Global debugger access
6. `enable_flow_debugging()` - Enable debugging globally
7. `disable_flow_debugging()` - Disable debugging globally
8. `add_flow_breakpoint(flow_id, condition)` - Add conditional breakpoint
9. `remove_flow_breakpoint(breakpoint_id)` - Remove breakpoint
10. `get_execution_trace(execution_id)` - Get execution trace
11. `export_execution_trace(trace, format)` - Export trace
12. `inspect_flow(flow)` - Flow introspection
13. `debug_session(flows)` - Interactive debug session
14. `step_debugger(context)` - Step-by-step execution

**Test file**: `tests/flowengine/observability/test_debugging.py`
**Test coverage**:
- Debugging session lifecycle
- Breakpoint management
- Execution tracing accuracy
- Variable inspection
- Interactive debugging scenarios
- Trace export functionality

**Dependencies**: `flowengine.flow`, `flowengine.observability.performance`
**Coverage**: 100% - all debugging features

---

### Epic 18: Migrate health monitoring
**Unit**: System health and configuration validation
**Source**: `old/goldentooth_agent/flow_engine/observability/health.py` (619 lines)
**Target**: Split into 3 files due to size constraints

#### File 1: `src/flowengine/observability/health/core.py` (300 lines)
**Enums to migrate**:
1. `HealthStatus` - Health status enumeration
   - Values: `HEALTHY`, `WARNING`, `CRITICAL`, `UNKNOWN`

**Classes to migrate**:
2. `HealthCheck` - Individual health check
   - Properties: `name`, `description`, `check_fn`, `interval`, `timeout`
   - Methods: `run_check()`, `is_healthy()`, `get_last_result()`

3. `HealthCheckResult` - Health check result
   - Properties: `status`, `message`, `timestamp`, `duration`, `metadata`
   - Methods: `to_dict()`, `is_healthy()`

4. `SystemHealth` - Overall system health
   - Properties: `status`, `checks`, `last_update`, `uptime`
   - Methods: `add_check()`, `remove_check()`, `get_overall_status()`, `to_dict()`

#### File 2: `src/flowengine/observability/health/checks.py` (200 lines)
**Classes to migrate**:
5. `FlowHealthMonitor` - Flow-specific health monitoring
   - Properties: `monitored_flows`, `health_checks`, `alert_thresholds`
   - Methods: `add_flow()`, `remove_flow()`, `check_flow_health()`, `get_flow_status()`

**Built-in health checks** (8 functions):
6. `check_flow_performance()` - Performance health check
7. `check_flow_errors()` - Error rate health check
8. `check_memory_usage()` - Memory health check
9. `check_flow_dependencies()` - Dependency health check
10. `check_flow_configuration()` - Configuration validation
11. `check_resource_limits()` - Resource limit check
12. `check_flow_responsiveness()` - Responsiveness check
13. `check_system_resources()` - System resource check

#### File 3: `src/flowengine/observability/health/reporting.py` (119 lines)
**Classes to migrate**:
14. `FlowConfigValidator` - Configuration validation
    - Methods: `validate_flow_config()`, `validate_combinator_config()`, `get_validation_errors()`

**Functions to migrate** (6 functions):
15. `health_check_stream()` - Add health checking to stream
16. `get_health_monitor()` - Global monitor access
17. `get_config_validator()` - Global validator access
18. `check_system_health()` - System-wide health check
19. `validate_flow_configuration(config)` - Validate configuration
20. `register_health_check(check)` - Register custom check
21. `export_health_report(format)` - Export health report

**Test files**:
- `tests/flowengine/observability/test_health_core.py`
- `tests/flowengine/observability/test_health_checks.py`
- `tests/flowengine/observability/test_health_reporting.py`

**Test coverage**:
- Health check execution and timing
- Status calculation algorithms
- Configuration validation rules
- Health monitoring lifecycle
- Alert threshold triggering
- Report generation and export

**Dependencies**: `flowengine.flow`, `flowengine.exceptions`
**Coverage**: 100% - all health monitoring features

---

### Epic 19: Create observability __init__.py
**Unit**: Observability module exports
**Source**: `old/goldentooth_agent/flow_engine/observability/__init__.py` (121 lines)
**Target**: `src/flowengine/observability/__init__.py`

**Complete export structure**:
```python
# Performance monitoring
from .performance import (
    FlowMetrics, PerformanceMonitor, monitored_stream, performance_stream,
    benchmark_stream, get_performance_monitor, enable_memory_tracking,
    get_performance_summary, export_performance_metrics, memory_profile_stream
)

# Analysis and optimization
from .analysis.core import FlowNode, FlowEdge, FlowGraph, FlowAnalyzer
from .analysis.graph import (
    analyze_flow, analyze_flow_composition, detect_flow_patterns,
    find_cycles, calculate_dependencies, visualize_flow_graph
)
from .analysis.optimization import (
    generate_flow_optimizations, export_flow_analysis, get_flow_analyzer,
    optimize_flow_composition
)

# Debugging and introspection
from .debugging import (
    FlowExecutionContext, FlowDebugger, debug_stream, traced_flow,
    get_flow_debugger, enable_flow_debugging, disable_flow_debugging,
    add_flow_breakpoint, remove_flow_breakpoint, get_execution_trace,
    export_execution_trace, inspect_flow, debug_session, step_debugger
)

# Health monitoring
from .health.core import HealthStatus, HealthCheck, HealthCheckResult, SystemHealth
from .health.checks import FlowHealthMonitor
from .health.reporting import (
    FlowConfigValidator, health_check_stream, get_health_monitor,
    get_config_validator, check_system_health, validate_flow_configuration,
    register_health_check, export_health_report
)

__all__ = [
    # Performance (9 exports)
    "FlowMetrics", "PerformanceMonitor", "monitored_stream", "performance_stream",
    "benchmark_stream", "get_performance_monitor", "enable_memory_tracking",
    "get_performance_summary", "export_performance_metrics",

    # Analysis (14 exports)
    "FlowNode", "FlowEdge", "FlowGraph", "FlowAnalyzer", "analyze_flow",
    "analyze_flow_composition", "detect_flow_patterns", "find_cycles",
    "calculate_dependencies", "visualize_flow_graph", "generate_flow_optimizations",
    "export_flow_analysis", "get_flow_analyzer", "optimize_flow_composition",

    # Debugging (14 exports)
    "FlowExecutionContext", "FlowDebugger", "debug_stream", "traced_flow",
    "get_flow_debugger", "enable_flow_debugging", "disable_flow_debugging",
    "add_flow_breakpoint", "remove_flow_breakpoint", "get_execution_trace",
    "export_execution_trace", "inspect_flow", "debug_session", "step_debugger",

    # Health (13 exports)
    "HealthStatus", "HealthCheck", "HealthCheckResult", "SystemHealth",
    "FlowHealthMonitor", "FlowConfigValidator", "health_check_stream",
    "get_health_monitor", "get_config_validator", "check_system_health",
    "validate_flow_configuration", "register_health_check", "export_health_report"
]
```

**Directory creation**: `src/flowengine/observability/__init__.py`
**Test updates**: Integration tests for complete observability API
**Dependencies**: All observability submodules
**Coverage**: 100% - complete observability API verification

---

### Epic 20: Migrate flow benchmarks tests
**Unit**: Performance benchmarking test suite
**Source**: `old/tests/flow_engine/observability/test_flow_benchmarks.py` (368 lines)
**Target**: `tests/flowengine/observability/test_benchmarks.py`

**Test classes to migrate**:
1. `TestFlowBenchmarks` - Core benchmarking tests
   - Methods: `test_simple_flow_performance()`, `test_complex_composition_performance()`, `test_memory_usage_tracking()`

2. `TestPerformanceRegression` - Regression testing
   - Methods: `test_performance_doesnt_degrade()`, `test_memory_leaks()`, `test_throughput_consistency()`

3. `TestBenchmarkReporting` - Benchmark reporting tests
   - Methods: `test_benchmark_export()`, `test_performance_comparison()`, `test_statistical_analysis()`

**Performance test scenarios**:
- Simple stream operations (map, filter)
- Complex compositions (nested flows)
- Large data volumes (1M+ items)
- Concurrent execution patterns
- Memory usage patterns
- Error handling performance

**Dependencies**: Complete observability system
**Coverage**: 100% - all benchmark scenarios

---

### Epic 21: Migrate observability integration tests
**Unit**: Observability system integration tests
**Source**: `old/tests/flow_engine/observability/test_observability_integration.py` (465 lines)
**Target**: `tests/flowengine/observability/test_integration.py`

**Test classes to migrate**:
1. `TestObservabilityIntegration` - Cross-component integration
   - Methods: `test_monitoring_debugging_integration()`, `test_health_performance_integration()`, `test_analysis_monitoring_integration()`

2. `TestObservabilityLifecycle` - Lifecycle management
   - Methods: `test_startup_shutdown()`, `test_configuration_changes()`, `test_resource_cleanup()`

3. `TestObservabilityScenarios` - Real-world scenarios
   - Methods: `test_production_monitoring()`, `test_development_debugging()`, `test_performance_optimization()`

**Integration test scenarios**:
- Multi-component observability workflows
- Resource management across components
- Configuration consistency
- Error propagation and handling
- Performance impact of observability
- Data consistency across systems

**Dependencies**: Complete observability system
**Coverage**: 100% - all integration scenarios

---

### Epic 22: Create observability test conftest
**Unit**: Observability test configuration
**Target**: `tests/flowengine/observability/conftest.py`

**Fixtures to create**:
1. `performance_monitor` - Configured performance monitor
2. `flow_analyzer` - Configured flow analyzer
3. `flow_debugger` - Configured debugger
4. `health_monitor` - Configured health monitor
5. `sample_flows` - Sample flows for testing
6. `benchmark_data` - Benchmark test data
7. `observability_config` - Test configuration

**Test utilities**:
8. `create_test_flow()` - Create flows for testing
9. `generate_test_stream()` - Generate test data streams
10. `assert_performance_within_bounds()` - Performance assertions
11. `cleanup_observability()` - Test cleanup

**Dependencies**: Complete observability system
**Coverage**: 100% - all test fixtures and utilities

---

## Phase 4: Registry System (Epics 23-26)

### Epic 23: Migrate flow registry
**Unit**: Flow discovery and registration system
**Source**: `old/goldentooth_agent/flow_engine/registry/main.py` (311 lines)
**Target**: `src/flowengine/registry/main.py`

**Classes to migrate**:
1. `FlowRegistry` - Main registry class
   - Properties: `flows`, `categories`, `tags`, `metadata`
   - Methods: `register()`, `unregister()`, `get()`, `list()`, `search()`, `clear()`

**Functions to migrate** (8 functions):
2. `register_flow(name, flow, category, tags, metadata)` - Register a flow
3. `get_flow(name)` - Get flow by name
4. `list_flows(category, tags)` - List flows with filters
5. `search_flows(query)` - Search flows by query
6. `unregister_flow(name)` - Remove flow from registry
7. `clear_registry()` - Clear all registered flows
8. `export_registry(format)` - Export registry contents
9. `import_registry(data)` - Import registry contents

**Registry features**:
- Name-based flow storage and retrieval
- Category and tag-based organization
- Metadata storage and querying
- Search functionality (name, description, tags)
- Export/import capabilities (JSON, YAML)
- Thread-safe registration operations

**Global registry instance**:
10. `flow_registry` - Global registry singleton

**Decorator support**:
11. `registered_flow(name, category, tags)` - Decorator for auto-registration

**Test file**: `tests/flowengine/registry/test_main.py`
**Test coverage**:
- Flow registration and retrieval
- Category and tag filtering
- Search functionality accuracy
- Export/import round-trip testing
- Concurrent registration scenarios
- Decorator functionality

**Dependencies**: `flowengine.flow`
**Coverage**: 100% - all registry features

---

### Epic 24: Create registry __init__.py
**Unit**: Registry module exports
**Source**: `old/goldentooth_agent/flow_engine/registry/__init__.py` (26 lines)
**Target**: `src/flowengine/registry/__init__.py`

**Export structure**:
```python
from .main import (
    FlowRegistry, register_flow, get_flow, list_flows, search_flows,
    unregister_flow, clear_registry, export_registry, import_registry,
    flow_registry, registered_flow
)

__all__ = [
    "FlowRegistry",
    "register_flow",
    "get_flow",
    "list_flows",
    "search_flows",
    "unregister_flow",
    "clear_registry",
    "export_registry",
    "import_registry",
    "flow_registry",
    "registered_flow"
]
```

**Directory creation**: `src/flowengine/registry/__init__.py`
**Test updates**: Registry API integration tests
**Dependencies**: `flowengine.registry.main`
**Coverage**: 100% - registry API verification

---

### Epic 25: Migrate registry tests
**Unit**: Registry system test suite
**Source**: `old/tests/flow_engine/registry/test_registry.py` (578 lines)
**Target**: `tests/flowengine/registry/test_registry.py`

**Test classes to migrate**:
1. `TestFlowRegistry` - Core registry functionality
   - Methods: `test_register_flow()`, `test_get_flow()`, `test_list_flows()`, `test_search_flows()`

2. `TestRegistryFiltering` - Filtering and search tests
   - Methods: `test_category_filtering()`, `test_tag_filtering()`, `test_combined_filtering()`, `test_search_queries()`

3. `TestRegistryPersistence` - Export/import functionality
   - Methods: `test_export_json()`, `test_export_yaml()`, `test_import_round_trip()`, `test_import_validation()`

4. `TestRegistryDecorator` - Decorator functionality
   - Methods: `test_registered_flow_decorator()`, `test_decorator_metadata()`, `test_decorator_categories()`

5. `TestRegistryConcurrency` - Concurrent access tests
   - Methods: `test_concurrent_registration()`, `test_concurrent_retrieval()`, `test_thread_safety()`

**Test scenarios**:
- Basic CRUD operations
- Advanced search and filtering
- Persistence and serialization
- Decorator auto-registration
- Error handling and validation
- Performance with large registries
- Concurrent access patterns

**Dependencies**: Complete registry system
**Coverage**: 100% - all registry functionality

---

### Epic 26: Create registry test conftest
**Unit**: Registry test configuration
**Target**: `tests/flowengine/registry/conftest.py`

**Fixtures to create**:
1. `empty_registry` - Fresh registry instance
2. `populated_registry` - Registry with sample flows
3. `sample_flows` - Collection of test flows
4. `flow_categories` - Test categories
5. `flow_tags` - Test tags
6. `registry_metadata` - Test metadata
7. `registry_config` - Test configuration

**Test utilities**:
8. `create_test_registry()` - Create registry for testing
9. `register_sample_flows()` - Populate with test data
10. `assert_registry_state()` - Registry state assertions
11. `cleanup_registry()` - Test cleanup

**Sample data**:
- 20+ sample flows with various categories
- Comprehensive tag sets
- Rich metadata examples
- Export/import test data

**Dependencies**: Complete registry system
**Coverage**: 100% - all test fixtures and utilities
