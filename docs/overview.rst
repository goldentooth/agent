System Overview
===============

The Goldentooth Agent is an intelligent agent system built on functional reactive programming principles, designed to orchestrate distributed systems with sophisticated AI capabilities.

Migration Status
----------------

**Flow Engine Migration: Epic 16 In Progress 🔄** (Phase 3A: Core Observability)

The Goldentooth Agent is undergoing a comprehensive migration from a legacy monolithic architecture to a new functional reactive system built on the Flow Engine. This migration emphasizes type safety, performance, and maintainability.

Progress Summary
~~~~~~~~~~~~~~~~

==================== ======= ============ ======================= ===================
Phase                Epics   Status       Lines Migrated          Coverage
==================== ======= ============ ======================= ===================
Core Infrastructure  1-4     ✅ Complete  ~500 lines              98%
Combinator Utilities 5-8     ✅ Complete  ~350 lines              97%
Core Combinators     9-14    ✅ Complete  ~1,800 lines            96%
Core Observability   15-18   🔄 Progress  ~550 lines (partial)    97%
Observability Int.   19-22   ⏳ Pending   -                       -
Registry System      23-26   ⏳ Pending   -                       -
Advanced Features    27-35   ⏳ Pending   -                       -
Package Completion   36-40   ⏳ Pending   -                       -
==================== ======= ============ ======================= ===================

**Total Progress**: 16/40 epics (40%), ~3,200 lines migrated, 96%+ average coverage

Current Architecture
~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   src/
   ├── flowengine/             # New Flow Engine package (40% migrated)
   │   ├── __init__.py         # Public API exports (84 functions/classes)
   │   ├── flow.py             # Core Flow class (23 methods)
   │   ├── exceptions.py       # Exception hierarchy (5 types)
   │   ├── protocols.py        # Type protocols (3 definitions)
   │   ├── combinators/        # Stream processing functions
   │   │   ├── __init__.py     # Combinator exports
   │   │   ├── utils.py        # Helper utilities (2 functions)
   │   │   ├── sources.py      # Stream creation (4 functions)
   │   │   ├── basic.py        # Core operations (13 functions)
   │   │   ├── aggregation.py  # Batching/windowing (11 functions)
   │   │   ├── temporal.py     # Time operations (6 functions)
   │   │   ├── observability.py # Logging/tracing (5 functions + 4 classes)
   │   │   ├── control_flow.py # Flow control (11 functions)
   │   │   └── advanced.py     # Complex patterns (10 functions)
   │   ├── observability/      # Monitoring and analysis
   │   │   ├── performance.py  # Performance monitoring (✅)
   │   │   └── analysis.py     # Flow graph analysis (✅)
   │   └── py.typed            # Type marker for py.typed
   │
   ├── git_hooks/              # Development tooling
   │   ├── cli.py              # Quality assurance CLI
   │   ├── core.py             # Hook utilities
   │   ├── file_validator.py   # File size validation (<1000 lines)
   │   ├── module_validator.py # Module size validation (<5000 lines)
   │   └── function_validator.py # Function complexity limits
   │
   └── goldentooth_agent/      # Main application (minimal during migration)
       ├── cli/                # Command-line interface
       │   └── main.py         # Typer CLI app
       └── core/               # Core functionality
           └── background_loop/ # Async event processing

Legacy Architecture (Reference)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   old/goldentooth_agent/      # Original 25K+ LOC implementation
   ├── cli/                    # Complete CLI with multiple commands
   ├── core/                   # Core system modules
   │   ├── context/            # Context management system
   │   ├── flow_agent/         # Agent framework
   │   ├── embeddings/         # Vector embeddings & search
   │   ├── rag/                # Retrieval-Augmented Generation
   │   ├── llm/                # LLM clients (Claude, OpenAI)
   │   ├── document_store/     # YAML document management
   │   └── background_loop/    # Async background processing
   └── flow_engine/            # Original Flow implementation (being migrated)

Flow Engine Features
--------------------

Completed Components
~~~~~~~~~~~~~~~~~~~~

**Core Infrastructure** (Epics 1-4)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Flow Class**: Complete implementation with 23 methods including:

  * Static factories: ``from_value_fn``, ``from_sync_fn``, ``from_event_fn``, ``from_iterable``, ``from_emitter``
  * Transformations: ``map``, ``filter``, ``flat_map``
  * Terminal operations: ``to_list``, ``for_each``, ``reduce``, ``first``, ``last``
  * Composition: ``pipe``, ``__rshift__`` operator support

