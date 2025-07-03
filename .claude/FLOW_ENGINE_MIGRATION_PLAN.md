# Flow Engine Migration Plan

## Executive Summary

This document outlines the detailed migration plan for extracting the Flow Engine from `old/goldentooth_agent/flow_engine` into the new codebase structure. The Flow Engine consists of **5,954 lines of source code** across **26 files** with **9,010 lines of comprehensive tests** across **18 test files**.

## Key Statistics

- **Source Files**: 26 Python files (5,954 total lines)
- **Test Files**: 18 Python files (9,010 total lines)
- **Dependencies**: Standard library only (no third-party)
- **Context Integration**: Optional, with lazy loading architecture
- **Estimated Commits**: ~1800 individual commits (one per unit, where a unit is a SINGLE function, class method, etc, and its accompanying tests)

## Migration Strategy

Following requirements 1, 4, and 6, this migration will be executed as a **separate package** with **individual commits per unit** and **no circular imports**.

### Package Structure Decision

The Flow Engine will be extracted as `flowengine` - a **separate package** that:
- Has zero dependencies on `goldentooth_agent`
- Is a dependency OF `goldentooth_agent`
- Can be used standalone
- Follows the existing clean architecture

## Phase 1: Foundation (Epics 1-8)

### Phase 1A: Core Infrastructure (Epics 1-4)

**Epic 1: Create flowengine package structure**
- Create `src/flowengine/__init__.py`
- Create `src/flowengine/py.typed`
- Update `pyproject.toml` dependencies
- Create basic package structure

**Epic 2: Migrate core exceptions**
- File: `src/flowengine/exceptions.py`
- Source: `old/goldentooth_agent/flow_engine/core/exceptions.py` (31 lines)
- Tests: `tests/flowengine/test_exceptions.py`
- Dependencies: None

**Epic 3: Migrate protocols**
- File: `src/flowengine/protocols.py`
- Source: `old/goldentooth_agent/flow_engine/protocols.py` (56 lines)
- Tests: `tests/flowengine/test_protocols.py`
- Dependencies: None

**Epic 4: Migrate core Flow class**
- File: `src/flowengine/flow.py`
- Source: `old/goldentooth_agent/flow_engine/core/flow.py` (342 lines)
- Tests: `tests/flowengine/test_flow.py`
- Dependencies: `flowengine.exceptions`

### Phase 1B: Combinator Utilities (Epics 5-8)

**Epic 5: Migrate combinator utilities**
- File: `src/flowengine/combinators/utils.py`
- Source: `old/goldentooth_agent/flow_engine/combinators/utils.py` (28 lines)
- Tests: `tests/flowengine/combinators/test_utils.py`
- Dependencies: None

**Epic 6: Migrate sources combinators**
- File: `src/flowengine/combinators/sources.py`
- Source: `old/goldentooth_agent/flow_engine/combinators/sources.py` (85 lines)
- Tests: `tests/flowengine/combinators/test_sources.py`
- Dependencies: `flowengine.flow`, `flowengine.combinators.utils`

**Epic 7: Migrate basic combinators**
- File: `src/flowengine/combinators/basic.py`
- Source: `old/goldentooth_agent/flow_engine/combinators/basic.py` (231 lines)
- Tests: `tests/flowengine/combinators/test_basic.py`
- Dependencies: `flowengine.flow`, `flowengine.exceptions`, `flowengine.combinators.utils`

**Epic 8: Create basic combinators __init__.py**
- File: `src/flowengine/combinators/__init__.py` (partial)
- Export basic combinators
- Tests: Update existing tests

## Phase 2: Core Combinators (Epics 9-14)

**Epic 9: Migrate aggregation combinators**
- File: `src/flowengine/combinators/aggregation.py`
- Source: `old/goldentooth_agent/flow_engine/combinators/aggregation.py` (360 lines)
- Tests: `tests/flowengine/combinators/test_aggregation.py`
- Dependencies: `flowengine.flow`, `flowengine.combinators.basic`

