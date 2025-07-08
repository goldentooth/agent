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
- When you prepare a commit, write the commit message to a file in a temporary directory, then create the commit using that message file. Do not write the message inline.

## Key Migration Learnings (from Context Migration Experience)

### Import Strategy for Tests
- **Use relative imports in tests**: `from context.symbol import Symbol` NOT `from src.context.symbol import Symbol`
- Poetry package structure works better with relative imports than absolute `src.` imports
- Test collection issues can occur when using absolute `src.` imports during pre-commit hooks

### Package Configuration
- **Always add new packages to pyproject.toml**: Add `{ include = "package_name", from = "src" }` to `[tool.poetry] packages`
- Run `poetry install` after adding new packages to update the development environment
- Package imports work through poetry's package management system

### Test Collection and Coverage
- Individual function tests should achieve 100% coverage for that specific function
- Global project coverage requirements (90%) may conflict during early migration phases
- Focus on individual function coverage rather than global project coverage during migration
- Pre-commit hooks run full test suite, so ensure all new test files can be collected properly

### Pre-commit Hook Considerations
- Hooks may stash/restore changes, causing import issues if not properly staged
- Always stage test files with correct imports before committing
- Import path consistency is critical for test collection success
- Use `git add` to stage corrected imports before running commit hooks

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

### ✅ Epic 41: Migrate extension registry class - DONE!
**Unit**: ExtensionRegistry management class
**Source**: `old/goldentooth_agent/flow_engine/extensions.py` (ExtensionRegistry class)
**Target**: `src/flowengine/extensions.py`

**Status**: ✅ **COMPLETED AND EXCEEDED REQUIREMENTS**

**Implemented Classes**:
1. `FlowExtension` - Abstract base class for all extensions
   - Properties: `name`, `description`, `enabled`
   - Methods: `on_flow_init()`, `get_methods()`, `get_config()`, `set_config()`

2. `ExtensionRegistry` - Extension management
   - Properties: `extensions`, `enabled_extensions`
   - Methods: `register_extension()`, `unregister_extension()`, `enable()`, `disable()`, `list_extensions()`

**Extension features**:
- Dynamic extension loading/unloading ✅
- Extension configuration management ✅
- Extension dependency resolution ✅
- Legacy support for function-based extensions ✅
- Legacy support for method extensions ✅
- Legacy support for initialization hooks ✅
- `extend_flow_class()` method for applying all extensions ✅

**Enhancements Beyond Requirements**:
- ✅ Comprehensive type safety with FlowExtension base class
- ✅ Legacy compatibility layer for old FlowExtensionRegistry patterns
- ✅ Configuration management with copy semantics
- ✅ Public methods for testing protected members
- ✅ Comprehensive test coverage (17 test cases)

**Dependencies**: ✅ FlowExtension class implemented
**Coverage**: ✅ 100% - extension registry functionality

---

### Epic 42: Migrate extension utility functions
**Unit**: Extension utility functions
**Source**: `old/goldentooth_agent/flow_engine/extensions.py` (utility functions)
**Target**: `src/flowengine/extensions.py`

**Functions to migrate**:
3. `install_extension(extension)` - Install flow extension
4. `uninstall_extension(name)` - Remove extension
5. `enable_extension(name)` - Enable extension
6. `disable_extension(name)` - Disable extension
7. `list_extensions()` - List available extensions
8. `get_extension_info(name)` - Get extension details

**Extension features**:
- Extension lifecycle management
- Extension information queries

**Dependencies**: Complete extension system
**Coverage**: 100% - extension utility functions

---

### Epic 43: Migrate trampoline constants and combinators
**Unit**: Trampoline constants and combinator class
**Source**: `old/goldentooth_agent/flow_engine/trampoline.py` (constants and TrampolineFlowCombinators)
**Target**: `src/flowengine/trampoline.py`

**Constants to migrate**:
1. `SHOULD_EXIT_KEY` - Trampoline exit signal key
2. `SHOULD_BREAK_KEY` - Trampoline break signal key
3. `SHOULD_SKIP_KEY` - Trampoline skip signal key

**Class to migrate**:
4. `TrampolineFlowCombinators` - Trampoline-aware combinators
   - Methods: `trampoline_map()`, `trampoline_filter()`, `trampoline_flat_map()`, `trampoline_fold()`

**Dependencies**: `flowengine.flow`
**Coverage**: 100% - trampoline constants and combinators

---

### Epic 44: Migrate trampoline execution functions
**Unit**: Trampoline execution functions
**Source**: `old/goldentooth_agent/flow_engine/trampoline.py` (execution functions)
**Target**: `src/flowengine/trampoline.py`

