# 🤖 Goldentooth Agent

An intelligent agent built for my [Pi Bramble](https://github.com/goldentooth/).

## 🎯 Overview

Goldentooth Agent is an **AI agent** that combines functional reactive programming with enterprise-grade features. Built on three core abstractions—**Flow**, **Context**, and **FlowAgent**—it provides type-safe, composable, and highly performant agent development with comprehensive security and tooling.

The system emphasizes **type safety**, **performance**, **security**, and **developer experience** while providing sophisticated features like reactive state management, intelligent caching, rate limiting, and comprehensive observability.

## 🏗️ Architecture

### Core Components

The system is organized into several key modules:

#### **Flow Engine (`flow/`)** ✅ **COMPLETE**
- **`Flow`** - Core reactive stream processing class with 23+ methods
- **Combinators** - 67+ stream processing functions across 8 categories:
  - **Basic** (13 functions): map, filter, compose, collect, etc.
  - **Aggregation** (11 functions): batch, buffer, group_by, scan, window, etc.
  - **Temporal** (5 functions): debounce, throttle, delay, timeout, sample
  - **Control Flow** (11 functions): retry, recover, circuit_breaker, branch, etc.
  - **Observability** (5 functions + 4 classes): log, trace, metrics, inspect, materialize
  - **Advanced** (10 functions): parallel, merge, race, zip, chain, etc.
  - **Sources** (4 functions): range, repeat, empty, start_with
  - **Utils** (2 functions): helper functions for flow creation

#### **Context System (`context/`, `context_flow/`)** ✅ **COMPLETE**
- **`Context`** - Hierarchical context management with computed properties
- **`ContextKey`** - Type-safe key system for context storage
- **`ContextFrame`** - Stack-based context frame management
- **`ContextFlow Integration`** - Seamless integration with Flow Engine
- **Trampoline System** - Advanced flow control and execution patterns
- **Snapshot Management** - Context state preservation and restoration
- **History Tracking** - Change tracking and rollback capabilities

#### **Agent Core (`goldentooth_agent/`)**
- **CLI Interface** - Typer-based command line interface
- **Core System** - Background processing and agent orchestration
- **Development Tools** - Quality assurance and validation

#### **Development Tools (`git_hooks/`)**
- **File Validation** - Size and complexity monitoring
- **Module Analysis** - Dependency and structure validation
- **Quality Checks** - Pre-commit hooks and CI/CD integration

### Key Features

- **🔒 Type Safety**: Full Pyright/MyPy compliance with strict type checking
- **⚡ Performance**: Async-first design with efficient stream processing
- **🧩 Composability**: Functional programming patterns with 67+ combinators
- **🔧 Zero Dependencies**: Standalone flow with minimal external dependencies
- **🧪 Test Coverage**: 96%+ test coverage with 150+ test cases
- **📊 Observability**: Built-in tracing, metrics, and monitoring
- **🛡️ Error Handling**: Comprehensive error recovery and circuit breaker patterns

## 🚀 Installation

### Prerequisites

- Python 3.13+
- Poetry (for dependency management)

### Install with Poetry

```bash
# Clone the repository
git clone https://github.com/goldentooth/goldentooth-agent.git
cd goldentooth-agent

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell

# Verify installation
goldentooth-agent --help
```

### Install with pip

```bash
# Install from PyPI (when available)
pip install goldentooth-agent

# Or install from source
pip install git+https://github.com/goldentooth/goldentooth-agent.git
```

## 🔧 Usage

### Command Line Interface

```bash
# Interactive chat
goldentooth-agent chat

# RAG-powered chat
goldentooth-agent chat --agent rag

# Single message mode
goldentooth-agent send "query" --agent rag

# Show help
goldentooth-agent --help
```

### Flow Engine Programming

```python
from flow import Flow

# Create flows from functions
double_flow = Flow.from_sync_fn(lambda x: x * 2)
filter_even = Flow.identity().filter(lambda x: x % 2 == 0)

# Compose flows with >> operator
pipeline = double_flow >> filter_even

# Process async streams
async def number_stream():
    for i in range(5):
        yield i

result = pipeline(number_stream())
items = [item async for item in result]  # [0, 2, 4, 6, 8]
```

### Advanced Flow Patterns

```python
from flow import Flow
from flow.combinators import (
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
```

### Context System Integration

```python
from context import Context, ContextKey
from context_flow.integration import ContextFlowCombinators
from context_flow.trampoline import TrampolineFlowCombinators

# Create typed context keys
user_key = ContextKey.create("user.name", str, "Current user name")
count_key = ContextKey.create("processing.count", int, "Processing count")

# Create context with hierarchical data
context = Context()
context[user_key] = "Alice"
context[count_key] = 0

# Create context-aware flows
increment_flow = ContextFlowCombinators.update_key(
    count_key, lambda x: x + 1
)
check_exit_flow = TrampolineFlowCombinators.check_should_exit()

# Compose context flows with regular flows
context_pipeline = (
    increment_flow
    >> check_exit_flow
    >> Flow.identity().filter(lambda should_exit: not should_exit)
)

# Use context with flow processing
async def process_with_context():
    async for result in context_pipeline(context_stream()):
        print(f"Processed: {result}")
```

## 🚀 Current Status

**Context System Migration: 98% Complete! 🎉**

Both the Flow Engine and Context System migrations are now **effectively complete** ✅:

### ✅ Flow Engine Migration Complete (13/13 Epics)
- **Epic 1-4**: Core infrastructure (package structure, exceptions, protocols, Flow class)
- **Epic 5**: Utils (2 functions: get_function_name, create_single_item_stream)
- **Epic 6**: Sources (4 functions: range_flow, repeat_flow, empty_flow, start_with_stream)
- **Epic 7**: Basic combinators (13 functions: map, filter, compose, collect, etc.)
- **Epic 9**: Aggregation combinators (11 functions: batch, buffer, group_by, scan, window, etc.)
- **Epic 10**: Temporal combinators (5 functions: debounce, throttle, delay, timeout, sample)
- **Epic 11**: Observability combinators (5 functions + 4 classes: log, trace, metrics, inspect, materialize)
- **Epic 12**: Control flow combinators (11 functions: retry, recover, circuit_breaker, branch, etc.)
- **Epic 13**: Advanced combinators (10 functions: parallel, merge, race, zip, chain, etc.)

### ✅ Context System Migration Complete (159/162 Commits - 98%)

**Phase 1: Core Context Package** ✅ **COMPLETE**
- **Context Core** (`src/context/`) - Full hierarchical context management
- **Symbol System** - Type-safe symbolic navigation
- **Context Keys** - Strongly-typed key system with generic support
- **Context Frames** - Stack-based context frame management
- **Dependency Graph** - Automatic dependency tracking for computed properties
- **History Tracking** - Complete change history and rollback capabilities
- **Snapshot Management** - Context state preservation and restoration

**Phase 2: Context-Flow Integration** ✅ **COMPLETE**
- **Flow Integration** (`src/context_flow/`) - Seamless Flow Engine integration
- **Trampoline System** - Advanced flow control patterns
  - ✅ Utility functions and context keys (Commits #129-133)
  - ✅ Control flow setters (set_should_exit, set_should_break, set_should_skip)
  - ✅ Control flow checkers (check_should_exit, check_should_break, check_should_skip)
  - ✅ Clear flag methods (clear_should_exit, clear_should_break, clear_should_skip)
  - ✅ Trampoline execution patterns (with_exit, with_break, with_skip)
  - ✅ Advanced combinators (exitable_chain, exitable_parallel, conditional_flow)
- **Context Bridge** - Complete protocol-based integration bridge between Context and Flow systems
  - ✅ Bridge initialization and protocol registration
  - ✅ Trampoline key management and context key registration
  - ✅ Dynamic method creation for Flow system integration
  - ✅ Package exports for seamless integration

**Phase 3: Documentation** 🔄 **IN PROGRESS**
- **README Updates** - Documenting the migration completion
- **API Documentation** - To be updated in docs/
- **Migration Guide** - For users upgrading from old system

### 🎯 What's New with Context Migration

The Context system has been completely rewritten from the ground up with:

1. **Modular Package Structure**
   - Separate `context` package with zero Flow dependencies
   - Dedicated `context_flow` integration package
   - Clean separation of concerns and dependencies

2. **Enhanced Type Safety**
   - Full generic type support for ContextKey[T]
   - Type-safe computed properties and transformations
   - Protocol-based integration avoiding circular dependencies

3. **Advanced Features**
   - Nested context operations with dot notation
   - Comprehensive snapshot and rollback capabilities
   - Full history tracking with event sourcing
   - Trampoline execution patterns for advanced flow control

4. **100% Test Coverage**
   - Every function/method has dedicated unit tests
   - Integration tests for cross-system functionality
   - Strict TDD approach throughout migration

### 📊 Migration Stats
- **Flow Engine**: 13/13 Epics Complete (100% ✅)
- **Context System**: 159/162 Commits Complete (98% ✅)
- **67+ flow combinators** with full type safety
- **150+ test cases** with 96%+ test coverage for Flow Engine
- **100% test coverage** for all Context system components
- **100% type safety** - Full Pyright/MyPy compliance
- **Zero dependencies** - Standalone flow package
- **Comprehensive testing** - Every function/method individually tested

### 🧪 Test Coverage
- **50+ test files** covering all functionality
- **TDD approach** - Tests written before implementation
- **Individual function testing** - Each commit includes complete test coverage
- **Integration testing** - Cross-system interaction validation
- **Type checking** enforced with strict mypy configuration
- **Pre-commit hooks** for code quality and consistency

## 📚 Documentation

### Local Documentation

```bash
# Build documentation
poetry run poe docs-build

# Serve documentation locally
poetry run poe docs-serve
# Visit http://localhost:8000

# Auto-rebuild documentation
poetry run poe docs-autobuild
```

### Key Documentation Files

- **[Development Guide](docs/development.rst)** - Comprehensive development practices
- **[API Reference](docs/api/)** - Complete API documentation
- **[Background Information](docs/background/)** - Project background and architecture
- **[Overview](docs/overview.rst)** - System overview and concepts

## 🧪 Development

### Development Commands

```bash
# Run all tests
poetry run poe pytest

# Type checking
poetry run poe mypy
poetry run poe pyright

# Code formatting
poetry run poe format

# Quality checks
poetry run poe precommit-run

# File/module analysis
poetry run poe file-length
poetry run poe module-size
poetry run poe function-length
```

### Quality Standards

- **Type Safety**: 100% type coverage with strict mypy configuration
- **Test Coverage**: Minimum 85% overall, 90% for new code
- **Code Quality**: Pre-commit hooks with black, isort, ruff, and bandit
- **Documentation**: Comprehensive docstrings and RST documentation
- **Performance**: Benchmarked critical paths with performance tests

## 🌀 Wilder Ideas

Goldentooth Agent is a modular, persona-driven intelligent agent architecture designed to orchestrate and evolve distributed compute systems, narrative metaphors, and symbolic reasoning on a self-hosted Raspberry Pi cluster named Goldentooth. The cluster consists of 12 Raspberry Pi 4B nodes (Allyrion through Lipps), running Kubernetes, Nomad, Vault, Consul, Prometheus, real-time observability, ML workflows, and simulation-based jobs.

The Agent operates as an extensible, runtime-modifiable DAG of flows—reactive, composable logic primitives. It integrates numerous tools (e.g. REST, shell, file search), distinct personas, and behavior orchestrators (e.g. trampoline, rule engine, middleware pipelines). Agents can instantiate sub-agents, alter behavior through context-aware masks, and simulate dramatic or symbolic interactions (e.g. the customary assistant persona being "kidnapped" by another scheming persona). Prompt configuration is modular and writable at runtime, enabling recursive, evolving behavior.

The Agent's narrative frame draws from Greek drama, Gormenghast, Edward Gorey, and ASOIAF heraldry, blending operational infrastructure with symbolic intelligence. It is capable of governing the Goldentooth cluster through declarative introspection, gossip CRDTs, Prometheus metrics, and service auto-discovery. The long-term goal is to blur the boundary between orchestration, narrative embodiment, and emergent symbolic computation—building a live actor-model-inspired system that is self-reflective, chaotic, aesthetic, and computationally useful. Subsystems like [Pulse](https://github.com/goldentooth/pulse/) (latency visualization), [Whispers](https://github.com/bitterbridge/whispers/) (CRDT state propagation), and Goldengrove (GPU-accelerated simulation architecture) form testbeds for this vision.

In sum: Goldentooth Agent is a programmable intelligence housed in a self-referential, story-aware cluster, designed to evolve both behavior and symbolic form while orchestrating real distributed infrastructure.

## 📄 License

This project is released into the public domain under the Unlicense - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This project builds upon excellent work from the Python ecosystem:

- **[Anthropic](https://github.com/anthropics/anthropic-sdk-python)**: Claude AI integration
- **[Pydantic](https://github.com/pydantic/pydantic)**: Schema validation and serialization
- **[Antidote](https://github.com/Finistere/antidote)**: Dependency injection framework
- **[Typer](https://github.com/tiangolo/typer)**: CLI framework
- **[Instructor](https://github.com/jxnl/instructor)**: Structured LLM output processing
- **[Cryptography](https://github.com/pyca/cryptography)**: Secure encryption and key management
