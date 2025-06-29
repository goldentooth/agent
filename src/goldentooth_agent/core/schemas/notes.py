from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Note(BaseModel):
    """Represents a note or document in the knowledge base."""

    id: str = Field(..., description="Note identifier")
    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Note content (markdown supported)")

    # Categorization
    category: str = Field("general", description="Note category")
    tags: list[str] = Field(default_factory=list, description="Note tags")

    # Status and priority
    status: str = Field("active", description="Note status: active, archived, draft")
    priority: str = Field("medium", description="Priority: low, medium, high, critical")

    # Authorship and source
    author: str | None = Field(None, description="Note author")
    source: str | None = Field(None, description="Source of information")
    source_url: str | None = Field(None, description="URL to source if applicable")

    # Relationships
    related_notes: list[str] = Field(
        default_factory=list, description="Related note IDs"
    )
    related_services: list[str] = Field(
        default_factory=list, description="Related service IDs"
    )
    related_nodes: list[str] = Field(
        default_factory=list, description="Related node IDs"
    )

    # Timestamps
    created_at: datetime | None = Field(None, description="When note was created")
    updated_at: datetime | None = Field(None, description="When note was last updated")

    # RAG metadata
    last_synced: datetime | None = Field(
        None, description="When this data was last synced"
    )
    rag_include: bool = Field(True, description="Whether to include in RAG indexing")
    rag_priority: str = Field("medium", description="RAG priority: low, medium, high")

    # Search and discovery
    keywords: list[str] = Field(default_factory=list, description="Keywords for search")
    summary: str | None = Field(None, description="Brief summary for RAG context")


class NoteAdapter:
    """Adapter for Note YAML serialization."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Note:
        """Create a Note from dictionary data."""
        # Handle datetime strings
        for date_field in ["created_at", "updated_at", "last_synced"]:
            if data.get(date_field) and isinstance(data[date_field], str):
                data[date_field] = datetime.fromisoformat(
                    data[date_field].replace("Z", "+00:00")
                )

        return Note(**data)

    @classmethod
    def to_dict(cls, id: str, obj: Note) -> dict[str, Any]:
        """Convert Note to dictionary for YAML serialization."""
        data = obj.model_dump()

        # Convert datetime objects to ISO strings
        for date_field in ["created_at", "updated_at", "last_synced"]:
            if data.get(date_field):
                data[date_field] = data[date_field].isoformat()

        return data
