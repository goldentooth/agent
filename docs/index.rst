Goldentooth Agent Documentation
===============================

Welcome to the Goldentooth Agent documentation. This is a sophisticated AI agent system currently undergoing migration to a new functional reactive architecture built on the Flow Engine.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   api/modules
   background/index
   development

Current Status
--------------

**Flow Engine Migration: Epic 4 Complete ✅**

The core Flow class has been fully migrated to the new ``flowengine`` package:

* ✅ **Complete Flow class (23/23 methods)** - All instance methods and static factory methods
* ✅ **100% test coverage** - 150+ test cases covering all functionality  
* ✅ **Strict type checking** - Full Pyright compliance with generic type preservation
* ✅ **Functional programming patterns** - Identity, composition, and pure value flows

Architecture Overview
---------------------

The system is organized into several core modules:

**New Architecture (Current Development)**

* **Flow Engine** (``flowengine``) - Functional reactive stream processing [**MIGRATED ✅**]

  * ``flowengine.flow`` - Core Flow class with 23 methods
  * ``flowengine.exceptions`` - Flow-specific error types
  * ``flowengine.protocols`` - Type protocols for the flow system

* **Development Tools** (``git_hooks``) - Quality assurance and validation

**Legacy Architecture (Being Migrated)**

* **CLI Interface** (``goldentooth_agent.cli``) - Typer-based command line interface
* **Core System** (``old/goldentooth_agent/core``) - 25K+ LOC of original functionality
* **Legacy Flow Engine** (``old/goldentooth_agent/flow_engine``) - Original implementation

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
   poetry run poe test                      # Run all tests
   poetry run poe typecheck                 # Type check with mypy

Architecture
------------

The system is organized into several core modules:

* **CLI Interface** (``goldentooth_agent.cli``) - Typer-based command line interface
* **Core System** (``goldentooth_agent.core``) - 25K+ LOC of core functionality
* **Flow Engine** (``goldentooth_agent.flow_engine``) - Functional flow composition
* **Context Management** (``goldentooth_agent.core.context``) - State and history
* **RAG System** (``goldentooth_agent.core.rag``) - Retrieval-Augmented Generation
* **Embeddings** (``goldentooth_agent.core.embeddings``) - Vector search and storage
* **Document Store** (``goldentooth_agent.core.document_store``) - Document management
* **LLM Integration** (``goldentooth_agent.core.llm``) - Claude and other LLM clients

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
