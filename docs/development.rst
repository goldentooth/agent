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
   poetry run poe pytest                   # Run all tests
   poetry run poe pytest --cov             # Run tests with coverage
   poetry run poe pytest tests/flow  # Run Flow Engine tests
   poetry run poe pytest tests/integration # Run integration tests

   # Type checking
   poetry run poe mypy                     # Type check source code with mypy
   poetry run poe pyright                  # Type check with pyright

   # Quality checks (run before committing)
   poetry run poe format                   # Format code with black, isort, ruff
   poetry run poe precommit-run           # Run all pre-commit hooks
   poetry run poe pytest && poetry run poe mypy  # Full quality check

   # Build package
   poetry build

Project Structure
-----------------

Current Architecture
~~~~~~~~~~~~~~~~~~~

The project has completed its migration to a modern, type-safe architecture:

.. code-block:: text

   src/
   ├── flow/                    # Flow Engine (COMPLETE ✅)
   │   ├── __init__.py               # Package exports
   │   ├── flow.py                   # Core Flow class (23+ methods)
   │   ├── exceptions.py             # Flow-specific errors
   │   ├── protocols.py              # Type protocols
   │   ├── observability/            # Performance monitoring
   │   └── combinators/              # 67+ stream processing functions
   │       ├── basic.py             # Basic combinators (13 functions)
   │       ├── aggregation.py       # Aggregation combinators (11 functions)
   │       ├── temporal.py          # Temporal combinators (5 functions)
   │       ├── control_flow.py      # Control flow combinators (11 functions)
   │       ├── observability.py     # Observability combinators (5 functions + 4 classes)
   │       ├── advanced.py          # Advanced combinators (10 functions)
   │       ├── sources.py           # Source combinators (4 functions)
   │       └── utils.py             # Utility functions (2 functions)
   ├── goldentooth_agent/            # Agent core
   │   ├── cli/                     # CLI interface
   │   └── core/                    # Core agent functionality
   └── git_hooks/                    # Development tooling
       ├── cli.py                   # Quality assurance CLI
       ├── core.py                  # Hook utilities
       └── config.py                # Configuration management

Test Structure
~~~~~~~~~~~~~~

Tests mirror the source structure exactly:

.. code-block:: text

   tests/
   ├── flow/                   # Flow Engine tests
   │   ├── combinators/             # Combinator tests
   │   │   ├── test_*.py           # Individual combinator tests
   │   ├── observability/           # Observability tests
   │   ├── test_flow_*.py          # Core Flow class tests
   │   └── core/                    # Core functionality tests
   ├── goldentooth_agent/           # Agent tests
   │   └── core/                    # Core agent tests
   ├── git_hooks/                   # Development tooling tests
   └── integration/                 # Cross-module integration tests

Code Quality Standards
----------------------

Type Safety Requirements
~~~~~~~~~~~~~~~~~~~~~~~~

**CRITICAL**: This project maintains strict type safety. All code must pass both ``mypy --strict`` and Pyright checks.

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

1. **Before any commit**: Run ``poetry run poe mypy`` and ``poetry run poe pyright``
2. **Fix all type errors**: Zero tolerance for type errors
3. **Prefer specific types**: Avoid ``Any`` except when absolutely necessary
4. **Test type fixes**: Verify imports and annotations work correctly

Testing Standards
~~~~~~~~~~~~~~~~~

Test Organization:
Tests mirror the source structure exactly for easy navigation and maintenance.

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

Flow Engine Testing:

.. code-block:: python

   # Test individual combinators
   @pytest.mark.asyncio
   async def test_map_stream():
       flow = Flow.from_iterable([1, 2, 3]).transform(map_stream(lambda x: x * 2))
       result = [item async for item in flow]
       assert result == [2, 4, 6]

   # Test complete pipelines
   @pytest.mark.asyncio
   async def test_complete_pipeline():
       pipeline = (
           Flow.from_iterable(range(10))
           .transform(map_stream(lambda x: x * 2))
           .transform(filter_stream(lambda x: x > 5))
           .transform(take_stream(3))
       )
       result = [item async for item in pipeline]
       assert result == [6, 8, 10]

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
   from flow import Flow
   from flow.combinators import map_stream, filter_stream

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

Flow Engine Development
----------------------

Architecture Guidelines
~~~~~~~~~~~~~~~~~~~~~~~

The Flow Engine follows functional reactive programming principles:

1. **Pure Functions**: Combinators should be pure functions without side effects
2. **Composability**: Every combinator should be composable with others
3. **Type Safety**: Full generic type preservation through transformations
4. **Async First**: Built on async iterators for efficient stream processing

Adding New Combinators:

.. code-block:: python

   # Template for new combinators
   from typing import TypeVar, Callable, AsyncIterator
   from flow.protocols import StreamTransform

   T = TypeVar("T")
   R = TypeVar("R")

   def new_combinator(param: SomeType) -> StreamTransform[T, R]:
       """Brief description of the combinator.

       Args:
           param: Description of the parameter

       Returns:
           Stream transform function
       """
       async def transform(stream: AsyncIterator[T]) -> AsyncIterator[R]:
           async for item in stream:
               # Process item
               yield processed_item

       return transform

Testing New Combinators:

.. code-block:: python

   @pytest.mark.asyncio
   async def test_new_combinator():
       # Test basic functionality
       flow = Flow.from_iterable([1, 2, 3]).transform(new_combinator(param))
       result = [item async for item in flow]
       assert result == expected_result

   @pytest.mark.asyncio
   async def test_new_combinator_edge_cases():
       # Test edge cases
       empty_flow = Flow.from_iterable([]).transform(new_combinator(param))
       result = [item async for item in empty_flow]
       assert result == []

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

