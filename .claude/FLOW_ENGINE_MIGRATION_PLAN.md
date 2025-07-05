# Flow Engine Migration Plan

## Executive Summary

This document outlines the detailed migration plan for extracting the Flow Engine from `old/goldentooth_agent/flow_engine` into the new codebase structure. The Flow Engine consists of **5,954 lines of source code** across **26 files** with **9,010 lines of comprehensive tests** across **18 test files**.

## General Notes
- **The migration of any single unit (a SINGLE function, SINGLE class method, SINGLE protocol, etc) and its accompanying tests MUST be in its own, discrete commit!**
- Each function/method must be in its own commit even if the code already exists. No exceptions!
- Please mark each epic ✅ DONE! as you complete it.
- If you encounter a reference to AsyncIterator, change it to AsyncGenerator.
- Update README.md and relevant files in docs/ as you complete each epic.
- Create a branch for each epic, add commits to it until you have completed the epic and related work, then create a pull request.
- If you have completed a Phase, take the time to create a .claude/FEM_RETRO_[phase id, e.g. "1A"].md file, matching the format of `.claude/FEM_RETRO_1A.md`.
- When you prepare a commit, write the commit message to a file in a temporary directory, then create the commit using that message file. Do not write the message inline.

## Key Statistics

- **Source Files**: 26 Python files (5,954 total lines)
- **Test Files**: 18 Python files (9,010 total lines)
- **Dependencies**: Standard library only (no third-party)
- **Context Integration**: Optional, with lazy loading architecture
- **Estimated Commits**: ~1800 individual commits (one per unit, where a unit is a SINGLE function, class method, protocol, etc, and its accompanying tests)

## Migration Strategy

Following requirements 1, 4, and 6, this migration will be executed as a **separate package** with **individual commits per unit** and **no circular imports**.

### Package Structure Decision

The Flow Engine will be extracted as `flowengine` - a **separate package** that:
- Has zero dependencies on `goldentooth_agent`
- Is a dependency OF `goldentooth_agent`
- Can be used standalone
- Follows the existing clean architecture

# Flow Engine Migration Plans - Part 2: Observability & Registry Systems

## Phase 3: Observability System (Epics 15-22)

...

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

## Phase 5: Advanced Features (Epics 27-35)

### Epic 27: Migrate extensions
**Unit**: Flow extension mechanisms
**Source**: `old/goldentooth_agent/flow_engine/extensions.py` (79 lines)
**Target**: `src/flowengine/extensions.py`

**Classes to migrate**:
1. `FlowExtension` - Base extension class
   - Properties: `name`, `version`, `description`, `enabled`
   - Methods: `install()`, `uninstall()`, `configure()`, `get_info()`

2. `ExtensionRegistry` - Extension management
   - Properties: `extensions`, `enabled_extensions`
   - Methods: `register_extension()`, `unregister_extension()`, `enable()`, `disable()`, `list_extensions()`

**Functions to migrate** (6 functions):
3. `install_extension(extension)` - Install flow extension
4. `uninstall_extension(name)` - Remove extension
5. `enable_extension(name)` - Enable extension
6. `disable_extension(name)` - Disable extension
7. `list_extensions()` - List available extensions
8. `get_extension_info(name)` - Get extension details

**Extension features**:
- Dynamic extension loading/unloading
- Extension configuration management
- Extension dependency resolution
- Extension lifecycle management
- Extension metadata and versioning

**Test file**: `tests/flowengine/test_extensions.py`
**Test coverage**:
- Extension installation and removal
- Enable/disable functionality
- Configuration management
- Dependency resolution
- Extension lifecycle events
- Error handling for invalid extensions

**Dependencies**: `flowengine.flow`
**Coverage**: 100% - all extension functionality

---

### Epic 28: Migrate trampoline (without context)
**Unit**: Trampoline execution patterns (context-independent parts)
**Source**: `old/goldentooth_agent/flow_engine/trampoline.py` (335 lines)
**Target**: `src/flowengine/trampoline.py`

**Constants to migrate**:
1. `SHOULD_EXIT_KEY` - Trampoline exit signal key
2. `SHOULD_BREAK_KEY` - Trampoline break signal key
3. `SHOULD_SKIP_KEY` - Trampoline skip signal key

