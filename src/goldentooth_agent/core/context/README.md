# Context

Context module

## Overview

- **Complexity**: High
- **Files**: 9 Python files
- **Lines of Code**: ~1633
- **Classes**: 15
- **Functions**: 122

## API Reference

### Classes

#### DependencyGraph
Manages dependency relationships between context keys and computed properties.

**Public Methods:**
- `add_dependency()`
- `remove_dependency()`
- `remove_all_dependencies()`
- `get_dependents()`
- `has_dependents()`
- `get_all_source_keys()`
- `clear()`
- `get_graph_copy()`

#### ContextKey
Class for context keys that can be used to store and retrieve values in a context.

**Public Methods:**
- `create()`
- `symbol()`

#### Symbol
Represents a symbolic key like 'agent.intent'.
    You can use Symbol('agent.intent') or just strings interchangeably.

**Public Methods:**
- `parts()`

#### SnapshotManager
Manages snapshots for Context objects.

**Public Methods:**
- `create_snapshot()`
- `restore_snapshot()`
- `list_snapshots()`
- `delete_snapshot()`
- `get_snapshot()`
- `clear_snapshots()`

#### ContextFlowError
Base exception for Flow-Context integration errors.

#### MissingRequiredKeyError
Raised when a required context key is missing.

#### ContextTypeMismatchError
Raised when a context key has the wrong type.

#### ContextFlowCombinators
Flow combinators for context manipulation with type safety.

**Public Methods:**
- `get_key()`
- `set_key()`
- `require_key()`
- `optional_key()`
- `move_key()`
- `copy_key()`
- `forget_key()`
- `require_keys()`
- `transform_key()`

#### ContextFrame
A single layer of the context stack, representing local bindings.

**Public Methods:**
- `copy()`

#### ContextSnapshot
Represents a snapshot of context state at a specific point in time.

**Public Methods:**
- `restore_to()`

#### ComputedProperty
Represents a computed property that automatically updates when its dependencies change.

**Public Methods:**
- `compute()`
- `invalidate()`
- `subscribe()`
- `notify_change()`

#### Transformation
Represents a value transformation applied to context keys.

**Public Methods:**
- `apply()`

#### Context
A layered, reactive, symbolic context with scoped access and EventFlow integration.

**Public Methods:**
- `get()`
- `set()`
- `push_layer()`
- `pop_layer()`
- `fork()`
- `fork_with_history()`
- `merge()`
- `diff()`
- `deep_diff()`
- `create_snapshot()`
- `restore_snapshot()`
- `list_snapshots()`
- `delete_snapshot()`
- `get_change_history()`
- `clear_history()`
- `get_history_size()`
- `set_max_history_size()`
- `rollback_to_timestamp()`
- `get_snapshots()`
- `replay_changes_since()`
- `keys()`
- `subscribe_sync()`
- `subscribe_async()`
- `as_flow()`
- `global_changes_sync()`
- `global_changes_async()`
- `global_changes_as_flow()`
- `dump()`
- `add_computed_property()`
- `remove_computed_property()`
- `add_transformation()`
- `remove_transformations()`
- `get_computed_value()`
- `is_computed_property()`
- `computed_properties()`
- `transformations()`
- `query()`
- `find_keys()`
- `find_values()`
- `filter_by_type()`
- `search()`
- `get_nested()`
- `set_nested()`
- `has_nested()`
- `flatten()`

#### ContextChangeEvent
Represents a single change event in context history.

#### HistoryTracker
Tracks change history for Context objects.

**Public Methods:**
- `record_change()`
- `get_history()`
- `clear_history()`
- `get_history_size()`
- `set_max_history_size()`
- `replay_changes_since()`
- `get_changes_to_reverse()`
- `get_all_history()`

### Functions

#### `def context_key(name: str, type_: type[T], description: str) -> ContextKey[T]`
Create a context key with the specified name and type.

#### `def run_flow_with_input(flow: Flow[T, R], input_item: T) -> R`
Run a flow with a single input item and return the first result.

    This is a convenience function for testing and simple use cases.

#### `def extend_flow_with_context() -> None`
Extend Flow class with context manipulation methods.

#### `def context_flow() -> ContextFlowDecorator`
Decorator to create a context-aware Flow with declared dependencies.

    Args:
        inputs: List of required input context keys
        outputs: List of output context keys this flow will set
        optional: Dict of optional keys with their default values
        name: Optional name for the flow

### Constants

#### `T`

#### `T`

#### `R`

#### `T`

## Dependencies

### Internal Dependencies
- `goldentooth_agent.core.event`

### External Dependencies
- `__future__`
- `asyncio`
- `collections`
- `copy`
- `dataclasses`
- `dependency_graph`
- `flow_integration`
- `frame`
- `functools`
- `goldentooth_agent`
- `history_tracker`
- `json`
- `key`
- `main`
- `pyee`
- `re`
- `snapshot_manager`
- `symbol`
- `time`
- `typing`
- `weakref`

## Exports

This module exports the following symbols:

- `Context`
- `ContextFlowCombinators`
- `ContextFlowError`
- `ContextFrame`
- `ContextKey`
- `ContextTypeMismatchError`
- `DependencyGraph`
- `HistoryTracker`
- `MissingRequiredKeyError`
- `SnapshotManager`
- `Symbol`
- `context_flow`
- `context_key`
- `extend_flow_with_context`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
