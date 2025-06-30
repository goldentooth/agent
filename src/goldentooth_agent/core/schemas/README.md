# Schemas

Schemas module

## Overview

- **Complexity**: High
- **Files**: 4 Python files
- **Lines of Code**: ~313
- **Classes**: 10
- **Functions**: 10

## API Reference

### Classes

#### GoldentoothNode
Represents a node in the Goldentooth cluster.

#### GoldentoothNodeAdapter
Adapter for GoldentoothNode YAML serialization.

**Public Methods:**
- `from_dict()`
- `to_dict()`

#### GoldentoothService
Represents a service in the Goldentooth ecosystem.

#### GoldentoothServiceAdapter
Adapter for GoldentoothService YAML serialization.

**Public Methods:**
- `from_dict()`
- `to_dict()`

#### Note
Represents a note or document in the knowledge base.

#### NoteAdapter
Adapter for Note YAML serialization.

**Public Methods:**
- `from_dict()`
- `to_dict()`

#### GitHubOrg
Represents a GitHub organization.

#### GitHubOrgAdapter
Adapter for GitHubOrg YAML serialization.

**Public Methods:**
- `from_dict()`
- `to_dict()`

#### GitHubRepo
Represents a GitHub repository.

#### GitHubRepoAdapter
Adapter for GitHubRepo YAML serialization.

**Public Methods:**
- `from_dict()`
- `to_dict()`

## Dependencies

### External Dependencies
- `datetime`
- `github`
- `goldentooth`
- `notes`
- `pydantic`
- `typing`

## Exports

This module exports the following symbols:

- `GitHubOrgAdapter`
- `GitHubRepoAdapter`
- `GoldentoothNodeAdapter`
- `GoldentoothServiceAdapter`
- `NoteAdapter`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
