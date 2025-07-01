# Schema

Schema module

# Background & Motivation

## Problem Statement

The RAG agent error `'dict' object has no attribute 'response'` highlighted a critical issue: inconsistent response handling across agents. Some components return dictionaries while others expect objects with attributes, leading to runtime failures that are difficult to debug.

## Theoretical Foundation

### Response Schema Pattern
This module implements the **Response Schema Pattern** from domain-driven design, where:
- All agent responses conform to a standardized schema
- Type safety is enforced at runtime through Pydantic validation
- Dictionary and object access patterns are unified

### Pydantic Integration
Uses Pydantic BaseModel for:
- Runtime validation of response data
- Automatic serialization/deserialization
- Type coercion and validation
- Clear error messages for invalid data

## Design Philosophy

### Consistency Over Flexibility
Rather than allowing arbitrary response formats, we enforce a consistent structure that all agents must follow. This trades some flexibility for reliability and debuggability.

### Type Safety First
All response fields are strictly typed with Pydantic, ensuring that:
- Invalid data is caught early
- IDE support provides accurate completion
- Runtime type errors are prevented

### Backward Compatibility
The `from_dict()` and `to_dict()` methods allow gradual migration from dictionary-based to object-based response handling.

## Technical Challenges Addressed

1. **Type Confusion**: Prevented confusion between dict and object access patterns
2. **Runtime Validation**: Ensured response data meets expected schema
3. **Developer Experience**: Provided clear error messages and IDE support
4. **Migration Path**: Enabled gradual adoption without breaking existing code

## Integration Patterns

### Agent Response Standardization
```python
# Before: Inconsistent return types
def process() -> dict | SomeObject | Any:
    return {"response": "text"}  # Type unclear

# After: Consistent schema
def process() -> AgentResponse:
    return AgentResponse(response="text")
```

### Error Prevention
The schema prevents common errors:
- Missing required fields
- Invalid confidence scores (outside 0-1 range)
- Unexpected extra fields
- Type mismatches

## Future Considerations

- Protocol definition for all agent interfaces
- Automatic schema validation decorators
- Response streaming support for large responses
- Schema versioning for backward compatibility

## Overview

- **Complexity**: Low
- **Files**: 2 Python files
- **Lines of Code**: ~47
- **Classes**: 1
- **Functions**: 2

## API Reference

### Classes

#### AgentResponse
Standardized agent response schema.

    This provides a consistent interface for all agent responses,
    ensuring type safety and preventing the dictionary/object access confusion.

**Public Methods:**
- `from_dict(cls, data: dict[str, Any]) -> 'AgentResponse'` - Create AgentResponse from dictionary with validation
- `to_dict(self) -> dict[str, Any]` - Convert to dictionary for serialization

## Dependencies

### External Dependencies
- `agent_response`
- `pydantic`
- `typing`

## Exports

This module exports the following symbols:

- `AgentResponse`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
