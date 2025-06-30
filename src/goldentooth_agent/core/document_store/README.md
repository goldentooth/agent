# Document Store

Document Store module

## Overview

- **Complexity**: Low
- **Files**: 2 Python files
- **Lines of Code**: ~172
- **Classes**: 1
- **Functions**: 15

## API Reference

### Classes

#### DocumentStore
Centralized document store managing all knowledge base YAML documents.

**Public Methods:**
- `github_orgs()`
- `github_repos()`
- `goldentooth_nodes()`
- `goldentooth_services()`
- `notes()`
- `list_all_documents()`
- `get_document_count()`
- `get_store_paths()`
- `document_exists()`
- `get_document_path()`
- `delete_document()`
- `get_all_document_paths()`
- `clear_all_documents()`

### Constants

#### `T`

## Dependencies

### External Dependencies
- `antidote`
- `document_store`
- `pathlib`
- `paths`
- `schemas`
- `typing`
- `yaml_store`

## Exports

This module exports the following symbols:

- `DocumentStore`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
