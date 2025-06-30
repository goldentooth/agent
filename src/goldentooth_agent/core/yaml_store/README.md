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
- `from_dict()`
- `to_dict()`

#### YamlStoreInstaller
A generic base class for installing YAML files from an embedded directory into a YAML store.

**Public Methods:**
- `install()`

#### YamlStore
A generic base class for managing YAML files in a directory.

**Public Methods:**
- `list()`
- `load()`
- `save()`
- `delete()`
- `exists()`

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
