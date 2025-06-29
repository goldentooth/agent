import os
from datetime import datetime
from typing import Any

from antidote import inject, injectable
from github.Organization import Organization
from github.Repository import Repository

from github import Github

from ..document_store import DocumentStore
from ..schemas.github import GitHubOrg, GitHubRepo


@injectable
class GitHubClient:
    """Client for retrieving and syncing GitHub organization and repository data."""

    def __init__(self, document_store: DocumentStore = inject.me()) -> None:
        """Initialize the GitHub client.

        Args:
            document_store: Document store for persisting GitHub data
        """
        self.document_store = document_store

        # Initialize GitHub API client
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise ValueError(
                "GitHub token is required. Set GITHUB_TOKEN environment variable."
            )

        self._github = Github(github_token)

    def get_authenticated_user_orgs(self) -> list[dict[str, Any]]:
        """Get organizations for the authenticated user.

        Returns:
            List of organization data dictionaries
        """
        try:
            user = self._github.get_user()
            orgs = []

            for org in user.get_orgs():
                org_data = self._extract_org_data(org)
                orgs.append(org_data)

            return orgs

        except Exception as e:
            raise ValueError(f"Failed to retrieve user organizations: {e}") from e

    def get_organization(self, org_name: str) -> dict[str, Any]:
        """Get data for a specific organization.

        Args:
            org_name: Name of the organization

        Returns:
            Organization data dictionary
        """
        try:
            org = self._github.get_organization(org_name)
            return self._extract_org_data(org)

        except Exception as e:
            raise ValueError(
                f"Failed to retrieve organization '{org_name}': {e}"
            ) from e

    def get_organization_repos(
        self,
        org_name: str,
        repo_type: str = "all",
        include_forks: bool = False,
        max_repos: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get repositories for an organization.

        Args:
            org_name: Name of the organization
            repo_type: Type of repos to retrieve ('all', 'public', 'private')
            include_forks: Whether to include forked repositories
            max_repos: Maximum number of repositories to retrieve

        Returns:
            List of repository data dictionaries
        """
        try:
            org = self._github.get_organization(org_name)
            repos = []

            count = 0
            for repo in org.get_repos(type=repo_type):
                if not include_forks and repo.fork:
                    continue

                repo_data = self._extract_repo_data(repo)
                repos.append(repo_data)

                count += 1
                if max_repos and count >= max_repos:
                    break

            return repos

        except Exception as e:
            raise ValueError(
                f"Failed to retrieve repositories for '{org_name}': {e}"
            ) from e

    def get_user_repos(
        self,
        username: str | None = None,
        repo_type: str = "all",
        include_forks: bool = False,
        max_repos: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get repositories for a user (defaults to authenticated user).

        Args:
            username: Username (None for authenticated user)
            repo_type: Type of repos to retrieve ('all', 'public', 'private')
            include_forks: Whether to include forked repositories
            max_repos: Maximum number of repositories to retrieve

        Returns:
            List of repository data dictionaries
        """
        try:
            if username:
                user = self._github.get_user(username)
            else:
                user = self._github.get_user()

            repos = []
            count = 0

            for repo in user.get_repos(type=repo_type):
                if not include_forks and repo.fork:
                    continue

                repo_data = self._extract_repo_data(repo)
                repos.append(repo_data)

                count += 1
                if max_repos and count >= max_repos:
                    break

            return repos

        except Exception as e:
            username_str = username or "authenticated user"
            raise ValueError(
                f"Failed to retrieve repositories for '{username_str}': {e}"
            ) from e

    def sync_organization(
        self, org_name: str, include_repos: bool = True
    ) -> dict[str, Any]:
        """Sync an organization and optionally its repositories to the document store.

        Args:
            org_name: Name of the organization to sync
            include_repos: Whether to also sync repositories

        Returns:
            Dictionary with sync results
        """
        try:
            # Get organization data
            org_data = self.get_organization(org_name)

            # Create GitHubOrg object and save to document store
            github_org = GitHubOrg(**org_data)
            self.document_store.github_orgs.save(org_name, github_org)

            synced_repos = 0
            if include_repos:
                # Get and sync repositories
                repos_data = self.get_organization_repos(
                    org_name, max_repos=50
                )  # Reasonable limit

                for repo_data in repos_data:
                    # Create repo ID for storage (replace special characters)
                    repo_id = repo_data["full_name"].replace("/", "_").replace("-", "_")

                    # Create GitHubRepo object and save
                    github_repo = GitHubRepo(**repo_data)
                    self.document_store.github_repos.save(repo_id, github_repo)
                    synced_repos += 1

            return {
                "organization": org_name,
                "org_synced": True,
                "repos_synced": synced_repos,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "organization": org_name,
                "org_synced": False,
                "repos_synced": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def sync_user_repos(
        self, username: str | None = None, max_repos: int | None = None
    ) -> dict[str, Any]:
        """Sync user repositories to the document store.

        Args:
            username: Username (None for authenticated user)
            max_repos: Maximum number of repositories to sync

        Returns:
            Dictionary with sync results
        """
        try:
            username_display = username or "authenticated user"
            repos_data = self.get_user_repos(
                username=username, include_forks=False, max_repos=max_repos
            )

            synced_count = 0
            for repo_data in repos_data:
                # Create repo ID for storage
                repo_id = repo_data["full_name"].replace("/", "_").replace("-", "_")

                # Create GitHubRepo object and save
                github_repo = GitHubRepo(**repo_data)
                self.document_store.github_repos.save(repo_id, github_repo)
                synced_count += 1

            return {
                "user": username_display,
                "repos_synced": synced_count,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "user": username or "authenticated user",
                "repos_synced": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _extract_org_data(self, org: Organization) -> dict[str, Any]:
        """Extract data from a GitHub Organization object.

        Args:
            org: GitHub Organization object

        Returns:
            Dictionary with organization data
        """
        return {
            "id": org.login,
            "name": org.name,
            "description": org.description,
            "url": org.html_url,
            "public_repos": org.public_repos,
            "created_at": org.created_at,
            "updated_at": org.updated_at,
            "last_synced": datetime.now(),
            "rag_include": True,
        }

    def _extract_repo_data(self, repo: Repository) -> dict[str, Any]:
        """Extract data from a GitHub Repository object.

        Args:
            repo: GitHub Repository object

        Returns:
            Dictionary with repository data
        """
        # Get languages (this makes an API call)
        try:
            languages_dict = repo.get_languages()
            languages = list(languages_dict.keys())
            primary_language = (
                max(languages_dict.items(), key=lambda x: x[1])[0]
                if languages_dict
                else None
            )
        except Exception:
            languages = []
            primary_language = None

        # Get topics
        try:
            topics = repo.get_topics()
        except Exception:
            topics = []

        return {
            "id": repo.full_name,
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "url": repo.html_url,
            "clone_url": repo.clone_url,
            "default_branch": repo.default_branch,
            "language": primary_language,
            "languages": languages,
            "topics": topics,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "open_issues": repo.open_issues_count,
            "size_kb": repo.size,
            "is_private": repo.private,
            "is_fork": repo.fork,
            "is_archived": repo.archived,
            "created_at": repo.created_at,
            "updated_at": repo.updated_at,
            "pushed_at": repo.pushed_at,
            "last_synced": datetime.now(),
            "rag_include": True,
            "priority": "high" if repo.stargazers_count > 10 else "medium",
        }

    def get_api_rate_limit(self) -> dict[str, Any]:
        """Get current GitHub API rate limit status.

        Returns:
            Dictionary with rate limit information
        """
        try:
            rate_limit = self._github.get_rate_limit()
            return {
                "core_limit": rate_limit.core.limit,
                "core_remaining": rate_limit.core.remaining,
                "core_reset": rate_limit.core.reset,
                "search_limit": rate_limit.search.limit,
                "search_remaining": rate_limit.search.remaining,
                "search_reset": rate_limit.search.reset,
            }
        except Exception as e:
            return {"error": str(e)}
