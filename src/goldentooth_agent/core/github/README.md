# Github

Github module

## Overview

- **Complexity**: Low
- **Files**: 2 Python files
- **Lines of Code**: ~287
- **Classes**: 1
- **Functions**: 10

## API Reference

### Classes

#### GitHubClient
Client for retrieving and syncing GitHub organization and repository data.

**Public Methods:**
- `get_authenticated_user_orgs()`
- `get_organization()`
- `get_organization_repos()`
- `get_user_repos()`
- `sync_organization()`
- `sync_user_repos()`
- `get_api_rate_limit()`

## Dependencies

### External Dependencies
- `antidote`
- `datetime`
- `document_store`
- `github`
- `github_client`
- `os`
- `schemas`
- `typing`

## Exports

This module exports the following symbols:

- `GitHubClient`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