* **Exception Hierarchy**: 5 specialized exception types for different error scenarios
* **Type Protocols**: 3 protocol definitions for extensibility and type safety

**Combinators** (Epics 5-14)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Flow Engine provides 66 combinator functions organized into 8 categories:

1. **Utilities** (2): Basic helper functions for flow creation
2. **Sources** (4): Functions to create flows from various inputs
3. **Basic** (13): Core stream operations like map, filter, take, skip
4. **Aggregation** (11): Batching, buffering, windowing, scanning
5. **Temporal** (6): Time-based operations like debounce, throttle, delay
6. **Observability** (9): Logging, tracing, metrics, and notifications
7. **Control Flow** (11): Conditionals, retry logic, error handling
8. **Advanced** (10): Parallel processing, merging, racing, zipping

**Observability System** (Epics 15-16)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Performance Monitoring**: FlowMetrics, PerformanceMonitor, benchmarking utilities
* **Flow Analysis**: FlowNode, FlowEdge, FlowGraph for visualization and optimization

Development Standards
---------------------

Type Safety Requirements
~~~~~~~~~~~~~~~~~~~~~~~~

This project maintains **strict type safety** with zero tolerance for type errors:

.. code-block:: python

   # ✅ Required: Complete function annotations
   async def process_stream(
       flow: Flow[Input, Output],
       handler: Callable[[Output], Awaitable[None]]
   ) -> None:
       """Process a flow with proper typing."""
       async for item in flow:
           await handler(item)

   # ✅ Required: Generic type preservation
   def transform_flow[T, R](
       flow: Flow[Any, T],
       fn: Callable[[T], R]
   ) -> Flow[Any, R]:
       """Transform preserving type relationships."""
       return flow.map(fn)

Testing Standards
~~~~~~~~~~~~~~~~~

* **Coverage Requirements**: 
  
  * Minimum 85% overall
  * 90% for new code
  * 100% for public APIs

* **Test Organization**:
  
  * Unit tests for individual functions
  * Integration tests for combinator chains
  * Property-based tests for invariants
  * Performance benchmarks for critical paths

* **Test Speed**:
  
  * Unit tests: <100ms per test
  * Integration tests: <1s per test
  * Full test suite: <60s total

Performance Guidelines
~~~~~~~~~~~~~~~~~~~~~~

Critical performance targets:

* **Flow overhead**: <50ms per stage in a flow pipeline
* **Memory usage**: Constant memory for infinite streams
* **Async operations**: Non-blocking throughout
* **Error propagation**: Zero-cost abstractions for error handling

Code Organization
~~~~~~~~~~~~~~~~~

* **File size limits**: Maximum 1,000 lines per file (enforced by git hooks)
* **Module size limits**: Maximum 5,000 lines per module
* **Function complexity**: Maximum 10 lines per function (with rare exceptions)
* **Class complexity**: Maximum 15 methods per class

Module Interdependencies
~~~~~~~~~~~~~~~~~~~~~~~~

The new architecture enforces clean dependencies:

* **flowengine**: Zero external dependencies, pure Python stdlib
* **goldentooth_agent**: Depends on flowengine but not vice versa
* **git_hooks**: Development-only, no runtime dependencies

Future Architecture
-------------------

The completed migration will enable:

1. **Standalone Flow Engine**: Usable as an independent package
2. **Context Integration**: Optional context system for stateful flows
3. **Plugin Architecture**: Extensible through protocols and interfaces
4. **Performance Optimization**: Specialized implementations for common patterns
5. **Distributed Execution**: Flow graphs that span multiple nodes

Next Steps
~~~~~~~~~~

**Immediate** (Epics 17-18):

* Complete observability system with debugging and health monitoring
* Add comprehensive flow debugging utilities

**Short-term** (Epics 19-26):

* Observability integration and test infrastructure
* Flow registry for dynamic flow discovery

**Medium-term** (Epics 27-35):

* Advanced features like extensions and trampoline
* Integration preparation with lazy imports

**Long-term** (Epics 36-40):

* Package completion and documentation
* Full integration with goldentooth_agent
* Public package release
