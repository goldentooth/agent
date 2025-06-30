# Flow Agent

Flow Agent module

## Overview

- **Complexity**: Medium
- **Files**: 5 Python files
- **Lines of Code**: ~593
- **Classes**: 7
- **Functions**: 22

## API Reference

### Classes

#### MockLLMClient
Mock LLM client for testing purposes.

    This client simulates LLM responses for testing the Instructor integration
    without requiring actual API calls.

**Public Methods:**
- `create_completion()`

#### InstructorFlow
Flow-based wrapper for Instructor-powered structured LLM output.

    InstructorFlow integrates with the FlowAgent system to provide structured
    LLM output using Instructor's validation and parsing capabilities.

**Public Methods:**
- `as_flow()`

#### FlowAgent
Flow-based agent using functional composition.

    FlowAgent implements a complete agent pipeline that:
    1. Validates input schemas
    2. Converts input to context
    3. Runs system flow (prompt generation, memory, etc.)
    4. Runs processing flow (LLM calls, tool execution, etc.)
    5. Extracts and validates output schemas

**Public Methods:**
- `as_flow()`

#### FlowTool
Flow-based tool with agent-like interface.

    FlowTool provides a unified interface for tools that can be used as flows
    or converted to agent-compatible interfaces.

**Public Methods:**
- `as_flow()`
- `as_agent()`

#### FlowIOSchema
Base schema for all Flow-based agent interactions with context integration.

**Public Methods:**
- `to_context()`
- `from_context()`

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
