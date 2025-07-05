# 🤖 Goldentooth Agent

An intelligent agent built for my [Pi Bramble](https://github.com/goldentooth/), featuring functional reactive programming with enterprise-grade features.

## 🎯 Overview

Goldentooth Agent is an **AI agent** that combines functional reactive programming with enterprise-grade features. Built on three core abstractions—**Flow**, **Context**, and **FlowAgent**—it provides type-safe, composable, and highly performant agent development with comprehensive security and tooling.

The system emphasizes **type safety**, **performance**, **security**, and **developer experience** while providing sophisticated features like reactive state management, intelligent caching, rate limiting, and comprehensive observability.

## 🚀 Current Status

### Flow Engine Migration Progress

**Epic 16 In Progress 🔄** (Phase 3A: Core Observability)

The Flow Engine migration is progressing steadily with comprehensive type safety and test coverage:

| Phase | Epics | Status | Progress |
|-------|-------|--------|----------|
| Phase 1A: Core Infrastructure | 1-4 | ✅ Complete | Flow class, exceptions, protocols |
| Phase 1B: Combinator Utilities | 5-8 | ✅ Complete | Utils, sources, basic combinators |
| Phase 2: Core Combinators | 9-14 | ✅ Complete | Aggregation, temporal, observability, control flow, advanced |
| Phase 3A: Core Observability | 15-18 | 🔄 In Progress | Performance ✅, Analysis ✅, Debugging/Health pending |
| Phase 3B: Observability Integration | 19-22 | ⏳ Pending | Integration and test infrastructure |
| Phase 4: Registry System | 23-26 | ⏳ Pending | Flow registry and discovery |
| Phase 5: Advanced Features | 27-35 | ⏳ Pending | Extensions, trampoline, integration |
| Phase 6: Package Completion | 36-40 | ⏳ Pending | Final packaging and documentation |

### Migration Statistics
- **16/40 Epics Complete** (40% overall progress)
- **~3,200 lines migrated** with 96%+ test coverage
- **100% type safety** - Full Pyright/MyPy compliance
- **Zero dependencies** - Standalone package architecture
- **84 total functions/classes** migrated across all combinators

### Completed Components

#### Core Infrastructure (Epics 1-4)
- ✅ Package structure and configuration
- ✅ Exception hierarchy (5 exception types)
- ✅ Type protocols (3 protocol definitions)
- ✅ Flow class (23 methods with full generic support)

#### Combinators (Epics 5-14)
- ✅ **Utils** (2): `get_function_name`, `create_single_item_stream`
- ✅ **Sources** (4): `range_flow`, `repeat_flow`, `empty_flow`, `start_with_stream`
- ✅ **Basic** (13): `map_stream`, `filter_stream`, `flat_map_stream`, `compose`, etc.
- ✅ **Aggregation** (11): `batch_stream`, `buffer_stream`, `scan_stream`, `window_stream`, etc.
- ✅ **Temporal** (6): `delay_stream`, `debounce_stream`, `throttle_stream`, `timeout_stream`, etc.
- ✅ **Observability** (5 + 4): `log_stream`, `trace_stream`, `metrics_stream`, plus notification classes
- ✅ **Control Flow** (11): `if_then_stream`, `retry_stream`, `circuit_breaker_stream`, etc.
- ✅ **Advanced** (10): `race_stream`, `parallel_stream`, `merge_stream`, `zip_stream`, etc.

#### Observability System (Epics 15-16)
- ✅ **Performance Monitoring** (Epic 15): FlowMetrics, PerformanceMonitor, benchmarking
- ✅ **Analysis Tools** (Epic 16): FlowNode, FlowEdge, FlowGraph, FlowAnalyzer

## 🏗️ Architecture

### Current Structure

```
src/
├── flowengine/             # New Flow Engine package (40% migrated)
│   ├── __init__.py        # Package exports
│   ├── flow.py            # Core Flow class (23 methods)
│   ├── exceptions.py      # Flow-specific errors 
│   ├── protocols.py       # Type protocols
│   ├── combinators/       # Stream processing functions
│   │   ├── utils.py       # Utility functions
│   │   ├── sources.py     # Stream creation
│   │   ├── basic.py       # Core operations
│   │   ├── aggregation.py # Batching and windowing
│   │   ├── temporal.py    # Time-based operations
│   │   ├── observability.py # Logging and tracing
│   │   ├── control_flow.py  # Conditionals and error handling
│   │   └── advanced.py    # Parallel and complex patterns
│   ├── observability/     # Monitoring and analysis
│   │   ├── performance.py # Performance monitoring
│   │   └── analysis.py    # Flow graph analysis
│   └── py.typed           # Type marker
├── git_hooks/             # Development tooling
│   ├── cli.py            # Quality assurance CLI
│   ├── core.py           # Hook utilities
│   ├── file_validator.py # File size validation
│   └── module_validator.py # Module size validation
└── goldentooth_agent/     # Main application
    ├── cli/              # Command-line interface
    └── core/             # Core functionality
        └── background_loop/ # Async event processing
```

### Legacy System (Reference)

The original implementation in `old/` contains 25,000+ lines of code that serves as the reference for the ongoing migration.

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/goldentooth-agent.git
cd goldentooth-agent

# Install dependencies using Poetry
poetry install

# Verify installation
poetry run pytest
```

## 📖 Usage

### Command Line Interface

```bash
# Run the agent CLI
goldentooth-agent --help

# Note: Full CLI functionality is being migrated
```

### Flow Engine Examples

```python
from flowengine import Flow
from flowengine.combinators import map_stream, filter_stream, compose

# Create a simple flow
flow = Flow.from_iterable([1, 2, 3, 4, 5])

# Transform data
result = await flow.pipe(
    map_stream(lambda x: x * 2),
    filter_stream(lambda x: x > 5)
).to_list()

print(result)  # [6, 8, 10]
```

## 🧪 Development

### Quality Standards

- **Type Safety**: 100% type coverage with mypy --strict
- **Test Coverage**: Minimum 85% overall, 90% for new code
- **Performance**: <50ms flow overhead, <100ms vector search
- **Code Quality**: Pre-commit hooks for formatting and linting

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov

# Type checking
poetry run mypy src/

# Linting
poetry run ruff check src/
```

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
