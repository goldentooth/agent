# 🤖 Goldentooth Agent

A modern, functional reactive agent framework built with strict type safety and composable stream processing patterns.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Type Checked](https://img.shields.io/badge/type--checked-mypy-blue)](http://mypy-lang.org/)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-471%20passing-green)](tests/)

> **⚠️ Experimental Status**: This project is currently in active development and proof-of-concept phase. While the architectural foundations are solid, core functionality is still being implemented. See our [roadmap](#roadmap) for development progress.

## 🎯 Overview

Goldentooth Agent explores a **functional reactive programming approach** to AI agent development, combining three core abstractions:

- **Flow**: Composable async stream processors with rich combinators
- **Context**: Reactive, hierarchical state management with time-travel debugging
- **FlowAgent**: Schema-driven agent orchestration with tool interoperability

The system emphasizes **type safety**, **composability**, and **functional programming principles** while providing sophisticated features like event-driven reactivity, dependency injection, and comprehensive observability.

## ✨ Features & Design Innovations

### 🔄 **Flow-Based Stream Processing**
- **Composable Pipelines**: Natural function composition with operators (`>>`, `map`, `filter`)
- **Type-Safe Transformations**: Full generic type support with strict mypy compliance
- **Async-First Architecture**: Built on `AsyncIterator` for efficient streaming
- **Rich Combinators**: Functional programming patterns for complex data flows

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

### 🎭 **Schema-Driven Agent Design**
- **Pydantic Integration**: Runtime validation with static type checking
- **Tool Interoperability**: Unified interface for tools and agents
- **Context Integration**: Automatic schema-to-context conversion
- **Instructor Support**: Structured LLM output processing

```python
class ChatInput(FlowIOSchema):
    message: str = Field(..., description="User message")
    context_data: dict[str, Any] = Field(default_factory=dict)

# Automatic context conversion
updated_context = input_data.to_context(context)
```

### 🔧 **Enterprise-Grade Engineering**
- **Dependency Injection**: Clean architecture with Antidote framework
- **Comprehensive Testing**: 471+ tests with property-based testing
- **Type Safety**: 100% mypy strict compliance across 52 source files
- **Quality Tooling**: Pre-commit hooks with black, ruff, mypy, and bandit

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
│ Combinators │    │   Events    │    │   Tools     │
│  & Operators│    │ & Reactivity│    │ & Registry  │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Design Principles

- **Functional Composition**: Everything composes through the Flow abstraction
- **Immutable Transformations**: State changes return new objects
- **Type-Safe Contracts**: Schemas define clear interfaces between components
- **Event-Driven Reactivity**: Changes propagate through reactive event systems
- **Separation of Concerns**: Clear boundaries between processing, state, and orchestration

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
from goldentooth_agent.core.flow import Flow
from goldentooth_agent.core.context import Context
from goldentooth_agent.core.flow_agent import FlowAgent, AgentInput, AgentOutput

# Create a simple echo agent
async def echo_system_flow(stream):
    """System flow for basic setup"""
    async for context in stream:
        # Add any system-level processing
        yield context

async def echo_processing_flow(stream):
    """Processing flow for business logic"""
    async for context in stream:
        # Extract input and create response
        input_data = AgentInput.from_context(context)

        # Simple echo logic
        output_data = AgentOutput(
            response=f"Echo: {input_data.message}",
            metadata={"processed_at": "now"}
        )

        # Add output to context
        yield output_data.to_context(context)

# Create and run the agent
agent = FlowAgent(
    name="echo_agent",
    input_schema=AgentInput,
    output_schema=AgentOutput,
    system_flow=Flow(echo_system_flow),
    processing_flow=Flow(echo_processing_flow)
)

# Process a message
async def main():
    input_data = AgentInput(message="Hello, World!")
    result = await agent.process(input_data)
    print(result.response)  # "Echo: Hello, World!"

asyncio.run(main())
```

### CLI Usage (Experimental)

```bash
# Start interactive chat (when implemented)
goldentooth-agent chat

# List available tools (when implemented)
goldentooth-agent tools list

# Get help
goldentooth-agent --help
```

## 📚 Examples

The `examples/` directory contains demonstrations of key concepts:

- **`flow_agent_demo.py`**: Basic agent creation and execution
- **`flow_agent_calculator.py`**: Mathematical tool integration
- **`flow_agent_instructor_demo.py`**: Structured LLM output processing
- **`context_eventflow_demo.py`**: Reactive context patterns
- **`trampoline_demo.py`**: Advanced flow execution patterns

## 🔄 Comparison to Prior Implementation

This version represents a **complete architectural reimagining** compared to the previous implementation:

### Previous Architecture (`old/` directory)
- **Thunk-based execution**: Complex functional abstractions
- **YAML-heavy configuration**: Extensive external configuration files
- **Multiple abstraction layers**: Personas, roles, scenarios, players
- **Complete implementation**: Full-featured but complex system

### Current Architecture (Experimental)
- **Flow-based processing**: Cleaner, more intuitive abstractions
- **Schema-driven design**: Type-safe contracts with runtime validation
- **Simplified concepts**: Three core abstractions (Flow, Context, FlowAgent)
- **Modern Python**: Leverages latest type system and async patterns

### Key Improvements
- ✅ **Reduced Complexity**: Simpler mental model with fewer concepts
- ✅ **Better Type Safety**: Strict mypy compliance vs. partial typing
- ✅ **Modern Patterns**: Async-first design with functional composition
- ✅ **Enhanced Testing**: Comprehensive test suite with property-based testing
- ⚠️ **Trade-off**: Less functionality currently implemented (work in progress)

## 🎯 Design Goals

### Primary Objectives
1. **Type Safety**: Leverage Python's type system for reliable, maintainable code
2. **Composability**: Enable complex behaviors through simple component composition
3. **Functional Purity**: Minimize side effects and embrace immutable transformations
4. **Developer Experience**: Provide intuitive APIs with excellent tooling support
5. **Production Readiness**: Build enterprise-grade reliability and observability

### Technical Philosophy
- **Behavior over Implementation**: Test externally observable behavior
- **Composition over Inheritance**: Favor functional composition patterns
- **Explicit over Implicit**: Clear, typed interfaces reduce cognitive load
- **Async by Default**: Built for concurrent, streaming workloads
- **Schema-First**: Contracts define system boundaries and interactions

## 📋 Roadmap

This project is actively evolving from proof-of-concept to production-ready platform. See our detailed [ROADMAP.md](ROADMAP.md) for comprehensive development plans.

### Current Status: **Proof of Concept** 🧪
- ✅ **Core Architecture**: Flow, Context, and FlowAgent foundations
- ✅ **Type Safety**: Strict mypy compliance with comprehensive annotations
- ✅ **Testing Framework**: Comprehensive test suite with 471+ passing tests
- ⚠️ **CLI Implementation**: Framework exists but commands are stubs
- ⚠️ **LLM Integration**: Dependencies ready but clients not implemented

### Phase 1: Foundation (Weeks 1-4)
- 🎯 **Working CLI**: Interactive chat and tool management
- 🎯 **LLM Clients**: Claude integration with streaming support
- 🎯 **Observability**: Logging, metrics, and debugging tools
- 🎯 **Error Handling**: Robust retry and recovery mechanisms

### Phase 2: Production Readiness (Weeks 5-8)
- 📖 **Documentation**: Comprehensive guides and API documentation
- ⚡ **Performance**: Benchmarking and optimization
- 🔒 **Security**: Input validation and credential management
- 🧪 **Integration Testing**: End-to-end testing with real APIs

### Long-term Vision
- 🌐 **Tool Ecosystem**: Rich library of production-ready tools
- 📈 **Scalability**: High-throughput concurrent processing
- 🔌 **Plugin Architecture**: Community-driven extensibility
- 🏢 **Enterprise Features**: Deployment, monitoring, and compliance

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

# Run tests
poetry run poe test

# Type checking
poetry run poe typecheck

# Run all quality checks
poetry run poe qa
```

### Code Quality

This project maintains high code quality standards:

- **Type Safety**: 100% mypy strict compliance
- **Test Coverage**: Comprehensive test suite with behavior-driven testing
- **Code Style**: Black formatting with isort import sorting
- **Linting**: Ruff for code quality and potential issues
- **Security**: Bandit for security vulnerability scanning

### Contributing

While this project is in early experimental phase, we welcome:

- 🐛 **Bug Reports**: Issues with current functionality
- 💡 **Feature Ideas**: Suggestions for the roadmap
- 📖 **Documentation**: Improvements to guides and examples
- 🧪 **Testing**: Additional test cases and scenarios

Please see our development guidelines in [CLAUDE.md](CLAUDE.md) for coding standards and practices.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This project builds upon excellent work from the Python ecosystem:

- **[Anthropic](https://github.com/anthropics/anthropic-sdk-python)**: Claude AI integration
- **[Pydantic](https://github.com/pydantic/pydantic)**: Schema validation and serialization
- **[Antidote](https://github.com/Finistere/antidote)**: Dependency injection framework
- **[Typer](https://github.com/tiangolo/typer)**: CLI framework
- **[Instructor](https://github.com/jxnl/instructor)**: Structured LLM output processing

---

**⚠️ Experimental Notice**: This project represents an exploration of functional reactive patterns for AI agent development. While the architectural foundations are solid, the system is actively evolving. We appreciate your patience as we work toward a production-ready release.

For questions, issues, or collaboration opportunities, please open an issue or start a discussion on GitHub.
