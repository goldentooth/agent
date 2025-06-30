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
- `from_dict(cls, data: dict[str, Any]) -> GoldentoothNode` - Create a GoldentoothNode from dictionary data
- `to_dict(cls, id: str, obj: GoldentoothNode) -> dict[str, Any]` - Convert GoldentoothNode to dictionary for YAML serialization

#### GoldentoothService
Represents a service in the Goldentooth ecosystem.

#### GoldentoothServiceAdapter
Adapter for GoldentoothService YAML serialization.

**Public Methods:**
- `from_dict(cls, data: dict[str, Any]) -> GoldentoothService` - Create a GoldentoothService from dictionary data
- `to_dict(cls, id: str, obj: GoldentoothService) -> dict[str, Any]` - Convert GoldentoothService to dictionary for YAML serialization

#### Note
Represents a note or document in the knowledge base.

#### NoteAdapter
Adapter for Note YAML serialization.

**Public Methods:**
- `from_dict(cls, data: dict[str, Any]) -> Note` - Create a Note from dictionary data
- `to_dict(cls, id: str, obj: Note) -> dict[str, Any]` - Convert Note to dictionary for YAML serialization

#### GitHubOrg
Represents a GitHub organization.

#### GitHubOrgAdapter
Adapter for GitHubOrg YAML serialization.

**Public Methods:**
- `from_dict(cls, data: dict[str, Any]) -> GitHubOrg` - Create a GitHubOrg from dictionary data
- `to_dict(cls, id: str, obj: GitHubOrg) -> dict[str, Any]` - Convert GitHubOrg to dictionary for YAML serialization

#### GitHubRepo
Represents a GitHub repository.

#### GitHubRepoAdapter
Adapter for GitHubRepo YAML serialization.

**Public Methods:**
- `from_dict(cls, data: dict[str, Any]) -> GitHubRepo` - Create a GitHubRepo from dictionary data
- `to_dict(cls, id: str, obj: GitHubRepo) -> dict[str, Any]` - Convert GitHubRepo to dictionary for YAML serialization

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
