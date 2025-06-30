# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Rules
- No Python source file should ever be longer than about 1000 lines. If it approaches that length, start thinking about refactoring and submodularizing.
- Every Python module or submodule should have a comprehensive README.md describing the contents of the module, usage examples, key components, dependencies, file count, lines-of-code and other statistics, test coverage statistics, etc. This file should be updated for accuracy whenever a Python file contained in the module is touched. The README.md must always contain a full specification of the public API.
- **README.meta.yaml files are automatically generated and maintained by pre-commit hooks.** Module metadata (symbols, dependencies, metrics) is kept current without manual intervention.
- We follow strict Test-Driven Development practices and aim for 100% coverage of all API functionality. Do not write brittle tests that focus too much on implementation details; instead, ensure all functionality can be tested through module-level APIs. We want 100% coverage of every public API reachable from outside a given module.
- This is a private project and I am the only user. We do not need to maintain backward compatibility or legacy code. Our only responsibility is to ensure that the code always works on deployment and any resources (e.g. RAG source documents) are maintained within a version-controlled repository.

## Current Project State

**Status**: This is a **mature, production-ready** codebase with 25K+ lines of code implementing a sophisticated AI agent system with RAG capabilities, flow-based architecture, and comprehensive tooling.

## Development Guidelines

**IMPORTANT**: This project follows strict development guidelines documented in the `guidelines/` directory. **Always review relevant guidelines before making changes.**

- **[Code Style](guidelines/code-style.md)**: Formatting, naming conventions, file organization
- **[Testing Standards](guidelines/testing-standards.md)**: TDD practices, test organization, coverage requirements
- **[Type Safety](guidelines/type-safety.md)**: Type annotation requirements, mypy configuration
- **[Type Safety Development](guidelines/type-safety-development.md)**: Practical guidelines to prevent common type errors
- **[Architecture](guidelines/architecture.md)**: System design patterns, dependency injection, module organization
- **[Performance](guidelines/performance.md)**: Performance standards, optimization strategies, benchmarking
- **[Documentation](guidelines/documentation.md)**: Documentation standards for code, APIs, and modules
- **[Module Development](guidelines/module-development.md)**: Working with large modules, refactoring strategies
- **[Error Handling](guidelines/error-handling.md)**: Exception patterns, async error handling, recovery strategies

These guidelines are enforced through pre-commit hooks, CI/CD pipelines, and code review processes.

## Development Commands

```bash
# Install dependencies
poetry install

# Run the agent CLI
goldentooth-agent --help
goldentooth-agent chat                      # Interactive chat with various agents
goldentooth-agent chat --agent rag          # RAG-powered document chat
goldentooth-agent send "query" --agent rag  # Single message mode

# Testing
poetry run poe test                      # Run all tests
poetry run poe test-cov                  # Run tests with coverage
poetry run poe test-sanity               # Basic sanity tests
poetry run poe test-core                 # All core module tests

# Coverage Analysis - Finding Low/No Coverage Areas
poetry run poe test-cov-report           # HTML + terminal coverage reports
poetry run poe test-cov-check            # Enforce 85% minimum coverage (fails if below)
poetry run poe test-cov-analyze          # Custom analysis script - shows lowest coverage files
poetry run poe test-cov-targets          # Top 10 files needing coverage attention

# For detailed coverage analysis guidance, see: coverage-quick-reference.md

# Coverage Analysis Workflow:
# 1. Run: poetry run poe test-cov-analyze
# 2. Review output for files with <85% coverage
# 3. Check htmlcov/index.html for detailed line-by-line analysis
# 4. Focus on public APIs and critical business logic first
# 5. Use: poetry run poe test-cov-check to validate improvements

# Coverage Report Interpretation:
# - Files with 0% coverage = completely untested (highest priority)
# - Files with <50% coverage = major gaps (high priority)  
# - Files with 50-84% coverage = missing edge cases (medium priority)
# - Focus on core/ modules over cli/ modules for critical coverage

# Type checking
poetry run poe typecheck                 # Type check source code with mypy
poetry run poe typecheck-all             # Type check entire project including tests

# Quality checks (run before committing)
poetry run poe test && poetry run poe typecheck

# Type Safety Pre-commit Checklist:
# - All functions have return type annotations (-> Type or -> None)
# - Variables with unclear types are annotated (var: Type = value)
# - No [no-untyped-def] or [var-annotated] errors in your changes
# - Function calls match expected signatures

# Module metadata management (automated via pre-commit)
goldentooth-agent dev module update [path]      # Update specific module
goldentooth-agent dev module update-all         # Update all modules
goldentooth-agent dev module update-changed     # Update only changed modules
goldentooth-agent dev module validate          # Validate metadata accuracy

# Build package
poetry build
```

