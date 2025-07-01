# Context

Context module

# Background & Motivation

## Problem Statement

The context module addresses the challenge of integrating event-driven programming with functional flow architectures, enabling reactive data processing while maintaining composability.

## Theoretical Foundation

### Core Concepts

This module implements state management concepts:
- **State Snapshots**: Immutable captures of system state for debugging and rollback
- **Context Propagation**: Passing shared state through computation chains
- **Dependency Resolution**: Managing complex object graphs and service dependencies

#### Design Philosophy

**Simplicity and Clarity**: Emphasizes straightforward implementations that are easy to understand and maintain.

### Technical Challenges Addressed

1. **Immutable State Management**: Providing stateful behavior while maintaining functional programming principles and avoiding shared mutable state
2. **Efficient Snapshots**: Creating lightweight, immutable state captures without excessive memory overhead
3. **Dependency Graph Resolution**: Managing complex service dependencies while avoiding circular references and ensuring proper initialization order
4. **Context Isolation**: Preventing context leakage between different execution environments or user sessions

### Integration & Usage

The context module integrates with the broader system through well-defined interfaces.

**Key Dependencies:**
- goldentooth_agent.core.event: Provides essential functionality required by this module
- __future__: Provides essential functionality required by this module
- asyncio: Provides essential functionality required by this module
- collections: Provides essential functionality required by this module
- copy: Provides essential functionality required by this module

**Usage Patterns:**
- **Dependency Injection**: Services are provided through the Antidote DI container
- **Type-Safe Interfaces**: All public APIs use comprehensive type annotations
- **Error Propagation**: Exceptions are handled consistently with the system's error handling patterns

---

*This background file was generated using AI analysis of the context module. Please review and customize as needed.*

## Overview

- **Complexity**: High
- **Files**: 9 Python files
- **Lines of Code**: ~1635
- **Classes**: 15
- **Functions**: 122

## API Reference

### Classes

#### DependencyGraph
Manages dependency relationships between context keys and computed properties.

**Public Methods:**
- `add_dependency(self, source_key: str, dependent_key: str) -> None` - Add a dependency relationship
- `remove_dependency(self, source_key: str, dependent_key: str) -> None` - Remove a specific dependency relationship
- `remove_all_dependencies(self, source_key: str) -> None` - Remove all dependencies for a source key
- `get_dependents(self, source_key: str) -> set[str]` - Get all keys that depend on the given source key
- `has_dependents(self, source_key: str) -> bool` - Check if a source key has any dependents
- `get_all_source_keys(self) -> set[str]` - Get all source keys that have dependents
- `clear(self) -> None` - Clear the entire dependency graph
- `get_graph_copy(self) -> dict[str, set[str]]` - Get a copy of the internal graph structure

#### ContextKey
Class for context keys that can be used to store and retrieve values in a context.

**Public Methods:**
- `create(cls, path: str, type_: type[T], description: str) -> ContextKey[T]` - Create a new context key with the specified name, type, and description
- `symbol(self) -> Symbol` - Return a Symbol representation of the context key

#### Symbol
Represents a symbolic key like 'agent.intent'.
    You can use Symbol('agent.intent') or just strings interchangeably.

**Public Methods:**
- `parts(self) -> list[str]` - Split the symbol into its parts based on the '.' delimiter

#### SnapshotManager
Manages snapshots for Context objects.

**Public Methods:**
- `create_snapshot(self, context: Context, name: str) -> ContextSnapshot` - Create a snapshot of the current context state
- `restore_snapshot(self, context: Context, name: str) -> None` - Restore the context to a previous snapshot state
- `list_snapshots(self) -> dict[str, float]` - List all available snapshots with their timestamps
- `delete_snapshot(self, name: str) -> None` - Delete a snapshot
- `get_snapshot(self, name: str) -> ContextSnapshot` - Get a specific snapshot
- `clear_snapshots(self) -> None` - Clear all snapshots

#### ContextFlowError
Base exception for Flow-Context integration errors.

#### MissingRequiredKeyError
Raised when a required context key is missing.

