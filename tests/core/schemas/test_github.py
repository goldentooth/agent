from datetime import UTC, datetime

from goldentooth_agent.core.schemas.github import (
    GitHubOrg,
    GitHubOrgAdapter,
    GitHubRepo,
    GitHubRepoAdapter,
)
from goldentooth_agent.core.yaml_store import YamlStoreAdapter


class TestGitHubOrgAdapter:
    """Test suite for GitHubOrgAdapter."""

    def test_adapter_implements_protocol(self):
        """Test that GitHubOrgAdapter implements YamlStoreAdapter protocol."""
        assert isinstance(GitHubOrgAdapter, YamlStoreAdapter)

    def test_from_dict_creates_github_org(self):
        """Test that from_dict creates a valid GitHubOrg."""
        data = {
            "id": "goldentooth",
            "name": "Goldentooth Systems",
            "description": "Distributed systems and automation",
            "url": "https://github.com/goldentooth",
            "public_repos": 15,
            "created_at": "2020-01-15T10:30:00Z",
            "updated_at": "2025-01-01T15:45:00Z",
            "rag_include": True,
        }

        org = GitHubOrgAdapter.from_dict(data)

        assert isinstance(org, GitHubOrg)
        assert org.id == "goldentooth"
        assert org.name == "Goldentooth Systems"
        assert org.public_repos == 15
        assert org.rag_include is True
        assert isinstance(org.created_at, datetime)
        assert isinstance(org.updated_at, datetime)

    def test_to_dict_converts_github_org(self):
        """Test that to_dict converts GitHubOrg to dictionary."""
        now = datetime.now(UTC)
        org = GitHubOrg(
            id="testorg",
            name="Test Organization",
            description="A test org",
            url="https://github.com/testorg",
            public_repos=5,
            created_at=now,
            last_synced=now,
            rag_include=True,
        )

        data = GitHubOrgAdapter.to_dict("testorg", org)

        assert data["id"] == "testorg"
        assert data["name"] == "Test Organization"
        assert data["public_repos"] == 5
        assert data["rag_include"] is True
        assert isinstance(data["created_at"], str)
        assert isinstance(data["last_synced"], str)

    def test_roundtrip_conversion(self):
        """Test that adapter can roundtrip convert org to dict and back."""
        original_data = {
            "id": "roundtrip",
            "name": "Roundtrip Test",
            "url": "https://github.com/roundtrip",
            "public_repos": 3,
            "rag_include": False,
        }

        org = GitHubOrgAdapter.from_dict(original_data)
        converted_data = GitHubOrgAdapter.to_dict("roundtrip", org)
        restored_org = GitHubOrgAdapter.from_dict(converted_data)

        assert restored_org.id == original_data["id"]
        assert restored_org.name == original_data["name"]
        assert restored_org.public_repos == original_data["public_repos"]
        assert restored_org.rag_include == original_data["rag_include"]


class TestGitHubRepoAdapter:
    """Test suite for GitHubRepoAdapter."""

    def test_adapter_implements_protocol(self):
        """Test that GitHubRepoAdapter implements YamlStoreAdapter protocol."""
        assert isinstance(GitHubRepoAdapter, YamlStoreAdapter)

    def test_from_dict_creates_github_repo(self):
        """Test that from_dict creates a valid GitHubRepo."""
        data = {
            "id": "goldentooth/agent",
            "name": "agent",
            "full_name": "goldentooth/agent",
            "description": "Goldentooth intelligent agent system",
            "url": "https://github.com/goldentooth/agent",
            "clone_url": "https://github.com/goldentooth/agent.git",
            "default_branch": "main",
            "language": "Python",
            "languages": ["Python", "Shell", "Dockerfile"],
            "topics": ["ai", "automation", "agent"],
            "stars": 42,
            "forks": 8,
            "open_issues": 3,
            "size_kb": 2048,
            "is_private": False,
            "is_fork": False,
            "is_archived": False,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2025-01-01T12:00:00Z",
            "pushed_at": "2025-01-01T11:30:00Z",
            "rag_include": True,
            "priority": "high",
        }

        repo = GitHubRepoAdapter.from_dict(data)

        assert isinstance(repo, GitHubRepo)
        assert repo.id == "goldentooth/agent"
        assert repo.name == "agent"
        assert repo.language == "Python"
        assert repo.languages == ["Python", "Shell", "Dockerfile"]
        assert repo.topics == ["ai", "automation", "agent"]
        assert repo.stars == 42
        assert repo.is_private is False
        assert repo.rag_include is True
        assert repo.priority == "high"
        assert isinstance(repo.created_at, datetime)
        assert isinstance(repo.updated_at, datetime)
        assert isinstance(repo.pushed_at, datetime)

    def test_to_dict_converts_github_repo(self):
        """Test that to_dict converts GitHubRepo to dictionary."""
        now = datetime.now(UTC)
        repo = GitHubRepo(
            id="test/repo",
            name="repo",
            full_name="test/repo",
            url="https://github.com/test/repo",
            clone_url="https://github.com/test/repo.git",
            language="JavaScript",
            languages=["JavaScript", "TypeScript"],
            topics=["web", "frontend"],
            stars=10,
            created_at=now,
            last_synced=now,
            rag_include=True,
            priority="medium",
        )

        data = GitHubRepoAdapter.to_dict("test_repo", repo)

        assert data["id"] == "test/repo"
        assert data["name"] == "repo"
        assert data["language"] == "JavaScript"
        assert data["languages"] == ["JavaScript", "TypeScript"]
        assert data["topics"] == ["web", "frontend"]
        assert data["stars"] == 10
        assert data["rag_include"] is True
        assert data["priority"] == "medium"
        assert isinstance(data["created_at"], str)
        assert isinstance(data["last_synced"], str)

    def test_roundtrip_conversion(self):
        """Test that adapter can roundtrip convert repo to dict and back."""
        original_data = {
            "id": "owner/project",
            "name": "project",
            "full_name": "owner/project",
            "url": "https://github.com/owner/project",
            "clone_url": "https://github.com/owner/project.git",
            "language": "Go",
            "topics": ["backend", "api"],
            "stars": 100,
            "is_private": True,
            "rag_include": True,
            "priority": "low",
        }

        repo = GitHubRepoAdapter.from_dict(original_data)
        converted_data = GitHubRepoAdapter.to_dict("owner_project", repo)
        restored_repo = GitHubRepoAdapter.from_dict(converted_data)

        assert restored_repo.id == original_data["id"]
        assert restored_repo.name == original_data["name"]
        assert restored_repo.language == original_data["language"]
        assert restored_repo.topics == original_data["topics"]
        assert restored_repo.stars == original_data["stars"]
        assert restored_repo.is_private == original_data["is_private"]
        assert restored_repo.rag_include == original_data["rag_include"]
        assert restored_repo.priority == original_data["priority"]

    def test_handles_optional_fields(self):
        """Test that adapter handles missing optional fields gracefully."""
        minimal_data = {
            "id": "minimal/repo",
            "name": "repo",
            "full_name": "minimal/repo",
            "url": "https://github.com/minimal/repo",
            "clone_url": "https://github.com/minimal/repo.git",
        }

        repo = GitHubRepoAdapter.from_dict(minimal_data)

        assert repo.description is None
        assert repo.language is None
        assert repo.languages == []
        assert repo.topics == []
        assert repo.stars == 0
        assert repo.is_private is False
        assert repo.created_at is None
        assert repo.rag_include is True
        assert repo.priority == "medium"