## Architecture Overview

### Core System Architecture

```
src/goldentooth_agent/
├── cli/                    # CLI interface (Typer-based)
│   ├── main.py            # Main CLI app
│   └── commands/          # Chat, tools, and other commands
├── core/                  # Core system modules (25K+ LOC)
│   ├── context/           # Context management system
│   ├── flow/              # Functional flow composition (5K+ LOC)
│   ├── flow_agent/        # Agent framework
│   ├── embeddings/        # Vector embeddings & search
│   ├── rag/               # Retrieval-Augmented Generation
│   ├── llm/               # LLM clients (Claude, etc.)
│   ├── document_store/    # YAML document management
│   ├── paths/             # Cross-platform path handling
│   ├── util/              # Shared utilities
│   └── background_loop/   # Async background processing
└── data/                  # Static configuration data
```

### Current Implementation Status

**✅ Fully Implemented:**
- Flow-based functional architecture with composition
- Context management with snapshots and history tracking
- RAG system with OpenAI embeddings and hybrid search
- Document store with GitHub, notes, and goldentooth data
- CLI with interactive and single-message modes
- Vector store with sqlite-vec for semantic search
- Comprehensive dependency injection with Antidote
- Background processing and event systems

**🔄 In Progress:**
- Module documentation and API surface documentation
- Code quality standardization across large modules
- Performance optimization for complex flow compositions

## Code Quality Standards

### Type Safety Requirements

**CRITICAL**: This project maintains strict type safety. All code must pass both `mypy --strict` and Pylance checks.

#### Type Annotation Standards:

```python
# ✅ Required: Complete function annotations
def process_data(items: list[str], count: int = 10) -> dict[str, Any]:
    """Process data with proper typing."""
    ...

# ✅ Required: Optional for nullable parameters
def create_flow(fn: Optional[Callable[[Input], Output]] = None) -> Flow:
    ...

# ✅ Required: Explicit variable annotations when unclear
errors: list[str] = []
queue: asyncio.Queue[tuple[A, B]] = asyncio.Queue()

# ✅ Required: Proper generic constraints
T = TypeVar("T")
R = TypeVar("R")

def process(item: T) -> R:
    ...
```

#### Type Checking Workflow:

1. **Before any commit**: Run `poetry run poe typecheck`
2. **Fix all type errors**: Zero tolerance for type errors
3. **Prefer specific types**: Avoid `Any` except when absolutely necessary
4. **Test type fixes**: Verify imports and annotations work correctly

### Code Style Standards

#### File Organization:
- **Maximum file size**: 500 lines preferred, 1000 lines absolute maximum
- **Class limits**: Maximum 5 classes per file, 15 methods per class
- **Function complexity**: Keep functions focused and readable

#### Import Standards:
```python
# Standard library imports first
import asyncio
import sys
from pathlib import Path

# Third-party imports
import typer
from antidote import inject, injectable

# Local imports last
from goldentooth_agent.core.context import Context
from goldentooth_agent.core.flow import Flow
```

#### Naming Conventions:
- **Functions/variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `ALL_CAPS`
- **Private attributes**: `_leading_underscore`
- **Type variables**: `T`, `R`, `Input`, `Output` (descriptive when possible)

#### Documentation Standards:
```python
def complex_operation(input_data: InputType) -> OutputType:
    """Brief one-line description.

    More detailed explanation if needed. Explain the 'why' not just the 'what'.

    Args:
        input_data: Description of the input parameter

    Returns:
        Description of what is returned

    Raises:
        SpecificError: When and why this error occurs
    """
```

### Testing Standards

#### Test Organization:
Tests mirror the source structure exactly:

```
tests/
├── core/                       # Tests for src/goldentooth_agent/core/
│   ├── context/                # Context system tests
│   ├── flow/                   # Flow system tests
│   ├── embeddings/             # Embeddings tests
│   ├── rag/                    # RAG system tests
│   └── ...
├── cli/                        # CLI tests
└── integration/                # Cross-module integration tests
```

#### Test Categories:
- **Unit tests**: Fast, isolated, test single functions/classes
- **Integration tests**: Test module interactions
- **End-to-end tests**: Full system workflows
- **Performance tests**: Benchmark critical paths

#### Test Quality Requirements:
- **Coverage**: Minimum 85% overall, 90% for new code
- **Speed**: Unit tests <100ms, integration tests <1s
- **Isolation**: Tests must not depend on external services
- **Reliability**: No flaky tests - fix or remove

### Dependency Injection Patterns

