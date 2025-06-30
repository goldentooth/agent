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
- `usage()`

#### LLMClient
Abstract base class for LLM clients.

**Public Methods:**
- `create_completion()`
- `create_chat_completion()`

#### ClaudeStreamingResponse
Wrapper for Claude streaming responses.

**Public Methods:**
- `usage()`

#### ClaudeFlowClient
Anthropic Claude client with Flow integration.

**Public Methods:**
- `create_completion()`
- `create_chat_completion()`

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
