# Context Module

## Overview
**Status**: 🔴 High Complexity | **Lines of Code**: 2078 | **Files**: 9

Brief description of the module's purpose and responsibilities.

## Key Components

### Classes (15)

#### `DependencyGraph`
- **File**: `dependency_graph.py`
- **Methods**: 12 methods
- **Purpose**: Manages dependency relationships between context keys and computed properties....

#### `ContextKey`
- **File**: `key.py`
- **Methods**: 6 methods
- **Purpose**: Class for context keys that can be used to store and retrieve values in a context....

#### `Symbol`
- **File**: `symbol.py`
- **Methods**: 2 methods
- **Purpose**: Represents a symbolic key like 'agent.intent'.
You can use Symbol('agent.intent') or just strings in...

#### `SnapshotManager`
- **File**: `snapshot_manager.py`
- **Methods**: 7 methods
- **Purpose**: Manages snapshots for Context objects....

#### `ContextFlowError`
- **File**: `flow_integration.py`
- **Methods**: 0 methods
- **Purpose**: Base exception for Flow-Context integration errors....

#### `MissingRequiredKeyError`
- **File**: `flow_integration.py`
- **Methods**: 0 methods
- **Purpose**: Raised when a required context key is missing....

#### `ContextTypeMismatchError`
- **File**: `flow_integration.py`
- **Methods**: 0 methods
- **Purpose**: Raised when a context key has the wrong type....

#### `ContextFlowCombinators`
- **File**: `flow_integration.py`
- **Methods**: 9 methods
- **Purpose**: Flow combinators for context manipulation with type safety....

#### `ContextFrame`
- **File**: `frame.py`
- **Methods**: 6 methods
- **Purpose**: A single layer of the context stack, representing local bindings....

#### `ContextSnapshot`
- **File**: `main.py`
- **Methods**: 2 methods
- **Purpose**: Represents a snapshot of context state at a specific point in time....

### Functions (103)

#### `add_dependency`
- **File**: `dependency_graph.py`
- **Purpose**: Add a dependency relationship.

Args:
    source_key: The key that is depended upon
    dependent_ke...

#### `remove_dependency`
- **File**: `dependency_graph.py`
- **Purpose**: Remove a specific dependency relationship.

Args:
    source_key: The key that is depended upon
    ...

#### `remove_all_dependencies`
- **File**: `dependency_graph.py`
- **Purpose**: Remove all dependencies for a source key.

Args:
    source_key: The key to remove all dependencies ...

#### `get_dependents`
- **File**: `dependency_graph.py`
- **Purpose**: Get all keys that depend on the given source key.

Args:
    source_key: The key to get dependents f...

#### `has_dependents`
- **File**: `dependency_graph.py`
- **Purpose**: Check if a source key has any dependents.

Args:
    source_key: The key to check

Returns:
    True...

#### `get_all_source_keys`
- **File**: `dependency_graph.py`
- **Purpose**: Get all source keys that have dependents.

Returns:
    Set of all source keys...

#### `clear`
- **File**: `dependency_graph.py`
- **Purpose**: Clear the entire dependency graph....

#### `get_graph_copy`
- **File**: `dependency_graph.py`
- **Purpose**: Get a copy of the internal graph structure.

Returns:
    Dictionary mapping source keys to sets of ...

#### `context_key`
- **File**: `key.py`
- **Purpose**: Create a context key with the specified name and type....

#### `create`
- **File**: `key.py`
- **Purpose**: Create a new context key with the specified name, type, and description....

## Public API

### Main Exports
```python
# TODO: Document main exports
from goldentooth_agent.core.context import (
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
# dataclasses
# pyee
# snapshot_manager
# weakref
# dependency_graph
# time
# main
# asyncio
# copy
# history_tracker
```

## Testing

### Test Coverage
- **Test files**: Located in `tests/core/context/`
- **Coverage target**: 85%+
- **Performance**: All tests <1s

### Running Tests
```bash
# Run all tests for this module
poetry run pytest tests/core/context/

# Run with coverage
poetry run pytest tests/core/context/ --cov=src/goldentooth_agent/core/context/
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
