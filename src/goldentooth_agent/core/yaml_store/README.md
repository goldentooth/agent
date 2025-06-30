# Yaml Store

Yaml Store module

## Overview

- **Complexity**: Medium
- **Files**: 4 Python files
- **Lines of Code**: ~78
- **Classes**: 3
- **Functions**: 10

## API Reference

### Classes

#### YamlStoreAdapter
Protocol for classes that can be serialized to and from YAML.

**Public Methods:**
- `from_dict(cls, data: YamlData) -> T` - Create an instance from a dictionary representation
- `to_dict(cls, id: str, obj: T) -> YamlData` - Convert the instance to a dictionary representation

#### YamlStoreInstaller
A generic base class for installing YAML files from an embedded directory into a YAML store.

**Public Methods:**
- `install(self, overwrite: bool) -> bool` - Install all YAML files from the embedded directory into the store

#### YamlStore
A generic base class for managing YAML files in a directory.

**Public Methods:**
- `list(self) -> list[str]` - List all available object names in the store
- `load(self, id: str) -> T` - Load an object by its ID from the YAML store
- `save(self, id: str, obj: T) -> None` - Save an object to the YAML store with the given ID
- `delete(self, id: str) -> None` - Delete an object by its ID from the YAML store
- `exists(self, id: str) -> bool` - Check if an object exists in the YAML store by its ID

### Constants

#### `T`

#### `T`

#### `T`

## Dependencies

### External Dependencies
- `adapter`
- `base`
- `installer`
- `pathlib`
- `typing`
- `yaml`

## Exports

This module exports the following symbols:

- `YamlStore`
- `YamlStoreAdapter`
- `YamlStoreInstaller`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
