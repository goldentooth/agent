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
- `set()`
- `get()`
- `remove()`
- `has()`
- `list_ids()`
- `all_objects()`
- `all_items()`
- `clear()`

#### Creatable
Protocol for a class that can be instantiated.

**Public Methods:**
- `create()`

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
