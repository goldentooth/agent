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
- `get_authenticated_user_orgs(self) -> list[dict[str, Any]]` - Get organizations for the authenticated user
- `get_organization(self, org_name: str) -> dict[str, Any]` - Get data for a specific organization
- `get_organization_repos(self, org_name: str, repo_type: str, include_forks: bool, max_repos: int | None) -> list[dict[str, Any]]` - Get repositories for an organization
- `get_user_repos(self, username: str | None, repo_type: str, include_forks: bool, max_repos: int | None) -> list[dict[str, Any]]` - Get repositories for a user (defaults to authenticated user)
- `sync_organization(self, org_name: str, include_repos: bool) -> dict[str, Any]` - Sync an organization and optionally its repositories to the document store
- `sync_user_repos(self, username: str | None, max_repos: int | None) -> dict[str, Any]` - Sync user repositories to the document store
- `get_api_rate_limit(self) -> dict[str, Any]` - Get current GitHub API rate limit status

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
