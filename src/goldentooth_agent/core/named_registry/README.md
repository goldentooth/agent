# Named Registry

Named Registry module

## Overview

- **Complexity**: Low
- **Files**: 2 Python files
- **Lines of Code**: ~96
- **Classes**: 3
- **Functions**: 12

## API Reference

### Classes

#### NamedRegistry
Generic registry for name-keyed objects of type T.

**Public Methods:**
- `set(self, id: str, obj: T) -> None` - Register an object with a given ID
- `get(self, id: str) -> T` - Retrieve an object by its ID
- `remove(self, id: str) -> None` - Remove an object by its ID
- `has(self, id: str) -> bool` - Check if an object with the given ID is registered
- `list_ids(self) -> list[str]` - List all registered IDs in the registry
- `all_objects(self) -> list[T]` - Get all registered objects
- `all_items(self) -> list[tuple[str, T]]` - Get all registered objects as (name, object) pairs
- `clear(self) -> None` - Clear all entries in the registry

#### Creatable
Protocol for a class that can be instantiated.

**Public Methods:**
- `create(cls) -> Tc` - Create an instance of the class

#### RegisterCallable
Protocol for a callable that registers an object with a name.

### Functions

#### `def make_register_fn(registry_cls: type[NamedRegistry[T]]) -> RegisterCallable[T]`
Create a registration function for the given type.

### Constants

#### `T`

## Dependencies

### External Dependencies
- `__future__`
- `collections`
- `main`
- `typing`

## Exports

This module exports the following symbols:

- `NamedRegistry`
- `make_register_fn`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
