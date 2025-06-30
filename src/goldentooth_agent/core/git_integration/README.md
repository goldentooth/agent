# Git Integration

Git Integration module

## Overview

- **Complexity**: Low
- **Files**: 2 Python files
- **Lines of Code**: ~307
- **Classes**: 1
- **Functions**: 5

## API Reference

### Classes

#### GitDataSync
Service for syncing knowledge base data to a Git repository.

**Public Methods:**
- `setup_git_repository()`
- `sync_to_git()`
- `get_git_status()`

## Dependencies

### External Dependencies
- `antidote`
- `datetime`
- `document_store`
- `embeddings`
- `git_sync`
- `pathlib`
- `paths`
- `subprocess`
- `typing`

## Exports

This module exports the following symbols:

- `GitDataSync`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
