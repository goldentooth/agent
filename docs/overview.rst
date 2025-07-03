System Overview
===============

Migration Status
----------------

**Flow Engine Migration: Epic 4 Complete ✅**

The Goldentooth Agent is undergoing a comprehensive migration from a legacy monolithic architecture to a new functional reactive system built on the Flow Engine.

Current Architecture
~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   src/
   ├── flowengine/             # New Flow Engine (MIGRATED ✅)
   │   ├── __init__.py        # Package exports
   │   ├── flow.py            # Core Flow class (23 methods)
   │   ├── exceptions.py      # Flow-specific errors 
   │   ├── protocols.py       # Type protocols
   │   └── py.typed           # Type marker
   ├── git_hooks/             # Development tooling
   │   ├── cli.py            # Quality assurance CLI
   │   ├── core.py           # Hook utilities
   │   ├── file_validator.py # File size validation
   │   └── module_validator.py # Module size validation
   └── goldentooth_agent/     # Legacy CLI (minimal)
       └── cli/              # Basic CLI interface

Legacy Architecture (In old/ directory)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   old/goldentooth_agent/      # Original 25K+ LOC implementation
   ├── cli/                   # CLI interface (Typer-based)  
   ├── core/                  # Core system modules
   │   ├── context/           # Context management system
   │   ├── flow_agent/        # Agent framework
   │   ├── embeddings/        # Vector embeddings & search
   │   ├── rag/               # Retrieval-Augmented Generation
   │   ├── llm/               # LLM clients (Claude, etc.)
   │   ├── document_store/    # YAML document management
   │   └── background_loop/   # Async background processing
   └── flow_engine/           # Original Flow implementation

Flow Engine Features
~~~~~~~~~~~~~~~~~~~~

**✅ Migrated and Production Ready:**

* **Complete Flow class** - All 23 methods with comprehensive test coverage
* **Type-safe composition** - Full generic type preservation through transformations
* **Functional patterns** - Identity, pure values, and monadic operations
* **Static factory methods** - from_value_fn, from_sync_fn, from_event_fn, from_iterable, from_emitter
* **Stream processing** - Async iterator-based reactive streams
* **Error handling** - Comprehensive exception propagation and edge case coverage
* **Development quality** - 150+ test cases, strict type checking, file size validation

**🔄 Next Steps (Epic 5):**

* Combinator utilities migration
* Advanced flow composition patterns
* Performance optimization helpers
* Integration with legacy context system

Development Standards
---------------------

Type Safety Requirements
~~~~~~~~~~~~~~~~~~~~~~~

This project maintains **strict type safety**. All code must pass both ``mypy --strict`` and Pylance checks.

Required annotations:

.. code-block:: python

   # ✅ Required: Complete function annotations
   def process_data(items: list[str], count: int = 10) -> dict[str, Any]:
       """Process data with proper typing."""
       ...

   # ✅ Required: Optional for nullable parameters
   def create_flow(fn: Optional[Callable[[Input], Output]] = None) -> Flow:
       ...

Testing Standards
~~~~~~~~~~~~~~~~~

* **Coverage**: Minimum 85% overall, 90% for new code
* **Speed**: Unit tests <100ms, integration tests <1s
* **TDD**: Strict Test-Driven Development practices
* **API Focus**: Test behavior through public APIs, not implementation details

Performance Guidelines
~~~~~~~~~~~~~~~~~~~~~~

Critical performance areas:

* **Vector search**: <100ms for typical queries
* **Flow execution**: <50ms overhead per flow stage
* **Context operations**: <10ms for get/set operations
* **Test suite**: <60s for full test run

Module Interdependencies
~~~~~~~~~~~~~~~~~~~~~~~~

* **Core dependencies**: ``context`` ← ``flow_agent`` ← ``rag``
* **Utility modules**: ``paths``, ``util`` used by most other modules
* **Data flow**: ``document_store`` → ``embeddings`` → ``rag`` → ``cli``
* **DI container**: Antidote manages service lifecycles across all modules