**Functions to migrate**:
5. `extend_flow_with_trampoline()` - Add trampoline methods to Flow class
6. `trampoline_execute(flow, stream)` - Execute with trampoline
7. `should_exit(item)` - Check for exit condition
8. `should_break(item)` - Check for break condition

**Trampoline features**:
- Non-recursive execution patterns
- Stack-safe execution for deep compositions

**Dependencies**: Trampoline constants and combinators
**Coverage**: 100% - trampoline execution functionality

---

### Epic 45: Migrate trampoline signal functions
**Unit**: Trampoline signal creation functions
**Source**: `old/goldentooth_agent/flow_engine/trampoline.py` (signal functions)
**Target**: `src/flowengine/trampoline.py`

**Functions to migrate**:
9. `should_skip(item)` - Check for skip condition
10. `create_exit_signal()` - Create exit signal
11. `create_break_signal()` - Create break signal
12. `create_skip_signal()` - Create skip signal

**Trampoline features**:
- Control flow signals (exit, break, skip)
- Signal-based flow control

**Dependencies**: Trampoline execution functions
**Coverage**: 100% - trampoline signal functionality

---

### Epic 49: Migrate property-based test class 1
**Unit**: Core flow and combinator property tests
**Source**: `old/tests/flow_engine/test_property_based.py` (TestFlowProperties, TestCombinatorProperties)
**Target**: `tests/flowengine/test_property_based.py`

**Test classes to migrate**:
1. `TestFlowProperties` - Core flow properties
   - Methods: `test_flow_composition_associativity()`, `test_flow_identity_laws()`, `test_flow_functor_laws()`

2. `TestCombinatorProperties` - Combinator mathematical properties
   - Methods: `test_map_composition()`, `test_filter_composition()`, `test_associativity_laws()`

**Property tests**:
- Mathematical laws (associativity, identity)
- Combinator composition properties

**Dependencies**: Complete core system, hypothesis library
**Coverage**: 100% - flow and combinator properties

---

### Epic 50: Migrate property-based test class 2
**Unit**: Stream and performance property tests
**Source**: `old/tests/flow_engine/test_property_based.py` (TestStreamProperties, TestPerformanceProperties)
**Target**: `tests/flowengine/test_property_based.py`

**Test classes to migrate**:
3. `TestStreamProperties` - Stream processing properties
   - Methods: `test_stream_ordering()`, `test_stream_completeness()`, `test_error_propagation()`

4. `TestPerformanceProperties` - Performance characteristics
   - Methods: `test_linear_scaling()`, `test_memory_bounds()`, `test_time_complexity()`

**Property tests**:
- Stream processing invariants
- Performance characteristic verification

**Dependencies**: Complete core system, hypothesis library
**Coverage**: 100% - stream and performance properties

---

### Epic 51: Create property-based test strategies
**Unit**: Hypothesis test strategies
**Source**: `old/tests/flow_engine/test_property_based.py` (strategy definitions)
**Target**: `tests/flowengine/test_property_based.py`

**Hypothesis strategies to create**:
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

**Strategy features**:
- Generate random flow compositions
- Test error handling properties
- Resource usage bounds checking

**Dependencies**: Complete core system, hypothesis library
**Coverage**: 100% - property test strategies

---

## Phase 6: Package Completion (Epics 52-60)

### Epic 52: Create lazy imports framework
**Unit**: Lazy import framework for optional dependencies
**Source**: `old/goldentooth_agent/flow_engine/lazy_imports.py` (36 lines, adapted)
**Target**: `src/flowengine/lazy_imports.py`

**Classes and functions to migrate**:
1. `LazyImport` - Lazy import wrapper
   - Properties: `module_name`, `imported_module`, `is_available`
   - Methods: `get_module()`, `get_attribute()`, `is_available()`

2. `lazy_import(module_name)` - Create lazy import
3. `try_import(module_name, fallback)` - Try import with fallback

**Dependencies**: None
**Coverage**: 100% - lazy import base functionality

---

### Epic 53: Complete lazy imports framework
**Unit**: Complete lazy import system
**Source**: `old/goldentooth_agent/flow_engine/lazy_imports.py` (remaining functions)
**Target**: `src/flowengine/lazy_imports.py`

**Functions to complete**:
4. `check_availability(module_name)` - Check if module available
5. `get_available_integrations()` - List available integrations

**Lazy import targets** (prepared for future integration):
- `goldentooth_agent.core.context` - Context system (optional)
- `goldentooth_agent.core.util.maybe_await` - Async utilities (optional)
- Third-party visualization libraries (optional)

**Dependencies**: LazyImport base classes
**Coverage**: 100% - complete lazy import functionality

---

### Epic 54: Create integration interfaces
**Unit**: Integration interface definitions
**Target**: `src/flowengine/integrations/__init__.py`