**Classes to migrate**:
4. `TrampolineFlowCombinators` - Trampoline-aware combinators
   - Methods: `trampoline_map()`, `trampoline_filter()`, `trampoline_flat_map()`, `trampoline_fold()`

**Functions to migrate** (8 functions, context features temporarily removed):
5. `extend_flow_with_trampoline()` - Add trampoline methods to Flow class
6. `trampoline_execute(flow, stream)` - Execute with trampoline
7. `should_exit(item)` - Check for exit condition
8. `should_break(item)` - Check for break condition
9. `should_skip(item)` - Check for skip condition
10. `create_exit_signal()` - Create exit signal
11. `create_break_signal()` - Create break signal
12. `create_skip_signal()` - Create skip signal

**Trampoline features**:
- Non-recursive execution patterns
- Control flow signals (exit, break, skip)
- Stack-safe execution for deep compositions
- Signal-based flow control
- Integration with standard combinators

**Context-dependent features removed temporarily**:
- Context-aware signal propagation
- Context-based execution state
- Context integration for complex flows

**Test file**: `tests/flowengine/test_trampoline.py`
**Test coverage**:
- Trampoline execution correctness
- Signal propagation and handling
- Stack safety for deep recursion
- Integration with existing combinators
- Performance characteristics
- Error handling in trampoline execution

**Dependencies**: `flowengine.flow`
**Coverage**: 100% - all trampoline features (minus context)

---

### Epic 29: Migrate ergonomics tests
**Unit**: API ergonomics and usability test suite
**Source**: `old/tests/flow_engine/test_ergonomics.py` (391 lines)
**Target**: `tests/flowengine/test_ergonomics.py`

**Test classes to migrate**:
1. `TestFlowChaining` - Method chaining ergonomics
   - Methods: `test_fluent_api()`, `test_method_composition()`, `test_readable_chains()`

2. `TestFlowCreation` - Flow creation patterns
   - Methods: `test_factory_methods()`, `test_decorator_patterns()`, `test_lambda_flows()`

3. `TestFlowDebugging` - Debugging ergonomics
   - Methods: `test_debug_labels()`, `test_flow_inspection()`, `test_error_messages()`

4. `TestFlowComposition` - Composition patterns
   - Methods: `test_pipe_operator()`, `test_compose_function()`, `test_nested_composition()`

5. `TestFlowDocumentation` - Self-documenting flows
   - Methods: `test_flow_names()`, `test_metadata_preservation()`, `test_introspection()`

**Ergonomics test scenarios**:
- Fluent API usability
- Method discoverability
- Error message clarity
- Documentation and introspection
- IDE integration (type hints)
- Common usage patterns
- Performance of ergonomic features

**Dependencies**: Complete core system
**Coverage**: 100% - all ergonomic features

---

### Epic 30: Migrate property-based tests
**Unit**: Property-based testing suite using Hypothesis
**Source**: `old/tests/flow_engine/test_property_based.py` (525 lines)
**Target**: `tests/flowengine/test_property_based.py`

**Test classes to migrate**:
1. `TestFlowProperties` - Core flow properties
   - Methods: `test_flow_composition_associativity()`, `test_flow_identity_laws()`, `test_flow_functor_laws()`

2. `TestCombinatorProperties` - Combinator mathematical properties
   - Methods: `test_map_composition()`, `test_filter_composition()`, `test_associativity_laws()`

3. `TestStreamProperties` - Stream processing properties
   - Methods: `test_stream_ordering()`, `test_stream_completeness()`, `test_error_propagation()`

4. `TestPerformanceProperties` - Performance characteristics
   - Methods: `test_linear_scaling()`, `test_memory_bounds()`, `test_time_complexity()`

**Property-based test strategies**:
- Generate random flow compositions
- Test mathematical laws (associativity, identity)
- Verify stream processing invariants
- Test error handling properties
- Performance characteristic verification
- Resource usage bounds checking

**Hypothesis strategies**:
```python
@composite
def flow_strategy(draw):
    """Generate arbitrary flows for testing."""

@composite
def stream_strategy(draw):
    """Generate arbitrary streams for testing."""

@composite
def combinator_strategy(draw):
    """Generate arbitrary combinator compositions."""
```

