Development Guide
=================

This guide covers development practices, testing strategies, and contribution guidelines for the Goldentooth Agent project.

Development Commands
--------------------

.. code-block:: bash

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

   # Type checking
   poetry run poe typecheck                 # Type check source code with mypy
   poetry run poe typecheck-all             # Type check entire project including tests

   # Quality checks (run before committing)
   poetry run poe test && poetry run poe typecheck

   # Build package
   poetry build

Code Quality Standards
----------------------

Type Safety Requirements
~~~~~~~~~~~~~~~~~~~~~~~~

**CRITICAL**: This project maintains strict type safety. All code must pass both ``mypy --strict`` and Pylance checks.

Type Annotation Standards:

.. code-block:: python

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

Type Checking Workflow:

1. **Before any commit**: Run ``poetry run poe typecheck``
2. **Fix all type errors**: Zero tolerance for type errors
3. **Prefer specific types**: Avoid ``Any`` except when absolutely necessary
4. **Test type fixes**: Verify imports and annotations work correctly

Testing Standards
~~~~~~~~~~~~~~~~~

Test Organization:
Tests mirror the source structure exactly:

.. code-block:: text

   tests/
   ├── core/                       # Tests for src/goldentooth_agent/core/
   │   ├── context/                # Context system tests
   │   ├── flow/                   # Flow system tests
   │   ├── embeddings/             # Embeddings tests
   │   ├── rag/                    # RAG system tests
   │   └── ...
   ├── cli/                        # CLI tests
   └── integration/                # Cross-module integration tests

Test Categories:

* **Unit tests**: Fast, isolated, test single functions/classes
* **Integration tests**: Test module interactions
* **End-to-end tests**: Full system workflows
* **Performance tests**: Benchmark critical paths

Test Quality Requirements:

* **Coverage**: Minimum 85% overall, 90% for new code
* **Speed**: Unit tests <100ms, integration tests <1s
* **Isolation**: Tests must not depend on external services
* **Reliability**: No flaky tests - fix or remove

Code Style Standards
~~~~~~~~~~~~~~~~~~~~

File Organization:

* **Maximum file size**: 500 lines preferred, 1000 lines absolute maximum
* **Class limits**: Maximum 5 classes per file, 15 methods per class
* **Function complexity**: Keep functions focused and readable

Import Standards:

.. code-block:: python

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

Naming Conventions:

* **Functions/variables**: ``snake_case``
* **Classes**: ``PascalCase``
* **Constants**: ``ALL_CAPS``
* **Private attributes**: ``_leading_underscore``
* **Type variables**: ``T``, ``R``, ``Input``, ``Output`` (descriptive when possible)

Documentation Standards:

.. code-block:: python

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

Dependency Injection Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This project uses Antidote for dependency injection. Follow these patterns:

.. code-block:: python

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

Error Handling Standards
~~~~~~~~~~~~~~~~~~~~~~~~

Exception Patterns:

.. code-block:: python

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

Performance Guidelines
~~~~~~~~~~~~~~~~~~~~~~

Critical Performance Areas:

* **Vector search**: <100ms for typical queries
* **Flow execution**: <50ms overhead per flow stage
* **Context operations**: <10ms for get/set operations
* **Test suite**: <60s for full test run

Optimization Patterns:

.. code-block:: python

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

Module Development Guidelines
-----------------------------

Large Module Management
~~~~~~~~~~~~~~~~~~~~~~~

Several modules exceed 1000 LOC and require special attention:

High-Complexity Modules:

* ``core/flow/`` (5K+ LOC) - Flow composition and execution
* ``core/rag/`` (3K+ LOC) - RAG system with multiple strategies
* ``core/embeddings/`` (2K+ LOC) - Vector storage and search
* ``core/context/`` (2K+ LOC) - Context management system

Module Development Rules:

1. **Always read the module README.md first** before making changes
2. **Update README.md** when making significant changes
3. **Run module-specific tests** before and after changes
4. **Check type coverage** for the specific module
5. **Consider splitting** if a file approaches 1000 LOC

Adding New Functionality
~~~~~~~~~~~~~~~~~~~~~~~~

Planning Process:

1. **Identify the appropriate module** - don't create new top-level modules unnecessarily
2. **Check existing patterns** - follow established conventions
3. **Write tests first** - TDD approach for new functionality
4. **Document public APIs** - update module README if adding public interfaces
5. **Verify type safety** - ensure complete type annotations

Integration Requirements:

* **Dependency injection**: Use Antidote patterns consistently
* **Error handling**: Follow established exception patterns
* **Logging**: Use structured logging where appropriate
* **Testing**: Include unit and integration tests
* **Documentation**: Update relevant READMEs and docstrings

Contributing
------------

Before contributing:

1. **Read the guidelines**: Review all files in the ``guidelines/`` directory
2. **Run quality checks**: ``poetry run poe qa``
3. **Update documentation**: Ensure README files are current
4. **Test thoroughly**: All tests must pass with good coverage
5. **Type check**: Zero type errors allowed

Pre-commit hooks will automatically check code quality, type safety, and documentation completeness.
