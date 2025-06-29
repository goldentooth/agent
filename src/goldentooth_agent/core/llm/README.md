# Llm Module

## Overview
**Status**: 🟢 Low Complexity | **Lines of Code**: 388 | **Files**: 3

Brief description of the module's purpose and responsibilities.

## Key Components

### Classes (4)

#### `StreamingResponse`
- **File**: `base.py`
- **Methods**: 1 methods
- **Purpose**: Protocol for streaming LLM responses....

#### `LLMClient`
- **File**: `base.py`
- **Methods**: 0 methods
- **Purpose**: Abstract base class for LLM clients....

#### `ClaudeStreamingResponse`
- **File**: `claude_client.py`
- **Methods**: 2 methods
- **Purpose**: Wrapper for Claude streaming responses....

#### `ClaudeFlowClient`
- **File**: `claude_client.py`
- **Methods**: 1 methods
- **Purpose**: Anthropic Claude client with Flow integration....

### Functions (3)

#### `usage`
- **File**: `base.py`
- **Purpose**: Token usage information....

#### `create_claude_agent`
- **File**: `claude_client.py`
- **Purpose**: Create a Claude-powered FlowAgent.

Args:
    name: Agent name
    model: Claude model to use
    sy...

#### `usage`
- **File**: `claude_client.py`
- **Purpose**: Token usage information....

## Public API

### Main Exports
```python
# TODO: Document main exports
from goldentooth_agent.core.llm import (
    # Add main classes and functions here
)
```

### Usage Examples
```python
# TODO: Add usage examples
```

## Dependencies

### Internal Dependencies
```python
# Key internal imports

```

### External Dependencies
```python
# Key external imports
# context
# os
# collections.abc
# abc
# flow
# base
# __future__
# flow_agent
# anthropic
# claude_client
```

## Testing

### Test Coverage
- **Test files**: Located in `tests/core/llm/`
- **Coverage target**: 85%+
- **Performance**: All tests <1s

### Running Tests
```bash
# Run all tests for this module
poetry run pytest tests/core/llm/

# Run with coverage
poetry run pytest tests/core/llm/ --cov=src/goldentooth_agent/core/llm/
```

## Known Issues

### Technical Debt
- [ ] TODO: Document known issues
- [ ] TODO: Type safety concerns
- [ ] TODO: Performance bottlenecks

### Future Improvements
- [ ] TODO: Planned enhancements
- [ ] TODO: Refactoring needs

## Development Notes

### Architecture Decisions
- TODO: Document key design decisions
- TODO: Explain complex interactions

### Performance Considerations
- TODO: Document performance requirements
- TODO: Known bottlenecks and optimizations

## Related Modules

### Dependencies
- **Depends on**: TODO: List module dependencies
- **Used by**: TODO: List modules that use this one

### Integration Points
- TODO: Document how this module integrates with others
