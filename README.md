# 🤖 Goldentooth Agent

An intelligent agent built for my [Pi Bramble](https://github.com/goldentooth/).

## 🎯 Overview

Goldentooth Agent is an **AI agent** that combines functional reactive programming with enterprise-grade features. Built on three core abstractions—**Flow**, **Context**, and **FlowAgent**—it provides type-safe, composable, and highly performant agent development with comprehensive security and tooling.

The system emphasizes **type safety**, **performance**, **security**, and **developer experience** while providing sophisticated features like reactive state management, intelligent caching, rate limiting, and comprehensive observability.

## 🏗️ Architecture

### Core Components

The system is organized into several key modules:

#### **Flow Engine (`flowengine/`)**
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
- **🔧 Zero Dependencies**: Standalone flowengine with minimal external dependencies
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
from flowengine import Flow

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
```

## 🚀 Current Status

**Flow Engine Migration: Epic 13 Complete ✅**

The Flow Engine migration is **complete** with comprehensive type safety and test coverage:

### ✅ Completed Epics (13/13)
- **Epic 1-4**: Core infrastructure (package structure, exceptions, protocols, Flow class)
- **Epic 5**: Utils (2 functions: get_function_name, create_single_item_stream)
- **Epic 6**: Sources (4 functions: range_flow, repeat_flow, empty_flow, start_with_stream)
- **Epic 7**: Basic combinators (13 functions: map, filter, compose, collect, etc.)
- **Epic 9**: Aggregation combinators (11 functions: batch, buffer, group_by, scan, window, etc.)
- **Epic 10**: Temporal combinators (5 functions: debounce, throttle, delay, timeout, sample)
- **Epic 11**: Observability combinators (5 functions + 4 classes: log, trace, metrics, inspect, materialize)
- **Epic 12**: Control flow combinators (11 functions: retry, recover, circuit_breaker, branch, etc.)
- **Epic 13**: Advanced combinators (10 functions: parallel, merge, race, zip, chain, etc.)

### 📊 Migration Stats
- **13/13 Epics Complete** (100% migration complete)
- **67+ combinators** implemented with full type safety
- **150+ test cases** with 96%+ test coverage
- **100% type safety** - Full Pyright/MyPy compliance
- **Zero dependencies** - Standalone flowengine package
- **33 source files** with comprehensive functionality

### 🧪 Test Coverage
- **50 test files** covering all functionality
- **Comprehensive test suite** with unit, integration, and performance tests
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