**Dependencies**: Complete core system, hypothesis library
**Coverage**: 100% - mathematical properties and invariants

---

### Epic 31: Create lazy imports framework
**Unit**: Lazy import framework for optional dependencies
**Source**: `old/goldentooth_agent/flow_engine/lazy_imports.py` (36 lines, adapted)
**Target**: `src/flowengine/lazy_imports.py`

**Classes to migrate**:
1. `LazyImport` - Lazy import wrapper
   - Properties: `module_name`, `imported_module`, `is_available`
   - Methods: `get_module()`, `get_attribute()`, `is_available()`

**Functions to migrate** (4 functions, adapted for standalone use):
2. `lazy_import(module_name)` - Create lazy import
3. `try_import(module_name, fallback)` - Try import with fallback
4. `check_availability(module_name)` - Check if module available
5. `get_available_integrations()` - List available integrations

**Lazy import targets** (prepared for future integration):
- `goldentooth_agent.core.context` - Context system (optional)
- `goldentooth_agent.core.util.maybe_await` - Async utilities (optional)
- Third-party visualization libraries (optional)
- Third-party export formats (optional)

**Features**:
- Graceful degradation when dependencies unavailable
- Runtime availability checking
- Fallback functionality
- Clear error messages for missing dependencies

**Test file**: `tests/flowengine/test_lazy_imports.py`
**Test coverage**:
- Lazy loading mechanism
- Availability checking
- Fallback behavior
- Error handling for missing modules
- Integration readiness

**Dependencies**: None
**Coverage**: 100% - all lazy import functionality

---

### Epic 32: Create integration interfaces
**Unit**: Integration interface definitions
**Target**: `src/flowengine/integrations/__init__.py`

**Protocol definitions** (prepared for future integration):
```python
from typing import Protocol, TypeVar, Any

T = TypeVar("T")

class ContextIntegrationProtocol(Protocol):
    """Protocol for context system integration."""

    def get_context_value(self, key: str) -> Any: ...
    def set_context_value(self, key: str, value: Any) -> None: ...
    def with_context(self, updates: dict[str, Any]) -> "ContextIntegrationProtocol": ...

class LoggingIntegrationProtocol(Protocol):
    """Protocol for logging system integration."""

    def log(self, level: str, message: str, **kwargs: Any) -> None: ...
    def get_logger(self, name: str) -> Any: ...

class MetricsIntegrationProtocol(Protocol):
    """Protocol for metrics system integration."""

    def record_metric(self, name: str, value: float, tags: dict[str, str]) -> None: ...
    def increment_counter(self, name: str, tags: dict[str, str]) -> None: ...
```

**Integration registry**:
```python
class IntegrationRegistry:
    """Registry for optional integrations."""

    def register_context_integration(self, integration: ContextIntegrationProtocol) -> None: ...
    def register_logging_integration(self, integration: LoggingIntegrationProtocol) -> None: ...
    def register_metrics_integration(self, integration: MetricsIntegrationProtocol) -> None: ...
```

**Test file**: `tests/flowengine/integrations/test_interfaces.py`
**Dependencies**: `flowengine.protocols`
**Coverage**: 100% - integration interface definitions

---

### Epic 33: Create integration tests structure
**Unit**: Integration test framework
**Target**: `tests/flowengine/integrations/__init__.py`

**Test base classes**:
```python
class IntegrationTestBase:
    """Base class for integration tests."""

    def setup_integration(self) -> None: ...
    def teardown_integration(self) -> None: ...
    def assert_integration_working(self) -> None: ...

class MockContextIntegration:
    """Mock context integration for testing."""

class MockLoggingIntegration:
    """Mock logging integration for testing."""

class MockMetricsIntegration:
    """Mock metrics integration for testing."""
```

**Test utilities**:
```python
def create_mock_context() -> MockContextIntegration: ...
def create_mock_logger() -> MockLoggingIntegration: ...
def create_mock_metrics() -> MockMetricsIntegration: ...
def assert_no_integration_errors() -> None: ...
```

**Dependencies**: `flowengine.integrations`
**Coverage**: 100% - integration test framework

---

### Epic 34: Migrate core flow tests
**Unit**: Comprehensive core flow test suite
**Source**: `old/tests/flow_engine/core/test_main.py` (992 lines)
**Target**: `tests/flowengine/test_flow_core.py`