**Protocol definitions**:
```python
from typing import Protocol, TypeVar, Any

T = TypeVar("T")

class ContextIntegrationProtocol(Protocol):
    """Protocol for context system integration."""
    def get_context_value(self, key: str) -> Any: ...
    def set_context_value(self, key: str, value: Any) -> None: ...
    def with_context(self, updates: dict[str, Any]) -> "ContextIntegrationProtocol": ...
```

**Dependencies**: `flowengine.protocols`
**Coverage**: 100% - context integration protocol

---

### Epic 55: Complete integration interfaces
**Unit**: Complete integration protocol definitions
**Target**: `src/flowengine/integrations/__init__.py`

**Additional protocols**:
```python
class LoggingIntegrationProtocol(Protocol):
    """Protocol for logging system integration."""
    def log(self, level: str, message: str, **kwargs: Any) -> None: ...
    def get_logger(self, name: str) -> Any: ...

class MetricsIntegrationProtocol(Protocol):
    """Protocol for metrics system integration."""
    def record_metric(self, name: str, value: float, tags: dict[str, str]) -> None: ...
    def increment_counter(self, name: str, tags: dict[str, str]) -> None: ...
```

**Dependencies**: Context integration protocol
**Coverage**: 100% - complete integration protocols

---

### Epic 56: Create integration registry
**Unit**: Integration registry implementation
**Target**: `src/flowengine/integrations/__init__.py`

**Integration registry**:
```python
class IntegrationRegistry:
    """Registry for optional integrations."""

    def register_context_integration(self, integration: ContextIntegrationProtocol) -> None: ...
    def register_logging_integration(self, integration: LoggingIntegrationProtocol) -> None: ...
    def register_metrics_integration(self, integration: MetricsIntegrationProtocol) -> None: ...
```

**Dependencies**: All integration protocols
**Coverage**: 100% - integration registry functionality

---

### Epic 57: Migrate core flow tests part 1
**Unit**: Flow construction and execution tests
**Source**: `old/tests/flow_engine/core/test_main.py` (TestFlowConstruction, TestFlowExecution)
**Target**: `tests/flowengine/test_flow_core.py`

**Test classes to migrate**:
1. `TestFlowConstruction` - Flow creation and initialization
   - Methods: `test_flow_creation()`, `test_flow_metadata()`, `test_flow_naming()`

2. `TestFlowExecution` - Core execution functionality
   - Methods: `test_basic_execution()`, `test_async_execution()`, `test_stream_processing()`

**Dependencies**: Complete core system
**Coverage**: 100% - flow construction and execution

---

### Epic 58: Migrate core flow tests part 2
**Unit**: Flow composition and methods tests
**Source**: `old/tests/flow_engine/core/test_main.py` (TestFlowComposition, TestFlowMethods)
**Target**: `tests/flowengine/test_flow_core.py`

**Test classes to migrate**:
3. `TestFlowComposition` - Flow composition patterns
   - Methods: `test_pipe_composition()`, `test_nested_composition()`, `test_complex_composition()`

4. `TestFlowMethods` - All Flow class methods
   - Methods: `test_map()`, `test_filter()`, `test_flat_map()`, `test_for_each()`, `test_to_list()`, etc.

**Dependencies**: Complete core system
**Coverage**: 100% - flow composition and methods

---

### Epic 59: Migrate core flow tests part 3
**Unit**: Flow factories and error handling tests
**Source**: `old/tests/flow_engine/core/test_main.py` (TestFlowFactories, TestFlowErrorHandling, TestFlowPerformance)
**Target**: `tests/flowengine/test_flow_core.py`

**Test classes to migrate**:
5. `TestFlowFactories` - Factory method functionality
   - Methods: `test_from_value_fn()`, `test_from_sync_fn()`, `test_from_event_fn()`, etc.

6. `TestFlowErrorHandling` - Error scenarios
   - Methods: `test_execution_errors()`, `test_composition_errors()`, `test_resource_cleanup()`

7. `TestFlowPerformance` - Performance characteristics
   - Methods: `test_large_streams()`, `test_memory_usage()`, `test_execution_time()`

**Dependencies**: Complete core system
**Coverage**: 100% - flow factories, error handling, and performance

---

### Epic 60: Create main test conftest and complete package
**Unit**: Global test configuration and package completion
**Source**: `old/tests/flow_engine/conftest.py` (83 lines)
**Target**: `tests/flowengine/conftest.py` and complete package setup

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

**Package completion tasks**:
- Create main package `__init__.py` with all exports
- Update `pyproject.toml` configuration
- Add integration to `goldentooth_agent`
- Create integration tests
- Update package documentation

**Dependencies**: All flowengine modules
**Coverage**: 100% - complete package and test infrastructure

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
