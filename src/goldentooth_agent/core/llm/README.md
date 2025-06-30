# Llm

Llm module

## Overview

- **Complexity**: Medium
- **Files**: 3 Python files
- **Lines of Code**: ~325
- **Classes**: 4
- **Functions**: 11

## API Reference

### Classes

#### StreamingResponse
Protocol for streaming LLM responses.

**Public Methods:**
- `usage(self) -> dict[str, Any]` - Token usage information

#### LLMClient
Abstract base class for LLM clients.

**Public Methods:**
- `async create_completion(self, response_model: type[T], messages: list[dict[str, Any]], model: str, temperature: float, max_tokens: int, stream: bool, **kwargs: Any) -> T | StreamingResponse` - Create a completion with structured output
- `async create_chat_completion(self, messages: list[dict[str, Any]], model: str, temperature: float, max_tokens: int, stream: bool, **kwargs: Any) -> str | StreamingResponse` - Create a chat completion without structured output

#### ClaudeStreamingResponse
Wrapper for Claude streaming responses.

**Public Methods:**
- `usage(self) -> dict[str, Any]` - Token usage information

#### ClaudeFlowClient
Anthropic Claude client with Flow integration.

**Public Methods:**
- `async create_completion(self, response_model: type[T], messages: list[dict[str, Any]], model: str | None, temperature: float, max_tokens: int | None, stream: bool, **kwargs: Any) -> T | StreamingResponse` - Create a completion with structured output using Instructor
- `async create_chat_completion(self, messages: list[dict[str, Any]], model: str | None, temperature: float, max_tokens: int | None, stream: bool, system: str | None, **kwargs: Any) -> str | StreamingResponse` - Create a chat completion without structured output

### Functions

#### `def create_claude_agent(name: str, model: str, system_prompt: str | None, temperature: float, max_tokens: int, api_key: str | None) -> FlowAgent`
Create a Claude-powered FlowAgent.

    Args:
        name: Agent name
        model: Claude model to use
        system_prompt: Optional system prompt
        temperature: Sampling temperature
        max_tokens: Maximum tokens per response
        api_key: Anthropic API key (defaults to env var)

    Returns:
        FlowAgent powered by Claude

### Constants

#### `T`

#### `T`

## Dependencies

### External Dependencies
- `__future__`
- `abc`
- `anthropic`
- `base`
- `claude_client`
- `collections`
- `context`
- `flow_agent`
- `goldentooth_agent`
- `instructor`
- `os`
- `typing`

## Exports

This module exports the following symbols:

- `ClaudeFlowClient`
- `LLMClient`
- `StreamingResponse`
- `create_claude_agent`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