This project uses Antidote for dependency injection. Follow these patterns:

```python
# Service definition
@injectable
class MyService:
    def __init__(self, dependency: SomeDependency = inject.me()) -> None:
        self.dependency = dependency

# Service usage
def create_component() -> Component:
    service = inject(MyService)
    return Component(service)

# In tests - override dependencies
@pytest.fixture
def mock_service():
    return MockService()

def test_with_mock(mock_service):
    with world.test.clone(freeze=False) as test_world:
        test_world[MyService] = mock_service
        # Test with mock
```

### Error Handling Standards

#### Exception Patterns:
```python
# ✅ Create specific exception types
class FlowExecutionError(Exception):
    """Raised when flow execution fails."""

# ✅ Preserve exception chains
try:
    risky_operation()
except SomeError as e:
    raise FlowExecutionError(f"Flow failed: {e}") from e

# ✅ Handle async exceptions properly
async def safe_async_operation():
    try:
        return await async_operation()
    except Exception as e:
        logger.error(f"Async operation failed: {e}")
        raise
```

### Performance Guidelines

#### Critical Performance Areas:
- **Vector search**: <100ms for typical queries
- **Flow execution**: <50ms overhead per flow stage
- **Context operations**: <10ms for get/set operations
- **Test suite**: <60s for full test run

#### Optimization Patterns:
```python
# ✅ Cache expensive operations
@functools.lru_cache(maxsize=128)
def expensive_computation(input_data: str) -> Result:
    ...

# ✅ Use async appropriately
async def io_operation():
    # Use async for I/O, not CPU-bound work
    ...

# ✅ Profile before optimizing
@pytest.mark.benchmark
def test_performance(benchmark):
    result = benchmark(function_to_test, args)
    assert result.stats.mean < 0.1  # 100ms threshold
```

## Module Development Guidelines

### Large Module Management

Several modules exceed 1000 LOC and require special attention:

#### High-Complexity Modules:
- `core/flow/` (5K+ LOC) - Flow composition and execution
- `core/rag/` (3K+ LOC) - RAG system with multiple strategies
- `core/embeddings/` (2K+ LOC) - Vector storage and search
- `core/context/` (2K+ LOC) - Context management system

#### Module Development Rules:
1. **Always read the module README.md first** before making changes
2. **Update README.md** when making significant changes
3. **Run module-specific tests** before and after changes
4. **Check type coverage** for the specific module
5. **Consider splitting** if a file approaches 1000 LOC

### Adding New Functionality

#### Planning Process:
1. **Identify the appropriate module** - don't create new top-level modules unnecessarily
2. **Check existing patterns** - follow established conventions
3. **Write tests first** - TDD approach for new functionality
4. **Document public APIs** - update module README if adding public interfaces
5. **Verify type safety** - ensure complete type annotations

#### Integration Requirements:
- **Dependency injection**: Use Antidote patterns consistently
- **Error handling**: Follow established exception patterns
- **Logging**: Use structured logging where appropriate
- **Testing**: Include unit and integration tests
- **Documentation**: Update relevant READMEs and docstrings

## Memory Management

### Development Workflow
- **Pre-commit**: Always run `poetry run poe test && poetry run poe typecheck`
- **Module changes**: Update README.md files when making significant changes
- **API changes**: Document breaking changes and migration paths
- **Performance**: Run benchmarks for performance-critical changes

### Known Technical Debt
- **Flow module complexity**: Needs refactoring into smaller submodules
- **RAG system optimization**: Some query expansion features have bugs
- **Test organization**: Some integration tests are slow
- **Documentation coverage**: Not all modules have comprehensive README files

### Module Interdependencies
- **Core dependencies**: `context` ← `flow` ← `flow_agent` ← `rag`
- **Utility modules**: `paths`, `util` used by most other modules
- **Data flow**: `document_store` → `embeddings` → `rag` → `cli`
- **DI container**: Antidote manages service lifecycles across all modules

## Entry Points

The package is configured with the entry point:
- `goldentooth-agent` → `goldentooth_agent.cli.main:app`

## Next Steps for Development

### Immediate Priorities:
1. **Module documentation**: Create comprehensive README files for all large modules
2. **Code organization**: Consider splitting large modules into focused packages
3. **Quality automation**: Improve pre-commit hooks and CI quality gates
4. **Performance optimization**: Address known bottlenecks in flow execution

### Long-term Goals:
1. **Architectural documentation**: Document system design decisions
2. **Developer experience**: Improve tooling for working with large codebase
3. **Code consistency**: Establish and enforce style guidelines automatically
4. **Module boundaries**: Clearer separation of concerns between major components
