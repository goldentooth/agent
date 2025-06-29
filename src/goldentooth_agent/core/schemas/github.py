from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class GitHubOrg(BaseModel):
    """Represents a GitHub organization."""

    id: str = Field(..., description="GitHub organization ID/login")
    name: str | None = Field(None, description="Display name of the organization")
    description: str | None = Field(None, description="Organization description")
    url: str = Field(..., description="GitHub URL")
    public_repos: int = Field(0, description="Number of public repositories")
    created_at: datetime | None = Field(None, description="When the org was created")
    updated_at: datetime | None = Field(
        None, description="When the org was last updated"
    )

    # RAG metadata
    last_synced: datetime | None = Field(
        None, description="When this data was last synced"
    )
    rag_include: bool = Field(True, description="Whether to include in RAG indexing")


class GitHubOrgAdapter:
    """Adapter for GitHubOrg YAML serialization."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GitHubOrg:
        """Create a GitHubOrg from dictionary data."""
        # Handle datetime strings
        for date_field in ["created_at", "updated_at", "last_synced"]:
            if data.get(date_field) and isinstance(data[date_field], str):
                data[date_field] = datetime.fromisoformat(
                    data[date_field].replace("Z", "+00:00")
                )

        return GitHubOrg(**data)

    @classmethod
    def to_dict(cls, id: str, obj: GitHubOrg) -> dict[str, Any]:
        """Convert GitHubOrg to dictionary for YAML serialization."""
        data = obj.model_dump()

        # Convert datetime objects to ISO strings
        for date_field in ["created_at", "updated_at", "last_synced"]:
            if data.get(date_field):
                data[date_field] = data[date_field].isoformat()

        return data


class GitHubRepo(BaseModel):
    """Represents a GitHub repository."""

    id: str = Field(..., description="Repository ID (org/repo format)")
    name: str = Field(..., description="Repository name")
    full_name: str = Field(..., description="Full name including org")
    description: str | None = Field(None, description="Repository description")
    url: str = Field(..., description="GitHub URL")
    clone_url: str = Field(..., description="Git clone URL")
    default_branch: str = Field("main", description="Default branch name")
    language: str | None = Field(None, description="Primary programming language")
    languages: list[str] = Field(default_factory=list, description="All languages used")
    topics: list[str] = Field(
        default_factory=list, description="Repository topics/tags"
    )

    # Statistics
    stars: int = Field(0, description="Number of stars")
    forks: int = Field(0, description="Number of forks")
    open_issues: int = Field(0, description="Number of open issues")
    size_kb: int = Field(0, description="Repository size in KB")

    # Status
    is_private: bool = Field(False, description="Whether repo is private")
    is_fork: bool = Field(False, description="Whether repo is a fork")
    is_archived: bool = Field(False, description="Whether repo is archived")

    # Timestamps
    created_at: datetime | None = Field(None, description="When repo was created")
    updated_at: datetime | None = Field(None, description="When repo was last updated")
    pushed_at: datetime | None = Field(None, description="When last push occurred")

    # RAG metadata
    last_synced: datetime | None = Field(
        None, description="When this data was last synced"
    )
    rag_include: bool = Field(True, description="Whether to include in RAG indexing")
    priority: str = Field("medium", description="RAG priority: low, medium, high")


class GitHubRepoAdapter:
    """Adapter for GitHubRepo YAML serialization."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GitHubRepo:
        """Create a GitHubRepo from dictionary data."""
        # Handle datetime strings
        for date_field in ["created_at", "updated_at", "pushed_at", "last_synced"]:
            if data.get(date_field) and isinstance(data[date_field], str):
                data[date_field] = datetime.fromisoformat(
                    data[date_field].replace("Z", "+00:00")
                )

        return GitHubRepo(**data)

    @classmethod
    def to_dict(cls, id: str, obj: GitHubRepo) -> dict[str, Any]:
        """Convert GitHubRepo to dictionary for YAML serialization."""
        data = obj.model_dump()

        # Convert datetime objects to ISO strings
        for date_field in ["created_at", "updated_at", "pushed_at", "last_synced"]:
            if data.get(date_field):
                data[date_field] = data[date_field].isoformat()

        return data