#### ContextTypeMismatchError
Raised when a context key has the wrong type.

#### ContextFlowCombinators
Flow combinators for context manipulation with type safety.

**Public Methods:**
- `get_key(key: ContextKey[T], default: T | None) -> Flow[Context, T | None]` - Create a Flow that extracts a value from a context key
- `set_key(key: ContextKey[T], value: T) -> Flow[Context, Context]` - Create a Flow that sets a context key to a specific value
- `require_key(key: ContextKey[T]) -> Flow[Context, T]` - Create a Flow that requires a context key to be present and returns its value
- `optional_key(key: ContextKey[T], default: T) -> Flow[Context, T]` - Create a Flow that gets an optional context key with a default value
- `move_key(source: ContextKey[T], destination: ContextKey[T]) -> Flow[Context, Context]` - Create a Flow that moves a value from one context key to another
- `copy_key(source: ContextKey[T], destination: ContextKey[T]) -> Flow[Context, Context]` - Create a Flow that copies a value from one context key to another
- `forget_key(key: ContextKey[T]) -> Flow[Context, Context]` - Create a Flow that removes a key from the context
- `require_keys(*keys: AnyContextKey) -> Flow[Context, Context]` - Create a Flow that validates multiple required keys are present
- `transform_key(key: ContextKey[T], transform_fn: Callable[[T], R], result_key: ContextKey[R] | None) -> Flow[Context, Context | R]` - Create a Flow that transforms a context key's value

#### ContextFrame
A single layer of the context stack, representing local bindings.

**Public Methods:**
- `copy(self) -> ContextFrame` - Create a copy of this context frame

#### ContextSnapshot
Represents a snapshot of context state at a specific point in time.

**Public Methods:**
- `restore_to(self, context: Context) -> None` - Restore this snapshot to the given context

#### ComputedProperty
Represents a computed property that automatically updates when its dependencies change.

**Public Methods:**
- `compute(self, context: Context) -> ContextValue` - Compute the property value for the given context
- `invalidate(self) -> None` - Invalidate the cached value, requiring recomputation
- `subscribe(self, context: Context) -> None` - Subscribe a context to this computed property for dependency tracking
- `notify_change(self) -> None` - Notify all subscribed contexts that this property may have changed

#### Transformation
Represents a value transformation applied to context keys.

**Public Methods:**
- `apply(self, value: ContextValue) -> ContextValue` - Apply the transformation to a value

#### Context
A layered, reactive, symbolic context with scoped access and EventFlow integration.

