# Integrations

Integrations module

## Overview

- **Complexity**: Low
- **Files**: 2 Python files
- **Lines of Code**: ~142
- **Classes**: 1
- **Functions**: 12

## API Reference

### Classes

#### ContextFlowBridge
Bridge between Flow Engine and Context system using protocols.

**Public Methods:**
- `ensure_context_keys()`
- `get_trampoline_key()`
- `register_trampoline_support()`

### Functions

#### `def initialize_context_integration() -> None`
Initialize context integration if available.

#### `def get_context_bridge() -> ContextFlowBridge`
Get the global context bridge instance.

## Dependencies

### External Dependencies
- `__future__`
- `extensions`
- `lazy_imports`
- `protocols`
- `typing`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