**Epic 10: Migrate temporal combinators**
- File: `src/flowengine/combinators/temporal.py`
- Source: `old/goldentooth_agent/flow_engine/combinators/temporal.py` (160 lines)
- Tests: `tests/flowengine/combinators/test_temporal.py`
- Dependencies: `flowengine.flow`, `flowengine.combinators.basic`

**Epic 11: Migrate observability combinators**
- File: `src/flowengine/combinators/observability.py`
- Source: `old/goldentooth_agent/flow_engine/combinators/observability.py` (197 lines)
- Tests: `tests/flowengine/combinators/test_observability.py`
- Dependencies: `flowengine.flow`

**Epic 12: Migrate control flow combinators (without context)**
- File: `src/flowengine/combinators/control_flow.py`
- Source: `old/goldentooth_agent/flow_engine/combinators/control_flow.py` (419 lines)
- Tests: `tests/flowengine/combinators/test_control_flow.py`
- Dependencies: `flowengine.flow`, `flowengine.exceptions`
- **Note**: Remove context-dependent features initially

**Epic 13: Migrate advanced combinators**
- File: `src/flowengine/combinators/advanced.py`
- Source: `old/goldentooth_agent/flow_engine/combinators/advanced.py` (474 lines)
- Tests: `tests/flowengine/combinators/test_advanced.py`
- Dependencies: `flowengine.flow`, `flowengine.combinators.basic`

**Epic 14: Complete combinators __init__.py**
- File: `src/flowengine/combinators/__init__.py` (complete)
- Source: `old/goldentooth_agent/flow_engine/combinators/__init__.py` (171 lines)
- Export all combinators

## Phase 3: Observability System (Epics 15-22)

### Phase 3A: Core Observability (Epics 15-18)

**Epic 15: Migrate performance monitoring**
- File: `src/flowengine/observability/performance.py`
- Source: `old/goldentooth_agent/flow_engine/observability/performance.py` (362 lines)
- Tests: `tests/flowengine/observability/test_performance.py`
- Dependencies: `flowengine.flow`

**Epic 16: Migrate analysis tools**
- File: `src/flowengine/observability/analysis.py`
- Source: `old/goldentooth_agent/flow_engine/observability/analysis.py` (551 lines)
- Tests: `tests/flowengine/observability/test_analysis.py`
- Dependencies: `flowengine.flow`, `flowengine.combinators`

**Epic 17: Migrate debugging tools**
- File: `src/flowengine/observability/debugging.py`
- Source: `old/goldentooth_agent/flow_engine/observability/debugging.py` (436 lines)
- Tests: `tests/flowengine/observability/test_debugging.py`
- Dependencies: `flowengine.flow`, `flowengine.observability.performance`

**Epic 18: Migrate health monitoring**
- File: `src/flowengine/observability/health.py`
- Source: `old/goldentooth_agent/flow_engine/observability/health.py` (619 lines)
- Tests: `tests/flowengine/observability/test_health.py`
- Dependencies: `flowengine.flow`, `flowengine.exceptions`

### Phase 3B: Observability Integration (Epics 19-22)

**Epic 19: Create observability __init__.py**
- File: `src/flowengine/observability/__init__.py`
- Source: `old/goldentooth_agent/flow_engine/observability/__init__.py` (121 lines)
- Export all observability tools

**Epic 20: Migrate flow benchmarks tests**
- File: `tests/flowengine/observability/test_benchmarks.py`
- Source: `old/tests/flow_engine/observability/test_flow_benchmarks.py` (368 lines)
- Dependencies: Complete observability system

**Epic 21: Migrate observability integration tests**
- File: `tests/flowengine/observability/test_integration.py`
- Source: `old/tests/flow_engine/observability/test_observability_integration.py` (465 lines)
- Dependencies: Complete observability system

**Epic 22: Create observability test conftest**
- File: `tests/flowengine/observability/conftest.py`
- Test configuration for observability tests

