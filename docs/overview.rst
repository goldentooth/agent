System Overview
===============

Architecture Components
-----------------------

Core System Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

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

Key Features
~~~~~~~~~~~~

**✅ Fully Implemented:**

* Flow-based functional architecture with composition
* Context management with snapshots and history tracking
* RAG system with OpenAI embeddings and hybrid search
* Document store with GitHub, notes, and goldentooth data
* CLI with interactive and single-message modes
* Vector store with sqlite-vec for semantic search
* Comprehensive dependency injection with Antidote
* Background processing and event systems

**🔄 In Progress:**

* Module documentation and API surface documentation
* Code quality standardization across large modules
* Performance optimization for complex flow compositions

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

* **Core dependencies**: ``context`` ← ``flow`` ← ``flow_agent`` ← ``rag``
* **Utility modules**: ``paths``, ``util`` used by most other modules
* **Data flow**: ``document_store`` → ``embeddings`` → ``rag`` → ``cli``
* **DI container**: Antidote manages service lifecycles across all modules
