# Registry

Registry module

## Overview

- **Complexity**: Low
- **Files**: 2 Python files
- **Lines of Code**: ~259
- **Classes**: 1
- **Functions**: 15

## API Reference

### Classes

#### FlowRegistry
Registry for named flows with discovery and introspection capabilities.

**Public Methods:**
- `register()`
- `get()`
- `list_flows()`
- `list_categories()`
- `search()`
- `remove()`
- `clear()`
- `info()`
- `print_registry()`

### Functions

#### `def register_flow(name: str, flow: AnyFlow, category: str | None) -> AnyFlow`
Register a flow in the global registry.

    Args:
        name: Unique name for the flow
        flow: Flow instance to register
        category: Optional category for organization

    Returns:
        The registered flow (for chaining)

#### `def get_flow(name: str) -> AnyFlow | None`
Get a flow from the global registry.

    Args:
        name: Name of the flow to retrieve

    Returns:
        Flow instance or None if not found

#### `def list_flows(category: str | None) -> list[str]`
List flows in the global registry.

    Args:
        category: Optional category to filter by

    Returns:
        List of flow names

#### `def search_flows(query: str) -> list[str]`
Search flows in the global registry.

    Args:
        query: Search query

    Returns:
        List of matching flow names

#### `def registered_flow(name: str, category: str | None) -> Callable[[Any], Any]`
Decorator to register a flow in the global registry.

    Args:
        name: Unique name for the flow
        category: Optional category for organization

    Example:
        @registered_flow("text_processor", "nlp")
        @Flow.from_sync_fn
        def process_text(text):
            return text.upper()

        Or with factory functions:
        @registered_flow("my_flow")
        def create_flow():
            return map_stream(lambda x: x + 1)

## Dependencies

### External Dependencies
- `collections`
- `core`
- `main`
- `typing`

## Exports

This module exports the following symbols:

- `FlowRegistry`
- `flow_registry`
- `get_flow`
- `list_flows`
- `register_flow`
- `registered_flow`
- `search_flows`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