## Phase 4: Registry System (Epics 23-26)

**Epic 23: Migrate flow registry**
- File: `src/flowengine/registry/main.py`
- Source: `old/goldentooth_agent/flow_engine/registry/main.py` (311 lines)
- Tests: `tests/flowengine/registry/test_main.py`
- Dependencies: `flowengine.flow`

**Epic 24: Create registry __init__.py**
- File: `src/flowengine/registry/__init__.py`
- Source: `old/goldentooth_agent/flow_engine/registry/__init__.py` (26 lines)
- Export registry functionality

**Epic 25: Migrate registry tests**
- File: `tests/flowengine/registry/test_registry.py`
- Source: `old/tests/flow_engine/registry/test_registry.py` (578 lines)
- Dependencies: Complete registry system

**Epic 26: Create registry test conftest**
- File: `tests/flowengine/registry/conftest.py`
- Test configuration for registry tests

## Phase 5: Advanced Features (Epics 27-35)

### Phase 5A: Standalone Features (Epics 27-30)

**Epic 27: Migrate extensions**
- File: `src/flowengine/extensions.py`
- Source: `old/goldentooth_agent/flow_engine/extensions.py` (79 lines)
- Tests: `tests/flowengine/test_extensions.py`
- Dependencies: `flowengine.flow`

**Epic 28: Migrate trampoline (without context)**
- File: `src/flowengine/trampoline.py`
- Source: `old/goldentooth_agent/flow_engine/trampoline.py` (335 lines, context-stripped)
- Tests: `tests/flowengine/test_trampoline.py`
- Dependencies: `flowengine.flow`
- **Note**: Remove context-dependent features initially

**Epic 29: Migrate ergonomics tests**
- File: `tests/flowengine/test_ergonomics.py`
- Source: `old/tests/flow_engine/test_ergonomics.py` (391 lines)
- Dependencies: Complete core system

**Epic 30: Migrate property-based tests**
- File: `tests/flowengine/test_property_based.py`
- Source: `old/tests/flow_engine/test_property_based.py` (525 lines)
- Dependencies: Complete core system, hypothesis

### Phase 5B: Integration Preparation (Epics 31-35)

**Epic 31: Create lazy imports framework**
- File: `src/flowengine/lazy_imports.py`
- Source: `old/goldentooth_agent/flow_engine/lazy_imports.py` (36 lines, adapted)
- Tests: `tests/flowengine/test_lazy_imports.py`
- Dependencies: None
- **Note**: Prepare for future context integration

**Epic 32: Create integration interfaces**
- File: `src/flowengine/integrations/__init__.py`
- Interface definitions for future integration

**Epic 33: Create integration tests structure**
- File: `tests/flowengine/integrations/__init__.py`
- Test structure for future integration

**Epic 34: Migrate core flow tests**
- File: `tests/flowengine/test_flow_core.py`
- Source: `old/tests/flow_engine/core/test_main.py` (992 lines)
- Dependencies: Complete core system

**Epic 35: Create main test conftest**
- File: `tests/flowengine/conftest.py`
- Source: `old/tests/flow_engine/conftest.py` (83 lines)
- Global test configuration

## Phase 6: Package Completion (Epics 36-40)

**Epic 36: Create main package __init__.py**
- File: `src/flowengine/__init__.py`
- Source: `old/goldentooth_agent/flow_engine/__init__.py` (319 lines, adapted)
- Export all functionality

**Epic 37: Update pyproject.toml**
- Add flowengine as separate package
- Configure package metadata
- Add to build system

**Epic 38: Add integration to goldentooth_agent**
- File: `src/goldentooth_agent/core/flow_engine.py`
- Import and integrate flowengine
- Minimal integration layer

**Epic 39: Create goldentooth integration tests**
- File: `tests/goldentooth_agent/core/test_flow_engine_integration.py`
- Test integration with main package

**Epic 40: Update package documentation**
- File: `src/flowengine/README.md`
- Documentation for standalone package

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
