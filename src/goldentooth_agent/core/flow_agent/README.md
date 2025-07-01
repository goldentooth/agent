# Flow Agent

Flow Agent module

## Background & Motivation

### Problem Statement

The flow_agent module addresses the need for functional composition of data processing operations.

### Theoretical Foundation

#### Core Concepts

This module implements functional flow composition concepts:
- **Function Composition**: Chaining operations in a type-safe, predictable manner
- **Immutable Data Flow**: Data transformations that preserve input integrity

#### Design Philosophy

**Simplicity and Clarity**: Emphasizes straightforward implementations that are easy to understand and maintain.

### Technical Challenges Addressed

1. **Functional Composition**: Designing composable operations that maintain referential transparency and avoid side effects
3. **Type-Safe Composition**: Ensuring type safety across dynamic function compositions without runtime overhead
4. **Error Propagation**: Handling errors gracefully in composed operations without breaking the functional chain

### Integration & Usage

The flow_agent module integrates with the broader system through well-defined interfaces.

**Key Dependencies:**
- __future__: Provides essential functionality required by this module
- agent: Provides essential functionality required by this module
- asyncio: Provides essential functionality required by this module
- collections: Provides essential functionality required by this module
- context: Provides essential functionality required by this module

**Usage Patterns:**
- **Dependency Injection**: Services are provided through the Antidote DI container
- **Type-Safe Interfaces**: All public APIs use comprehensive type annotations
- **Error Propagation**: Exceptions are handled consistently with the system's error handling patterns

---

*This background file was generated using AI analysis of the flow_agent module. Please review and customize as needed.*

## Overview

- **Complexity**: Medium
- **Files**: 5 Python files
- **Lines of Code**: ~604
- **Classes**: 7
- **Functions**: 22

## API Reference

### Classes

#### MockLLMClient
Mock LLM client for testing purposes.

    This client simulates LLM responses for testing the Instructor integration
    without requiring actual API calls.

**Public Methods:**
- `async create_completion(self, response_model: type[R], messages: list[MessageData], model: str, **kwargs: FlowKwargs) -> R` - Mock completion creation that returns predefined responses

#### InstructorFlow
Flow-based wrapper for Instructor-powered structured LLM output.

    InstructorFlow integrates with the FlowAgent system to provide structured
    LLM output using Instructor's validation and parsing capabilities.

**Public Methods:**
- `as_flow(self) -> Flow[Context, Context]` - Convert InstructorFlow to a composable Flow

#### FlowAgent
Flow-based agent using functional composition.

    FlowAgent implements a complete agent pipeline that:
    1. Validates input schemas
    2. Converts input to context
    3. Runs system flow (prompt generation, memory, etc.)
    4. Runs processing flow (LLM calls, tool execution, etc.)
    5. Extracts and validates output schemas

**Public Methods:**
- `as_flow(self) -> Flow[FlowIOSchema, FlowIOSchema]` - Convert agent to a composable flow

#### FlowTool
Flow-based tool with agent-like interface.

    FlowTool provides a unified interface for tools that can be used as flows
    or converted to agent-compatible interfaces.

**Public Methods:**
- `as_flow(self) -> AnyFlow` - Convert tool to a composable flow
- `as_agent(self) -> AnyAgent` - Convert tool to an agent-compatible interface

#### FlowIOSchema
Base schema for all Flow-based agent interactions with context integration.

**Public Methods:**
- `to_context(self, context: Context) -> Context` - Convert schema to context entries
- `from_context(cls: type[T], context: Context) -> T` - Extract schema from context

#### AgentInput
Standard input for agent flows.

#### AgentOutput
Standard output for agent flows.

### Functions

#### `def create_instructor_flow(client: LLMClient, model: str, input_schema: type[T], output_schema: type[R], system_prompt: str | None, **kwargs: FlowKwargs) -> Flow[Context, Context]`
Factory function to create an InstructorFlow as a Flow.

    Args:
        client: LLM client instance
        model: Model name
        input_schema: Input schema type
        output_schema: Output schema type
        system_prompt: Optional system prompt
        **kwargs: Additional arguments passed to InstructorFlow

    Returns:
        Flow that performs structured LLM completion

#### `def create_system_prompt_flow(prompt: str) -> Flow[Context, Context]`
Create a flow that adds a system prompt to the context.

    Args:
        prompt: System prompt text

    Returns:
        Flow that adds the system prompt to context

#### `def create_model_config_flow(model: str, temperature: float, max_tokens: int | None) -> Flow[Context, Context]`
Create a flow that adds model configuration to the context.

    Args:
        model: Model name
        temperature: Temperature setting
        max_tokens: Optional maximum tokens

    Returns:
        Flow that adds model configuration to context

### Constants

#### `T`

#### `R`

#### `SYSTEM_PROMPT_KEY`

#### `MODEL_NAME_KEY`

#### `TEMPERATURE_KEY`

#### `MAX_TOKENS_KEY`

#### `COMPLETION_METADATA_KEY`

#### `T`

#### `R`

#### `T`

## Dependencies

### External Dependencies
- `__future__`
- `agent`
- `asyncio`
- `collections`
- `context`
- `goldentooth_agent`
- `instructor_integration`
- `pydantic`
- `schema`
- `tool`
- `typing`

## Exports

This module exports the following symbols:

- `AgentInput`
- `AgentOutput`
- `FlowAgent`
- `FlowIOSchema`
- `FlowTool`
- `InstructorFlow`
- `MockLLMClient`
- `create_instructor_flow`
- `create_model_config_flow`
- `create_system_prompt_flow`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