**Test classes to migrate**:
1. `TestFlowConstruction` - Flow creation and initialization
   - Methods: `test_flow_creation()`, `test_flow_metadata()`, `test_flow_naming()`

2. `TestFlowExecution` - Core execution functionality
   - Methods: `test_basic_execution()`, `test_async_execution()`, `test_stream_processing()`

3. `TestFlowComposition` - Flow composition patterns
   - Methods: `test_pipe_composition()`, `test_nested_composition()`, `test_complex_composition()`

4. `TestFlowMethods` - All Flow class methods
   - Methods: `test_map()`, `test_filter()`, `test_flat_map()`, `test_for_each()`, `test_to_list()`, etc.

5. `TestFlowFactories` - Factory method functionality
   - Methods: `test_from_value_fn()`, `test_from_sync_fn()`, `test_from_event_fn()`, etc.

6. `TestFlowErrorHandling` - Error scenarios
   - Methods: `test_execution_errors()`, `test_composition_errors()`, `test_resource_cleanup()`

7. `TestFlowPerformance` - Performance characteristics
   - Methods: `test_large_streams()`, `test_memory_usage()`, `test_execution_time()`

**Comprehensive test scenarios**:
- All 23 Flow methods with edge cases
- Complex composition patterns
- Error propagation and handling
- Resource management
- Performance under load
- Memory leak detection
- Async behavior verification

**Dependencies**: Complete core system
**Coverage**: 100% - exhaustive core flow testing

---

### Epic 35: Create main test conftest
**Unit**: Global test configuration
**Source**: `old/tests/flow_engine/conftest.py` (83 lines)
**Target**: `tests/flowengine/conftest.py`

**Global fixtures**:
1. `event_loop` - Async test event loop
2. `async_test_timeout` - Test timeout configuration
3. `test_data_dir` - Test data directory
4. `temp_dir` - Temporary directory for tests
5. `sample_data` - Common test data sets
6. `performance_config` - Performance test configuration
7. `debug_config` - Debug test configuration

**Test utilities**:
8. `async_range(n)` - Generate async range
9. `async_list(items)` - Create async iterator from list
10. `collect_async(iterator)` - Collect async iterator to list
11. `assert_streams_equal(stream1, stream2)` - Compare async streams
12. `time_async_operation(coro)` - Time async operations
13. `assert_performance_within_bounds(operation, bounds)` - Performance assertions

**Test data factories**:
14. `create_test_flow()` - Generic test flow factory
15. `create_large_stream()` - Large data stream factory
16. `create_error_stream()` - Error-producing stream factory
17. `create_slow_stream()` - Slow stream factory

**Global configuration**:
- Pytest async configuration
- Test timeouts and retries
- Performance test parameters
- Debug and logging settings
- Resource cleanup procedures

**Dependencies**: None (pure pytest configuration)
**Coverage**: 100% - all test utilities and fixtures

---

## Phase 6: Package Completion (Epics 36-40)

### Epic 36: Create main package __init__.py
**Unit**: Complete flowengine package exports
**Source**: `old/goldentooth_agent/flow_engine/__init__.py` (319 lines, adapted)
**Target**: `src/flowengine/__init__.py`

