# Registry

Registry module

## Background & Motivation

### Problem Statement

The registry module addresses domain-specific registry functionality that required specialized architectural solutions.

### Theoretical Foundation

#### Core Concepts

The module implements domain-specific concepts tailored to its functional requirements.

#### Design Philosophy

**Simplicity and Clarity**: Emphasizes straightforward implementations that are easy to understand and maintain.

### Technical Challenges Addressed

1. **Modularity**: Designing clean interfaces that promote reusability and testability
2. **Maintainability**: Structuring code for easy modification and extension
3. **Integration**: Seamlessly connecting with other system components

### Integration & Usage

The registry module integrates with the broader system through well-defined interfaces.

**Key Dependencies:**
- collections: Provides essential functionality required by this module
- core: Provides essential functionality required by this module
- main: Provides essential functionality required by this module
- typing: Provides essential functionality required by this module

**Usage Patterns:**
- **Dependency Injection**: Services are provided through the Antidote DI container
- **Type-Safe Interfaces**: All public APIs use comprehensive type annotations
- **Error Propagation**: Exceptions are handled consistently with the system's error handling patterns

---

*This background file was generated using AI analysis of the registry module. Please review and customize as needed.*

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
- `register(self, name: str, flow: AnyFlow, category: str | None) -> AnyFlow` - Register a flow with the given name
- `get(self, name: str) -> AnyFlow | None` - Get a flow by name
- `list_flows(self, category: str | None) -> list[str]` - List all registered flow names
- `list_categories(self) -> list[str]` - List all categories
- `search(self, query: str) -> list[str]` - Search for flows by name or metadata
- `remove(self, name: str) -> bool` - Remove a flow from the registry
- `clear(self, category: str | None) -> None` - Clear flows from registry
- `info(self, name: str) -> FlowInfo | None` - Get detailed information about a flow
- `print_registry(self) -> None` - Print a formatted view of the registry

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

    Example::

        @registered_flow("text_processor", "nlp")
        @Flow.from_sync_fn
        def process_text(text):
            return text.upper()

    Or with factory functions::

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
