Goldentooth Agent Documentation
==============================

Welcome to the Goldentooth Agent documentation. This is a sophisticated AI agent system with RAG capabilities, flow-based architecture, and comprehensive tooling.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   api/modules
   background/index
   development

Overview
--------

Goldentooth Agent is a mature, production-ready codebase with 25K+ lines of code implementing:

* **Flow-based functional architecture** with composition
* **Context management** with snapshots and history tracking
* **RAG system** with OpenAI embeddings and hybrid search
* **Document store** with GitHub, notes, and goldentooth data
* **CLI** with interactive and single-message modes
* **Vector store** with sqlite-vec for semantic search
* **Comprehensive dependency injection** with Antidote
* **Background processing** and event systems

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