* **Flow execution**: <50ms overhead per flow stage
* **Stream processing**: Memory-efficient async iteration
* **Type checking**: Full static analysis without runtime overhead
* **Test suite**: <60s for full test run

Optimization Patterns:

.. code-block:: python

   # ✅ Use async generators for memory efficiency
   async def memory_efficient_combinator(stream: AsyncIterator[T]) -> AsyncIterator[R]:
       async for item in stream:
           yield process_item(item)  # Process one item at a time

   # ✅ Leverage async for I/O-bound operations
   async def io_bound_combinator(stream: AsyncIterator[T]) -> AsyncIterator[R]:
       async for item in stream:
           result = await async_io_operation(item)
           yield result

   # ✅ Use benchmarks for performance testing
   @pytest.mark.benchmark
   async def test_performance():
       start_time = time.time()
       # ... run performance test
       end_time = time.time()
       assert end_time - start_time < threshold

Development Workflow
-------------------

Feature Development
~~~~~~~~~~~~~~~~~~

1. **Create feature branch**: ``git checkout -b feature/new-combinator``
2. **Write tests first**: TDD approach for new functionality
3. **Implement functionality**: Following type safety and style guidelines
4. **Run quality checks**: ``poetry run poe format && poetry run poe pytest && poetry run poe mypy``
5. **Update documentation**: Add to combinators documentation
6. **Submit PR**: With comprehensive description and test coverage

Quality Assurance
~~~~~~~~~~~~~~~~~

Pre-commit Checks:

.. code-block:: bash

   # Automatic pre-commit hooks
   poetry run poe precommit-install    # Install hooks
   poetry run poe precommit-run        # Run all hooks manually

   # Manual quality checks
   poetry run poe format               # Format code
   poetry run poe pytest               # Run tests
   poetry run poe mypy                 # Type check
   poetry run poe pyright              # Additional type checking

File and Module Validation:

.. code-block:: bash

   # Check file sizes and complexity
   poetry run poe file-length          # Check file sizes
   poetry run poe module-size          # Check module complexity
   poetry run poe function-length      # Check function complexity

   # Run with warnings for monitoring
   poetry run poe file-length-warnings
   poetry run poe module-size-warnings
   poetry run poe function-length-warnings

Documentation Development
~~~~~~~~~~~~~~~~~~~~~~~~~

Building Documentation:

.. code-block:: bash

   # Build documentation
   poetry run poe docs-build

   # Serve documentation locally
   poetry run poe docs-serve
   # Visit http://localhost:8000

   # Auto-rebuild documentation during development
   poetry run poe docs-autobuild

Documentation Standards:

* **Comprehensive docstrings**: All public functions and classes
* **Usage examples**: Practical examples for complex functionality
* **Type annotations**: Complete type information in documentation
* **Performance notes**: Document performance characteristics

Contributing
------------

Before contributing:

1. **Read the guidelines**: Review all development standards
2. **Run quality checks**: ``poetry run poe format && poetry run poe pytest && poetry run poe mypy``
3. **Update documentation**: Ensure documentation is current
4. **Test thoroughly**: All tests must pass with good coverage
5. **Type check**: Zero type errors allowed

Pull Request Process:

1. **Fork the repository**
2. **Create feature branch**: ``git checkout -b feature/description``
3. **Follow development workflow**: TDD, quality checks, documentation
4. **Submit PR**: With clear description and test coverage
5. **Address feedback**: Respond to code review comments

Code Review Criteria:

* **Type safety**: 100% type coverage
* **Test coverage**: Minimum 85% overall, 90% for new code
* **Documentation**: Complete docstrings and usage examples
* **Performance**: No performance regressions
* **Style**: Consistent with project standards

Debugging and Troubleshooting
-----------------------------

Common Issues
~~~~~~~~~~~~

**Type Errors:**

.. code-block:: bash

   # Run type checking
   poetry run poe mypy src/
   poetry run poe pyright src/

   # Fix common type issues
   # 1. Add missing type annotations
   # 2. Use Optional for nullable parameters
   # 3. Add explicit type variables for generics

**Test Failures:**

.. code-block:: bash

   # Run specific test file
   poetry run poe pytest tests/flow/test_flow.py

   # Run with verbose output
   poetry run poe pytest -v

   # Run with coverage
   poetry run poe pytest --cov=src/flow

**Performance Issues:**

.. code-block:: bash

   # Profile Flow Engine performance
   poetry run poe pytest tests/flow/test_performance.py

   # Check for memory leaks
   poetry run poe pytest --memray

Flow Engine Debugging:

.. code-block:: python

   # Use observability combinators for debugging
   from flow.combinators import log_stream, trace_stream, inspect_stream

   debug_pipeline = (
       Flow.identity()
       .transform(log_stream("Input"))
       .transform(inspect_stream(lambda x: print(f"Processing: {x}")))
       .transform(trace_stream("debug"))
       .transform(log_stream("Output"))
   )

Migration Notes
---------------

The Flow Engine migration is **complete**. All functionality has been migrated to the new architecture:

**✅ Completed Migration:**
* Core Flow class with 23+ methods
* 67+ combinators across 8 categories
* Comprehensive test suite with 150+ test cases
* Full type safety with Pyright/MyPy compliance
* Performance optimization and monitoring

**Current Status:**
* All 13 migration epics are complete
* 100% type safety coverage
* 96%+ test coverage
* Zero external dependencies for core functionality
* Production-ready architecture

The project is now ready for feature development and enhancement based on the solid Flow Engine foundation.
