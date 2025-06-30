# 🤖 Goldentooth Agent

An intelligent agent built for my [Pi Bramble](https://github.com/goldentooth/).

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Type Checked](https://img.shields.io/badge/type--checked-mypy-blue)](http://mypy-lang.org/)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-834%20passing-green)](tests/)
[![Security](https://img.shields.io/badge/security-enterprise--grade-green)](src/goldentooth_agent/core/security/)
[![Documentation](https://img.shields.io/badge/docs-sphinx-blue)](https://[your-username].github.io/goldentooth-agent/)

## 🎯 Overview

Goldentooth Agent is a **production-ready AI agent framework** that combines functional reactive programming with enterprise-grade features. Built on three core abstractions—**Flow**, **Context**, and **FlowAgent**—it provides type-safe, composable, and highly performant agent development with comprehensive security and tooling.

The system emphasizes **type safety**, **performance**, **security**, and **developer experience** while providing sophisticated features like reactive state management, intelligent caching, rate limiting, and comprehensive observability.

## 🌀 Wilder Ideas

Goldentooth Agent is a modular, persona-driven intelligent agent architecture designed to orchestrate and evolve distributed compute systems, narrative metaphors, and symbolic reasoning on a self-hosted Raspberry Pi cluster named Goldentooth. The cluster consists of 12 Raspberry Pi 4B nodes (Allyrion through Lipps), running Kubernetes, Nomad, Vault, Consul, Prometheus, real-time observability, ML workflows, and simulation-based jobs.

The Agent operates as an extensible, runtime-modifiable DAG of flows—reactive, composable logic primitives. It integrates numerous tools (e.g. REST, shell, file search), distinct personas, and behavior orchestrators (e.g. trampoline, rule engine, middleware pipelines). Agents can instantiate sub-agents, alter behavior through context-aware masks, and simulate dramatic or symbolic interactions (e.g. the customary assistant persona being “kidnapped” by another scheming persona). Prompt configuration is modular and writable at runtime, enabling recursive, evolving behavior.

The Agent’s narrative frame draws from Greek drama, Gormenghast, Edward Gorey, and ASOIAF heraldry, blending operational infrastructure with symbolic intelligence. It is capable of governing the Goldentooth cluster through declarative introspection, gossip CRDTs, Prometheus metrics, and service auto-discovery. The long-term goal is to blur the boundary between orchestration, narrative embodiment, and emergent symbolic computation—building a live actor-model-inspired system that is self-reflective, chaotic, aesthetic, and computationally useful. Subsystems like [Pulse](https://github.com/goldentooth/pulse/) (latency visualization), [Whispers](https://github.com/bitterbridge/whispers/) (CRDT state propagation), and Goldengrove (GPU-accelerated simulation architecture) form testbeds for this vision.

In sum: Goldentooth Agent is a programmable intelligence housed in a self-referential, story-aware cluster, designed to evolve both behavior and symbolic form while orchestrating real distributed infrastructure.

## ✨ Key Features

### 🔄 **Flow-Based Stream Processing**
- **Composable Pipelines**: Natural function composition with operators (`>>`, `map`, `filter`)
- **Type-Safe Transformations**: Full generic type support with strict mypy compliance
- **Async-First Architecture**: Built on `AsyncIterator` for efficient streaming
- **Performance Optimized**: Connection pooling, caching, and parallel execution

```python
# Composable flow pipelines
chat_flow = (
    input_validator
    >> context_enricher
    >> llm_processor
    >> response_formatter
)
```

### 🧠 **Reactive Context System**
- **Layered State Management**: Multi-frame context with scoped isolation
- **Computed Properties**: Automatic dependency tracking and invalidation
- **Event Integration**: Built-in reactive patterns with EventFlow
- **Time-Travel Debugging**: Snapshots and history with rollback capabilities

```python
# Reactive context with computed properties
context.add_computed_property(
    "user_greeting",
    lambda ctx: f"Hello, {ctx['user_name']}!",
    dependencies=["user_name"]
)
```

### 🛡️ **Enterprise Security**
- **Input Validation**: XSS, SQL injection, and path traversal protection
- **Secret Management**: Encrypted storage with automatic rotation
- **Rate Limiting**: DoS protection with multiple algorithms
- **Audit Logging**: Comprehensive compliance and security tracking

```python
# Secure input validation
@validate_flow_input
async def secure_handler(input_data: SecureInput) -> SecureOutput:
    # All inputs automatically validated and sanitized
    return await process_safely(input_data)
```

### ⚡ **Performance Optimization**
- **Intelligent Caching**: Adaptive strategies with cache hierarchies
- **Connection Pooling**: Optimized HTTP client management
- **Parallel Execution**: Concurrent processing with backpressure control
- **Memory Optimization**: Streaming patterns for large datasets

```python
# High-performance parallel processing
async with executor.parallel_context():
    results = executor.parallel_flow_map(inputs, processor, max_concurrent=10)
```

### 🔧 **Production Tooling**
- **Comprehensive CLI**: Interactive chat, tool management, and debugging
- **LLM Integration**: Claude AI with streaming and structured output
- **Tool Library**: 12+ production-ready tools (web, file, AI, system)
- **Instructor Support**: Type-safe structured LLM responses

## 🏗️ Architecture

### Core Components

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Flow     │────│   Context   │────│ FlowAgent   │
│  Processor  │    │   Manager   │    │Orchestrator │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Security  │    │ Performance │    │    Tools    │
│& Validation │    │& Caching    │    │ & Registry  │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Production Features

- **Type Safety**: 100% mypy strict compliance across 74 source files
- **Test Coverage**: 834+ tests including security, performance, and integration
- **Security Hardened**: Enterprise-grade input validation and secret management
- **High Performance**: Optimized for throughput with intelligent caching
- **Observability**: Comprehensive logging, metrics, and debugging tools

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/goldentooth-agent.git
cd goldentooth-agent

# Install with Poetry
poetry install

# Or install with pip
pip install -e .
```

### Basic Usage

```python
import asyncio
from goldentooth_agent.core.flow_agent import FlowAgent, FlowIOSchema
from goldentooth_agent.core.flow import Flow
from pydantic import Field

# Define input/output schemas
class ChatInput(FlowIOSchema):
    message: str = Field(..., description="User message")
    context_data: dict[str, Any] = Field(default_factory=dict)

class ChatOutput(FlowIOSchema):
    response: str = Field(..., description="Agent response")
    metadata: dict[str, Any] = Field(default_factory=dict)

# Create processing flows
async def chat_system_flow(stream):
    """System initialization and setup"""
    async for context in stream:
        # Add system-level processing
        yield context

async def chat_processing_flow(stream):
    """Main business logic"""
    async for context in stream:
        input_data = ChatInput.from_context(context)

        # Process the message (integrate with LLM, tools, etc.)
        response = f"I received: {input_data.message}"

        output_data = ChatOutput(
            response=response,
            metadata={"processed_at": time.time()}
        )

        yield output_data.to_context(context)

# Create and run the agent
agent = FlowAgent(
    name="chat_agent",
    input_schema=ChatInput,
    output_schema=ChatOutput,
    system_flow=Flow(chat_system_flow),
    processing_flow=Flow(chat_processing_flow)
)

# Process messages
async def main():
    input_data = ChatInput(message="Hello, Goldentooth!")
    result = await agent.process(input_data)
    print(result.response)

asyncio.run(main())
```

### CLI Usage

```bash
# Interactive chat with Claude AI
goldentooth-agent chat

# List available tools
goldentooth-agent tools list

# Run a specific tool
goldentooth-agent tools run calculator --expression "2 + 2"

# Get help
goldentooth-agent --help
```

### Tool Integration

```python
from goldentooth_agent.core.tools import HttpRequestTool, TextAnalysisTool

# Use built-in tools
http_tool = HttpRequestTool()
analysis_tool = TextAnalysisTool()

# Tools automatically integrate with security and performance features
async for result in http_tool.as_flow()(input_stream):
    analyzed = await analysis_tool.process(result)
```

## 📚 Examples

The `examples/` directory contains comprehensive demonstrations:

- **`flow_agent_demo.py`**: Basic agent creation and execution
- **`flow_agent_calculator.py`**: Mathematical tool integration
- **`flow_agent_instructor_demo.py`**: Structured LLM output processing
- **`performance_optimization_demo.py`**: High-performance parallel processing
- **`security_demo.py`**: Security validation and protection features

## 🛠️ Development

### Prerequisites
- Python 3.13+
- Poetry for dependency management
- Git for version control

### Setup

```bash
# Install dependencies
poetry install

# Install pre-commit hooks
poetry run poe precommit-install

# Run all tests
poetry run poe test

# Run security tests
poetry run pytest tests/core/security/ -v

# Run performance tests
python examples/performance_optimization_demo.py

# Type checking
poetry run poe typecheck

# Run all quality checks
poetry run poe qa
```

### Code Quality Standards

This project maintains enterprise-grade code quality:

- **Type Safety**: 100% mypy strict compliance
- **Security**: Comprehensive input validation and secret management
- **Performance**: Optimized for high-throughput production workloads
- **Test Coverage**: 834+ tests including unit, integration, and security
- **Code Style**: Black formatting with ruff linting

### Documentation

Comprehensive API documentation is generated using Sphinx:

```bash
# Build documentation
poetry run poe docs-build          # Build HTML documentation
poetry run poe docs-clean          # Clean build (rebuild everything)
poetry run poe docs-serve          # Serve docs at http://localhost:8000
poetry run poe docs-autobuild      # Live reload for development
```

The documentation includes:
- **API Reference**: Auto-generated from docstrings with full type information
- **Module Backgrounds**: In-depth explanations of design decisions and theoretical foundations
- **Developer Guide**: Code quality standards, testing practices, and contribution guidelines
- **Architecture Overview**: System design and module interdependencies

Documentation is automatically built and deployed to GitHub Pages on every push to the main branch.
View the live documentation at: https://[your-username].github.io/goldentooth-agent/

### Available Commands

```bash
# Test suites
poetry run poe test                 # All tests
poetry run poe test-core           # Core module tests
poetry run poe test-sanity         # Basic sanity tests
poetry run poe test-cov            # Tests with coverage

# Type checking
poetry run poe typecheck           # Source code only
poetry run poe typecheck-all       # All code including tests

# Documentation
poetry run poe docs-build          # Build Sphinx documentation
poetry run poe docs-serve          # Serve documentation locally

# Code quality
poetry run poe lint                # Run ruff linting
poetry run poe format              # Format code with black
poetry run poe qa                  # All quality checks
```

## 🔒 Security Features

### Input Validation & Sanitization
- **XSS Protection**: HTML escaping and script injection prevention
- **SQL Injection**: Pattern detection and query sanitization
- **Path Traversal**: File system access protection
- **Data Validation**: Schema-based input validation with Pydantic

### Secret Management
- **Encryption**: AES-256 with Fernet symmetric encryption
- **Storage Options**: Environment variables, encrypted files, or memory
- **Rotation**: Automatic secret rotation with configurable policies
- **Audit Trail**: Comprehensive logging for compliance

### Rate Limiting & DoS Protection
- **Multiple Algorithms**: Token bucket, sliding window, fixed window
- **Flexible Keys**: Per-IP, per-user, or custom rate limiting
- **High Performance**: Memory and Redis backend support
- **HTTP Compliance**: Standard rate limit headers

## ⚡ Performance Features

### Intelligent Caching
- **Adaptive Strategies**: LRU, LFU, TTL, and adaptive algorithms
- **Cache Hierarchies**: Separate caches for flows, tools, and LLM operations
- **Performance Metrics**: Hit rates, latency tracking, and optimization
- **Memory Management**: Automatic cleanup and size limiting

### Parallel Processing
- **Concurrent Execution**: Configurable worker pools with backpressure
- **Batch Processing**: Optimized batch operations for high throughput
- **Streaming**: Memory-efficient processing of large datasets
- **Connection Pooling**: Optimized HTTP client management

### Benchmarks
- **HTTP Throughput**: 5 concurrent requests in 1.18s with pooling
- **Parallel Processing**: 412 ops/sec with full optimization stack
- **Cache Performance**: 10,902x speedup on cached operations
- **Memory Efficiency**: Constant memory usage processing 1000+ items

## 🧪 Testing

### Test Organization

```
tests/
├── core/
│   ├── security/          # Security validation tests
│   ├── flow_agent/        # Agent orchestration tests
│   ├── context/           # Context system tests
│   ├── flow/              # Flow processing tests
│   └── tools/             # Tool library tests
├── cli/                   # CLI interface tests
└── examples/              # Example integration tests
```

### Running Tests

```bash
# All tests (834+ tests)
poetry run poe test

# Specific test suites
poetry run pytest tests/core/security/ -v      # Security tests
poetry run pytest tests/core/flow_agent/ -v    # Agent tests
poetry run pytest tests/core/context/ -v       # Context tests

# Performance tests
python examples/performance_optimization_demo.py

# Integration tests
poetry run pytest tests/ -k integration -v
```

## 📈 Production Readiness

### Current Status: **Production Ready** 🚀

✅ **Core Architecture**: Flow, Context, and FlowAgent fully implemented
✅ **CLI Implementation**: Complete interactive interface with tool management
✅ **LLM Integration**: Claude AI client with streaming and structured output
✅ **Security Systems**: Enterprise-grade validation, secrets, and rate limiting
✅ **Performance Optimization**: Caching, pooling, and parallel processing
✅ **Tool Library**: 12+ production-ready tools for common operations
✅ **Type Safety**: 100% mypy compliance across 74 source files
✅ **Comprehensive Testing**: 834+ tests including security and performance

### Enterprise Features

- **🔒 Security Hardened**: Input validation, secret management, audit logging
- **⚡ High Performance**: Connection pooling, intelligent caching, parallel execution
- **🛡️ DoS Protection**: Rate limiting with multiple algorithms and backends
- **📊 Observability**: Comprehensive metrics, logging, and debugging tools
- **🎯 Type Safety**: Strict mypy compliance with comprehensive error handling
- **🧪 Battle Tested**: Extensive test suite covering security, performance, and edge cases

### Deployment Ready

Goldentooth Agent is ready for production deployment with:

- **Docker Support**: Containerized deployment configurations
- **Environment Configuration**: Flexible configuration management
- **Secret Management**: Secure credential handling for production
- **Monitoring Integration**: Metrics and logging for observability
- **Performance Optimization**: Production-tuned defaults and scaling patterns

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This project builds upon excellent work from the Python ecosystem:

- **[Anthropic](https://github.com/anthropics/anthropic-sdk-python)**: Claude AI integration
- **[Pydantic](https://github.com/pydantic/pydantic)**: Schema validation and serialization
- **[Antidote](https://github.com/Finistere/antidote)**: Dependency injection framework
- **[Typer](https://github.com/tiangolo/typer)**: CLI framework
- **[Instructor](https://github.com/jxnl/instructor)**: Structured LLM output processing
- **[Cryptography](https://github.com/pyca/cryptography)**: Secure encryption and key management

---

**🚀 Production Ready**: Goldentooth Agent provides a complete, enterprise-grade platform for building secure, high-performance AI agents with comprehensive tooling and developer experience.

For questions, issues, or collaboration opportunities, please open an issue or start a discussion on GitHub.