**Public Methods:**
- `get(self, key: str, default: T | None) -> T | None` - Get the value for a key, searching through all frames and computed properties
- `set(self, key: str, value: ContextValue) -> None` - Set a value for a key in the current frame and notify subscribers/emit events
- `push_layer(self) -> None` - Push a new layer onto the context stack
- `pop_layer(self) -> None` - Pop the top layer from the context stack
- `fork(self) -> Context` - Create a fork of the current context with copies of the frames, computed properties, and transformations
- `fork_with_history(self) -> Context` - Create a fork of the current context that includes history and snapshots
- `merge(self, other: Context) -> Context` - Merge another context into this one, updating frames
- `diff(self, other: Context) -> ContextDiff` - Compute the differences between this context and another
- `deep_diff(self, other: Context, delimiter: str) -> ContextDiff` - Compute deep differences including nested values
- `create_snapshot(self, name: str) -> ContextSnapshot` - Create a snapshot of the current context state
- `restore_snapshot(self, name: str) -> None` - Restore the context to a previous snapshot state
- `list_snapshots(self) -> dict[str, float]` - List all available snapshots with their timestamps
- `delete_snapshot(self, name: str) -> None` - Delete a snapshot
- `get_change_history(self, limit: int | None, since: float | None) -> list[ContextChangeEvent]` - Get the change history for this context
- `clear_history(self) -> None` - Clear the change history
- `get_history_size(self) -> int` - Get the current size of the change history
- `set_max_history_size(self, size: int) -> None` - Set the maximum history size
- `rollback_to_timestamp(self, timestamp: float) -> None` - Rollback context to state at a specific timestamp
- `get_snapshots(self) -> dict[str, ContextSnapshot]` - Get all snapshots (returns a copy)
- `replay_changes_since(self, timestamp: float) -> list[ContextChangeEvent]` - Get all changes that occurred since a specific timestamp
- `keys(self) -> Iterator[str]` - Yield all unique keys from the context, including computed properties
- `subscribe_sync(self, key: str) -> SyncEventFlow[ContextValue]` - Get a synchronous EventFlow for changes to a specific key
- `subscribe_async(self, key: str) -> AsyncEventFlow[ContextValue]` - Get an asynchronous EventFlow for changes to a specific key
- `as_flow(self, key: str, use_async: bool) -> Flow[None, Any]` - Convert context key changes to a Flow stream
- `global_changes_sync(self) -> SyncGlobalEventFlow` - Get a synchronous EventFlow for all context changes
- `global_changes_async(self) -> AsyncGlobalEventFlow` - Get an asynchronous EventFlow for all context changes
- `global_changes_as_flow(self, use_async: bool) -> Flow[None, GlobalChangeData]` - Convert all context changes to a Flow stream
- `dump(self) -> str` - Dump the context as a JSON string, merging all frames
- `add_computed_property(self, key: str, func: ComputedFunction, dependencies: list[str] | None) -> None` - Add a computed property to the context
- `remove_computed_property(self, key: str) -> None` - Remove a computed property from the context
- `add_transformation(self, key: str, func: TransformFunction) -> None` - Add a value transformation for a specific key
- `remove_transformations(self, key: str) -> None` - Remove all transformations for a specific key
- `get_computed_value(self, key: str) -> ContextValue` - Get the value of a computed property
- `is_computed_property(self, key: str) -> bool` - Check if a key represents a computed property
- `computed_properties(self) -> dict[str, ComputedProperty]` - Get all computed properties in this context
- `transformations(self) -> dict[str, list[Transformation]]` - Get all transformations in this context
- `query(self, pattern: str | None, key_filter: Callable[[str], bool] | None, value_filter: ValuePredicate | None, include_computed: bool) -> ContextData` - Query context data with various filtering options
- `find_keys(self, pattern: str) -> list[str]` - Find all keys matching a regex pattern
- `find_values(self, predicate: ValuePredicate) -> ContextData` - Find all key-value pairs where the value matches a predicate
- `filter_by_type(self, value_type: type) -> ContextData` - Filter context entries by value type
- `search(self, search_term: str, case_sensitive: bool) -> ContextData` - Search for keys or values containing a term
- `get_nested(self, path: str, delimiter: str) -> ContextValue` - Get a nested value using dot notation or custom delimiter
- `set_nested(self, path: str, value: ContextValue, delimiter: str, create_missing: bool) -> None` - Set a nested value using dot notation or custom delimiter
- `has_nested(self, path: str, delimiter: str) -> bool` - Check if a nested path exists
- `flatten(self, delimiter: str, max_depth: int | None) -> FlattenedData` - Flatten nested dictionaries into dot-separated keys

#### ContextChangeEvent
Represents a single change event in context history.

#### HistoryTracker
Tracks change history for Context objects.

**Public Methods:**
- `record_change(self, key: str, old_value: TrackedValue, new_value: TrackedValue, context_id: int) -> None` - Record a change event in the history
- `get_history(self, limit: int | None, since: float | None) -> list[ContextChangeEvent]` - Get the change history
- `clear_history(self) -> None` - Clear the change history
- `get_history_size(self) -> int` - Get the current size of the change history
- `set_max_history_size(self, size: int) -> None` - Set the maximum history size
- `replay_changes_since(self, timestamp: float) -> list[ContextChangeEvent]` - Get all changes that occurred since a specific timestamp
- `get_changes_to_reverse(self, timestamp: float) -> list[ContextChangeEvent]` - Get changes that need to be reversed for rollback to a timestamp
- `get_all_history(self) -> list[ContextChangeEvent]` - Get all history without filtering or reversing

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