**Complete package export structure**:
```python
"""
FlowEngine - Async stream processing and flow composition library.

A high-performance, type-safe library for building complex data processing
pipelines using functional composition patterns.
"""

# Core classes
from .flow import Flow
from .exceptions import (
    FlowError, FlowValidationError, FlowExecutionError,
    FlowTimeoutError, FlowConfigurationError
)
from .protocols import ContextKeyProtocol, ContextProtocol, FlowProtocol

# All combinators (68 functions)
from .combinators import *

# Complete observability system (50+ exports)
from .observability import *

# Registry system (11 exports)
from .registry import *

# Extensions and advanced features
from .extensions import (
    FlowExtension, ExtensionRegistry, install_extension, uninstall_extension,
    enable_extension, disable_extension, list_extensions, get_extension_info
)

# Trampoline execution (12 exports)
from .trampoline import (
    SHOULD_EXIT_KEY, SHOULD_BREAK_KEY, SHOULD_SKIP_KEY, TrampolineFlowCombinators,
    extend_flow_with_trampoline, trampoline_execute, should_exit, should_break,
    should_skip, create_exit_signal, create_break_signal, create_skip_signal
)

# Integration support
from .integrations import IntegrationRegistry
from .lazy_imports import lazy_import, try_import, check_availability

# Package metadata
__version__ = "1.0.0"
__author__ = "Goldentooth Agent"
__description__ = "Async stream processing and flow composition library"

# Automatically extend Flow with trampoline methods
extend_flow_with_trampoline()

__all__ = [
    # Core (6 exports)
    "Flow", "FlowError", "FlowValidationError", "FlowExecutionError",
    "FlowTimeoutError", "FlowConfigurationError",

    # Protocols (3 exports)
    "ContextKeyProtocol", "ContextProtocol", "FlowProtocol",

    # All combinator exports (68 exports via *)
    # All observability exports (50+ exports via *)
    # All registry exports (11 exports via *)

    # Extensions (8 exports)
    "FlowExtension", "ExtensionRegistry", "install_extension", "uninstall_extension",
    "enable_extension", "disable_extension", "list_extensions", "get_extension_info",

    # Trampoline (12 exports)
    "SHOULD_EXIT_KEY", "SHOULD_BREAK_KEY", "SHOULD_SKIP_KEY", "TrampolineFlowCombinators",
    "extend_flow_with_trampoline", "trampoline_execute", "should_exit", "should_break",
    "should_skip", "create_exit_signal", "create_break_signal", "create_skip_signal",

    # Integration (4 exports)
    "IntegrationRegistry", "lazy_import", "try_import", "check_availability",

    # Metadata
    "__version__", "__author__", "__description__"
]
```

**Package features verification**:
- All 150+ exports properly exposed
- Version and metadata
- Automatic trampoline integration
- Comprehensive __all__ list

**Dependencies**: All flowengine modules
**Coverage**: 100% - complete package API

---

### Epic 37: Update pyproject.toml
**Unit**: Package configuration and build system
**Target**: `pyproject.toml` (updates)

**Package configuration additions**:
```toml
[project]
name = "goldentooth-agent"
# ... existing config ...

# Add flowengine as internal package
[tool.poetry]
packages = [
    { include = "goldentooth_agent", from = "src" },
    { include = "git_hooks", from = "src" },
    { include = "flowengine", from = "src" }  # ADD THIS
]

# Optional dependencies for flowengine
[project.optional-dependencies]
flowengine-viz = ["graphviz>=0.20.0", "matplotlib>=3.5.0"]
flowengine-export = ["pandas>=1.5.0", "openpyxl>=3.0.0"]
flowengine-dev = ["hypothesis>=6.0.0", "pytest-benchmark>=4.0.0"]

# Tool configuration for flowengine
[tool.mypy]
# Add flowengine to type checking
[[tool.mypy.overrides]]
module = ["flowengine.*"]
strict = true
warn_return_any = true
disallow_untyped_defs = true

[tool.black]
# Include flowengine in formatting
include = '\.pyi?$'
extend-exclude = '''
/(
  \.eggs | \.git | \.hg | \.mypy_cache | \.tox | \.venv | build | dist | old
)/
'''

[tool.ruff]
# Include flowengine in linting
extend-exclude = ["old/"]

[tool.vulture]
# Include flowengine in dead code detection
paths = ["src"]

[tool.pytest.ini_options]
# Test configuration for flowengine
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
```

**Dependencies**: Complete flowengine package
**Coverage**: Build system configuration

---

### Epic 38: Add integration to goldentooth_agent
**Unit**: Integration layer with main package
**Target**: `src/goldentooth_agent/core/flow_engine.py`

