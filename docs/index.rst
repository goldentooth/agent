Goldentooth Agent Documentation
===============================

Welcome to the Goldentooth Agent documentation. This is a sophisticated AI agent system built on a comprehensive functional reactive architecture powered by the Flow Engine.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   flowengine
   api/modules
   background/index
   development

Current Status
--------------

**Flow Engine Migration: Epic 13 Complete ✅**

The Flow Engine migration is **complete** with comprehensive type safety and test coverage:

**✅ All 13 Epics Complete (100% migration complete)**

* **Epic 1-4**: Core infrastructure (package structure, exceptions, protocols, Flow class)
* **Epic 5**: Utils (2 functions: get_function_name, create_single_item_stream)
* **Epic 6**: Sources (4 functions: range_flow, repeat_flow, empty_flow, start_with_stream)
* **Epic 7**: Basic combinators (13 functions: map, filter, compose, collect, etc.)
* **Epic 9**: Aggregation combinators (11 functions: batch, buffer, group_by, scan, window, etc.)
* **Epic 10**: Temporal combinators (5 functions: debounce, throttle, delay, timeout, sample)
* **Epic 11**: Observability combinators (5 functions + 4 classes: log, trace, metrics, inspect, materialize)
* **Epic 12**: Control flow combinators (11 functions: retry, recover, circuit_breaker, branch, etc.)
* **Epic 13**: Advanced combinators (10 functions: parallel, merge, race, zip, chain, etc.)

**Migration Statistics:**

* ✅ **67+ combinators** implemented with full type safety
* ✅ **150+ test cases** with 96%+ test coverage  
* ✅ **100% type safety** - Full Pyright/MyPy compliance
* ✅ **Zero dependencies** - Standalone flowengine package
* ✅ **33 source files** with comprehensive functionality
* ✅ **50 test files** covering all functionality

Architecture Overview
---------------------

The system is organized into several core modules:

**Current Architecture (Migration Complete)**

* **Flow Engine** (``flowengine``) - Functional reactive stream processing [**COMPLETE ✅**]

  * ``flowengine.flow`` - Core Flow class with 23+ methods
  * ``flowengine.combinators`` - 67+ stream processing functions across 8 categories
  * ``flowengine.observability`` - Performance monitoring and analysis
  * ``flowengine.exceptions`` - Flow-specific error types
  * ``flowengine.protocols`` - Type protocols for the flow system

* **Agent Core** (``goldentooth_agent``) - Main agent functionality

  * ``goldentooth_agent.cli`` - Typer-based command line interface
  * ``goldentooth_agent.core`` - Background processing and agent orchestration

* **Development Tools** (``git_hooks``) - Quality assurance and validation

  * File validation and size monitoring
  * Module analysis and structure validation
  * Pre-commit hooks and CI/CD integration

Flow Engine Features
-------------------

The Flow Engine provides comprehensive functional reactive programming:

**Core Capabilities:**

* **Type-safe composition**: Full generic type preservation through transformations
* **Functional patterns**: Identity, pure values, and monadic operations
* **Static factory methods**: Multiple ways to create flows from various sources
* **Async streaming**: Built on async iterators for efficient stream processing
* **Comprehensive testing**: 150+ test cases with full coverage

**Combinator Categories:**

* **Basic (13 functions)**: map, filter, compose, collect, guard, flatten, etc.
* **Aggregation (11 functions)**: batch, buffer, group_by, scan, window, distinct, etc.
* **Temporal (5 functions)**: debounce, throttle, delay, timeout, sample
* **Control Flow (11 functions)**: retry, recover, circuit_breaker, branch, switch, etc.
* **Observability (5 functions + 4 classes)**: log, trace, metrics, inspect, materialize
* **Advanced (10 functions)**: parallel, merge, race, zip, chain, combine_latest, etc.
* **Sources (4 functions)**: range, repeat, empty, start_with
* **Utils (2 functions)**: Helper functions for flow creation and introspection

Quick Start
-----------

.. code-block:: bash

   # Install dependencies
   poetry install

   # Run the agent CLI
   goldentooth-agent --help
   goldentooth-agent chat                      # Interactive chat
   goldentooth-agent chat --agent rag          # RAG-powered chat
   goldentooth-agent send "query" --agent rag  # Single message mode

   # Testing and Quality
   poetry run poe pytest                   # Run all tests
   poetry run poe mypy                     # Type check with mypy
   poetry run poe pyright                  # Type check with pyright

Flow Engine Example
------------------

.. code-block:: python

   from flowengine import Flow
   from flowengine.combinators import (
       batch_stream, debounce_stream, parallel_stream, 
       retry_stream, circuit_breaker_stream
   )

   # Create a robust data processing pipeline
   pipeline = (
       Flow.identity()
       .transform(debounce_stream(delay=0.1))      # Debounce inputs
       .transform(batch_stream(size=10))           # Batch processing
       .transform(parallel_stream(workers=4))       # Parallel processing
       .transform(retry_stream(max_retries=3))     # Retry on failure
       .transform(circuit_breaker_stream(threshold=5))  # Circuit breaker
   )

   # Process data with error handling and observability
   async def process_data():
       async for batch in pipeline(data_source()):
           print(f"Processed batch: {batch}")

Development
-----------

.. code-block:: bash

   # Run quality checks
   poetry run poe format                   # Format code
   poetry run poe precommit-run           # Run all pre-commit hooks
   poetry run poe file-length             # Check file sizes
   poetry run poe module-size             # Check module complexity

   # Build documentation
   poetry run poe docs-build              # Build docs
   poetry run poe docs-serve              # Serve docs locally
   poetry run poe docs-autobuild          # Auto-rebuild docs

Quality Standards
----------------

The project maintains high quality standards:

* **Type Safety**: 100% type coverage with strict mypy configuration
* **Test Coverage**: Minimum 85% overall, 90% for new code
* **Code Quality**: Pre-commit hooks with black, isort, ruff, and bandit
* **Documentation**: Comprehensive docstrings and RST documentation
* **Performance**: Benchmarked critical paths with performance tests

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
