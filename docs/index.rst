Goldentooth Agent Documentation
===============================

Welcome to the Goldentooth Agent documentation. This is a sophisticated AI agent system currently undergoing migration to a new functional reactive architecture built on the Flow Engine.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   quickstart
   migration-status
   flowengine-guide
   api/modules
   background/index
   development
   dead-code-detection

Current Status
--------------

**Flow Engine Migration: Epic 16 In Progress 🔄**

The Flow Engine migration has reached 40% completion with comprehensive test coverage and type safety:

Migration Progress
~~~~~~~~~~~~~~~~~~

==================== ======= ============ ===================================
Phase                Epics   Status       Components
==================== ======= ============ ===================================
Core Infrastructure  1-4     ✅ Complete  Flow class, exceptions, protocols
Combinator Utilities 5-8     ✅ Complete  Utils, sources, basic combinators
Core Combinators     9-14    ✅ Complete  All combinator categories
Core Observability   15-18   🔄 Progress  Performance ✅, Analysis ✅
Observability Int.   19-22   ⏳ Pending   Integration infrastructure
Registry System      23-26   ⏳ Pending   Flow registry and discovery
Advanced Features    27-35   ⏳ Pending   Extensions and integration
Package Completion   36-40   ⏳ Pending   Final packaging
==================== ======= ============ ===================================

Key Achievements
~~~~~~~~~~~~~~~~

* **16/40 Epics Complete** - 40% overall progress
* **3,200+ lines migrated** - With 96%+ test coverage
* **84 functions/classes** - Fully typed and tested
* **Zero dependencies** - Standalone Flow Engine package
* **100% type safety** - Strict mypy and Pyright compliance

Architecture Overview
---------------------

The system is built on a functional reactive architecture with three main components:

**Flow Engine** (``flowengine``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The core reactive stream processing engine:

.. code-block:: text

   flowengine/
   ├── flow.py              # Core Flow class (23 methods)
   ├── exceptions.py        # Flow-specific exceptions
   ├── protocols.py         # Type protocols and interfaces
   ├── combinators/         # Stream processing functions
   │   ├── utils.py        # Helper utilities
   │   ├── sources.py      # Stream creation
   │   ├── basic.py        # Core operations
   │   ├── aggregation.py  # Batching and windowing
   │   ├── temporal.py     # Time-based operations
   │   ├── observability.py # Logging and monitoring
   │   ├── control_flow.py # Conditionals and error handling
   │   └── advanced.py     # Parallel and complex patterns
   └── observability/       # Monitoring and analysis tools
       ├── performance.py   # Performance monitoring
       └── analysis.py      # Flow graph analysis

**Main Application** (``goldentooth_agent``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The agent application built on top of the Flow Engine:

* **CLI Interface** - Command-line tools and utilities
* **Core System** - Background loops and agent logic
* **Integration Layer** - Connects Flow Engine with application logic

**Development Tools** (``git_hooks``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Quality assurance and development utilities:

* **File validation** - Enforces size limits
* **Module validation** - Ensures module organization
* **Function validation** - Maintains function complexity limits

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/yourusername/goldentooth-agent.git
   cd goldentooth-agent

   # Install with Poetry
   poetry install

   # Run tests
   poetry run pytest

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from flowengine import Flow
   from flowengine.combinators import map_stream, filter_stream

   # Create a flow from an iterable
   flow = Flow.from_iterable([1, 2, 3, 4, 5])

   # Transform the stream
   result = await flow.pipe(
       map_stream(lambda x: x * 2),
       filter_stream(lambda x: x > 5)
   ).to_list()

   print(result)  # [6, 8, 10]

Development
-----------

The project follows strict development standards:

* **Type Safety**: 100% type coverage with mypy --strict
* **Test Coverage**: Minimum 85% overall, 90% for new code
* **Code Quality**: Enforced through pre-commit hooks
* **Documentation**: Comprehensive docstrings and guides

See the :doc:`development` guide for detailed information.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