**Integration module**:
```python
"""
Flow Engine integration for Goldentooth Agent.

This module provides the integration layer between the standalone flowengine
package and the goldentooth_agent system.
"""

from typing import Any, Optional
import flowengine
from flowengine import Flow, FlowRegistry

# Re-export flowengine for convenience
from flowengine import *  # noqa: F403, F401

class GoldentoothFlowIntegration:
    """Integration between flowengine and goldentooth_agent."""

    def __init__(self) -> None:
        self.registry = FlowRegistry()
        self._context_integration: Optional[Any] = None

    def setup_context_integration(self, context_system: Any) -> None:
        """Setup integration with goldentooth context system."""
        # Future: integrate with context system
        pass

    def register_agent_flows(self) -> None:
        """Register common agent flows."""
        # Register flows commonly used by agents
        pass

    def get_flow_registry(self) -> FlowRegistry:
        """Get the flow registry."""
        return self.registry

# Global integration instance
flow_integration = GoldentoothFlowIntegration()

# Convenience functions
def get_flow_registry() -> FlowRegistry:
    """Get the global flow registry."""
    return flow_integration.get_flow_registry()

def setup_flow_integration(context_system: Any = None) -> None:
    """Setup flow engine integration."""
    if context_system:
        flow_integration.setup_context_integration(context_system)
    flow_integration.register_agent_flows()
```

**Test file**: `tests/goldentooth_agent/core/test_flow_engine_integration.py`
**Dependencies**: `flowengine` package
**Coverage**: 100% - integration functionality

---

### Epic 39: Create goldentooth integration tests
**Unit**: Integration test suite
**Target**: `tests/goldentooth_agent/core/test_flow_engine_integration.py`

**Test classes**:
1. `TestFlowEngineIntegration` - Basic integration
   - Methods: `test_flowengine_import()`, `test_flow_creation()`, `test_registry_access()`

2. `TestGoldentoothFlowIntegration` - Integration class tests
   - Methods: `test_integration_setup()`, `test_context_integration()`, `test_agent_flows()`

3. `TestFlowRegistryIntegration` - Registry integration
   - Methods: `test_registry_access()`, `test_flow_registration()`, `test_registry_persistence()`

**Integration test scenarios**:
- Flowengine package import and usage
- Integration with existing goldentooth systems
- Registry functionality within goldentooth
- Resource sharing and cleanup
- Error handling and isolation

**Dependencies**: Complete goldentooth integration
**Coverage**: 100% - integration scenarios

---

### Epic 40: Update package documentation
**Unit**: Package documentation and README
**Target**: `src/flowengine/README.md`

**Documentation sections**:
1. **Overview** - What is FlowEngine
2. **Installation** - How to install and import
3. **Quick Start** - Basic usage examples
4. **Core Concepts** - Flows, streams, combinators
5. **API Reference** - Complete API documentation
6. **Examples** - Real-world usage patterns
7. **Performance** - Performance characteristics
8. **Integration** - Integration with other systems
9. **Contributing** - Development guidelines
10. **License** - License information

**Code examples**:
```python
# Basic flow creation and execution
from flowengine import Flow

# Create a flow that doubles numbers
double_flow = Flow.from_sync_fn(lambda x: x * 2)

# Create input stream
async def number_stream():
    for i in range(5):
        yield i

# Execute flow
result = await double_flow(number_stream()).to_list()
print(result)  # [0, 2, 4, 6, 8]

# Complex composition
from flowengine import map_stream, filter_stream, compose

# Compose multiple operations
pipeline = compose(
    map_stream(lambda x: x * 2),
    filter_stream(lambda x: x > 5),
    map_stream(lambda x: f"Result: {x}")
)

# Execute pipeline
result = await pipeline(number_stream()).to_list()
print(result)  # ["Result: 6", "Result: 8"]
```

## File Size and Module Constraints

### Adherence to Guidelines

- **File Size**: All files under 1,000 lines (largest is health.py at 619 lines)
- **Module Size**: Will track total lines per module during migration
- **Function Size**: All functions under 10 lines (verified in source)

### Large Files Breakdown

1. **health.py (619 lines)**: Will be split into:
   - `health/core.py` - Core health monitoring (300 lines)
   - `health/checks.py` - Health check implementations (200 lines)
   - `health/reporting.py` - Health reporting (119 lines)

2. **analysis.py (551 lines)**: Will be split into:
   - `analysis/core.py` - Core analysis tools (300 lines)
   - `analysis/graph.py` - Flow graph analysis (151 lines)
   - `analysis/optimization.py` - Flow optimizations (100 lines)

3. **advanced.py (474 lines)**: Will be split into:
   - `advanced/core.py` - Core advanced combinators (250 lines)
   - `advanced/circuit_breaker.py` - Circuit breaker logic (150 lines)
   - `advanced/parallel.py` - Parallel processing (74 lines)

