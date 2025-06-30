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
- `github_orgs(self) -> YamlStore[Any]` - Access to GitHub organizations store
- `github_repos(self) -> YamlStore[Any]` - Access to GitHub repositories store
- `goldentooth_nodes(self) -> YamlStore[Any]` - Access to Goldentooth nodes store
- `goldentooth_services(self) -> YamlStore[Any]` - Access to Goldentooth services store
- `notes(self) -> YamlStore[Any]` - Access to notes store
- `list_all_documents(self) -> dict[str, list[str]]` - List all documents across all stores
- `get_document_count(self) -> dict[str, int]` - Get count of documents in each store
- `get_store_paths(self) -> dict[str, Path]` - Get the file system paths for each document store
- `document_exists(self, store_type: str, document_id: str) -> bool` - Check if a document exists in a specific store
- `get_document_path(self, store_type: str, document_id: str) -> Path` - Get the file system path for a specific document
- `delete_document(self, store_type: str, document_id: str) -> None` - Delete a document from a specific store
- `get_all_document_paths(self) -> list[Path]` - Get paths to all YAML documents across all stores
- `clear_all_documents(self) -> dict[str, int]` - Clear all documents from all stores (for testing/reset)

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