## Testing Strategy

### Test Coverage Requirements

- **100% line coverage** for all functions
- **100% branch coverage** for all conditional logic
- **100% expression coverage** for all operations

### Test Structure

Tests will mirror source structure exactly:
```
tests/flowengine/
├── __init__.py
├── conftest.py
├── test_flow.py
├── test_exceptions.py
├── test_protocols.py
├── combinators/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_basic.py
│   ├── test_aggregation.py
│   ├── test_advanced.py
│   ├── test_control_flow.py
│   ├── test_observability.py
│   ├── test_sources.py
│   ├── test_temporal.py
│   └── test_utils.py
├── observability/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_analysis.py
│   ├── test_debugging.py
│   ├── test_health.py
│   ├── test_performance.py
│   ├── test_benchmarks.py
│   └── test_integration.py
└── registry/
    ├── __init__.py
    ├── conftest.py
    ├── test_main.py
    └── test_registry.py
```

### Test Factory Pattern

Each test module will include factory functions for generating test data:

```python
def get_mock_flow(overrides: Optional[dict] = None) -> Flow:
    """Factory for creating test flows."""

def get_mock_stream(items: list, overrides: Optional[dict] = None) -> AsyncIterator:
    """Factory for creating test streams."""
```

## Context Integration Strategy

### Phase 1: Deferred Context Features

The following features depend on the context system and will be **temporarily removed** during initial migration:

1. **trampoline.py** - Context-dependent execution control
2. **control_flow.py** - Context-aware control flow combinators
3. **lazy_imports.py** - Context system integration

### Phase 2: Context Abstraction (Future)

After core migration, context features will be re-implemented using:

1. **Protocol-based interfaces** - Abstract context dependencies
2. **Dependency injection** - Allow context system to be provided
3. **Optional integration** - Work with or without context

### Phase 3: Context Re-integration (Future)

Final phase will reconnect with the new context system using clean interfaces.

## Risk Mitigation

### Identified Risks

1. **File Size Violations**: Some files exceed 1,000 lines
   - **Mitigation**: Pre-split large files during migration

2. **Context Dependencies**: Some features require context system
   - **Mitigation**: Deferred migration, protocol-based interfaces

3. **Test Coverage**: Ensuring 100% coverage during migration
   - **Mitigation**: Migrate tests simultaneously with source

### Testing Strategy

Each commit will:
1. Run full test suite
2. Verify 100% test coverage
3. Pass all pre-commit hooks
4. Maintain working codebase state

## Quality Assurance

### Pre-commit Hooks

All commits must pass:
- mypy type checking
- ruff linting
- black formatting
- pytest with 100% coverage
- File size validation
- Module size validation

### Documentation Requirements

Each unit will include:
- Comprehensive docstrings
- Type annotations
- Usage examples
- Error handling documentation

## Timeline Estimation

### Commit Velocity

- **Simple migrations** (< 100 lines): 1-2 commits per day
- **Complex migrations** (> 300 lines): 1 commit per 2 days
- **Test migrations**: 1 commit per day

### Total Estimated Timeline

- **40 epics** across 6 phases
- **Estimated duration**: 6-8 weeks
- **Parallel work possible**: Documentation, test creation

## Success Criteria

### Migration Complete When:

1. ✅ All 26 source files migrated with 100% test coverage
2. ✅ All 18 test files migrated and passing
3. ✅ No circular imports with goldentooth_agent
4. ✅ Package installable and importable standalone
5. ✅ Integration with goldentooth_agent functional
6. ✅ All pre-commit hooks passing
7. ✅ Documentation complete

### Quality Gates

- **No files > 1,000 lines**
- **No modules > 5,000 lines**
- **No functions > 10 lines**
- **100% test coverage**
- **Zero mypy errors**
- **All pre-commit hooks passing**

## Conclusion

This migration plan provides a systematic approach to extracting the Flow Engine while maintaining code quality, test coverage, and architectural integrity. The phased approach allows for incremental progress with each commit leaving the system in a working state.

The plan respects all constraints while delivering a high-quality, standalone Flow Engine package that can be used independently or integrated with the main goldentooth_agent system.
